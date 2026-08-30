#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  echo "usage: $0 <linux-source> <profile: allmodconfig|allyesconfig> <output-dir>" >&2
  exit 2
}

[[ $# -eq 3 ]] || usage
src="$(realpath "$1")"
profile="$2"
dist="$(realpath -m "$3")"
case "$profile" in allmodconfig|allyesconfig) ;; *) usage ;; esac

work="${RUNNER_TEMP:-/tmp}/zigux-${profile}"
out="$work/out"
pkgroot="$work/pkgroot"
pkgbuild="$work/pkgbuild"
smoke="$work/smoke"
rm -rf "$work"
mkdir -p "$out" "$pkgroot" "$pkgbuild" "$smoke" "$dist"

cfg="$src/scripts/config"
pkgbase="linux-zigux-${profile}"
localversion="-zigux-${profile}"

export ARCH=x86
export KBUILD_BUILD_USER=zigux
export KBUILD_BUILD_HOST=github-actions
export KBUILD_BUILD_VERSION=1
export KBUILD_BUILD_TIMESTAMP='Thu Jan 1 00:00:00 UTC 1970'

make -C "$src" O="$out" "$profile"
cp "$out/.config" "$dist/config-${profile}-original"

# Keep the broad compile profile while removing mutually specialised
# instrumentation plus boot-time options proven hostile to this media lane:
# FTRACE_STARTUP_TEST wedges allmodconfig in the postponed tracer self-tests
# under QEMU TCG, while the MA35D1 console emits through console index -1 in
# allyesconfig and floods the serial log before PID 1 can be reached. KCOV's
# instrument-all path recursively faults in __sanitizer_cov_trace_pc while
# kcov_init is allocating its per-CPU IRQ areas in both exhaustive profiles.
# Built-in runtime and torture tests can consume the full QEMU smoke window
# before PID 1; retain them in the original config artifact, but not in the
# bootable kernel that must carry the CachyOS media. COMPILE_TEST also admits
# foreign-hardware drivers on x86; their built-in BMan/QMan tests require DPAA
# portals and fault during init when no such hardware exists under QEMU.
# DEBUG_KOBJECT_RELEASE defers failed-device teardown and races block-mq SRCU
# cleanup during the same allyesconfig boot, so those hazardous debug paths
# remain represented by the original artifact rather than the media kernel.
for symbol in \
  WERROR RUST GCC_PLUGINS DEBUG_INFO DEBUG_KERNEL DEBUG_KOBJECT_RELEASE DEBUG_PAGEALLOC \
  KASAN KCSAN GCOV_KERNEL MODULE_SIG_ALL COMPILE_TEST \
  FTRACE_STARTUP_TEST SERIAL_NUVOTON_MA35D1_CONSOLE KCOV \
  RUNTIME_TESTING_MENU BACKTRACE_SELF_TEST TEST_CLOCKSOURCE_WATCHDOG \
  RING_BUFFER_STARTUP_TEST BTRFS_FS_RUN_SANITY_TESTS \
  DEBUG_OBJECTS_SELFTEST DEBUG_LOCKING_API_SELFTESTS \
  LOCK_TORTURE_TEST SCF_TORTURE_TEST RCU_SCALE_TEST RCU_TORTURE_TEST RCU_REF_SCALE_TEST \
  DMAPOOL_TEST KALLSYMS_SELFTEST CPA_DEBUG OF_UNITTEST \
  FSL_BMAN_TEST FSL_BMAN_TEST_API FSL_QMAN_TEST FSL_QMAN_TEST_API FSL_QMAN_TEST_STASH; do
  "$cfg" --file "$out/.config" --disable "$symbol"
done
"$cfg" --file "$out/.config" --set-str SYSTEM_TRUSTED_KEYS ''
"$cfg" --file "$out/.config" --set-str SYSTEM_REVOCATION_KEYS ''
"$cfg" --file "$out/.config" --disable LOCALVERSION_AUTO
"$cfg" --file "$out/.config" --set-str LOCALVERSION "$localversion"
"$cfg" --file "$out/.config" --set-str DEFAULT_HOSTNAME "zigux-${profile}"

# Force only the facilities required to boot the ArchISO and disk image on
# physical x86_64 hardware and under QEMU. BINFMT_SCRIPT must be built in
# because the smoke initramfs reaches PID 1 through its /init shell script,
# before any module can be loaded. allmodconfig remains module-heavy;
# allyesconfig remains built-in-heavy.
for symbol in \
  64BIT X86_64 MODULES BLK_DEV_INITRD RD_GZIP DEVTMPFS DEVTMPFS_MOUNT TMPFS \
  PROC_FS SYSFS BINFMT_ELF BINFMT_SCRIPT PRINTK TTY SERIAL_8250 SERIAL_8250_CONSOLE \
  PCI PCI_MSI ACPI EFI EFI_STUB EFI_PARTITION PARTITION_ADVANCED \
  BLOCK SCSI BLK_DEV_SD ATA SATA_AHCI NVME_CORE BLK_DEV_NVME \
  VIRTIO VIRTIO_PCI VIRTIO_BLK VIRTIO_NET VIRTIO_CONSOLE \
  EXT4_FS FAT_FS VFAT_FS MSDOS_FS ISO9660_FS UDF_FS SQUASHFS OVERLAY_FS BLK_DEV_LOOP BLK_DEV_SR \
  USB_SUPPORT USB_XHCI_HCD USB_STORAGE DRM DRM_VIRTIO_GPU FRAMEBUFFER_CONSOLE \
  CGROUPS NAMESPACES USER_NS SECCOMP INOTIFY_USER EPOLL \
  IKCONFIG IKCONFIG_PROC UNIX INET PACKET; do
  "$cfg" --file "$out/.config" --enable "$symbol"
done

make -C "$src" O="$out" olddefconfig
for required in X86_64 BLK_DEV_INITRD DEVTMPFS SERIAL_8250_CONSOLE EXT4_FS SQUASHFS; do
  grep -Eq "^CONFIG_${required}=(y|m)$" "$out/.config" || {
    echo "required CONFIG_${required} was not enabled" >&2
    exit 1
  }
done
for required_builtin in BINFMT_SCRIPT; do
  grep -q "^CONFIG_${required_builtin}=y$" "$out/.config" || {
    echo "required built-in CONFIG_${required_builtin} was not enabled" >&2
    exit 1
  }
done
for forbidden in \
  COMPILE_TEST DEBUG_KOBJECT_RELEASE DEBUG_PAGEALLOC \
  FTRACE_STARTUP_TEST SERIAL_NUVOTON_MA35D1_CONSOLE KCOV \
  RUNTIME_TESTING_MENU BACKTRACE_SELF_TEST TEST_CLOCKSOURCE_WATCHDOG \
  RING_BUFFER_STARTUP_TEST BTRFS_FS_RUN_SANITY_TESTS \
  DEBUG_OBJECTS_SELFTEST DEBUG_LOCKING_API_SELFTESTS \
  LOCK_TORTURE_TEST SCF_TORTURE_TEST RCU_SCALE_TEST RCU_TORTURE_TEST RCU_REF_SCALE_TEST \
  DMAPOOL_TEST KALLSYMS_SELFTEST CPA_DEBUG OF_UNITTEST \
  FSL_BMAN_TEST FSL_BMAN_TEST_API FSL_QMAN_TEST FSL_QMAN_TEST_API FSL_QMAN_TEST_STASH; do
  if grep -Eq "^CONFIG_${forbidden}=(y|m)$" "$out/.config"; then
    echo "boot-hostile CONFIG_${forbidden} was unexpectedly re-enabled" >&2
    exit 1
  fi
done
cp "$out/.config" "$dist/config-${profile}-bootable"

make -C "$src" O="$out" -j"$(nproc)" bzImage modules
release="$(make -s -C "$src" O="$out" kernelrelease)"
image="$out/arch/x86/boot/bzImage"
[[ -s "$image" ]] || { echo "missing bzImage" >&2; exit 1; }

modulesdir="$pkgroot/usr/lib/modules/$release"
mkdir -p "$modulesdir" "$pkgroot/boot" "$pkgroot/etc/mkinitcpio.d" \
         "$pkgroot/usr/share/licenses/$pkgbase"
make -C "$src" O="$out" \
  INSTALL_MOD_PATH="$pkgroot/usr" INSTALL_MOD_STRIP=1 DEPMOD=/bin/true modules_install
rm -f "$modulesdir/build" "$modulesdir/source"
install -Dm644 "$image" "$modulesdir/vmlinuz"
install -Dm644 "$image" "$pkgroot/boot/vmlinuz-$pkgbase"
printf '%s\n' "$pkgbase" > "$modulesdir/pkgbase"
install -Dm644 "$out/.config" "$modulesdir/config"
install -Dm644 "$out/System.map" "$modulesdir/System.map"
install -Dm644 "$src/COPYING" "$pkgroot/usr/share/licenses/$pkgbase/COPYING"
ln -s usr/lib "$pkgroot/lib"
depmod -b "$pkgroot" "$release"
rm "$pkgroot/lib"

cat > "$pkgroot/etc/mkinitcpio.d/${pkgbase}.preset" <<PRESET
# Generated by Zigux exhaustive-kernel CI
ALL_config="/etc/mkinitcpio.conf"
ALL_kver="/boot/vmlinuz-${pkgbase}"
PRESETS=('default')
default_image="/boot/initramfs-${pkgbase}.img"
PRESET

cat > "$pkgbuild/${pkgbase}.install" <<INSTALL
post_install() {
  depmod '${release}'
  if command -v mkinitcpio >/dev/null 2>&1; then
    mkinitcpio -p '${pkgbase}'
  fi
}
post_upgrade() { post_install; }
pre_remove() {
  rm -f '/boot/vmlinuz-${pkgbase}' \
        '/boot/initramfs-${pkgbase}.img'
}
post_remove() { depmod '${release}' || true; }
INSTALL

tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner \
  -C "$pkgroot" -I 'zstd -T0 -19' -cf "$pkgbuild/root.tar.zst" .
sha="$(sha256sum "$pkgbuild/root.tar.zst" | awk '{print $1}')"
pkgver="$(printf '%s' "$release" | sed -E 's/[^A-Za-z0-9.+]+/./g; s/^\.+|\.+$//g')"
install_sha="$(sha256sum "$pkgbuild/${pkgbase}.install" | awk '{print $1}')"

cat > "$pkgbuild/PKGBUILD" <<PKGBUILD
pkgname='${pkgbase}'
pkgver='${pkgver}'
pkgrel=1
pkgdesc='Zigux Linux ${profile} exhaustive x86_64 kernel and modules'
arch=('x86_64')
url='https://github.com/adybag14-cyber/Zigux'
license=('GPL-2.0-only')
depends=('coreutils' 'kmod' 'mkinitcpio')
optdepends=('linux-firmware: firmware for physical hardware')
provides=('WIREGUARD-MODULE' 'KSMBD-MODULE' 'NTSYNC-MODULE')
options=('!strip')
install='${pkgbase}.install'
source=('root.tar.zst' '${pkgbase}.install')
sha256sums=('${sha}' '${install_sha}')
package() {
  bsdtar -xf "\$srcdir/root.tar.zst" -C "\$pkgdir"
}
PKGBUILD

# makepkg supplies canonical Arch package metadata (.PKGINFO, .BUILDINFO,
# .MTREE) rather than merely renaming a tar archive.
docker run --rm \
  -v "$pkgbuild:/work" -w /work archlinux:base-devel bash -Eeuo pipefail -c '
    pacman -Syu --noconfirm --needed base-devel zstd mkinitcpio >/dev/null
    useradd -m builder
    chown -R builder:builder /work
    su builder -c "makepkg --noconfirm --clean --cleanbuild --force"
  '

pkgfile="$(find "$pkgbuild" -maxdepth 1 -type f -name "${pkgbase}-*.pkg.tar.zst" -print -quit)"
[[ -n "$pkgfile" ]] || { echo "makepkg did not produce a package" >&2; exit 1; }
cp "$pkgfile" "$dist/"
cp "$out/Module.symvers" "$dist/Module.symvers-${profile}" 2>/dev/null || true
printf '%s\n' "$release" > "$dist/kernel-release-${profile}.txt"
printf '%s\n' "$pkgbase" > "$dist/package-name-${profile}.txt"
sha256sum "$dist"/* > "$dist/SHA256SUMS-${profile}"

# A direct kernel smoke test catches a kernel that compiled but cannot reach
# PID 1. Keep this as a hard gate because the downstream CachyOS media boots
# allmodconfig by default; assembling media from a non-booting kernel only
# moves the same failure into the much more expensive image job.
root="$smoke/root"
mkdir -p "$root/bin"
cp /usr/bin/busybox "$root/bin/busybox"
for applet in sh echo uname poweroff sync; do ln -s busybox "$root/bin/$applet"; done
cat > "$root/init" <<'INIT'
#!/bin/sh
echo ZIGUX_KERNEL_BOOT_OK
uname -a
sync
poweroff -f
INIT
chmod 0755 "$root/init"
(
  cd "$root"
  find . -print0 | sort -z | cpio --null -o --format=newc --owner=0:0 2>/dev/null | gzip -9
) > "$smoke/initramfs.cpio.gz"

set +e
timeout 180 qemu-system-x86_64 \
  -machine q35,accel=tcg -cpu max -m 2048 -smp 2 \
  -kernel "$image" -initrd "$smoke/initramfs.cpio.gz" \
  -append 'console=ttyS0 earlyprintk=ttyS0 panic=-1' \
  -display none -serial stdio -monitor none -no-reboot \
  > "$dist/qemu-kernel-${profile}.log" 2>&1
qemu_rc=$?
set -e
if grep -q ZIGUX_KERNEL_BOOT_OK "$dist/qemu-kernel-${profile}.log"; then
  echo success > "$dist/QEMU_KERNEL_RESULT-${profile}"
else
  echo "failed rc=$qemu_rc" > "$dist/QEMU_KERNEL_RESULT-${profile}"
  tail -n 120 "$dist/qemu-kernel-${profile}.log" >&2 || true
  exit 20
fi
