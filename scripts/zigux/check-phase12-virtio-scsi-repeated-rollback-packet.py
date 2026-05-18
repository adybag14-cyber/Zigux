#!/usr/bin/env python3
"""Fail closed on the Phase 12 virtio_scsi repeated-rollback packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile

SURVEY_PATH = Path("Documentation/zigux/phase12-virtio-scsi-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase12_virtio_scsi_manifest.json")
BUILD_PATH = Path("zigux/tests/phase12_build.zig")
ROLLBACK_GATE_PATH = Path("zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig")

REQUIRED_MARKERS = {
    SURVEY_PATH: [
        "current `master` now carries `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig` so the second-cycle rollback contract and post-restore readiness stay explicit",
        "current `master` still carries `zigux/tests/phase12_build.zig`, and that shared build route still runs the direct `virtio_scsi` tests, syntax-lab smoke, repeated-replan gate, repeated-rollback gate, and packet replay",
        "reversible-delivery evidence: current `master` keeps the direct test, syntax lab, repeated-replan gate, repeated-rollback gate, support packet, survey note, survey gate, shared `zigux/tests/phase12_build.zig` route, and `zigux/Makefile` wrappers aligned around the same bounded queue-submit-completion-and-recovery packet",
    ],
    MANIFEST_PATH: [
        '"id": "phase12-virtio-scsi-repeated-rollback-gate"',
        '"status": "landed_on_master"',
        '"kind": "validation"',
        '"zigux_destination": "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig"',
        '"why_now": "The repeated-rollback gate keeps the second-cycle rollback contract and post-restore readiness explicit without claiming runtime reset execution."',
    ],
    BUILD_PATH: [
        '.root_source_file = b.path("phase12_virtio_scsi_repeated_rollback_gate.zig"),',
        '.name = "phase12-virtio-scsi-repeated-rollback-gate-tests",',
        "run_repeated_rollback_tests.setCwd(b.path(\"../..\"));",
        "smoke_step.dependOn(&run_repeated_rollback_tests.step);",
        "test_step.dependOn(&run_repeated_rollback_tests.step);",
    ],
    ROLLBACK_GATE_PATH: [
        'test "phase12 virtio scsi repeated rollback gate reuses only replanned queue and depth state" {',
        "_ = try lab.restoreAfterTransportReset();",
        "try std.testing.expectError(error.TransportNotFrozen, lab.recoveryQueuePlan());",
        "try std.testing.expectEqual(@as(u16, 2), second_restore.recovery_generation);",
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
            if relative_path == BUILD_PATH:
                text = text.replace(
                    "test_step.dependOn(&run_repeated_rollback_tests.step);\n", ""
                )
            path.write_text(text, encoding="utf-8")

        broken_errors = validate(broken_root)
        expected = (
            f"{BUILD_PATH}: missing marker: "
            "test_step.dependOn(&run_repeated_rollback_tests.step);"
        )
        if expected not in broken_errors:
            print("self-test did not catch missing repeated rollback build wiring", file=sys.stderr)
            print("PHASE12_VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_SELF_TEST=fail")
            return 1

    print("PHASE12_VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_SELF_TEST=pass")
    print("PHASE12_VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_SELF_TEST_CASES=2")
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
