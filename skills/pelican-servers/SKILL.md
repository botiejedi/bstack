---
name: pelican-servers
private: false
description: Manage the lifecycle of game servers on a Pelican panel — eggs (import, fixing startup), allocations, creating, parking, redeploying and retiring servers, backups, and SteamCMD auto-update by cron.
triggers:
  - /pelican-servers
  - new game server
  - pelican egg
  - park the server
  - retire the server
  - game server backup
  - auto-update game server
---

# /pelican-servers — game server lifecycle

Power actions, health checks and `scripts/pelican-power.php` live in `/pelican`.
Every start/stop below goes through the panel or that script, never `docker`.

## Eggs

- Pelican imports PTDL_v1/v2 (Pterodactyl) and PLCN_v1/v2 eggs. Import via
  Admin → Eggs → Import (file or URL), or in code:
  ```php
  app(App\Services\Eggs\Sharing\EggImporterService::class)
      ->fromContent($json, App\Enums\EggFormat::JSON, $existingEgg /* or null */);
  ```
- Community eggs: `github.com/pelican-eggs/*` (legacy: `parkervcp/eggs`).
  Read the egg's install script before importing; it runs as root.
- **Check the startup actually consumes the variables the egg shows.** A
  Palworld egg exposed `AUTO_UPDATE` but its startup never ran steamcmd, so the
  toggle was inert. A gated prefix on the startup command fixes it without a
  reinstall:
  ```sh
  if [ "${AUTO_UPDATE}" = "1" ]; then ./steamcmd/steamcmd.sh +force_install_dir /home/container +login anonymous +app_update ${SRCDS_APPID} +quit; fi;
  ```
- **Prefer editing the startup command over reinstalling.** Egg reinstall
  scripts can overwrite configs and leave files owned by root.

## Allocations

- One allocation per IP:port the game listens on. For remote players over
  Tailscale, give the server two allocations on the same port: the LAN IP and
  the tailnet IP. No socat, no forwarders.
- Leave RCON deliberately unallocated: it stays on loopback inside the
  container, unreachable from outside.
- Tailnet allocations depend on Wings starting after `tailscaled` — see the
  boot-race note in `/pelican`.

## Create a server — checklist

1. **Node headroom.** Pelican refuses creation over node memory × overallocate.
   Check Admin → Nodes before choosing limits. Never set memory `0` (that is
   unlimited).
2. **Allocation(s)** free on the node (add them first under the node's
   Allocations tab).
3. **Egg variables**, including required secrets (server/admin passwords).
   Store secret values in a password manager, never in notes. Eggs that pass
   passwords on the command line expose them in `docker top` / `ps` on the
   node — prefer config-file variables where the egg offers them.
4. Create, wait for the install to finish (server console shows install
   output, then "Offline").
5. **Verify volume ownership** matches Wings `system.user` uid:gid (commands in
   `/pelican` → Gotchas). A root-owned volume = a server that can't save.
6. Start via the panel or `pelican-power.php <id> start`, then prove
   reachability with the packet capture from `/pelican`.

## Park, redeploy, retire

**Park** (reversible, keeps everything):

1. Stop via the panel.
2. Edit Build Configuration: memory `1024` (not `0`!), lower disk and CPU.
3. Note in the server's description why and when it was parked.

**Redeploy a parked server:** raise the limits back, start via the panel,
verify ownership and reachability.

**Retire** (irreversible — the panel deletes the volume):

1. Stop via the panel.
2. Archive the volume off-box first:
   ```bash
   V=<volumes-dir>/<server-uuid>; A=<name>-$(date +%F).tar.zst
   tar --zstd -cf "/root/$A" -C "$(dirname "$V")" "$(basename "$V")"
   sha256sum "/root/$A" > "/root/$A.sha256"
   # copy both to the destination, then ON THE DESTINATION:
   sha256sum -c "$A.sha256" && zstd -t "$A"
   ```
3. Next to the archive write a `MANIFEST` with: server name, egg, original
   UUID, allocations, startup command, egg variables (no secret values),
   archive sha256, and restore steps (create server with same egg → stop →
   extract into the new volume → chown to Wings uid:gid → start).
4. Only after the destination check passes: delete the server in the panel.

## Backups

- Wings stores local backups in `system.backup_directory` (`config.yml`) —
  on the same disk as the game data, so they are not off-box.
- Panel backup driver: Admin → Settings (local or S3). After changing it:
  ```bash
  cd /var/www/pelican && php artisan config:clear && systemctl restart pelican-queue
  ```
- Scheduled backups: per server, Schedules → task "Create backup". Set a backup
  limit on the server or the task fails silently once full.
- **A game volume with no off-box copy is not backed up.** Say so plainly when
  reporting backup state; a local Wings backup does not survive the disk.

## Auto-update pattern for SteamCMD games

Host cron script, one per server. Logic:

1. `export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`
   (cron's PATH lacks `/usr/sbin`).
2. Steam's public build:
   ```bash
   REMOTE=$(curl -fsS "https://api.steamcmd.net/v1/info/$APPID" | jq -r ".data[\"$APPID\"].depots.branches.public.buildid")
   ```
3. Installed build:
   ```bash
   LOCAL=$(awk -F'"' '/"buildid"/ {print $4; exit}' "$VOL/steamapps/appmanifest_$APPID.acf")
   ```
4. Stop here unless `REMOTE` is a number greater than `LOCAL`.
5. Stop here unless `pelican-power.php <id> status` says `running`. **Never
   start a stopped server** — stopped is a decision someone made.
6. Back up the save directory (timestamped tar), then
   `pelican-power.php <id> restart` (the egg's `AUTO_UPDATE` startup runs
   steamcmd).
7. Circuit breaker: count failed attempts in a state file; after 3, stop trying
   and log loudly until a human clears it.
8. Log one line per run with REMOTE, LOCAL and the action taken.
