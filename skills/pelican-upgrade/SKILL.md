---
name: pelican-upgrade
description: Upgrade a Pelican panel, its Wings nodes, or the PHP under them — pre-flight checks for beta migration bugs, DB and APP_KEY backup, manual or scripted panel upgrade, checksum-verified Wings swap, verification and rollback.
triggers:
  - /pelican-upgrade
  - upgrade pelican
  - update wings
  - pelican update
---

# /pelican-upgrade — panel + Wings upgrades

Health checks referenced below are in `/pelican`. Building a panel from a
pinned commit is in `/pelican-deploy`.

## Before anything

- **Pelican is beta.** Every tag is `1.0.0-betaNN`; migrations have shipped
  with data-loss bugs. Read the release notes **and** open issues for the
  target version (search "migration", "upgrade") before upgrading. If a
  release is broken, wait or use a pinned-main build with green CI.
- **PHP first.** Panel main requires PHP `^8.4 || ^8.5` (pelican/panel PR
  #2563). If the box is on an older PHP, install 8.4, switch php-fpm in the
  vhost and `update-alternatives --set php /usr/bin/php8.4`, confirm the
  current panel still works, then upgrade the panel.
- Upgrade the panel and Wings in the same window; check the release notes for
  a required Wings version.

## Pre-flight (mandatory — `migrate` is one-way)

```bash
cd /var/www/pelican
php artisan p:info > /root/pelican-preupgrade-info.txt
mysqldump --single-transaction --routines --triggers <panel db> | zstd > /root/pelican-$(date +%F).sql.zst
cp -p .env /root/pelican-$(date +%F).env
tar --zstd -cf /root/pelican-webroot-$(date +%F).tar.zst -C /var/www pelican
```

Copy the dump and the `.env` copy **off the box** before continuing. `.env`
holds `APP_KEY`; without it the DB dump cannot decrypt node tokens, API keys or
2FA secrets.

Record current versions for the rollback note: panel version (from `p:info`),
`/usr/local/bin/wings version` on each node.

## Panel — manual upgrade

```bash
cd /var/www/pelican
php artisan down
curl -fsSLO https://github.com/pelican/panel/releases/latest/download/panel.tar.gz   # or the pinned build
curl -fsSLO https://github.com/pelican/panel/releases/latest/download/checksum.txt
cat checksum.txt; sha256sum panel.tar.gz       # must match
tar -xzf panel.tar.gz && rm panel.tar.gz checksum.txt
COMPOSER_ALLOW_SUPERUSER=1 composer install --no-dev --optimize-autoloader    # never `composer update`
php artisan storage:link
php artisan optimize:clear && php artisan filament:optimize
php artisan migrate --seed --force 2>&1 | tee /root/pelican-upgrade-migrate.log
chmod -R 755 storage/* bootstrap/cache/ && chown -R www-data:www-data /var/www/pelican
php artisan queue:restart
php artisan up
```

If `migrate` fails halfway: **stop**. Leave the panel down, go to Rollback. Do
not re-run hoping it completes; a half-applied migration is not reliably
re-runnable.

Official script alternative — read it before running it:

```bash
curl -fsSL https://pelican.dev/updatePanel.sh -o /root/updatePanel.sh && less /root/updatePanel.sh
bash /root/updatePanel.sh
```

Plugins live in `/var/www/pelican/plugins`; manage with `php artisan p:plugin:*`
and check each is compatible with the new version.

## Wings

Per node, one at a time. Running game servers restart (Wings restores each
server's saved state on start), so warn players first.

```bash
REL=https://github.com/pelican/wings/releases/latest/download   # pinned: .../releases/download/<tag>
cd /tmp
curl -fsSLO "$REL/wings_linux_amd64"
curl -fsSLO "$REL/checksums.txt"
grep ' wings_linux_amd64$' checksums.txt | sha256sum -c -
cp -p /usr/local/bin/wings /usr/local/bin/wings.prev     # keep until verified
systemctl stop wings
install -m 755 wings_linux_amd64 /usr/local/bin/wings
systemctl start wings
/usr/local/bin/wings version
journalctl -u wings -n 50 --no-pager     # "creating new server object from API response" per server
```

## Verify

1. All `/pelican` health checks: services active, HealthQueueJob every minute,
   `/login` 200, application API 401, Wings API 401, no new errors in
   `laravel-*.log`.
2. `php artisan p:info` shows the new version.
3. Every server: `php pelican-power.php <id> status` matches its pre-upgrade
   state; a running server's game port proven reachable (packet capture).
4. Log in through the browser with a 2FA user; open one server's console and
   file manager.

Only then delete `wings.prev` and the webroot tarball (keep the DB dump).

## Rollback

**Never `php artisan migrate:rollback`.** Restore instead:

```bash
php artisan down
mysql -e "DROP DATABASE <panel db>; CREATE DATABASE <panel db>;"
zstd -dc /root/pelican-<date>.sql.zst | mysql <panel db>
rm -rf /var/www/pelican && tar --zstd -xf /root/pelican-webroot-<date>.tar.zst -C /var/www
cp -p /root/pelican-<date>.env /var/www/pelican/.env
cd /var/www/pelican && php artisan optimize:clear && php artisan queue:restart && php artisan up
# each node:
systemctl stop wings && mv /usr/local/bin/wings.prev /usr/local/bin/wings && systemctl start wings
```

Then re-run Verify. The `DROP DATABASE` is irreversible: confirm the dump
restores (e.g. into a scratch DB) before dropping.
