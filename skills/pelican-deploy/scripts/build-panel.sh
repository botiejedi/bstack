#!/bin/sh
# Build a Pelican panel.tar.gz from a pinned main commit, the same way
# .github/workflows/release.yaml builds release tarballs.
#   build-panel.sh <commit-sha>     (output: /root/pelican-build/panel.tar.gz)
# Pick a commit with green CI first:
#   gh api repos/pelican/panel/commits/<sha>/check-runs
set -eu
SHA=${1:?usage: build-panel.sh <commit-sha>}
B=/root/pelican-build
rm -rf "$B"; mkdir -p "$B"; cd "$B"

if [ ! -x /usr/local/bin/composer ]; then
  EXPECTED=$(curl -fsS https://composer.github.io/installer.sig)
  curl -fsS -o composer-setup.php https://getcomposer.org/installer
  ACTUAL=$(php8.4 -r "echo hash_file('sha384','composer-setup.php');")
  [ "$EXPECTED" = "$ACTUAL" ] || { echo "composer installer checksum mismatch"; exit 1; }
  php8.4 composer-setup.php --quiet --install-dir=/usr/local/bin --filename=composer
  rm composer-setup.php
fi

# Latest Node 22, verified against the official SHASUMS256.txt.
curl -fsSL -o SHASUMS256.txt https://nodejs.org/dist/latest-v22.x/SHASUMS256.txt
NODE_TAR=$(awk '/ node-v22\.[0-9.]+-linux-x64\.tar\.xz$/ {print $2; exit}' SHASUMS256.txt)
[ -n "$NODE_TAR" ] || { echo "no linux-x64 tarball in SHASUMS256.txt"; exit 1; }
NODE=${NODE_TAR%.tar.xz}
curl -fsSL -o "$NODE_TAR" "https://nodejs.org/dist/latest-v22.x/$NODE_TAR"
grep " $NODE_TAR\$" SHASUMS256.txt | sha256sum -c -
tar -xJf "$NODE_TAR"; rm "$NODE_TAR" SHASUMS256.txt
export PATH="$B/$NODE/bin:$PATH"

curl -fsSL -o src.tar.gz "https://codeload.github.com/pelican/panel/tar.gz/$SHA"
mkdir src; tar -xzf src.tar.gz -C src --strip-components=1; rm src.tar.gz
cd src
# composer before yarn: the Tailwind build imports vendor/filament/... CSS.
COMPOSER_ALLOW_SUPERUSER=1 php8.4 /usr/local/bin/composer install --no-interaction --no-progress --no-autoloader --no-scripts --no-dev -q
corepack enable --install-directory "$B/$NODE/bin" yarn
COREPACK_ENABLE_DOWNLOAD_PROMPT=0 yarn install --frozen-lockfile --silent
yarn build >/dev/null
rm -rf node_modules vendor tests CODE_OF_CONDUCT.md CONTRIBUTING.md phpunit.xml shell.nix
tar -czf "$B/panel.tar.gz" * .env.example
cd "$B"; rm -rf src "$NODE"
ls -la "$B"; echo BUILD_OK
