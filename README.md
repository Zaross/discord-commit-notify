# 🔔 Discord Notification API

<h1 align="left">
    <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg"/>
    <img src="https://img.shields.io/github/forks/zaross/discord-commit-notify"/>
    <img src="https://img.shields.io/github/license/zaross/discord-commit-notify"/>
    <img src="https://img.shields.io/github/stars/zaross/discord-commit-notify"/>
    <img src="https://img.shields.io/github/issues/zaross/discord-commit-notify"/>
    <img src="https://img.shields.io/github/last-commit/Zaross/discord-commit-notify/main"/>
</h1>

---

# 🔗 Optimizing Your Discord Notification Experience

The Discord Commit Notify is an API written in Python🐍. It was written because the standard GitHub notifications in Discord are not the best.

---

# ✨ Features
- **Better Overview of Commits in Discord**: The API provides a clear display of commits directly in Discord.
- **Health Checks**: Monitors the status of the API and webhooks to ensure everything is functioning smoothly.
- **Easy to Use**: The API is designed with user-friendliness in mind, making integration and usage straightforward.

---

> [!NOTE] 
> You can use Docker Compose. it is important that you modify the config.json file accordingly.

---

> [!TIP]  
> An example for the config.json:
>```
>{
>  "repositories": {
>    "zaros/discord-commit-notify": {
>      "secret": "123456",
>      "discord_webhook_url": "https://discord.com/api/webhooks/" 
>    },
>    "example-orga/example-repo": {
>      "secret": "123456",
>      "discord_webhook_url": "https://discord.com/api/webhooks/" 
>    }
>  },
>  "unknown_webhook_url": "https://discord.com/api/webhooks/" 
>}
>```
> the unknown_webhook_url is for warnings that a person tried to use your API.

---

# ⚙️ How to install

When you are on your server. go to the directory where it is saved. enter the following command and confirm:
```
git clone https://github.com/Zaross/discord-commit-notify.git
```

> [!WARNING]
> Make sure you have installed git on your system.

After downloading the repository, configure your config.json. and start your container with:
```
docker compose up -d
```
Now you are finished, and the API is started.

---

# 🚀 How to use

If you run it via the Docker Compose unchanged, then you can simply call the API with your ip followed by the port and /webhook.
Example:
ip:5000/webhook

to check if it is active, for example for monitoring with Uptime Kuma., you can enter your ip followed by the port and /health 
Example:
ip:5000/health

---

# 🖥️ Supported OS

The Docker image which can be found on Docker Hub was built for the following versions: linux/386,linux/amd64,linux/arm/v6,linux/arm/v7,linux/arm64/v8,linux/ppc64le,linux/s390x

---

# ☁️ Using cloudflare for security reasons

If you want to running cloudflare for the docker container, simple add following to the docker-compose.yml file:

```
cloudflared:
    restart: unless-stopped
    container_name: cloudflare_github_api
    image: cloudflare/cloudflared:latest
    command: tunnel --no-autoupdate run --token <YOUR TOKEN>
    networks:
      - github_api
```

> [!WARNING]
> Replace 'Your-Token' in the cloudflared with your Cloudflare Zero Trust token.

