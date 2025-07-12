# RomM

[The RomM Project](https://romm.app) is a self-hosted manager for all of your personally owned ROMs. It has EmulatorJS implemented, which allows you to play your ROMs over your browser.

![RomM Interface](./image.png)

## Installation

```
sudo docker compose up -d
```

See [docker-compose.yml](./docker-compose.yml).

## Environment Variables

- `ROMM_AUTH_SECRET_KEY` - for auth salting, use `openssl rand -hex 32` to generate
- `IGDB_CLIENT_ID` - your Twitch application's client ID
- `IGDB_CLIENT_SECRET` - your Twitch application's client secret
- `MOBYGAMES_API_KEY` - your Moby Games API key
- `STEAMGRIDDB_API_KEY` - your SteamGridDB API key
- `SCREENSCRAPER_USER` - your ScreenScraper username
- `SCREENSCRAPER_PASSWORD` - your ScreenScraper password
- `RETROACHIEVEMENTS_API_KEY` - your RetroAchievements API key
- `LIBRARY_PATH` - the path to your ROM library, using RomM's file structure
