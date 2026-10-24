#!/usr/bin/env bash
# Run only inside the disposable Arch/CachyOS build container.
set -Eeuo pipefail
pacman-key --init
pacman-key --populate archlinux
if ! pacman-key --list-keys F3B607488DB35A47 >/dev/null 2>&1; then
  pacman-key --recv-keys F3B607488DB35A47 --keyserver hkps://keyserver.ubuntu.com || \
    pacman-key --recv-keys F3B607488DB35A47 --keyserver hkps://keys.openpgp.org
fi
pacman-key --lsign-key F3B607488DB35A47
curl -fL --retry 4 \
  -o /tmp/cachyos-keyring.pkg.tar.zst \
  https://mirror.cachyos.org/repo/x86_64/cachyos/cachyos-keyring-20240331-1-any.pkg.tar.zst
pacman -U --noconfirm /tmp/cachyos-keyring.pkg.tar.zst
pacman-key --populate cachyos

if ! grep -q '^\[cachyos\]$' /etc/pacman.conf; then
  # Prefer the generic x86_64 CachyOS repository; no host-specific -march flags.
  # shellcheck disable=SC2016 # pacman expands $arch and $repo, not this shell.
  sed -i '/^\[core\]/i [cachyos]\nServer = https://mirror.cachyos.org/repo/$arch/$repo\n' /etc/pacman.conf
fi
