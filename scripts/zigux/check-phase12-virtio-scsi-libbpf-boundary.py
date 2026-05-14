#!/usr/bin/env python3
"""PHASE12_CHECK_PACKET=virtio_scsi_libbpf_boundary

Fail-closed checker for the bounded Phase 12 virtio_scsi recovery anchor and the
parked libbpf verify-shard boundary.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

MARKER = "PHASE12_CHECK_PACKET=virtio_scsi_libbpf_boundary"

VIRTIO_SCSI_DRIVER_PATH = "drivers/scsi/virtio_scsi.zig"
VIRTIO_SCSI_TEST_PATH = "zigux/tests/phase12_virtio_scsi.zig"
VIRTIO_SCSI_REPEATED_ROLLBACK_PATH = (
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig"
)
LIBBPF_SURVEY_PATH = "Documentation/zigux/phase12-libbpf-segment-survey.md"
LIBBPF_VERIFY_NOTE_PATH = "Documentation/zigux/phase12-libbpf-verify-shard-note.md"
LIBBPF_SNAPSHOT_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"

REQUIRED_FILES = [
    VIRTIO_SCSI_DRIVER_PATH,
    VIRTIO_SCSI_TEST_PATH,
    VIRTIO_SCSI_REPEATED_ROLLBACK_PATH,
    LIBBPF_SURVEY_PATH,
    LIBBPF_VERIFY_NOTE_PATH,
    LIBBPF_SNAPSHOT_PATH,
]

VIRTIO_SCSI_DRIVER_MARKERS = [
    '.anchor = "drivers/scsi/virtio_scsi.c"',
    ".touches_live_dma = false",
    ".touches_transport_reset = true",
    "pub fn recoveryQueuePlan(",
    "pub fn recoveryQueueDepthSummary(",
    "pub fn recoveryIoQueueMapSummary(",
    "pub fn recoveryEventBufferOwnershipSummary(",
    "pub fn recoveryRequestQueueRestoreSummary(",
    "pub fn recoveryHostScanSummary(",
    "pub fn restoreAfterTransportReset(",
]

VIRTIO_SCSI_TEST_MARKERS = [
    'test "phase12 virtio scsi recovery queue depth summary mirrors the frozen clamp"',
    'test "phase12 virtio scsi recovery host scan summary records restore ordering before rescan"',
    "recoveryQueueDepthSummary()",
    "recoveryHostScanSummary()",
]

VIRTIO_SCSI_REPEATED_ROLLBACK_MARKERS = [
    'test "phase12 virtio scsi repeated rollback gate reuses only replanned queue and depth state"',
    "recoveryEventBufferOwnershipSummary()",
    "recoveryHostScanSummary()",
    "recoveryQueuePlan()",
    "recoveryQueueDepthSummary()",
    "const second_restore = try lab.restoreAfterTransportReset();",
]

LIBBPF_SNAPSHOT_MARKERS = [
    '"lane_key": "P12-L16"',
    '"tools/lib/bpf/zigux_segments/verify.zig"',
    '"tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"',
]

LIBBPF_VERIFY_NOTE_MARKERS = [
    "`PHASE12_STATUS=parked`",
    "the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/verify.zig` stay recorded only through shared survey, parked, or anti-overlap notes until they land again on current `master`",
    "the snapshot anchor remains the truthful bounded signal here while those direct replay files stay absent from the shipped checkout",
]

LIBBPF_SURVEY_MARKERS = [
    "That matters because current `master` still exposes a bounded direct `zigux_segments` footing through `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `online_cpu_routing.zig`, `perf_buffer_poll.zig`, and `manifest.json`, while `verify.zig`, `file_path_handle_bridge.zig`, and the direct `phase12_libbpf_*` replay files remain parked note-owned boundaries.",
    "the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/verify.zig` and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` still stay recorded only through the survey, verify-shard, and anti-overlap notes until they land on current `master`",
    "The same boundary applies to the current checked-in `tools/lib/bpf/zigux_segments/manifest.json` story: current Phase 12 wording should keep treating it as present helper evidence on current `master`, while `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and the direct `phase12_libbpf_*` replay files still remain outside the shipped smoke-first route.",
]

LIBBPF_SURVEY_FORBIDDEN_MARKERS = [
    "current `master` still exposes a bounded direct libbpf segment footing under `tools/lib/bpf/zigux_segments/` through `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `online_cpu_routing.zig`, `perf_buffer_poll.zig`, `manifest.json`, `verify.zig`, and `file_path_handle_bridge.zig`.",
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


def require_absent(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"forbidden marker present in {rel_path}: {marker}")


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

    require_markers(
        errors,
        VIRTIO_SCSI_DRIVER_PATH,
        read_text(root / VIRTIO_SCSI_DRIVER_PATH),
        VIRTIO_SCSI_DRIVER_MARKERS,
    )
    require_markers(
        errors,
        VIRTIO_SCSI_TEST_PATH,
        read_text(root / VIRTIO_SCSI_TEST_PATH),
        VIRTIO_SCSI_TEST_MARKERS,
    )
    require_markers(
        errors,
        VIRTIO_SCSI_REPEATED_ROLLBACK_PATH,
        read_text(root / VIRTIO_SCSI_REPEATED_ROLLBACK_PATH),
        VIRTIO_SCSI_REPEATED_ROLLBACK_MARKERS,
    )
    require_markers(
        errors,
        LIBBPF_SNAPSHOT_PATH,
        read_text(root / LIBBPF_SNAPSHOT_PATH),
        LIBBPF_SNAPSHOT_MARKERS,
    )
    require_markers(
        errors,
        LIBBPF_VERIFY_NOTE_PATH,
        read_text(root / LIBBPF_VERIFY_NOTE_PATH),
        LIBBPF_VERIFY_NOTE_MARKERS,
    )
    survey_text = read_text(root / LIBBPF_SURVEY_PATH)
    require_markers(errors, LIBBPF_SURVEY_PATH, survey_text, LIBBPF_SURVEY_MARKERS)
    require_absent(
        errors,
        LIBBPF_SURVEY_PATH,
        survey_text,
        LIBBPF_SURVEY_FORBIDDEN_MARKERS,
    )
    return errors


def good_virtio_scsi_driver_text() -> str:
    return "\n".join(
        [
            'const descriptor = .{ .anchor = "drivers/scsi/virtio_scsi.c", .touches_live_dma = false, .touches_transport_reset = true };',
            "pub fn recoveryQueuePlan() void {}",
            "pub fn recoveryQueueDepthSummary() void {}",
            "pub fn recoveryIoQueueMapSummary() void {}",
            "pub fn recoveryEventBufferOwnershipSummary() void {}",
            "pub fn recoveryRequestQueueRestoreSummary() void {}",
            "pub fn recoveryHostScanSummary() void {}",
            "pub fn restoreAfterTransportReset() void {}",
            "",
        ]
    )


def good_virtio_scsi_test_text() -> str:
    return "\n".join(
        [
            'test "phase12 virtio scsi recovery queue depth summary mirrors the frozen clamp" {',
            "    _ = recoveryQueueDepthSummary();",
            "}",
            'test "phase12 virtio scsi recovery host scan summary records restore ordering before rescan" {',
            "    _ = recoveryHostScanSummary();",
            "}",
            "",
        ]
    )


def good_repeated_rollback_text() -> str:
    return "\n".join(
        [
            'test "phase12 virtio scsi repeated rollback gate reuses only replanned queue and depth state" {',
            "    _ = recoveryQueuePlan();",
            "    _ = recoveryQueueDepthSummary();",
            "    _ = recoveryEventBufferOwnershipSummary();",
            "    _ = recoveryHostScanSummary();",
            "    const second_restore = try lab.restoreAfterTransportReset();",
            "    _ = second_restore;",
            "}",
            "",
        ]
    )


def good_snapshot_text() -> str:
    return "\n".join(
        [
            "{",
            '  "lane_key": "P12-L16",',
            '  "parked_absent_boundaries": [',
            '    "tools/lib/bpf/zigux_segments/verify.zig",',
            '    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"',
            "  ]",
            "}",
            "",
        ]
    )


def good_verify_note_text() -> str:
    return "\n".join(
        [
            "# Phase 12 Libbpf Verify Shard Note",
            "",
            "- `PHASE12_STATUS=parked`",
            "- the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/verify.zig` stay recorded only through shared survey, parked, or anti-overlap notes until they land again on current `master`",
            "- the snapshot anchor remains the truthful bounded signal here while those direct replay files stay absent from the shipped checkout",
            "",
        ]
    )


def good_survey_text() -> str:
    return "\n".join(
        [
            "# Phase 12 Libbpf Segment Survey",
            "",
            "That matters because current `master` still exposes a bounded direct `zigux_segments` footing through `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `online_cpu_routing.zig`, `perf_buffer_poll.zig`, and `manifest.json`, while `verify.zig`, `file_path_handle_bridge.zig`, and the direct `phase12_libbpf_*` replay files remain parked note-owned boundaries.",
            "",
            "The direct helper-first footing remains roadmap-relevant, while the broader parked libbpf reviewability packet has to stay described through the survey, verify-shard, anti-overlap notes, and snapshot anchor until the shared replay order actually adopts it.",
            "",
            "- the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/verify.zig` and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` still stay recorded only through the survey, verify-shard, and anti-overlap notes until they land on current `master`",
            "- The same boundary applies to the current checked-in `tools/lib/bpf/zigux_segments/manifest.json` story: current Phase 12 wording should keep treating it as present helper evidence on current `master`, while `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and the direct `phase12_libbpf_*` replay files still remain outside the shipped smoke-first route.",
            "",
        ]
    )


def write_fixture_tree(root: Path) -> None:
    write_text(root / VIRTIO_SCSI_DRIVER_PATH, good_virtio_scsi_driver_text())
    write_text(root / VIRTIO_SCSI_TEST_PATH, good_virtio_scsi_test_text())
    write_text(root / VIRTIO_SCSI_REPEATED_ROLLBACK_PATH, good_repeated_rollback_text())
    write_text(root / LIBBPF_SNAPSHOT_PATH, good_snapshot_text())
    write_text(root / LIBBPF_VERIFY_NOTE_PATH, good_verify_note_text())
    write_text(root / LIBBPF_SURVEY_PATH, good_survey_text())


def expect_contains(errors: list[str], needle: str, label: str) -> None:
    if not any(needle in error for error in errors):
        raise SystemExit(f"{label}: {errors!r}")


def run_self_test() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="phase12-virtio-scsi-libbpf-boundary-"))
    try:
        write_fixture_tree(tmp_root)
        if errors := check(tmp_root, source_text=MARKER):
            raise SystemExit(f"self-test expected success but failed: {errors!r}")

        write_fixture_tree(tmp_root)
        (tmp_root / VIRTIO_SCSI_REPEATED_ROLLBACK_PATH).unlink()
        expect_contains(
            check(tmp_root, source_text=MARKER),
            f"missing file: {VIRTIO_SCSI_REPEATED_ROLLBACK_PATH}",
            "missing repeated rollback gate",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / LIBBPF_SURVEY_PATH,
            good_survey_text().replace(LIBBPF_SURVEY_MARKERS[0], "", 1),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            LIBBPF_SURVEY_MARKERS[0],
            "missing corrected survey footing marker",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / LIBBPF_SURVEY_PATH,
            good_survey_text() + LIBBPF_SURVEY_FORBIDDEN_MARKERS[0] + "\n",
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            LIBBPF_SURVEY_FORBIDDEN_MARKERS[0],
            "forbidden survey overclaim not detected",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / LIBBPF_VERIFY_NOTE_PATH,
            good_verify_note_text().replace(LIBBPF_VERIFY_NOTE_MARKERS[1], "", 1),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            LIBBPF_VERIFY_NOTE_MARKERS[1],
            "missing verify-note parked-boundary marker",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / VIRTIO_SCSI_DRIVER_PATH,
            good_virtio_scsi_driver_text().replace(
                "pub fn recoveryHostScanSummary() void {}\n", "", 1
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "pub fn recoveryHostScanSummary(",
            "missing virtio-scsi recovery marker",
        )

        write_fixture_tree(tmp_root)
        write_text(
            tmp_root / VIRTIO_SCSI_REPEATED_ROLLBACK_PATH,
            good_repeated_rollback_text().replace(
                "    _ = recoveryEventBufferOwnershipSummary();\n", "", 1
            ),
        )
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "recoveryEventBufferOwnershipSummary()",
            "missing repeated rollback ownership marker",
        )

        expect_contains(
            check(tmp_root, source_text="PHASE12_CHECK_PACKET=broken"),
            "checker marker missing from checker source",
            "missing checker marker not detected",
        )
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_SELF_TEST=pass")
    print("PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_SELF_TEST_CASE_COUNT=7")
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

    print("phase12 virtio_scsi libbpf boundary validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
