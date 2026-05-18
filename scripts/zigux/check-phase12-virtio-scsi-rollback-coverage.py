#!/usr/bin/env python3
"""Fail closed on the Phase 12 virtio_scsi rollback-coverage packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile

SURVEY_PATH = Path("Documentation/zigux/phase12-virtio-scsi-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase12_virtio_scsi_manifest.json")
SURVEY_GATE_PATH = Path("zigux/tests/phase12_virtio_scsi_survey.zig")
BUILD_PATH = Path("zigux/tests/phase12_build.zig")

REQUIRED_MARKERS = {
    SURVEY_PATH: [
        "`PHASE12_LANE=P12-L13`",
        "current `master` now carries `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig` so the second-cycle rollback contract and post-restore readiness stay explicit",
        "fallback path: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` remains the read-only degraded-read companion for this packet",
        "rollback drill: when this packet moves",
    ],
    MANIFEST_PATH: [
        '"lane_key": "P12-L13"',
        '"preexisting_phase12_repeated_rollback_gate_present": true',
        '"preexisting_phase12_survey_gate_present": true',
    ],
    SURVEY_GATE_PATH: [
        'try std.testing.expectEqualStrings("P12-L13", manifest.lane_key);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12_virtio_scsi_repeated_rollback_gate.zig") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "second-cycle rollback contract") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "second-cycle rollback readiness") != null);',
    ],
    BUILD_PATH: [
        '.root_source_file = b.path("phase12_virtio_scsi_repeated_rollback_gate.zig"),',
        '.name = "phase12-virtio-scsi-repeated-rollback-gate-tests",',
        "smoke_step.dependOn(&run_repeated_rollback_tests.step);",
        "test_step.dependOn(&run_repeated_rollback_tests.step);",
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
            print("PHASE12_VIRTIO_SCSI_ROLLBACK_COVERAGE_SELF_TEST=fail")
            return 1

        broken_root = root / "broken"
        for relative_path, markers in REQUIRED_MARKERS.items():
            path = broken_root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            text = "\n".join(markers) + "\n"
            if relative_path == MANIFEST_PATH:
                text = text.replace(
                    '"preexisting_phase12_repeated_rollback_gate_present": true\n',
                    "",
                )
            path.write_text(text, encoding="utf-8")

        broken_errors = validate(broken_root)
        expected = (
            f"{MANIFEST_PATH}: missing marker: "
            '"preexisting_phase12_repeated_rollback_gate_present": true'
        )
        if expected not in broken_errors:
            print("self-test did not catch missing manifest rollback marker", file=sys.stderr)
            print("PHASE12_VIRTIO_SCSI_ROLLBACK_COVERAGE_SELF_TEST=fail")
            return 1

    print("PHASE12_VIRTIO_SCSI_ROLLBACK_COVERAGE_SELF_TEST=pass")
    print("PHASE12_VIRTIO_SCSI_ROLLBACK_COVERAGE_SELF_TEST_CASES=2")
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

    print("Phase 12 virtio_scsi rollback coverage check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
