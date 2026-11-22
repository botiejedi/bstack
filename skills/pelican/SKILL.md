---
name: pelican
private: false
description: Operate an existing Pelican game-server panel and its Wings nodes (pelican.dev, the Pterodactyl fork) — health checks, power actions, logs and troubleshooting for "the game server". Routes deploys, server lifecycle and upgrades to pelican-deploy, pelican-servers and pelican-upgrade.
triggers:
  - /pelican
  - pelican panel
  - pelican wings
  - wings
  - game server
  - game server down
  - restart the game server
---

# /pelican — operate a Pelican panel + Wings

## Route first

| Task | Skill |
| --- | --- |
| New panel or node, or migrating from Pterodactyl | `/pelican-deploy` |
| Create, park, retire, back up or auto-update a game server; eggs; allocations | `/pelican-servers` |
| Upgrading the panel, Wings or PHP | `/pelican-upgrade` |
| Status, power, logs, "it's down", anything else | this skill |

Read-only first. A game server is someone's live session; a stop or restart is
visible to players.

## Architecture

- **Panel**: Laravel 13 + Filament, PHP 8.4+, MariaDB/MySQL/Postgres, Redis,
  nginx + php-fpm, in `/var/www/pelican`. Admin UI at `/admin`, server UI at
  `/server`.
  - Queue worker: systemd unit `pelican-queue`.
  - Scheduler: `* * * * * www-data php /var/www/pelican/artisan schedule:run`
    in a cron file.
  - Logs: `storage/logs/laravel-*.log`.
- **Wings**: Go daemon, systemd unit `wings`, drives Docker. API on `:8080`,
  SFTP on `:2022`. Config `/etc/pelican/config.yml` — Wings does **not** fall
  back to `/etc/pterodactyl`.
  - Defaults: `/var/lib/pelican/{volumes,backups,archives}`, network
    `pelican_nw` / bridge `pelican0` on `172.18.0.0/16`, system user `pelican`.
  - A config migrated from Pterodactyl keeps explicit pterodactyl paths,
    `pterodactyl_nw` and user `pterodactyl`. That is fine; leave it.
- The panel controls Wings. Wings never acts on its own except restoring saved
  server state when it starts.

## Health checks

Run on the panel host unless noted. Substitute the PHP version in use.

```bash
systemctl is-active pelican-queue nginx php8.4-fpm
journalctl -u pelican-queue -n 5     # a Spatie HealthQueueJob every minute = cron + queue both work
cd /var/www/pelican && php artisan p:info
curl -s -o /dev/null -w '%{http_code}\n' -H 'Accept: application/json' https://<panel>/api/application/nodes   # 401 = alive
tail -n 50 storage/logs/laravel-$(date +%F).log
```

On each Wings node:

```bash
systemctl is-active wings docker
/usr/local/bin/wings version          # subcommand; prints e.g. "wings v1.0.0-beta29"
curl -s -o /dev/null -w '%{http_code}\n' http://<wings>:8080/   # 401 = alive
journalctl -u wings -n 50 --no-pager
docker ps                             # container names are server UUIDs
```

A healthy Wings start logs `creating new server object from API response` once
per server: that proves panel ↔ Wings auth works.

## Power actions — always through the panel

**Never `docker stop` / `docker restart` a game container.** Wings runs with
`crash_detection.detect_clean_exit_as_crash: true`, so any out-of-band stop is
logged as a crash and may be auto-restarted.

Use `scripts/pelican-power.php` from this skill. Copy it to the panel host and
run as root or www-data:

```bash
php pelican-power.php <server-id> status
php pelican-power.php <server-id> start|stop|restart
```

`<server-id>` is the numeric panel ID (Admin → Servers), not the UUID.

Alternatives:

```bash
# Client API, with an account key (prefix pacc_)
curl -X POST -H "Authorization: Bearer $KEY" -H 'Accept: application/json' -H 'Content-Type: application/json' \
  -d '{"signal":"restart"}' https://<panel>/api/client/servers/<uuid_short>/power

php artisan p:server:bulk-power    # many servers at once; see --help
```

API key prefixes: `pacc_` = client/account, `papp_` = application. Old
Pterodactyl `ptla_` / `ptlc_` keys keep working after a migration if `APP_KEY`
was preserved. Never paste a key value into a note or a command that lands in
shell history; read it from a file or env var.

## Gotchas (each verified in production)

- **`memory = 0` means UNLIMITED, not none.** To park a server, set memory to
  `1024`, never `0`.
- **Volume ownership after any egg install.** An install once left a volume
  `root:root` and the server silently couldn't save. Check it matches Wings
  `system.user` uid:gid and fix:
  ```bash
  grep -A4 '^  user:' /etc/pelican/config.yml      # system.user uid/gid
  stat -c '%u:%g' <volumes-dir>/<server-uuid>
  chown -R <uid>:<gid> <volumes-dir>/<server-uuid>
  ```
- **`docker ps` "Up" says nothing about reachability.** Neither does a bound
  UDP port. Prove a game port with a capture inside the container's network
  namespace while a client on another machine connects:
  ```bash
  PID=$(docker inspect -f '{{.State.Pid}}' <server-uuid>)
  nsenter -t "$PID" -n tcpdump -n -i any "udp port <port>"
  ```
- **Palworld does not answer A2S queries.** A failed server-browser query is a
  false negative for it.
- **Tailscale-published servers**: add the tailnet IP as a *second* allocation
  on the server. No socat or port forwarders.
- **Boot race**: if Wings starts before `tailscaled` has assigned the tailnet
  IP, Docker fails with `cannot assign requested address` on that allocation
  and the server stays down with nothing alerting. Fix with the `ExecStartPre`
  wait in `/pelican-deploy`'s `scripts/wings.service`. After any node reboot,
  check every tailnet-published server is actually running.
- **Proxmox LXC**: `pct exec` has a PATH without `/usr/local/bin`; call
  `/usr/local/bin/wings` by absolute path.
- **Cron PATH lacks `/usr/sbin`** (e.g. `pct`). Scripts run from cron must
  `export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`.
- **Locked out by captcha**: Pelican uses Turnstile, not reCAPTCHA. Set
  `CAPTCHA_TURNSTILE_ENABLED=false` in `.env`, then `php artisan config:clear`.
- **Lost 2FA**: `php artisan p:user:disable2fa`.
- **Config changes in `.env`** need `php artisan config:clear` and
  `systemctl restart pelican-queue` (or `php artisan queue:restart`).

## Troubleshooting order

1. Panel up? (`/login` 200, API 401.) If not: nginx, php-fpm, `laravel-*.log`.
2. Queue + cron alive? (HealthQueueJob every minute.) If not: the cron file and
   `pelican-queue`.
3. Wings up and authenticated? (API 401, journal shows server objects.) If
   panel shows the node offline: `remote:` in `config.yml` must match the
   panel URL, and the node's FQDN/port must be reachable from the browser.
4. Server state per `pelican-power.php status`, then the container's console
   in the panel, then `docker logs <server-uuid>`.
5. Reachability last, with the packet capture above — never conclude from
   `docker ps`.
