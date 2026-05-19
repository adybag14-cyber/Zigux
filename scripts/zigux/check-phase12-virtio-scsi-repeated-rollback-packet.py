#!/usr/bin/env python3
"""Fail closed on the Phase 12 virtio_scsi repeated-rollback packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile

SURVEY_PATH = Path("Documentation/zigux/phase12-virtio-scsi-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase12_virtio_scsi_manifest.json")
SURVEY_GATE_PATH = Path("zigux/tests/phase12_virtio_scsi_survey.zig")
ROLLBACK_GATE_PATH = Path("zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig")
SUPPORT_MANIFEST_PATH = Path("zigux/tests/fixtures/phase12_virtio_scsi_manifest.json")

REQUIRED_MARKERS = {
    SURVEY_PATH: [
        "phase12_virtio_scsi_repeated_rollback_gate.zig",
        "second-cycle rollback contract",
        "second-cycle rollback readiness",
        "rollback drill: when this packet moves",
    ],
    MANIFEST_PATH: [
        '"preexisting_phase12_repeated_rollback_gate_present": true',
        '"id": "phase12-virtio-scsi-repeated-rollback-gate"',
        '"status": "landed_on_master"',
        '"zigux_destination": "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig"',
        '"why_now": "The repeated-rollback gate keeps the second-cycle rollback contract and post-restore readiness explicit without claiming runtime reset execution."',
    ],
    SURVEY_GATE_PATH: [
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12_virtio_scsi_repeated_rollback_gate.zig") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "second-cycle rollback contract") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "second-cycle rollback readiness") != null);',
        'try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig"));',
    ],
    ROLLBACK_GATE_PATH: [
        'test "phase12 virtio scsi repeated rollback gate reuses only replanned queue and depth state" {',
        "_ = try lab.restoreAfterTransportReset();",
        "try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueuePlan());",
        "try std.testing.expectEqual(@as(u16, 2), second_restore.recovery_generation);",
    ],
    SUPPORT_MANIFEST_PATH: [
        '"zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig"',
        "existing Phase 12 virtio_scsi survey packet",
    ],
}

FORBIDDEN_MARKERS = {
    SURVEY_PATH: [
        "shared build route still runs the direct `virtio_scsi` tests",
    ],
    ROLLBACK_GATE_PATH: [
        "shared `smoke` step",
    ],
}


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = root / relative_path
        if not path.is_file():
            errors.append(f"missing required file: {relative_path}")
            continue

        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative_path}: missing marker: {marker}")

    for relative_path, markers in FORBIDDEN_MARKERS.items():
        path = root / relative_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                errors.append(f"{relative_path}: forbidden stale marker: {marker}")

    return errors


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for relative_path, markers in REQUIRED_MARKERS.items():
            path = root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(markers) + "\n", encoding="utf-8")

        errors = validate(root)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            print("PHASE12_VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_SELF_TEST=fail")
            return 1

        broken_root = root / "broken"
        for relative_path, markers in REQUIRED_MARKERS.items():
            path = broken_root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            text = "\n".join(markers) + "\n"
            if relative_path == SURVEY_GATE_PATH:
                text = text.replace(
                    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "second-cycle rollback readiness") != null);\n',
                    "",
                )
            path.write_text(text, encoding="utf-8")

        broken_errors = validate(broken_root)
        expected = (
            f"{SURVEY_GATE_PATH}: missing marker: "
            'try std.testing.expect(std.mem.indexOf(u8, survey_note, "second-cycle rollback readiness") != null);'
        )
        if expected not in broken_errors:
            print("self-test did not catch missing survey-gate rollback marker", file=sys.stderr)
            print("PHASE12_VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_SELF_TEST=fail")
            return 1

        stale_root = root / "stale"
        for relative_path, markers in REQUIRED_MARKERS.items():
            path = stale_root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            text = "\n".join(markers) + "\n"
            if relative_path == SURVEY_PATH:
                text += "shared build route still runs the direct `virtio_scsi` tests\n"
            path.write_text(text, encoding="utf-8")

        stale_errors = validate(stale_root)
        stale_expected = (
            f"{SURVEY_PATH}: forbidden stale marker: "
            "shared build route still runs the direct `virtio_scsi` tests"
        )
        if stale_expected not in stale_errors:
            print("self-test did not catch stale shared-build wording", file=sys.stderr)
            print("PHASE12_VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_SELF_TEST=fail")
            return 1

    print("PHASE12_VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_SELF_TEST=pass")
    print("PHASE12_VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_SELF_TEST_CASES=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate(Path(args.root))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("Phase 12 virtio_scsi repeated rollback packet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
