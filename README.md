# rsdash

Personal RuneScape activity/goal tracker. Single-user, RS3-first (OSRS support planned).

## Features
- Skill XP tracking (auto-synced from the public hiscores)
- Boss/activity kill counts (same source)
- Weekly task checklist, resets Tuesday 6 PM Mountain Time
- Custom goals with progress notes
- Drops/activity feed from your Adventurer's Log (RS3 only — requires the log's privacy set to "Public" in-game)

## Running locally

```bash
cp .env.example .env
# edit .env and set RSN_RS3=YourDisplayName
docker compose up --build
```

Then visit http://localhost:8082

## Data sources
- Hiscores: `secure.runescape.com/m=hiscore/index_lite.json` (RS3) / `m=hiscore_oldschool/index_lite.json` (OSRS) — official, public, named skills/activities in the JSON.
- Adventurer's Log: `apps.runescape.com/runemetrics/profile/profile` — unofficial/undocumented but confirmed live; the RuneMetrics website itself was retired but this JSON endpoint still responds. May stop working without notice.

## Deployment (Portainer)

1. In Portainer: **Stacks → Add stack → Repository**
2. Repository URL: `https://github.com/Jake-Porter/rsdash`, reference `refs/heads/main`, compose path `docker-compose.yml`
3. Under **Environment variables**, set at least `RSN_RS3` (and `RSN_OSRS` later, once OSRS support lands). `TZ`, `HISCORES_POLL_MINUTES`, `FEED_POLL_MINUTES` already have sane defaults in the compose file.
4. Before deploying, create the data directory on the host so the SQLite DB persists across stack rebuilds: `mkdir -p /opt/rsdash/data` on srv-docker-02.
5. Deploy the stack. Portainer will clone the repo and build the image from the included `Dockerfile`.
6. To pick up future code changes, use Portainer's **Pull and redeploy** on the stack (re-clones the repo and rebuilds).

Runs as `ctnr-rsdash-01` on port `8082`, matching the `ctnr-<app>-01` naming used by other containers on this host.
