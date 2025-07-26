# tinyauth

[Tinyauth](https://tinyauth.app/) is a short & simple auth provider, allowing you to easily log into your services using email & password or OAuth.

## Installation

```
sudo docker compose up -d
```

See: [docker-compose.yml](./docker-compose.yml)

## Environment Variables

- `APP_URL`
  - the URL you intend to use (ie. `auth.example.com`)
- `SECRET`
  - The secret you've generated using `openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32`
- `USERS`
  - your users, generated using `docker run -i -t --rm ghcr.io/steveiliop56/tinyauth:v3 user create --interactive`
