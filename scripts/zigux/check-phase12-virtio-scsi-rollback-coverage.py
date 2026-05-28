#!/usr/bin/env python3
"""Fail closed on the Phase 12 virtio_scsi rollback-only coverage packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile

SURVEY_PATH = Path("Documentation/zigux/phase12-virtio-scsi-survey.md")
FALLBACK_CATALOG_PATH = Path("Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md")
MANIFEST_PATH = Path("zigux/tests/phase12_virtio_scsi_manifest.json")
FIXTURE_MANIFEST_PATH = Path("zigux/tests/fixtures/phase12_virtio_scsi_manifest.json")
SURVEY_GATE_PATH = Path("zigux/tests/phase12_virtio_scsi_survey.zig")
BUILD_PATH = Path("zigux/tests/phase12_build.zig")

REQUIRED_MARKERS = {
    SURVEY_PATH: [
        "`PHASE12_LANE=P12-L09`",
        "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`",
        "rollback-only split machine-checkable",
        "reversible-delivery evidence: current `master` preserves the survey note, fixture manifest, survey manifest, survey gate, dedicated survey-build route, checker, shared build bundle, and `zigux/Makefile` as rollback evidence while the driver-local starter and replay gates remain absent",
        "rollback drill: when this packet moves",
    ],
    FALLBACK_CATALOG_PATH: [
        "- survey-build replay: `zigux/tests/phase12_virtio_scsi_survey_build.zig`",
        "- current `master` still carries this fallback catalog, the survey note, the slice note, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_virtio_scsi_survey_build.zig`, `scripts/zigux/check-phase12-virtio-scsi-packet.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-build-inventory.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-cross-compile-smoke.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, `scripts/zigux/validate-phase12.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`",
        "- keep this note archival only while the current-master survey note, fixture manifest, survey manifest, survey replay, survey-build replay, survey gate, validator, shared build route, and `zigux/Makefile` are rollback evidence only",
    ],
    MANIFEST_PATH: [
        '"preexisting_phase12_repeated_rollback_gate_present": false',
        '"preexisting_phase12_support_manifest_present": true',
        '"id": "phase12-virtio-scsi-repeated-rollback-gate"',
        '"status": "missing_on_master"',
        '"why_now": "Current master no longer serves the repeated rollback gate, so post-restore readiness evidence is archival only."',
    ],
    FIXTURE_MANIFEST_PATH: [
        '"fixture_kind": "rollback_evidence_presence_manifest"',
        '"zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig"',
        '"expected_absent_paths"',
        "rollback-only current-master state",
    ],
    SURVEY_GATE_PATH: [
        "try std.testing.expect(!manifest.survey_summary.preexisting_phase12_repeated_rollback_gate_present);",
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "rollback-only split machine-checkable") != null);',
        'try std.testing.expect(!try pathExists("zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig"));',
    ],
}

FORBIDDEN_MARKERS = {
    SURVEY_PATH: [
        "current `master` now carries `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig` so the second-cycle rollback contract and post-restore readiness stay explicit",
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
        for relative_path in FORBIDDEN_MARKERS:
            path = root / relative_path
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")

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
                    '"preexisting_phase12_repeated_rollback_gate_present": false\n',
                    "",
                )
            path.write_text(text, encoding="utf-8")
        for relative_path in FORBIDDEN_MARKERS:
            path = broken_root / relative_path
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")

        broken_errors = validate(broken_root)
        expected = (
            f"{MANIFEST_PATH}: missing marker: "
            '"preexisting_phase12_repeated_rollback_gate_present": false'
        )
        if expected not in broken_errors:
            print("self-test did not catch missing manifest absence marker", file=sys.stderr)
            print("PHASE12_VIRTIO_SCSI_ROLLBACK_COVERAGE_SELF_TEST=fail")
            return 1

        stale_root = root / "stale"
        for relative_path, markers in REQUIRED_MARKERS.items():
            path = stale_root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(markers) + "\n", encoding="utf-8")
        for relative_path, markers in FORBIDDEN_MARKERS.items():
            path = stale_root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            text = ""
            if relative_path == BUILD_PATH:
                text = markers[0] + "\n"
            path.write_text(text, encoding="utf-8")

        stale_errors = validate(stale_root)
        stale_expected = (
            f"{BUILD_PATH}: forbidden stale marker: "
            '.root_source_file = b.path("phase12_virtio_scsi_repeated_rollback_gate.zig"),'
        )
        if stale_expected not in stale_errors:
            print("self-test did not catch stale shared-build rollback marker", file=sys.stderr)
            print("PHASE12_VIRTIO_SCSI_ROLLBACK_COVERAGE_SELF_TEST=fail")
            return 1

    print("PHASE12_VIRTIO_SCSI_ROLLBACK_COVERAGE_SELF_TEST=pass")
    print("PHASE12_VIRTIO_SCSI_ROLLBACK_COVERAGE_SELF_TEST_CASES=3")
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
