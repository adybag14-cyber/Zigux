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
        "active `P12-L13` survey packet",
        "current `master` no longer serves `drivers/scsi/virtio_scsi.zig`",
        "rollback evidence only",
        "throughput-parity, and survey-gate tests through the shared `smoke` and `test` steps",
    ],
    SURVEY_NOTE_PATH: [
        "`PHASE12_STATUS=rollback-evidence-only-live-starter-missing`",
        "* `PHASE12_LANE=P12-L13`",
        "* verified on: `2026-05-21`",
        "* `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`",
        "rollback owner: `P12-L13` keeps the active virtio_scsi survey packet",
        "throughput-parity, and survey-gate tests as support-bundle evidence",
        "make -C zigux phase12-validate",
        "rollback-only split machine-checkable",
    ],
    FALLBACK_CATALOG_PATH: [
        "`PHASE12_STATUS=archival-raw-read-fallback`",
        "commit pin: `ee64eec272a352da1d967999c99bb3c3560c9b97`",
        "- exact coverage evidence refreshed on `2026-05-21` against live current `master`",
        "- survey-backed anchor: `zigux/tests/phase12_virtio_scsi_manifest.json`",
        "- survey note: `Documentation/zigux/phase12-virtio-scsi-survey.md`",
        "- survey replay: `zigux/tests/phase12_virtio_scsi_survey.zig`",
        "- survey gate: `scripts/zigux/check-phase12-virtio-scsi-packet.py`",
        "- verifier and replay companions on current `master`: `scripts/zigux/check-phase12-virtio-scsi-packet.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`",
        "current authoritative packet truth now lives in the shared-tree survey companions and validator surfaces reread for this lane",
        "current `master` no longer serves `drivers/scsi/virtio_scsi.zig`",
        "exact current shared support-bundle and replay order is `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, then `make -C zigux phase12`",
        "`make -C zigux phase12-validate` is current repo evidence again and now reruns the shared build-only and release-readiness checkers plus `scripts/zigux/validate-phase12.py`",
        "archival commit-pinned history only",
    ],
    SURVEY_GATE_PATH: [
        '"phase12-virtio-scsi-driver-starter"',
        '"missing_on_master"',
        '"rollback_evidence_present"',
        'pathExists("drivers/scsi/virtio_scsi.zig")',
        '"rollback owner: `P12-L13` keeps the active virtio_scsi survey packet"',
        '"survey-gate tests"',
    ],
    PHASE12_BUILD_PATH: [
        "phase12_virtio_net_receive_refill_replay.zig",
        "phase12_virtio_net_survey.zig",
        "phase12-virtio-net-receive-refill-replay-tests",
        "phase12-virtio-net-survey-tests",
        "receive-refill replay",
    ],
    MAKEFILE_PATH: [
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
}

FORBIDDEN_MARKERS = [
    "PHASE12_STATUS=starter-present-queue-submit-completion-and-recovery-survey",
    "current `master` now carries `zigux/tests/phase12_virtio_scsi.zig` as the direct bounded replay",
    "`make -C zigux phase12-validate` stays reminder-only validator wrapper vocabulary until that wrapper returns on current `master`",
]

EXPECTED_ABSENT = [
    "drivers/scsi/virtio_scsi.zig",
    "zigux/tests/phase12_virtio_scsi.zig",
    "zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
]

EXPECTED_REQUIRED_PATHS = [
    "Documentation/zigux/phase12-virtio-scsi-slice.md",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_virtio_scsi_survey.zig",
    "scripts/zigux/check-phase12-virtio-scsi-packet.py",
    "zigux/tests/phase12_build.zig",
    "zigux/Makefile",
]

EXPECTED_SUMMARY_FLAGS = {
    "preexisting_virtio_scsi_zig_present": False,
    "preexisting_phase12_direct_test_present": False,
    "preexisting_phase12_syntax_lab_present": False,
    "preexisting_phase12_repeated_replan_gate_present": False,
    "preexisting_phase12_repeated_rollback_gate_present": False,
    "preexisting_phase12_support_packet_present": False,
    "preexisting_phase12_support_manifest_present": True,
    "preexisting_phase12_packet_checker_present": True,
    "preexisting_phase12_slice_note_present": True,
    "preexisting_phase12_build_present": True,
    "preexisting_phase12_make_targets_present": True,
    "preexisting_phase12_survey_note_present": True,
    "preexisting_phase12_fallback_catalog_present": True,
    "preexisting_phase12_survey_gate_present": True,
}

EXPECTED_ROADMAP_GAP_STATUSES = {
    "dma_safe_abstractions": "rollback_evidence_only_live_starter_missing",
    "queueing_correctness": "rollback_evidence_present_no_live_queue_planner",
    "throughput_and_recovery_parity": "rollback_evidence_present_no_runtime_recovery_replay",
    "segmented_rollout": "survey_packet_and_fallback_present_driver_local_replay_missing",
}

EXPECTED_GAP_STATUSES = {
    "phase12-virtio-scsi-driver-starter": "missing_on_master",
    "phase12-virtio-scsi-direct-replay": "missing_on_master",
    "phase12-virtio-scsi-syntax-lab": "missing_on_master",
    "phase12-virtio-scsi-repeated-replan-gate": "missing_on_master",
    "phase12-virtio-scsi-repeated-rollback-gate": "missing_on_master",
    "phase12-build-gate": "shared_support_bundle_present",
    "phase12-make-target": "shared_make_targets_present",
    "phase12-virtio-scsi-survey-gate": "rollback_evidence_present",
    "phase12-virtio-scsi-survey-note": "rollback_evidence_present",
    "phase12-virtio-scsi-runtime-request-flow": "blocked_on_driver_return_dma_scsi_host_runtime",
}


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

    survey_note_text = read_text(root / SURVEY_NOTE_PATH)
    if survey_note_text.count("`zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`") != 1:
        errors.append("survey note fixture manifest boundary drift")
    if survey_note_text.count("`zigux/tests/phase12_virtio_scsi_manifest.json`") != 1:
        errors.append("survey note survey manifest boundary drift")

    fixture_manifest = json.loads(read_text(root / FIXTURE_MANIFEST_PATH))
    survey_manifest = json.loads(read_text(root / SURVEY_MANIFEST_PATH))

    if fixture_manifest.get("lane_key") != "P12-L13":
        errors.append("fixture manifest lane_key drift")
    if fixture_manifest.get("phase") != "Phase 12":
        errors.append("fixture manifest phase drift")
    if fixture_manifest.get("surveyed_commit") != "unresolved_on_master":
        errors.append("fixture manifest surveyed_commit drift")
    if fixture_manifest.get("verified_on") != "2026-05-21":
        errors.append("fixture manifest verified_on drift")
    if fixture_manifest.get("anchor") != "drivers/scsi/virtio_scsi.c":
        errors.append("fixture manifest anchor drift")
    if fixture_manifest.get("fixture_kind") != "rollback_evidence_presence_manifest":
        errors.append("fixture manifest fixture_kind drift")
    if fixture_manifest.get("source_manifest") != SURVEY_MANIFEST_PATH:
        errors.append("fixture manifest source_manifest drift")
    if fixture_manifest.get("required_paths") != EXPECTED_REQUIRED_PATHS:
        errors.append("fixture manifest required_paths drift")
    if fixture_manifest.get("expected_absent_paths") != EXPECTED_ABSENT:
        errors.append("fixture manifest expected_absent_paths drift")
    notes = fixture_manifest.get("notes")
    if not isinstance(notes, list) or len(notes) != 2:
        errors.append("fixture manifest notes drift")
    for rel_path in fixture_manifest.get("required_paths", []):
        if not (root / rel_path).exists():
            errors.append(f"fixture required path missing: {rel_path}")
    for rel_path in EXPECTED_ABSENT:
        if (root / rel_path).exists():
            errors.append(f"expected absent path unexpectedly present: {rel_path}")

    if survey_manifest.get("lane_key") != "P12-L13":
        errors.append("survey manifest lane_key drift")
    if survey_manifest.get("phase") != "Phase 12":
        errors.append("survey manifest phase drift")
    if survey_manifest.get("surveyed_commit") != "unresolved_on_master":
        errors.append("survey manifest surveyed_commit drift")
    if survey_manifest.get("verified_on") != "2026-05-21":
        errors.append("survey manifest verified_on drift")
    if survey_manifest.get("anchor") != "drivers/scsi/virtio_scsi.c":
        errors.append("survey manifest anchor drift")
    if survey_manifest.get("roadmap_destinations") != [
        "drivers/scsi/virtio_scsi.zig",
        "zigux/tests/",
    ]:
        errors.append("survey manifest roadmap_destinations drift")

    summary = survey_manifest.get("survey_summary", {})
    for key, expected in EXPECTED_SUMMARY_FLAGS.items():
        if summary.get(key) is not expected:
            errors.append(f"survey manifest summary drift: {key}")

    roadmap_gap_check = survey_manifest.get("roadmap_gap_check", {})
    for key, expected_status in EXPECTED_ROADMAP_GAP_STATUSES.items():
        gap_info = roadmap_gap_check.get(key, {})
        if gap_info.get("status") != expected_status:
            errors.append(f"survey manifest roadmap gap drift: {key}")

    gap_statuses = {
        gap.get("id"): gap.get("status")
        for gap in survey_manifest.get("gaps", [])
        if isinstance(gap, dict)
    }
    for gap_id, expected_status in EXPECTED_GAP_STATUSES.items():
        if gap_statuses.get(gap_id) != expected_status:
            errors.append(f"survey manifest gap drift: {gap_id}")

    build_gap = next(
        (
            gap
            for gap in survey_manifest.get("gaps", [])
            if isinstance(gap, dict) and gap.get("id") == "phase12-build-gate"
        ),
        None,
    )
    if build_gap is None:
        errors.append("survey manifest phase12-build-gate entry missing")
    elif "survey-gate tests" not in build_gap.get("why_now", ""):
        errors.append("survey manifest phase12-build-gate why_now drift")

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
