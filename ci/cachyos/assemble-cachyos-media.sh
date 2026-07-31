#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  echo "usage: $0 <packages-dir> <cachyos-live-iso-dir> <dist-dir> [disk-size-gib]" >&2
  exit 2
}
[[ $# -ge 3 && $# -le 4 ]] || usage
packages="$(realpath "$1")"
iso_src="$(realpath "$2")"
dist="$(realpath -m "$3")"
disk_gib="${4:-32}"
[[ "$disk_gib" =~ ^[0-9]+$ ]] && (( disk_gib >= 20 )) || {
  echo "disk size must be an integer of at least 20 GiB" >&2
  exit 2
}
mkdir -p "$dist"
workspace="$(realpath "$(dirname "$0")/../..")"

# Image construction requires pacman, pacstrap, archiso, loop devices and GRUB.
# A privileged Arch container keeps those mutable tools out of the Ubuntu host.
docker run --rm --privileged --network host \
  -e DISK_GIB="$disk_gib" \
  -e SOURCE_REF="${SOURCE_REF:-unknown}" \
  -e CACHYOS_ISO_REF="${CACHYOS_ISO_REF:-unknown}" \
  -v /dev:/dev \
  -v "$workspace:/workspace" \
  -v "$packages:/packages:ro" \
  -v "$iso_src:/cachyos-live-iso:ro" \
  -v "$dist:/dist" \
  archlinux:base-devel bash /workspace/ci/cachyos/assemble-in-arch.sh
