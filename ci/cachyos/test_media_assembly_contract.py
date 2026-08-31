#!/usr/bin/env python3
"""Static regression checks for safe CachyOS media assembly and retries."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSEMBLER = ROOT / "ci" / "cachyos" / "assemble-in-arch.sh"
QEMU_TEST = ROOT / "ci" / "cachyos" / "qemu-test-media.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "cachyos-exhaustive-media.yml"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    assembler = ASSEMBLER.read_text(encoding="utf-8")
    qemu_test = QEMU_TEST.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    keyring_kill = (
        "gpgconf --homedir /etc/pacman.d/gnupg --kill all" in assembler
    )
    require(keyring_kill, "target pacman keyring agent must be stopped before unmount")
    require(
        "for attempt in 1 2 3 4 5; do" in assembler,
        "target unmount must use bounded retries",
    )
    require(
        "report_target_holders" in assembler and "findmnt -R \"$root\"" in assembler,
        "failed unmounts must report process and mount evidence",
    )
    require(
        "umount -R -l" not in assembler and "umount --lazy" not in assembler,
        "media completion must not rely on a lazy unmount",
    )
    require(
        assembler.index("stop_target_keyring\narch-chroot \"$root\" mkinitcpio -P")
        < assembler.index("unmount_target\nlosetup -d \"$loopdev\""),
        "keyring teardown and verified unmount must precede loop detachment",
    )
    require(
        'rm -f "$img"' in assembler,
        "failed assembly must remove the non-final raw image",
    )
    require(
        "After=local-fs.target" in assembler
        and "After=systemd-user-sessions.service" not in assembler,
        "boot marker must run after the real root is mounted, not after late user setup",
    )
    require(
        '$profile/airootfs/root/customize_airootfs.sh' in assembler,
        "live initramfs customization must run after package installation",
    )
    require(
        '$profile/airootfs/etc/mkinitcpio.d' not in assembler,
        "profile overlay must not collide with package-owned mkinitcpio presets",
    )
    require(
        "-c /etc/mkinitcpio.conf.d/archiso.conf" in assembler
        and '-g "/boot/initramfs-${kernel}.img"' in assembler,
        "custom kernels must receive archiso-hook initramfs images",
    )
    iso_packages = set(
        assembler.split("<<'ISOPKGS'\n", maxsplit=1)[1]
        .split("\nISOPKGS", maxsplit=1)[0]
        .split()
    )
    required_live_packages = {
        "cachyos-mirrorlist",
        "mkinitcpio-nfs-utils",
        "nbd",
        "nfs-utils",
        "pv",
    }
    require(
        required_live_packages <= iso_packages,
        "live package list is missing pinned profile dependencies: "
        f"{sorted(required_live_packages - iso_packages)}",
    )

    qemu_timeout = re.search(r"timeout (?P<seconds>\d+) qemu-system-x86_64", qemu_test)
    require(qemu_timeout is not None, "media QEMU timeout was not found")
    require(
        int(qemu_timeout.group("seconds")) >= 1200,
        "exhaustive TCG media boots require at least a 1200-second wall-clock budget",
    )

    require(
        "kernel_artifact_run_id:" in workflow,
        "workflow dispatch must support reuse of proven kernel artifacts",
    )
    require(
        "run-id: ${{ inputs.kernel_artifact_run_id || github.run_id }}" in workflow,
        "artifact download must select the requested prior run",
    )
    require(
        "!media-dist/*.img" in workflow,
        "failure artifacts must exclude uncompressed raw disk images",
    )
    require(
        "python3 ci/cachyos/test_media_assembly_contract.py" in workflow,
        "workflow must execute this media safety contract",
    )

    print("CachyOS media assembly contract: OK")


if __name__ == "__main__":
    main()
