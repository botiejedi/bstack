---
name: pelican-deploy
private: false
description: Deploy a new Pelican panel or Wings node (pelican.dev), build a panel from a pinned commit when a release is broken, or migrate an existing Pterodactyl panel + Wings to Pelican side by side with a verified cutover.
triggers:
  - /pelican-deploy
  - install pelican
  - new wings node
  - migrate pterodactyl
  - pterodactyl to pelican
---

# /pelican-deploy — new instance or Pterodactyl migration

Day-to-day operation and health checks live in `/pelican`. Run its health
checks at the end of every section here.

## Fresh panel (Debian 12/13)

Debian 12 ships PHP 8.2; Pelican needs 8.4+. Use packages.sury.org.

```bash
apt install -y ca-certificates curl gnupg lsb-release unzip nginx mariadb-server redis-server
curl -fsSLo /usr/share/keyrings/sury-php.gpg https://packages.sury.org/php/apt.gpg
echo "deb [signed-by=/usr/share/keyrings/sury-php.gpg] https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/sury-php.list
apt update
apt install -y php8.4-{fpm,cli,gd,mysql,mbstring,bcmath,xml,curl,zip,intl,sqlite3}
update-alternatives --set php /usr/bin/php8.4     # if more than one PHP is installed
```

Composer, signature-checked:

```bash
EXPECTED=$(curl -fsS https://composer.github.io/installer.sig)
curl -fsS -o composer-setup.php https://getcomposer.org/installer
[ "$EXPECTED" = "$(php -r "echo hash_file('sha384','composer-setup.php');")" ] || { echo MISMATCH; exit 1; }
php composer-setup.php --quiet --install-dir=/usr/local/bin --filename=composer && rm composer-setup.php
```

Panel:

```bash
mkdir -p /var/www/pelican && cd /var/www/pelican
curl -fsSLO https://github.com/pelican/panel/releases/latest/download/panel.tar.gz
curl -fsSLO https://github.com/pelican/panel/releases/latest/download/checksum.txt
cat checksum.txt; sha256sum panel.tar.gz       # must match before extracting
tar -xzf panel.tar.gz && rm panel.tar.gz checksum.txt
COMPOSER_ALLOW_SUPERUSER=1 composer install --no-dev --optimize-autoloader
php artisan p:environment:setup                # generates APP_KEY
```

**Back up `APP_KEY` off the box now.** It decrypts node tokens, API keys and
2FA secrets; losing it means re-pairing every node and every user re-enrolling.

Then either the web installer at `https://<panel>/installer`, or set the DB /
Redis / mail values in `.env` and run `php artisan migrate --seed --force`.
Finish:

```bash
php artisan storage:link && php artisan optimize:clear && php artisan filament:optimize
chmod -R 755 storage/* bootstrap/cache/
chown -R www-data:www-data /var/www/pelican
chown root:www-data .env && chmod 640 .env
php artisan p:environment:queue-service --service-name=pelican-queue --user=www-data --group=www-data
echo '* * * * * www-data php /var/www/pelican/artisan schedule:run >/dev/null 2>&1' > /etc/cron.d/pelican
```

`p:environment:queue-service` writes `ExecStart=/usr/bin/php`; set the
`update-alternatives` above first or the queue runs on the wrong PHP.

nginx vhost essentials:

```nginx
server {
    listen 80;
    server_name <panel host>;
    root /var/www/pelican/public;
    index index.php;
    client_max_body_size 100m;
    location / { try_files $uri $uri/ /index.php?$query_string; }
    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_pass unix:/run/php/php8.4-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        fastcgi_param PHP_VALUE "upload_max_filesize = 100M \n post_max_size = 100M";
    }
    location ~ /\.ht { deny all; }
}
```

Behind a tunnel or reverse proxy: `TRUSTED_PROXIES=*` and
`APP_URL=https://<public host>` in `.env`, then `php artisan config:clear`.

Any new LXC: set an explicit `nameserver`. Inheriting a Tailscale-owned host
`resolv.conf` once killed DNS in a guest that wasn't on the tailnet.

## Pinned-main build (when the release is broken)

Release tarballs come from `.github/workflows/release.yaml`: composer install
(no-dev, no autoloader, no scripts) → Node 22 `yarn install --frozen-lockfile`
→ `yarn build` → strip dev files → tar. Composer must run before yarn because
the Tailwind build imports `vendor/filament/...` CSS.

1. Pick a commit with green CI:
   `gh api repos/pelican/panel/commits/<sha>/check-runs --jq '.check_runs[] | [.name,.conclusion] | @tsv'`
2. Copy `scripts/build-panel.sh` to a Linux box with php8.4 and run
   `sh build-panel.sh <sha>`. Output: `/root/pelican-build/panel.tar.gz`. Use it
   in place of the release tarball.

Build on Linux. Windows clones fail on long test filenames unless
`git config core.longpaths true`.

## Wings node

Docker is required (`curl -fsSL https://get.docker.com | sh`, or distro
packages — review before running).

```bash
REL=https://github.com/pelican/wings/releases/latest/download   # pinned: .../releases/download/<tag>
cd /tmp
curl -fsSLO "$REL/wings_linux_amd64"
curl -fsSLO "$REL/checksums.txt"
grep ' wings_linux_amd64$' checksums.txt | sha256sum -c -
install -m 755 wings_linux_amd64 /usr/local/bin/wings
```

1. Panel: Admin → Nodes → create the node, then open its Configuration tab.
2. Paste the generated config into `/etc/pelican/config.yml`, `chmod 600`.
3. Install `scripts/wings.service` as `/etc/systemd/system/wings.service`. The
   `ExecStartPre` tailnet wait only matters when servers publish on a
   Tailscale IP; it is harmless otherwise (gives up after 60 s and starts).
4. `systemctl daemon-reload && systemctl enable --now wings`
5. Node shows a green heart in the panel; Wings API answers 401.

## Migrating from Pterodactyl (verified procedure)

Side by side: the old panel stays untouched until cutover. **A half-failed
migration is not reliably re-runnable — always migrate a copy of the DB.**

1. **Check the Pelican release for migration bugs first.** v1.0.0-beta38
   cannot migrate a Pterodactyl DB that has a root admin (halts halfway; fixed
   by pelican/panel PR #2613, merged 2026-10-04), drops 2FA secrets (#2611) and
   deletes legitimate subusers (#2612). Use a release containing those fixes,
   or a pinned-main build. Search open issues for "migration" before starting.
2. **Inventory the old DB** (save the output to compare later):
   ```sql
   select id, use_totp from users;
   select count(*) from subusers;
   select count(*) from servers; select count(*) from allocations;
   select count(*) from eggs; select count(*) from egg_variables;
   select count(*) from server_variables;
   ```
3. **Install Pelican** in `/var/www/pelican` alongside (fresh-panel steps above,
   minus setup/installer). PHP 8.4 co-exists with 8.3.
4. **Copy the DB:**
   ```bash
   mysql -e "CREATE DATABASE pelican; GRANT ALL ON pelican.* TO '<panel db user>'@'<same host as its existing grant>';"
   mysqldump --single-transaction --routines --triggers panel | mysql pelican
   ```
5. **`.env`** — copy secrets file-to-file on the box, never echo them:
   - `APP_KEY` = the OLD panel's key (mandatory)
   - `DB_CONNECTION=mariadb`, `DB_DATABASE=pelican`, existing DB user/password
   - `APP_INSTALLED=true`
   - `REDIS_DB` / `REDIS_CACHE_DB` = unused numbers (e.g. 2 / 3) so the two
     panels don't share Redis
   - `CACHE_STORE=redis`, `QUEUE_CONNECTION=redis`, `SESSION_DRIVER=redis`
   - `MAIL_MAILER`, `TRUSTED_PROXIES`, `CAPTCHA_TURNSTILE_ENABLED=false`
6. **Migrate:**
   ```bash
   cd /var/www/pelican && php artisan migrate --seed --force 2>&1 | tee /root/pelican-migrate.log
   php artisan storage:link && php artisan optimize:clear && php artisan filament:optimize
   chmod -R 755 storage/* bootstrap/cache/ && chown -R www-data:www-data /var/www/pelican
   ```
7. **Verify:**
   - Step-2 counts match; `use_totp` users still have `totp_secret`.
   - Nests became egg `tags`; locations became node tags; `startup` became
     `startup_commands`.
   - Secrets decrypt, via the models:
     ```bash
     php artisan tinker --execute='echo strlen(App\Models\Node::find(1)->daemon_token), PHP_EOL; echo strlen(App\Models\ApiKey::first()?->token ?? ""), PHP_EOL;'
     ```
     Use the model, not raw `decrypt()` — the cast stores values unserialized,
     so `decrypt()` false-fails.
   - One "The payload is invalid" from migration
     `2024_05_31_204646_fix_old_encrypted_values` is harmless when that user's
     `totp_secret` was NULL.
8. **Test vhost** on a spare port (e.g. `listen 8081`, php8.4-fpm socket):
   `/login` → 200, `/api/application/nodes` with `Accept: application/json` →
   401.
9. **Cutover** — two panels must never drive Wings at once:
   ```bash
   systemctl disable --now pteroq
   rm /etc/cron.d/<pterodactyl schedule file>      # or remove the line from crontab -u www-data
   php artisan p:environment:queue-service --service-name=pelican-queue --user=www-data --group=www-data
   echo '* * * * * www-data php /var/www/pelican/artisan schedule:run >/dev/null 2>&1' > /etc/cron.d/pelican
   # move the pelican vhost to :80, disable the pterodactyl vhost
   nginx -t && systemctl reload nginx
   ```
10. **Wings swap** on every node (download + verify as in "Wings node" above):
    ```bash
    mkdir -p /etc/pelican && cp -p /etc/pterodactyl/config.yml /etc/pelican/config.yml
    cp scripts/wings.service /etc/systemd/system/wings.service   # WorkingDirectory=/etc/pelican
    systemctl stop wings
    cp -p /usr/local/bin/wings /usr/local/bin/wings.pterodactyl
    install -m 755 /tmp/wings_linux_amd64 /usr/local/bin/wings
    systemctl daemon-reload && systemctl start wings
    journalctl -u wings -n 50 --no-pager
    ```
    The copied config keeps explicit pterodactyl paths, `pterodactyl_nw` and
    user `pterodactyl`: no data moves, and no new token is needed when
    `APP_KEY` was kept. `remote:` stays valid if the panel URL is unchanged.
    Healthy: `creating new server object from API response` per server. Wings
    restores each server's previous state, so running servers restart.
11. **Verify** each server with `pelican-power.php <id> status` (from
    `/pelican`); public panel 200; Wings API 401.
12. **Port local scripts:**
    - `Pterodactyl\Repositories\Wings\DaemonPowerRepository::send()` →
      `App\Repositories\Daemon\DaemonServerRepository::power()`
    - `Pterodactyl\Models\*` → `App\Models\*`
    - Egg import: `App\Services\Eggs\Sharing\EggImporterService::fromContent($json, App\Enums\EggFormat::JSON, ?Egg)`
      — no nest argument.
13. **Only after days of clean running**, remove: old webroot, `panel` DB,
    `pteroq` unit, old vhost, old PHP, `wings.pterodactyl`, `/etc/pterodactyl`.
    **Never the volumes directory.** Never `migrate:rollback` a migrated
    Pterodactyl DB.

Do not leave a Pterodactyl Wings behind a Pelican panel long-term — the
daemon API changed (pelican/panel PR #2576). Swap both at cutover.
