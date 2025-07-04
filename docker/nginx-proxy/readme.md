# NGINX Proxy Manager (w/ Tinyauth)

[NPM](https://nginxproxymanager.com/) is a easily configurable reverse-proxy to setup subdomains for all your services in a single web ui. It also has really nice integrations with Let's Encrypt SSL certificates.

Alongside this, I use [Tinyauth](https://tinyauth.app/) as a simple identity provider for my services. You can read more about that setup on their [docs](https://tinyauth.app/docs/getting-started.html) (it is so very simple). This is not required for NPM to run, so you are able to easily just remove the container if you so wish.

![NPM Interface](./image.png)

## Installation

```
sudo docker compose up -d
```

See: [docker-compose.yml](./docker-compose.yml)

## Themepark

This service uses a custom [Theme.park](https://theme-park.dev) theme, which is mounted as a volume. You can get it from [here](https://docs.theme-park.dev/themes/nginx-proxy-manager/).
