#!/usr/bin/env python3
"""PHASE12_CHECK_PACKET=virtio_scsi_packet

Fail-closed checker for the rollback-only Phase 12 virtio_scsi survey packet.
It keeps the slice note, survey note, fallback catalog, fixture manifest,
survey manifest, survey gate, and shared support-bundle reminders aligned around
current repo reality.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

MARKER = "PHASE12_CHECK_PACKET=virtio_scsi_packet"

SLICE_PATH = "Documentation/zigux/phase12-virtio-scsi-slice.md"
SURVEY_NOTE_PATH = "Documentation/zigux/phase12-virtio-scsi-survey.md"
FALLBACK_CATALOG_PATH = (
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"
)
FIXTURE_MANIFEST_PATH = "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json"
SURVEY_MANIFEST_PATH = "zigux/tests/phase12_virtio_scsi_manifest.json"
SURVEY_GATE_PATH = "zigux/tests/phase12_virtio_scsi_survey.zig"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
MAKEFILE_PATH = "zigux/Makefile"

REQUIRED_FILES = [
    SLICE_PATH,
    SURVEY_NOTE_PATH,
    FALLBACK_CATALOG_PATH,
    FIXTURE_MANIFEST_PATH,
    SURVEY_MANIFEST_PATH,
    SURVEY_GATE_PATH,
    PHASE12_BUILD_PATH,
    MAKEFILE_PATH,
]

TEXT_MARKERS = {
    SLICE_PATH: [
        "`PHASE12_SLICE=virtio-scsi-rollback-evidence`",
        "current `master` no longer serves `drivers/scsi/virtio_scsi.zig`",
        "rollback evidence only",
    ],
    SURVEY_NOTE_PATH: [
        "`PHASE12_STATUS=rollback-evidence-only-live-starter-missing`",
        "* `PHASE12_LANE=P12-L13`",
        "* verified on: `2026-05-20`",
        "rollback-only split machine-checkable",
    ],
    FALLBACK_CATALOG_PATH: [
        "`PHASE12_STATUS=archival-raw-read-fallback`",
        "commit pin: `ee64eec272a352da1d967999c99bb3c3560c9b97`",
        "archival commit-pinned history only",
    ],
    SURVEY_GATE_PATH: [
        '"phase12-virtio-scsi-driver-starter"',
        '"missing_on_master"',
        '"rollback_evidence_present"',
        'pathExists("drivers/scsi/virtio_scsi.zig")',
    ],
    MAKEFILE_PATH: [
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-smoke phase12-test",
    ],
}

FORBIDDEN_MARKERS = [
    "PHASE12_STATUS=starter-present-queue-submit-completion-and-recovery-survey",
    "current `master` now carries `zigux/tests/phase12_virtio_scsi.zig` as the direct bounded replay",
]

EXPECTED_ABSENT = [
    "drivers/scsi/virtio_scsi.zig",
    "zigux/tests/phase12_virtio_scsi.zig",
    "zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
]


def repo_root() -> Path:
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_markers(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing marker in {rel_path}: {marker}")


def forbid_markers(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"forbidden stale marker in {rel_path}: {marker}")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            errors.append(f"missing file: {rel_path}")
    if errors:
        return errors

    checker_source = read_text(Path(__file__))
    if MARKER not in checker_source:
        errors.append("checker marker missing from checker source")

    for rel_path, markers in TEXT_MARKERS.items():
        text = read_text(root / rel_path)
        require_markers(errors, rel_path, text, markers)
        forbid_markers(errors, rel_path, text, FORBIDDEN_MARKERS)

    fixture_manifest = json.loads(read_text(root / FIXTURE_MANIFEST_PATH))
    survey_manifest = json.loads(read_text(root / SURVEY_MANIFEST_PATH))

    if fixture_manifest.get("verified_on") != "2026-05-20":
        errors.append("fixture manifest verified_on drift")
    if fixture_manifest.get("expected_absent_paths") != EXPECTED_ABSENT:
        errors.append("fixture manifest expected_absent_paths drift")
    for rel_path in fixture_manifest.get("required_paths", []):
        if not (root / rel_path).exists():
            errors.append(f"fixture required path missing: {rel_path}")
    for rel_path in EXPECTED_ABSENT:
        if (root / rel_path).exists():
            errors.append(f"expected absent path unexpectedly present: {rel_path}")

    summary = survey_manifest.get("survey_summary", {})
    if survey_manifest.get("verified_on") != "2026-05-20":
        errors.append("survey manifest verified_on drift")
    if summary.get("preexisting_virtio_scsi_zig_present") is not False:
        errors.append("survey manifest still claims driver starter present")
    if summary.get("preexisting_phase12_direct_test_present") is not False:
        errors.append("survey manifest still claims direct replay present")
    if summary.get("preexisting_phase12_repeated_rollback_gate_present") is not False:
        errors.append("survey manifest still claims repeated rollback gate present")
    if summary.get("preexisting_phase12_survey_gate_present") is not True:
        errors.append("survey manifest lost survey gate presence")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=repo_root(),
        help="repository root to validate",
    )
    args = parser.parse_args()

    errors = check(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("phase12 virtio_scsi rollback-evidence packet validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
