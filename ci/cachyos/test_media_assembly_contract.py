#!/usr/bin/env python3
"""Static regression checks for safe CachyOS media assembly and retries."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSEMBLER = ROOT / "ci" / "cachyos" / "assemble-in-arch.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "cachyos-exhaustive-media.yml"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    assembler = ASSEMBLER.read_text(encoding="utf-8")
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
