# caddy

[Caddy](https://caddyserver.com/) is a lightweight HTTP server that I use to reverse proxy to all of my services across my homelab with domains & SSL.

You can see my config in the [Caddyfile](./config/Caddyfile). This container also builds with the Cloudflare DNS plugin, as you can see in the [Dockerfile](./dockerfile).

## Installation

```
sudo docker compose up -d
```

See: [docker-compose.yml](./docker-compose.yml)
