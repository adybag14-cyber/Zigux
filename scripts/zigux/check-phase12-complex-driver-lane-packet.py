#!/usr/bin/env python3
"""Fail-closed checker for the shared Phase 12 complex-driver lane packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


CHECK_NAME = "PHASE12_COMPLEX_DRIVER_LANE_PACKET"

NOTE_PATH = Path("Documentation/zigux/phase12-complex-driver-lane-sequencing.md")
BUILD_PATH = Path("zigux/tests/phase12_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_FILES = (
    NOTE_PATH,
    BUILD_PATH,
    MAKEFILE_PATH,
)

NOTE_MARKERS = (
    "`PHASE12_LANE=complex-driver-shared-release-packet`",
    "`drivers/net/virtio_net_queue_resume.zig`, `drivers/net/virtio_net_receive_refill_replay.zig`, `drivers/net/virtio_net_transmit_recycle.zig`, `drivers/net/virtio_net_post_reset_replay.zig`, and `drivers/net/virtio_net_throughput_parity.zig` are now present on `master`.",
    "`zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, and `zigux/tests/phase12_virtio_net_throughput_parity.zig` are now present on `master` as the directly coupled review packet for that split-helper family.",
    "`drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, and `zigux/tests/phase12_virtio_net_syntax_lab.zig` are currently absent on `master`",
    "current `zigux/Makefile` now ships `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12`, so `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are current wrapper proof on `master`.",
    "`Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, and `zigux/tests/phase12_nvme_pci_manifest.json` while leaving it outside the shared smoke-first route.",
    "`Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` remains the one commit-pinned direct replay artifact, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the current-master gap-inventory companion, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors.",
)

BUILD_MARKERS = (
    "phase12_virtio_net_queue_resume.zig",
    "phase12-virtio-net-queue-resume-tests",
    "phase12_virtio_net_receive_refill_replay.zig",
    "phase12-virtio-net-receive-refill-replay-tests",
    "phase12_virtio_net_transmit_recycle.zig",
    "phase12-virtio-net-transmit-recycle-tests",
    "phase12_virtio_net_post_reset_replay.zig",
    "phase12-virtio-net-post-reset-replay-tests",
    "phase12_virtio_net_throughput_parity.zig",
    "phase12-virtio-net-throughput-parity-tests",
)

MAKEFILE_MARKERS = (
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase12: phase12-smoke phase12-test",
)


class CheckFailure(RuntimeError):
    pass


def read_text(root: Path, relative_path: Path) -> str:
    try:
        return (root / relative_path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {relative_path}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{label} missing marker: {marker}")


def require_forbidden_absent(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise CheckFailure(f"{label} stale marker present: {marker}")


def check(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            raise CheckFailure(f"missing required file: {relative_path}")

    require_markers(read_text(root, NOTE_PATH), NOTE_MARKERS, str(NOTE_PATH))
    require_markers(read_text(root, BUILD_PATH), BUILD_MARKERS, str(BUILD_PATH))

    makefile_text = read_text(root, MAKEFILE_PATH)
    require_markers(makefile_text, MAKEFILE_MARKERS, str(MAKEFILE_PATH))
    require_forbidden_absent(
        makefile_text,
        FORBIDDEN_MAKEFILE_MARKERS,
        str(MAKEFILE_PATH),
    )


def write_fixture(root: Path) -> None:
    files = {
        NOTE_PATH: "\n".join(NOTE_MARKERS) + "\n",
        BUILD_PATH: "\n".join(BUILD_MARKERS) + "\n",
        MAKEFILE_PATH: "\n".join(MAKEFILE_MARKERS) + "\n",
    }
    for relative_path, text in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-complex-driver-lane-") as tmp:
        root = Path(tmp)

        write_fixture(root)
        check(root)
        cases += 1

        write_fixture(root)
        (root / NOTE_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if "phase12-complex-driver-lane-sequencing.md" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected note marker failure")

        write_fixture(root)
        (root / BUILD_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if "zigux/tests/phase12_build.zig" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected build marker failure")

        write_fixture(root)
        (root / MAKEFILE_PATH).write_text("phase12-smoke:\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if "zigux/Makefile" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected makefile marker failure")

        write_fixture(root)
        (root / MAKEFILE_PATH).write_text(
            "\n".join((
                "phase12-validate:",
                "phase12-smoke:",
                "phase12-test:",
                "phase12: phase12-smoke phase12-test",
            ))
            + "\n",
            encoding="utf-8",
        )
        try:
            check(root)
        except CheckFailure as exc:
            if "zigux/Makefile" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected stale makefile marker failure")

    print(f"{CHECK_NAME}_SELF_TEST=pass")
    print(f"{CHECK_NAME}_SELF_TEST_CASES={cases}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    try:
        check(Path(args.root))
    except CheckFailure as exc:
        print(f"{CHECK_NAME}=fail")
        print(f"{CHECK_NAME}_ERROR={exc}")
        return 1

    print(f"{CHECK_NAME}=pass")
    print(f"{CHECK_NAME}_SCOPE=complex_driver_lane_truth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
