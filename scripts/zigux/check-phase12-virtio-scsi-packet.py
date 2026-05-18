#!/usr/bin/env python3
"""PHASE12_CHECK_PACKET=virtio_scsi_packet

Fail-closed checker for the bounded Phase 12 virtio_scsi support packet.
It keeps the existing slice note, support-manifest fixture, survey gate, and
shared Phase 12 route reminder aligned around one packet-local validation hook.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

MARKER = "PHASE12_CHECK_PACKET=virtio_scsi_packet"

SLICE_PATH = "Documentation/zigux/phase12-virtio-scsi-slice.md"
SURVEY_NOTE_PATH = "Documentation/zigux/phase12-virtio-scsi-survey.md"
SURVEY_GATE_PATH = "zigux/tests/phase12_virtio_scsi_survey.zig"
SUPPORT_MANIFEST_FIXTURE_PATH = "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json"
SUPPORT_PACKET_PATH = "zigux/tests/phase12_virtio_scsi_packet.zig"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
MAKEFILE_PATH = "zigux/Makefile"

REQUIRED_FILES = [
    SLICE_PATH,
    SURVEY_NOTE_PATH,
    SURVEY_GATE_PATH,
    SUPPORT_MANIFEST_FIXTURE_PATH,
    SUPPORT_PACKET_PATH,
    PHASE12_BUILD_PATH,
    MAKEFILE_PATH,
]

SLICE_MARKERS = [
    "# Phase 12 virtio_scsi Slice",
    "`PHASE12_SLICE=virtio-scsi-queue-lab-support`",
    "- lane: `complex-drivers-infra`",
    "- `zigux/tests/phase12_virtio_scsi_packet.zig` remains the manifest-backed support replay for this bounded infra-prep slice",
    "- `zigux/tests/phase12_build.zig` keeps the direct replay, syntax-lab smoke, repeated-replan gate, repeated-rollback gate, survey gate, and support packet wired into the shared `phase12` smoke and test routes",
    "- `scripts/zigux/check-phase12-virtio-scsi-packet.py` fails closed if the manifest, slice note, or build route drifts",
    "## Repo-reality boundaries",
    "- `drivers/nvme/host/pci.zig` now lives in the separate Phase 12 NVMe packet on current `master`, so this `virtio_scsi` support note should treat NVMe as neighboring packet evidence rather than a repo-reality gap",
    "- `Documentation/zigux/phase12-closure.md` is still absent on the surveyed head",
]

FORBIDDEN_SLICE_MARKERS = [
    "- `drivers/nvme/host/pci.zig` is still absent on the surveyed head",
]

SUPPORT_MANIFEST_FIXTURE_MARKERS = [
    '"lane_key": "P12-L13"',
    '"source_manifest": "zigux/tests/phase12_virtio_scsi_manifest.json"',
    '"Documentation/zigux/phase12-virtio-scsi-slice.md"',
    '"Documentation/zigux/phase12-virtio-scsi-survey.md"',
    '"zigux/tests/phase12_virtio_scsi_packet.zig"',
    '"zigux/tests/phase12_build.zig"',
    '"zigux/Makefile"',
    '"scripts/zigux/check-phase12-virtio-scsi-packet.py"',
]

SURVEY_GATE_MARKERS = [
    'test "phase12 virtio scsi survey gate keeps present lane files explicit"',
    'try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-scsi-slice.md"));',
    'try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-scsi-survey.md"));',
    'try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_scsi_packet.zig"));',
    'try std.testing.expect(try pathExists("zigux/tests/fixtures/phase12_virtio_scsi_manifest.json"));',
    'try std.testing.expect(try pathExists("scripts/zigux/check-phase12-virtio-scsi-packet.py"));',
    'try std.testing.expect(try pathExists("zigux/tests/phase12_build.zig"));',
    'try std.testing.expect(try pathExists("zigux/Makefile"));',
]

MAKEFILE_MARKERS = [
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-smoke phase12-test",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} (expected 1, found {count})"
            )


def forbid_markers(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"forbidden stale marker in {rel_path}: {marker}")


def repo_root() -> Path:
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


def check(root: Path, source_text: str | None = None) -> list[str]:
    errors: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            errors.append(f"missing file: {rel_path}")
    if errors:
        return errors

    checker_source = source_text if source_text is not None else read_text(Path(__file__))
    if MARKER not in checker_source:
        errors.append("checker marker missing from checker source")

    slice_text = read_text(root / SLICE_PATH)
    require_markers(errors, SLICE_PATH, slice_text, SLICE_MARKERS)
    forbid_markers(errors, SLICE_PATH, slice_text, FORBIDDEN_SLICE_MARKERS)
    require_markers(
        errors,
        SUPPORT_MANIFEST_FIXTURE_PATH,
        read_text(root / SUPPORT_MANIFEST_FIXTURE_PATH),
        SUPPORT_MANIFEST_FIXTURE_MARKERS,
    )
    require_markers(
        errors,
        SURVEY_GATE_PATH,
        read_text(root / SURVEY_GATE_PATH),
        SURVEY_GATE_MARKERS,
    )
    require_markers(errors, MAKEFILE_PATH, read_text(root / MAKEFILE_PATH), MAKEFILE_MARKERS)
    return errors


def good_slice_text() -> str:
    return "\n".join(
        [
            "# Phase 12 virtio_scsi Slice",
            "- `PHASE12_SLICE=virtio-scsi-queue-lab-support`",
            "- lane: `complex-drivers-infra`",
            "- `zigux/tests/phase12_virtio_scsi_packet.zig` remains the manifest-backed support replay for this bounded infra-prep slice",
            "- `zigux/tests/phase12_build.zig` keeps the direct replay, syntax-lab smoke, repeated-replan gate, repeated-rollback gate, survey gate, and support packet wired into the shared `phase12` smoke and test routes",
            "- `scripts/zigux/check-phase12-virtio-scsi-packet.py` fails closed if the manifest, slice note, or build route drifts",
            "",
            "## Repo-reality boundaries",
            "- `drivers/nvme/host/pci.zig` now lives in the separate Phase 12 NVMe packet on current `master`, so this `virtio_scsi` support note should treat NVMe as neighboring packet evidence rather than a repo-reality gap",
            "- `Documentation/zigux/phase12-closure.md` is still absent on the surveyed head",
            "",
        ]
    )


def good_support_manifest_fixture_text() -> str:
    return "\n".join(
        [
            "{",
            '  "lane_key": "P12-L13",',
            '  "source_manifest": "zigux/tests/phase12_virtio_scsi_manifest.json",',
            '  "required_paths": [',
            '    "Documentation/zigux/phase12-virtio-scsi-slice.md",',
            '    "Documentation/zigux/phase12-virtio-scsi-survey.md",',
            '    "zigux/tests/phase12_virtio_scsi_packet.zig",',
            '    "zigux/tests/phase12_build.zig",',
            '    "zigux/Makefile",',
            '    "scripts/zigux/check-phase12-virtio-scsi-packet.py"',
            "  ]",
            "}",
            "",
        ]
    )


def good_survey_gate_text() -> str:
    return "\n".join(
        [
            'test "phase12 virtio scsi survey gate keeps present lane files explicit" {',
            '    try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-scsi-slice.md"));',
            '    try std.testing.expect(try pathExists("Documentation/zigux/phase12-virtio-scsi-survey.md"));',
            '    try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_scsi_packet.zig"));',
            '    try std.testing.expect(try pathExists("zigux/tests/fixtures/phase12_virtio_scsi_manifest.json"));',
            '    try std.testing.expect(try pathExists("scripts/zigux/check-phase12-virtio-scsi-packet.py"));',
            '    try std.testing.expect(try pathExists("zigux/tests/phase12_build.zig"));',
            '    try std.testing.expect(try pathExists("zigux/Makefile"));',
            "}",
            "",
        ]
    )


def good_makefile_text() -> str:
    return "\n".join(
        [
            ".PHONY: phase12-smoke phase12-test phase12",
            "phase12-smoke:",
            "\t@true",
            "phase12-test:",
            "\t@true",
            "phase12: phase12-smoke phase12-test",
            "",
        ]
    )


def write_fixture_tree(root: Path) -> None:
    write_text(root / SLICE_PATH, good_slice_text())
    write_text(root / SURVEY_NOTE_PATH, "# Phase 12 Virtio SCSI Survey\n")
    write_text(root / SURVEY_GATE_PATH, good_survey_gate_text())
    write_text(root / SUPPORT_MANIFEST_FIXTURE_PATH, good_support_manifest_fixture_text())
    write_text(root / SUPPORT_PACKET_PATH, "// phase12 virtio scsi support packet fixture\n")
    write_text(root / PHASE12_BUILD_PATH, "// phase12 build fixture\n")
    write_text(root / MAKEFILE_PATH, good_makefile_text())


def expect_contains(errors: list[str], needle: str, label: str) -> None:
    if not any(needle in error for error in errors):
        raise SystemExit(f"{label}: {errors!r}")


def run_self_test() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="phase12-virtio-scsi-packet-"))
    try:
        write_fixture_tree(tmp_root)
        if errors := check(tmp_root, source_text=MARKER):
            raise SystemExit(f"self-test expected success but failed: {errors!r}")

        write_fixture_tree(tmp_root)
        (tmp_root / SUPPORT_PACKET_PATH).unlink()
        expect_contains(
            check(tmp_root, source_text=MARKER),
            f"missing file: {SUPPORT_PACKET_PATH}",
            "missing support packet",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / SLICE_PATH,
            good_slice_text().replace(SLICE_MARKERS[5] + "\n", "", 1),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            SLICE_MARKERS[5],
            "missing slice checker marker",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / SLICE_PATH,
            good_slice_text().replace(SLICE_MARKERS[7] + "\n", "", 1),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            SLICE_MARKERS[7],
            "missing nvme boundary marker",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / SLICE_PATH,
            good_slice_text() + FORBIDDEN_SLICE_MARKERS[0] + "\n",
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            FORBIDDEN_SLICE_MARKERS[0],
            "stale nvme gap marker not rejected",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / SUPPORT_MANIFEST_FIXTURE_PATH,
            good_support_manifest_fixture_text().replace(
                SUPPORT_MANIFEST_FIXTURE_MARKERS[-1] + "\n",
                "",
                1,
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            SUPPORT_MANIFEST_FIXTURE_MARKERS[-1],
            "missing fixture checker path",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / SURVEY_GATE_PATH,
            good_survey_gate_text().replace(SURVEY_GATE_MARKERS[-3] + "\n", "", 1),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            SURVEY_GATE_MARKERS[-3],
            "missing survey-gate checker path",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / MAKEFILE_PATH,
            good_makefile_text().replace(MAKEFILE_MARKERS[-1] + "\n", "", 1),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            MAKEFILE_MARKERS[-1],
            "missing make route summary",
        )

        expect_contains(
            check(tmp_root, source_text="PHASE12_CHECK_PACKET=broken"),
            "checker marker missing from checker source",
            "missing checker marker not detected",
        )
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("PHASE12_VIRTIO_SCSI_PACKET_SELF_TEST=pass")
    print("PHASE12_VIRTIO_SCSI_PACKET_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    parser.add_argument(
        "--root",
        type=Path,
        default=repo_root(),
        help="repository root to validate (defaults to the checker directory)",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("phase12 virtio_scsi support packet validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())