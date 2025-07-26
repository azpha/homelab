# caddy

[Caddy](https://caddyserver.com/) is a lightweight HTTP server that I use to reverse proxy to all of my services across my homelab with domains & SSL.

You can see an example config in the [Caddyfile](./Caddyfile.example) (rename this to `Caddyfile` so it's recognized by Caddy). This container also builds with the Cloudflare DNS plugin, as you can see in the [Dockerfile](./dockerfile).

## Installation

```
sudo docker compose up -d
```

See: [docker-compose.yml](./docker-compose.yml)
