#!/usr/bin/env bash
set -Eeuo pipefail

usage() { echo "usage: $0 <dist-dir>" >&2; exit 2; }
[[ $# -eq 1 ]] || usage
dist="$(realpath "$1")"
iso="$dist/zigux-cachyos-exhaustive-x86_64.iso"
imgz="$dist/zigux-cachyos-exhaustive-x86_64.img.zst"
[[ -s "$iso" && -s "$imgz" ]] || { echo 'media files are missing' >&2; exit 1; }

img="$RUNNER_TEMP/zigux-cachyos-test.img"
zstd -T0 --sparse -d -f "$imgz" -o "$img"

run_test() {
  local name=$1; shift
  local log="$dist/qemu-${name}.log"
  set +e
  timeout 1200 qemu-system-x86_64 \
    -machine q35,accel=tcg -cpu max -m 4096 -smp 2 \
    -display none -serial stdio -monitor none -no-reboot \
    "$@" >"$log" 2>&1
  local rc=$?
  set -e
  if grep -q ZIGUX_CACHYOS_MEDIA_BOOT_OK "$log"; then
    echo success | tee "$dist/QEMU_${name^^}_RESULT"
    return 0
  fi
  echo "failed rc=$rc" | tee "$dist/QEMU_${name^^}_RESULT"
  tail -n 160 "$log" >&2 || true
  return 1
}

# The ISO's BIOS path uses Syslinux; the persistent image's BIOS path uses GRUB.
# Both default to CachyOS LTS. The exhaustive kernels have separate direct PID 1
# smoke gates and remain explicit experimental choices on the finished media.
run_test iso -boot d -cdrom "$iso"
run_test disk -drive "file=$img,format=raw,if=virtio,cache=unsafe"
rm -f "$img"
sha256sum "$dist"/qemu-*.log "$dist"/QEMU_*_RESULT > "$dist/QEMU-SHA256SUMS"
