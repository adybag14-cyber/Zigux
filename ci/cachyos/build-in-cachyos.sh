#!/usr/bin/env bash
set -Eeuo pipefail
[[ $# -eq 3 ]] || { echo 'usage: build-in-cachyos.sh <source> <profile> <dist>' >&2; exit 2; }
src=$(realpath "$1")
profile=$2
dist=$(realpath -m "$3")
case "$profile" in allmodconfig|allyesconfig) ;; *) exit 2 ;; esac
workspace=$(realpath "$(dirname "$0")/../..")
work="${RUNNER_TEMP:?}/cachyos-builder-${profile}"
mkdir -p "$dist" "$work"
[[ "${SOURCE_SHA:?}" =~ ^[0-9a-f]{40}$ ]] || exit 2
test "$(git -C "$src" rev-parse HEAD)" = "$SOURCE_SHA"

docker pull archlinux:base-devel
image_id=$(docker image inspect --format '{{.Id}}' archlinux:base-devel)
printf '%s\n' "$image_id" > "$dist/build-container-${profile}.txt"
docker run --rm \
  -e SOURCE_SHA -e PROFILE="$profile" -e RUNNER_TEMP=/build \
  -e ZIGUX_CACHYOS_BUILD=1 -e BUSYBOX_STATIC=/smoke/busybox \
  -v "$workspace:/workspace:ro" -v "$src:/linux:ro" \
  -v "$dist:/dist" -v "$work:/build" \
  -v /usr/bin/busybox:/smoke/busybox:ro \
  "$image_id" bash -Eeuo pipefail -c '
    pacman -Syu --noconfirm --needed curl gnupg
    bash /workspace/ci/cachyos/setup-cachyos-repo.sh
    pacman -Syu --noconfirm --needed \
      base-devel bc bison cpio elfutils flex git kmod mkinitcpio openssl \
      pahole python qemu-system-x86 rsync xz zstd
    git config --global --add safe.directory /linux
    { cat /etc/os-release; pacman -Q gcc binutils glibc pahole mkinitcpio; } \
      > "/dist/build-toolchain-${PROFILE}.txt"
    bash /workspace/ci/cachyos/build-kernel-package.sh /linux "$PROFILE" /dist
  '
