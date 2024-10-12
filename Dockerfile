FROM python:3.12-alpine

WORKDIR /app

COPY *.py .
COPY requirements.txt .

ENV TERM xterm
ENV PYTHONUNBUFFERED 1

ARG TARGETPLATFORM
ARG BUILD_DATE
ARG COMMIT

RUN apk add --no-cache --virtual .build-deps build-base linux-headers libffi-dev openssl-dev && \
    python -m pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install gunicorn && \
    pip install -r requirements.txt && \
    apk del .build-deps

EXPOSE 5000

CMD ["gunicorn", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "2", "main:app", "-b", ":5000"]