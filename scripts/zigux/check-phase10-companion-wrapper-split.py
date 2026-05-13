#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

TARGET_FILE = "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"

WRAPPER_SPLIT_MARKERS = [
    "Wrapper ownership for the input lane stays split:",
    "`drivers/virtio/virtio.zig` owns shared device-status bookkeeping",
    "`drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning",
    "`drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning",
    "transport-facing queue and registration-lifecycle work stays parked outside the input lane.",
    (
        "Current repo-reality gaps on `master` still include "
        "`Documentation/zigux/phase10-virtio-core-slice.md`, "
        "`Documentation/zigux/phase10-virtio-ring-slice.md`, "
        "`Documentation/zigux/phase10-virtio-input-slice.md`, "
        "`Documentation/zigux/phase10-virtio-input-module-slice.md`, and "
        "`Documentation/zigux/phase10-virtio-mmio-slice.md`"
    ),
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    path = root / TARGET_FILE
    if not path.exists():
        return [TARGET_FILE], []

    text = read_text(root, TARGET_FILE)
    missing = [
        f"wrapper_split:{marker}" for marker in WRAPPER_SPLIT_MARKERS if marker not in text
    ]
    return [], missing


def write_fixture(root: Path) -> None:
    path = root / TARGET_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Phase 10, 11, and 13 Tests-Root Review Companion",
                "",
                "## Phase 10 tests-root packet",
                "",
                (
                    "Wrapper ownership for the input lane stays split: "
                    "`drivers/virtio/virtio.zig` owns shared device-status bookkeeping, "
                    "`drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and "
                    "notification planning, and `drivers/virtio/virtio_mmio.zig` owns "
                    "MMIO wrapper planning, so transport-facing queue and "
                    "registration-lifecycle work stays parked outside the input lane."
                ),
                "",
                (
                    "Current repo-reality gaps on `master` still include "
                    "`Documentation/zigux/phase10-virtio-core-slice.md`, "
                    "`Documentation/zigux/phase10-virtio-ring-slice.md`, "
                    "`Documentation/zigux/phase10-virtio-input-slice.md`, "
                    "`Documentation/zigux/phase10-virtio-input-module-slice.md`, and "
                    "`Documentation/zigux/phase10-virtio-mmio-slice.md`; keep those "
                    "absent packet-local companions recorded as gaps instead of "
                    "presenting them as shipped shared-review evidence."
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase10-companion-wrapper-split-self-test:{label}:"
            f"unexpected_missing_files:{','.join(missing_files)}"
        )
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase10-companion-wrapper-split-self-test:{label}:"
            f"expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def expect_missing_file(root: Path) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(
            "phase10-companion-wrapper-split-self-test:missing_file:"
            f"unexpected_missing_markers:{','.join(missing_markers)}"
        )
    if TARGET_FILE not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(
            "phase10-companion-wrapper-split-self-test:missing_file:"
            f"expected_missing_file:{TARGET_FILE}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_companion_wrapper_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-companion-wrapper-split-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        path = root / TARGET_FILE
        original = path.read_text(encoding="utf-8")

        replacements = [
            (
                "wrapper_split_heading",
                "Wrapper ownership for the input lane stays split:",
                "Wrapper ownership drifted again:",
            ),
            (
                "wrapper_split_status_owner",
                "`drivers/virtio/virtio.zig` owns shared device-status bookkeeping",
                "`drivers/virtio/virtio.zig` owns transport-facing queue setup",
            ),
            (
                "wrapper_split_ring_owner",
                "`drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning",
                "`drivers/virtio/virtio_ring.zig` owns interrupt-complete delivery",
            ),
            (
                "wrapper_split_mmio_owner",
                "`drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning",
                "`drivers/virtio/virtio_mmio.zig` owns registration teardown parity",
            ),
            (
                "wrapper_split_parked_boundary",
                "transport-facing queue and registration-lifecycle work stays parked outside the input lane.",
                "transport-facing queue and registration-lifecycle work is now ready to land.",
            ),
            (
                "wrapper_split_gap_inventory",
                "`Documentation/zigux/phase10-virtio-input-module-slice.md`, and "
                "`Documentation/zigux/phase10-virtio-mmio-slice.md`",
                "`Documentation/zigux/phase10-virtio-input-module-slice.md`, and "
                "`Documentation/zigux/phase10-virtio-mmio-slice-shipped.md`",
            ),
        ]

        for label, needle, replacement in replacements:
            path.write_text(original.replace(needle, replacement, 1), encoding="utf-8")
            expected = (
                WRAPPER_SPLIT_MARKERS[-1]
                if label == "wrapper_split_gap_inventory"
                else needle
            )
            expect_missing_marker(label, root, f"wrapper_split:{expected}")
            path.write_text(original, encoding="utf-8")

        path.unlink()
        expect_missing_file(root)

    print("PHASE10_COMPANION_WRAPPER_SPLIT_SELF_TEST=pass")
    print("PHASE10_COMPANION_WRAPPER_SPLIT_SELF_TEST_CASE_COUNT=7")
    return 0


if "--self-test" in sys.argv[1:]:
    sys.exit(run_self_test())

missing_files, missing_markers = validate(ROOT)
if missing_files:
    print("PHASE10_COMPANION_WRAPPER_SPLIT=fail")
    print("MISSING_PHASE10_COMPANION_WRAPPER_SPLIT_FILES_START")
    for item in missing_files:
        print(item)
    print("MISSING_PHASE10_COMPANION_WRAPPER_SPLIT_FILES_END")
    sys.exit(1)

if missing_markers:
    print("PHASE10_COMPANION_WRAPPER_SPLIT=fail")
    print("MISSING_PHASE10_COMPANION_WRAPPER_SPLIT_MARKERS_START")
    for item in missing_markers:
        print(item)
    print("MISSING_PHASE10_COMPANION_WRAPPER_SPLIT_MARKERS_END")
    sys.exit(1)

print("PHASE10_COMPANION_WRAPPER_SPLIT=pass")
print("PHASE10_COMPANION_WRAPPER_SPLIT_REQUIRED_FILE_COUNT=1")
print(
    "PHASE10_COMPANION_WRAPPER_SPLIT_REQUIRED_MARKER_COUNT="
    f"{len(WRAPPER_SPLIT_MARKERS)}"
)
