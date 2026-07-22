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

Then visit http://localhost:8083

## Data sources
- Hiscores: `secure.runescape.com/m=hiscore/index_lite.json` (RS3) / `m=hiscore_oldschool/index_lite.json` (OSRS) — official, public, named skills/activities in the JSON.
- Adventurer's Log: `apps.runescape.com/runemetrics/profile/profile` — unofficial/undocumented but confirmed live; the RuneMetrics website itself was retired but this JSON endpoint still responds. May stop working without notice.

## Deployment (Portainer on srv-docker-02)

Portainer's own build step (Stacks → Repository) doesn't work against this host's Docker Engine version — it fails with a BuildKit/HTTP2 protocol error regardless of the compose file. Workaround: build the image on the host directly, then have Portainer just run the already-built image (no `build:` step involved).

1. Source lives at `/opt/rsdash/src` on srv-docker-02 (`git clone`/`git pull` from this repo).
2. Build: `cd /opt/rsdash/src && docker build -t rsdash:latest .`
3. Data directory: `mkdir -p /opt/rsdash/data` (persists the SQLite DB across redeploys).
4. In Portainer: **Stacks → Add stack → Web editor**, paste `docker-compose.yml` but replace `build: .` with `image: rsdash:latest` and add `pull_policy: never` (stops Portainer trying to pull a nonexistent registry image).
5. Set `RSN_RS3` (and `RSN_OSRS` later) in the environment variables.
6. To ship a code update: `git pull && docker build -t rsdash:latest .` on the host, then redeploy the stack in Portainer.

Runs as `ctnr-rsdash-01` on port `8083` (`8082` is already used by `ctnr-palette-01`), matching the `ctnr-<app>-01` naming used by other containers on this host.
