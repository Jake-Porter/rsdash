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

## Deployment
Deployed as a Docker container on the user's own infrastructure (see project notes for the Portainer stack config used on srv-docker-02).
