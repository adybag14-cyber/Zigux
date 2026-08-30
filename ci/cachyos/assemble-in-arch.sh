#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s nullglob

log() { printf '\n==> %s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

packages=(/packages/linux-zigux-*.pkg.tar.zst)
(( ${#packages[@]} == 2 )) || die "expected exactly two Zigux kernel packages in /packages"
[[ -d /cachyos-live-iso/archiso ]] || die "missing CachyOS ArchISO source"
mkdir -p /dist

work=/work/zigux-cachyos-media
root=$work/rootfs
profile=$work/archiso-profile
iso_work=$work/archiso-work
repo=/zigux-repo
img=/dist/zigux-cachyos-exhaustive-x86_64.img
imgz=${img}.zst
iso=/dist/zigux-cachyos-exhaustive-x86_64.iso
disk_gib=${DISK_GIB:-32}
loopdev=

stop_target_keyring() {
  [[ -x "$root/usr/bin/gpgconf" ]] || return 0
  arch-chroot "$root" gpgconf --homedir /etc/pacman.d/gnupg --kill all \
    >/dev/null 2>&1 || true
}

report_target_holders() {
  local proc_path pid proc_root proc_cwd
  for proc_path in /proc/[0-9]*; do
    pid=${proc_path##*/}
    proc_root=$(readlink -f "$proc_path/root" 2>/dev/null || true)
    proc_cwd=$(readlink -f "$proc_path/cwd" 2>/dev/null || true)
    if [[ "$proc_root" == "$root" || "$proc_root" == "$root/"* ||
          "$proc_cwd" == "$root" || "$proc_cwd" == "$root/"* ]]; then
      printf 'target holder pid=%s root=%q cwd=%q cmd=' "$pid" "$proc_root" "$proc_cwd" >&2
      tr '\0' ' ' < "$proc_path/cmdline" >&2 2>/dev/null || true
      printf '\n' >&2
    fi
  done
}

unmount_target() {
  local attempt
  stop_target_keyring
  for attempt in 1 2 3 4 5; do
    sync
    mountpoint -q "$root" || return 0
    if umount -R "$root"; then
      return 0
    fi
    sleep "$attempt"
  done
  findmnt -R "$root" >&2 || true
  report_target_holders
  die "target root remained busy after bounded keyring teardown and unmount retries"
}

cleanup() {
  set +e
  stop_target_keyring
  if mountpoint -q "$root"; then umount -R "$root"; fi
  if [[ -n "$loopdev" ]]; then losetup -d "$loopdev" 2>/dev/null || true; fi
  rm -f "$img"
}
trap cleanup EXIT INT TERM

log "Install image-construction tools"
pacman -Syu --noconfirm --needed \
  arch-install-scripts archiso base-devel curl dosfstools e2fsprogs git gnupg grub \
  mtools pacman-contrib parted qemu-img rsync squashfs-tools syslinux xorriso zstd

log "Initialize Arch and CachyOS package trust"
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

rm -rf "$work" "$repo"
mkdir -p "$work" "$repo"
cp -a "${packages[@]}" "$repo/"
repo-add "$repo/zigux-local.db.tar.gz" "$repo"/*.pkg.tar.zst

pacman_conf=$work/pacman.conf
cat > "$pacman_conf" <<'PACMAN'
[options]
Architecture = auto
SigLevel = Required DatabaseOptional
LocalFileSigLevel = Optional
ParallelDownloads = 10
DisableDownloadTimeout
DisableSandbox

[zigux-local]
SigLevel = Optional TrustAll
Server = file:///zigux-repo

[cachyos]
Server = https://mirror.cachyos.org/repo/$arch/$repo

[core]
Include = /etc/pacman.d/mirrorlist

[extra]
Include = /etc/pacman.d/mirrorlist

[multilib]
Include = /etc/pacman.d/mirrorlist
PACMAN
pacman -Sy --noconfirm --config "$pacman_conf"

common_packages=(
  base cachyos-keyring linux-cachyos-lts linux-firmware amd-ucode intel-ucode
  linux-zigux-allmodconfig linux-zigux-allyesconfig
  mkinitcpio grub efibootmgr networkmanager sudo
  plasma-desktop plasma-workspace plasma-nm plasma-pa sddm
  pipewire pipewire-alsa pipewire-pulse wireplumber
  konsole dolphin kate firefox nano vim openssh
  btrfs-progs dosfstools e2fsprogs exfatprogs f2fs-tools ntfs-3g xfsprogs
  bluez bluez-utils cups avahi
  mesa vulkan-virtio spice-vdagent qemu-guest-agent
)

install_marker() {
  local target=$1
  install -Dm755 /dev/stdin "$target/usr/local/bin/zigux-media-boot-marker" <<'MARKER'
#!/usr/bin/env bash
set -u
msg="ZIGUX_CACHYOS_MEDIA_BOOT_OK kernel=$(uname -r)"
printf '%s\n' "$msg" | tee /dev/console >/dev/null || true
printf '%s\n' "$msg" > /dev/ttyS0 2>/dev/null || true
logger -t zigux-media "$msg" 2>/dev/null || true
MARKER
  install -Dm644 /dev/stdin "$target/etc/systemd/system/zigux-media-boot.service" <<'SERVICE'
[Unit]
Description=Emit Zigux CachyOS boot-test marker
After=systemd-user-sessions.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/zigux-media-boot-marker
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
SERVICE
  mkdir -p "$target/etc/systemd/system/multi-user.target.wants"
  ln -sfn ../zigux-media-boot.service \
    "$target/etc/systemd/system/multi-user.target.wants/zigux-media-boot.service"
}

configure_root() {
  local target=$1
  printf 'zigux-cachyos\n' > "$target/etc/hostname"
  sed -i 's/^#en_GB.UTF-8 UTF-8/en_GB.UTF-8 UTF-8/' "$target/etc/locale.gen"
  arch-chroot "$target" locale-gen
  printf 'LANG=en_GB.UTF-8\n' > "$target/etc/locale.conf"
  ln -sfn /usr/share/zoneinfo/Europe/London "$target/etc/localtime"
  arch-chroot "$target" hwclock --systohc || true
  arch-chroot "$target" useradd -m -G wheel,audio,video,storage -s /bin/bash zigux
  printf 'zigux:zigux\nroot:zigux\n' | arch-chroot "$target" chpasswd
  printf '%%wheel ALL=(ALL:ALL) ALL\n' > "$target/etc/sudoers.d/10-wheel"
  chmod 0440 "$target/etc/sudoers.d/10-wheel"
  arch-chroot "$target" systemctl enable NetworkManager.service sddm.service sshd.service \
    qemu-guest-agent.service 2>/dev/null || true
  install_marker "$target"
}

log "Create persistent CachyOS GPT disk image (${disk_gib} GiB sparse)"
truncate -s "${disk_gib}G" "$img"
parted -s "$img" mklabel gpt
parted -s "$img" mkpart BIOS 1MiB 3MiB
parted -s "$img" set 1 bios_grub on
parted -s "$img" mkpart ESP fat32 3MiB 515MiB
parted -s "$img" set 2 esp on
parted -s "$img" mkpart ROOT ext4 515MiB 100%
loopdev=$(losetup --find --show --partscan "$img")
udevadm settle
mkfs.fat -F32 -n ZIGUXEFI "${loopdev}p2"
mkfs.ext4 -F -L ZIGUXROOT "${loopdev}p3"
mkdir -p "$root"
mount "${loopdev}p3" "$root"
mkdir -p "$root/boot/efi"
mount "${loopdev}p2" "$root/boot/efi"

log "Install CachyOS userspace, Plasma desktop, firmware and three kernels"
pacstrap -K -C "$pacman_conf" "$root" "${common_packages[@]}"
genfstab -U "$root" > "$root/etc/fstab"
configure_root "$root"

log "Generate initramfs images"
arch-chroot "$root" pacman-key --init
arch-chroot "$root" pacman-key --populate archlinux cachyos
stop_target_keyring
arch-chroot "$root" mkinitcpio -P

root_uuid=$(blkid -s UUID -o value "${loopdev}p3")
cat > "$root/etc/default/grub" <<GRUBDEFAULT
GRUB_DEFAULT=0
GRUB_TIMEOUT=8
GRUB_DISTRIBUTOR='Zigux CachyOS'
GRUB_CMDLINE_LINUX_DEFAULT='rw console=tty0 console=ttyS0,115200n8'
GRUB_CMDLINE_LINUX='root=UUID=${root_uuid}'
GRUB_TERMINAL_INPUT='console serial'
GRUB_TERMINAL_OUTPUT='console serial'
GRUB_SERIAL_COMMAND='serial --speed=115200 --unit=0 --word=8 --parity=no --stop=1'
GRUB_DISABLE_RECOVERY=true
GRUBDEFAULT

cat > "$root/etc/grub.d/09_zigux_exhaustive" <<EOFGRUB
#!/bin/sh
cat <<'EOF'
menuentry 'Zigux CachyOS — allmodconfig' --class cachyos --class gnu-linux {
    search --no-floppy --fs-uuid --set=root ${root_uuid}
    linux /boot/vmlinuz-linux-zigux-allmodconfig root=UUID=${root_uuid} rw console=tty0 console=ttyS0,115200n8
    initrd /boot/initramfs-linux-zigux-allmodconfig.img
}
menuentry 'Zigux CachyOS — allyesconfig (experimental)' --class cachyos --class gnu-linux {
    search --no-floppy --fs-uuid --set=root ${root_uuid}
    linux /boot/vmlinuz-linux-zigux-allyesconfig root=UUID=${root_uuid} rw console=tty0 console=ttyS0,115200n8
    initrd /boot/initramfs-linux-zigux-allyesconfig.img
}
EOF
EOFGRUB
chmod 0755 "$root/etc/grub.d/09_zigux_exhaustive"

log "Install GRUB for legacy BIOS and removable x86_64 UEFI"
grub-install --target=i386-pc --boot-directory="$root/boot" "$loopdev"
grub-install --target=x86_64-efi --efi-directory="$root/boot/efi" \
  --boot-directory="$root/boot" --bootloader-id=Zigux --removable --no-nvram
arch-chroot "$root" grub-mkconfig -o /boot/grub/grub.cfg

cat > "$root/README-ZIGUX.txt" <<'README'
Zigux CachyOS exhaustive x86_64 image

Default account: zigux
Initial password: zigux
Root password: zigux
Change both passwords immediately after first boot.

Boot choices:
  1. linux-zigux-allmodconfig (default)
  2. linux-zigux-allyesconfig (experimental)
  3. linux-cachyos-lts (fallback, generated by GRUB)
README

sync
unmount_target
losetup -d "$loopdev"
loopdev=

log "Compress persistent disk image"
zstd -T0 -19 --long=27 --sparse -f "$img" -o "$imgz"
rm -f "$img"

log "Prepare CachyOS-derived ArchISO profile"
cp -a /cachyos-live-iso/archiso "$profile"
cp "$pacman_conf" "$profile/pacman.conf"
cat > "$profile/packages.x86_64" <<'ISOPKGS'
archiso
base
cachyos-keyring
linux-cachyos-lts
linux-firmware
amd-ucode
intel-ucode
linux-zigux-allmodconfig
linux-zigux-allyesconfig
mkinitcpio-archiso
mkinitcpio-nfs-utils
nbd
nfs-utils
pv
grub
syslinux
networkmanager
sudo
plasma-desktop
plasma-workspace
plasma-nm
plasma-pa
sddm
pipewire
pipewire-alsa
pipewire-pulse
wireplumber
konsole
dolphin
kate
firefox
nano
vim
openssh
btrfs-progs
dosfstools
e2fsprogs
exfatprogs
f2fs-tools
ntfs-3g
xfsprogs
bluez
bluez-utils
cups
avahi
mesa
vulkan-virtio
spice-vdagent
qemu-guest-agent
ISOPKGS
cp "$profile/packages.x86_64" "$profile/packages_desktop.x86_64" 2>/dev/null || true

sed -i \
  -e 's/^iso_name=.*/iso_name="zigux-cachyos"/' \
  -e 's/^iso_publisher=.*/iso_publisher="Zigux using CachyOS packages <https:\/\/github.com\/adybag14-cyber\/Zigux>"/' \
  -e 's/^iso_application=.*/iso_application="Zigux CachyOS Exhaustive Live System"/' \
  "$profile/profiledef.sh"

mkdir -p "$profile/airootfs/root" \
  "$profile/airootfs/etc/systemd/system/multi-user.target.wants"
# mkarchiso copies profile overlays before pacstrap, so pre-creating a package-owned
# preset makes pacman reject the kernel package. Its pinned post-package customization
# hook instead regenerates only the two live initramfs images with the archiso hooks.
cat > "$profile/airootfs/root/customize_airootfs.sh" <<'CUSTOMIZE'
#!/usr/bin/env bash
set -Eeuo pipefail
for kernel in linux-zigux-allmodconfig linux-zigux-allyesconfig; do
  mkinitcpio \
    -c /etc/mkinitcpio.conf.d/archiso.conf \
    -k "/boot/vmlinuz-${kernel}" \
    -g "/boot/initramfs-${kernel}.img"
done
CUSTOMIZE
chmod 0755 "$profile/airootfs/root/customize_airootfs.sh"
install_marker "$profile/airootfs"

mkdir -p "$profile/airootfs/etc/systemd/system"
ln -sfn /usr/lib/systemd/system/sddm.service \
  "$profile/airootfs/etc/systemd/system/display-manager.service"

cat > "$profile/grub/grub.cfg" <<'ISO_GRUB'
insmod part_gpt
insmod part_msdos
insmod fat
insmod iso9660
insmod all_video
insmod serial
serial --unit=0 --speed=115200 --word=8 --parity=no --stop=1
terminal_input console serial
terminal_output console serial
set default=0
set timeout=8

menuentry 'Zigux CachyOS allmodconfig' {
  linux /%INSTALL_DIR%/boot/%ARCH%/vmlinuz-linux-zigux-allmodconfig archisobasedir=%INSTALL_DIR% archisosearchuuid=%ARCHISO_UUID% copytoram=auto console=tty0 console=ttyS0,115200n8
  initrd /%INSTALL_DIR%/boot/%ARCH%/initramfs-linux-zigux-allmodconfig.img
}
menuentry 'Zigux CachyOS allyesconfig (experimental)' {
  linux /%INSTALL_DIR%/boot/%ARCH%/vmlinuz-linux-zigux-allyesconfig archisobasedir=%INSTALL_DIR% archisosearchuuid=%ARCHISO_UUID% copytoram=auto console=tty0 console=ttyS0,115200n8
  initrd /%INSTALL_DIR%/boot/%ARCH%/initramfs-linux-zigux-allyesconfig.img
}
menuentry 'CachyOS LTS fallback' {
  linux /%INSTALL_DIR%/boot/%ARCH%/vmlinuz-linux-cachyos-lts archisobasedir=%INSTALL_DIR% archisosearchuuid=%ARCHISO_UUID% copytoram=auto console=tty0 console=ttyS0,115200n8
  initrd /%INSTALL_DIR%/boot/%ARCH%/initramfs-linux-cachyos-lts.img
}
ISO_GRUB

cat > "$profile/syslinux/archiso_sys-linux.cfg" <<'ISO_SYSLINUX'
LABEL zigux
MENU LABEL Zigux CachyOS allmodconfig
LINUX /%INSTALL_DIR%/boot/%ARCH%/vmlinuz-linux-zigux-allmodconfig
INITRD /%INSTALL_DIR%/boot/%ARCH%/initramfs-linux-zigux-allmodconfig.img
APPEND archisobasedir=%INSTALL_DIR% archisosearchuuid=%ARCHISO_UUID% copytoram=auto console=tty0 console=ttyS0,115200n8

LABEL zigux-allyes
MENU LABEL Zigux CachyOS allyesconfig (experimental)
LINUX /%INSTALL_DIR%/boot/%ARCH%/vmlinuz-linux-zigux-allyesconfig
INITRD /%INSTALL_DIR%/boot/%ARCH%/initramfs-linux-zigux-allyesconfig.img
APPEND archisobasedir=%INSTALL_DIR% archisosearchuuid=%ARCHISO_UUID% copytoram=auto console=tty0 console=ttyS0,115200n8

LABEL zigux-lts
MENU LABEL CachyOS LTS fallback
LINUX /%INSTALL_DIR%/boot/%ARCH%/vmlinuz-linux-cachyos-lts
INITRD /%INSTALL_DIR%/boot/%ARCH%/initramfs-linux-cachyos-lts.img
APPEND archisobasedir=%INSTALL_DIR% archisosearchuuid=%ARCHISO_UUID% copytoram=auto console=tty0 console=ttyS0,115200n8
ISO_SYSLINUX
cp "$profile/syslinux/archiso_sys-linux.cfg" "$profile/syslinux/archiso_pxe-linux.cfg"

rm -rf "$iso_work" /dist/iso-out
mkdir -p /dist/iso-out
log "Build bootable CachyOS KDE live ISO"
mkarchiso -v -w "$iso_work" -o /dist/iso-out "$profile"
built_iso=$(find /dist/iso-out -maxdepth 1 -type f -name '*.iso' -print -quit)
[[ -n "$built_iso" ]] || die "mkarchiso did not produce an ISO"
mv "$built_iso" "$iso"
rm -rf /dist/iso-out

cat > /dist/README.txt <<EOF
Zigux CachyOS exhaustive x86_64 media

Linux source commit: ${SOURCE_REF:-unknown}
CachyOS Live ISO source commit: ${CACHYOS_ISO_REF:-unknown}

Artifacts:
  zigux-cachyos-exhaustive-x86_64.iso      Live KDE ISO, BIOS and UEFI
  zigux-cachyos-exhaustive-x86_64.img.zst  Persistent GPT disk, BIOS and UEFI

Default disk credentials: zigux / zigux (root password: zigux)
Change these passwords immediately.

The allmodconfig kernel is the default. allyesconfig is experimental.
linux-cachyos-lts remains installed as a recovery kernel.
EOF

sha256sum /dist/*.iso /dist/*.img.zst /dist/README.txt > /dist/SHA256SUMS
ls -lh /dist
