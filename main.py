import os
import json
import hmac
import hashlib
import requests
from datetime import datetime
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

with open('config.json') as config_file:
    config = json.load(config_file)

def verify_github_signature(secret, data, signature):
    """Verify the HMAC-SHA256 signature with the given secret."""
    mac = hmac.new(secret.encode('utf-8'), msg=data, digestmod=hashlib.sha256)
    expected_signature = f"sha256={mac.hexdigest()}"
    return hmac.compare_digest(expected_signature, signature)

def detect_webhook(headers):
    user_agent = headers.get("user-agent", "").lower()
    
    if "github-hookshot" in user_agent:
        return "GitHub"
    else:
        return "Unknown"

def split_text(text, limit=4000):
    """Split the text into several parts that are smaller than the character limit."""
    if len(text) <= limit:
        return [text]

    parts = []
    while len(text) > limit:
        split_index = text.rfind('\n', 0, limit)
        if split_index == -1:
            split_index = limit
        parts.append(text[:split_index])
        text = text[split_index:].lstrip()
    parts.append(text)
    return parts

@app.route('/webhook', methods=['POST'])
def webhook():
    if not request.json:
        abort(400, "Anfrage muss JSON enthalten.")

    """Main webhook endpoint that processes the incoming webhook events."""    
    if detect_webhook(request.headers) == "GitHub":
        try:
            payload = request.json
            repository = payload.get('repository', {}).get('full_name')

            if repository not in config['repositories']:
                abort(404, "Repository not configured.")

            repo_config = config['repositories'][repository]
            secret = repo_config['secret']
            discord_webhook_url = repo_config['discord_webhook_url']

            signature = request.headers.get('X-Hub-Signature-256')
            if not signature:
                abort(403, "Signature not available.")

            data = request.data

            if not verify_github_signature(secret, data, signature):
                abort(403, "Invalid signature.")

            pusher_name = payload['pusher']['name']
            commits = payload['commits']
            repository_name = payload['repository']['name']
            repository_url = payload['repository']['html_url']
            committer_avatar_url = payload['sender']['avatar_url']
            
            added_commits = []
            modified_commits = []
            removed_commits = []
            
            if pusher_name == "dependabot[bot]":
                return "Dependency updates are ignored.", 200

            for commit in commits:
                commit_url = commit['url']
                commit_message = commit['message']
                commit_id = commit['id'][:7]
                commit_author = commit['author']['name']

                if "secret" in commit_message.lower():
                    commit_message = "🕵️ This commit is secret."

                formatted_commit = f"[`{commit_id}`]({commit_url}) - {commit_message} - {commit_author}"

                if commit.get('added', []):
                    added_commits.append(formatted_commit)
                if commit.get('modified', []):
                    modified_commits.append(formatted_commit)
                if commit.get('removed', []):
                    removed_commits.append(formatted_commit)

            added_text = "\n".join(added_commits) if added_commits else "\n"
            modified_text = "\n".join(modified_commits) if modified_commits else "\n"
            removed_text = "\n".join(removed_commits) if removed_commits else "\n"

            discord_description = (
                f"**🚀 Added:**\n{added_text}\n\n"
                f"**📦 Edited:**\n{modified_text}\n\n"
                f"**⛔ Removed:**\n{removed_text}"
            )

            discord_embeds = []
            for part in split_text(discord_description):
                embed = {
                    "author": {
                        "name": "Github Notification", 
                        "icon_url": "https://cdn-icons-png.flaticon.com/512/25/25231.png",
                        "url": repository_url
                    },
                    "title": f"{repository_name}",
                    "description": part,
                    "color": 1752220,
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {
                        "text": pusher_name,
                        "icon_url": f"{committer_avatar_url}"
                    }
                }
                discord_embeds.append({"embeds": [embed]})

            for embed in discord_embeds:
                headers = {'Content-Type': 'application/json'}
                response = requests.post(discord_webhook_url, data=json.dumps(embed), headers=headers)

                if response.status_code != 204:
                    return f"Error when sending the message: {response.text}", 500

            return "Message sent successfully", 200

        except Exception as e:
            return f"Ein Fehler ist aufgetreten: {str(e)}", 500

    elif detect_webhook(request.headers) == "Unknown":
        """Process unknown webhook events."""
        try:
            ip_address = request.headers.get('X-Real-IP', 'Not available')
            user_agent = request.headers.get('User-Agent', 'Not available')
            headers = {key: value for key, value in request.headers if key.startswith('X-') or key.startswith('Content-')}
            real_ip = request.headers.get('X-Real-IP', request.remote_addr)
            body = request.get_json()
            if not real_ip:
                real_ip = ip_address
            unknown_message = (
                f"An unknown webhook event was received. It was sent via the IP address: {real_ip} \nHere are the details:\n\n"
                f"**🌐 IP-Adresse:** {ip_address}\n"
                f"**🤖 User-Agent:** {user_agent}\n"
                f"**💾 Headers: ** {json.dumps(headers, indent=2)}\n\n"
                f"**📷  Body: ** {json.dumps(body, indent=2)}\n\n"
                f"**🕔 Zeitpunkt: **{datetime.utcnow().strftime('%d.%m.%Y um %H:%M:%S')} UTC"
            )

            discord_message = {
                "embeds": [{
                    "author": {
                        "name": "Github Notification", 
                        "icon_url": "https://cdn-icons-png.flaticon.com/512/25/25231.png",
                    },
                    "title": "⚠️ Unknown event on the API",
                    "description": unknown_message,
                    "color": 1752220,
                    "timestamp": datetime.utcnow().isoformat(),
                }]
            }

            headers = {'Content-Type': 'application/json'}
            response = requests.post(config['unknown_webhook_url'], data=json.dumps(discord_message), headers=headers)

            if response.status_code == 204:
                return "unauthorized.", 200
            else:
                return f"Error when sending the message: {response.text}", 500

        except Exception as e:
            return f"An error has occurred: {str(e)}", 500
        
@app.route('/health', methods=['GET'])
def health_check():
    return "", 200
     

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
