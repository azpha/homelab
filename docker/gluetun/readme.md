# Gluetun

[Gluetun](https://github.com/qdm12/gluetun) is a lightweight VPN client to connect stuff like Docker containers to multiple VPN providers.

## Installation

```
sudo docker compose up -d
```

See [docker-compose.yml](./docker-compose.yml).

## Environment Variables

- `VPN_SERVICE_PROVIDER` ([docs](https://github.com/qdm12/gluetun-wiki/tree/main/setup/providers))
- `VPN_TYPE`
- `WIREGUARD_PRIVATE_KEY`
- `WIREGUARD_ADDRESSES`
- `TZ`
- `SERVER_COUNTRIES`
- `SERVER_CITIES`
- `SERVER_HOSTNAMES`
