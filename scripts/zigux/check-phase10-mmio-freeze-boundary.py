#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path(__file__).resolve().parent
MMIO_MANIFEST_PATH = "zigux/tests/phase10_virtio_mmio_manifest.json"
CLOSURE_MANIFEST_PATH = "zigux/tests/phase10_closure_manifest.json"
FREEZE_BOUNDARY_CHECK = "python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py"
EXPECTED_MMIO_EVIDENCE = [
    "drivers/virtio/virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    MMIO_MANIFEST_PATH,
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
]
EXPECTED_SHARED_FIELDS = [
    "freeze_map",
    "freeze_boundary_status",
    "freeze_status_change_claimed",
    "risky_transport_posture",
    "allowed_evidence_kinds",
    "forbidden_transport_claims",
    "architecture_council_reopen_required",
    "architecture_council_reopen_attached",
]
EXPECTED_ROADMAP_DESTINATIONS = [
    "drivers/virtio/*.zig",
    "zigux/kernel/",
    "zigux/helpers/",
]
EXPECTED_MMIO_BLOCKER = "phase10-mmio-lifecycle-and-irq-paths"
EXPECTED_EXACT_CHECK_TAIL = [
    FREEZE_BOUNDARY_CHECK,
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]


def read_json(root: Path, rel_path: str) -> dict:
    return json.loads((root / rel_path).read_text(encoding="utf-8"))


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files: list[str] = []
    missing_markers: list[str] = []

    for rel_path in (MMIO_MANIFEST_PATH, CLOSURE_MANIFEST_PATH):
        if not (root / rel_path).exists():
            missing_files.append(rel_path)
    if missing_files:
        return missing_files, missing_markers

    mmio_manifest = read_json(root, MMIO_MANIFEST_PATH)
    closure_manifest = read_json(root, CLOSURE_MANIFEST_PATH)

    if mmio_manifest.get("roadmap_destinations") != EXPECTED_ROADMAP_DESTINATIONS:
        missing_markers.append("mmio_manifest:roadmap_destinations")
    if closure_manifest.get("allowed_roadmap_destinations") != EXPECTED_ROADMAP_DESTINATIONS:
        missing_markers.append("closure_manifest:allowed_roadmap_destinations")

    for key in EXPECTED_SHARED_FIELDS:
        if closure_manifest.get(key) != mmio_manifest.get(key):
            missing_markers.append(f"shared_field:{key}")

    scoreboard = closure_manifest.get("roadmap_parity_scoreboard")
    if not isinstance(scoreboard, dict):
        missing_markers.append("closure_manifest:roadmap_parity_scoreboard")
    else:
        mmio_wrappers = scoreboard.get("mmio_wrappers")
        if not isinstance(mmio_wrappers, dict):
            missing_markers.append("closure_manifest:mmio_wrappers")
        else:
            if mmio_wrappers.get("status") != "starter_landed":
                missing_markers.append("closure_manifest:mmio_wrappers.status")
            if mmio_wrappers.get("evidence") != EXPECTED_MMIO_EVIDENCE:
                missing_markers.append("closure_manifest:mmio_wrappers.evidence")

        dual_impl = scoreboard.get("dual_implementations_for_risky_areas")
        if not isinstance(dual_impl, dict):
            missing_markers.append("closure_manifest:dual_implementations_for_risky_areas")
        else:
            if dual_impl.get("status") != mmio_manifest.get("risky_transport_posture"):
                missing_markers.append("closure_manifest:dual_implementations_for_risky_areas.status")
            evidence = dual_impl.get("evidence")
            if not isinstance(evidence, list) or MMIO_MANIFEST_PATH not in evidence:
                missing_markers.append("closure_manifest:dual_implementations_for_risky_areas.evidence")

        lab_validation = scoreboard.get("lab_only_driver_validation")
        if not isinstance(lab_validation, dict):
            missing_markers.append("closure_manifest:lab_only_driver_validation")
        else:
            evidence = lab_validation.get("evidence")
            if not isinstance(evidence, list) or FREEZE_BOUNDARY_CHECK not in evidence:
                missing_markers.append("closure_manifest:lab_only_driver_validation.evidence")

    survey_provenance = closure_manifest.get("survey_provenance")
    if not isinstance(survey_provenance, dict):
        missing_markers.append("closure_manifest:survey_provenance")
    else:
        lane_keys = survey_provenance.get("lane_keys")
        if not isinstance(lane_keys, dict) or lane_keys.get("mmio") != mmio_manifest.get("lane_key"):
            missing_markers.append("closure_manifest:survey_provenance.lane_keys.mmio")
        surveyed_commits = survey_provenance.get("surveyed_commits")
        if not isinstance(surveyed_commits, dict) or surveyed_commits.get("mmio") != mmio_manifest.get("surveyed_commit"):
            missing_markers.append("closure_manifest:survey_provenance.surveyed_commits.mmio")

    blocked_transport_gaps = closure_manifest.get("blocked_transport_gaps")
    if not isinstance(blocked_transport_gaps, dict) or blocked_transport_gaps.get(MMIO_MANIFEST_PATH) != EXPECTED_MMIO_BLOCKER:
        missing_markers.append("closure_manifest:blocked_transport_gaps.mmio")

    ready_transport_followups = closure_manifest.get("ready_transport_followups")
    if not isinstance(ready_transport_followups, dict) or ready_transport_followups.get(MMIO_MANIFEST_PATH) != EXPECTED_MMIO_BLOCKER:
        missing_markers.append("closure_manifest:ready_transport_followups.mmio")

    exact_checks = closure_manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        missing_markers.append("closure_manifest:exact_checks")
    else:
        for marker in EXPECTED_EXACT_CHECK_TAIL:
            if marker not in exact_checks:
                missing_markers.append(f"closure_manifest:exact_checks:{marker}")
        if exact_checks.count(FREEZE_BOUNDARY_CHECK) != 1:
            missing_markers.append("closure_manifest:exact_checks:freeze_boundary_count")

    return missing_files, missing_markers


def write_json(target: Path, payload: dict) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def baseline_manifests() -> tuple[dict, dict]:
    mmio_manifest = {
        "lane_key": "P10-L10",
        "phase": "Phase 10",
        "surveyed_commit": "84f90e23ad1c28ae345905d5293a8c5395f37d43",
        "anchor": "drivers/virtio/virtio_mmio.c",
        "roadmap_destinations": EXPECTED_ROADMAP_DESTINATIONS,
        "freeze_map": "Documentation/zigux/freeze-map.md",
        "freeze_boundary_status": "aligned",
        "freeze_status_change_claimed": False,
        "risky_transport_posture": "blocked_on_risky_transport",
        "allowed_evidence_kinds": [
            "driver_local_lab_slices",
            "survey_manifests",
            "shared_validation_gates",
        ],
        "forbidden_transport_claims": [
            "queue_setup_reset_paths",
            "irq_parity",
            "dma_paths",
            "input_registration_lifecycle",
            "probe_remove_lifecycle",
        ],
        "architecture_council_reopen_required": True,
        "architecture_council_reopen_attached": False,
    }
    closure_manifest = {
        "freeze_map": mmio_manifest["freeze_map"],
        "freeze_boundary_status": mmio_manifest["freeze_boundary_status"],
        "freeze_status_change_claimed": mmio_manifest["freeze_status_change_claimed"],
        "risky_transport_posture": mmio_manifest["risky_transport_posture"],
        "allowed_roadmap_destinations": EXPECTED_ROADMAP_DESTINATIONS,
        "allowed_evidence_kinds": mmio_manifest["allowed_evidence_kinds"],
        "architecture_council_reopen_required": mmio_manifest["architecture_council_reopen_required"],
        "architecture_council_reopen_attached": mmio_manifest["architecture_council_reopen_attached"],
        "forbidden_transport_claims": mmio_manifest["forbidden_transport_claims"],
        "roadmap_parity_scoreboard": {
            "mmio_wrappers": {
                "status": "starter_landed",
                "evidence": EXPECTED_MMIO_EVIDENCE,
            },
            "lab_only_driver_validation": {
                "status": "starter_landed",
                "evidence": [FREEZE_BOUNDARY_CHECK],
            },
            "dual_implementations_for_risky_areas": {
                "status": mmio_manifest["risky_transport_posture"],
                "evidence": [MMIO_MANIFEST_PATH],
            },
        },
        "survey_provenance": {
            "lane_keys": {"mmio": mmio_manifest["lane_key"]},
            "surveyed_commits": {"mmio": mmio_manifest["surveyed_commit"]},
        },
        "blocked_transport_gaps": {MMIO_MANIFEST_PATH: EXPECTED_MMIO_BLOCKER},
        "ready_transport_followups": {MMIO_MANIFEST_PATH: EXPECTED_MMIO_BLOCKER},
        "exact_checks": EXPECTED_EXACT_CHECK_TAIL,
    }
    return mmio_manifest, closure_manifest


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_mmio_freeze_boundary_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        mmio_manifest, closure_manifest = baseline_manifests()
        write_json(tmp_root / MMIO_MANIFEST_PATH, mmio_manifest)
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-mmio-freeze-boundary-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["freeze_boundary_status"] = "drifted"
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "shared_field:freeze_boundary_status" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_freeze_status_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["survey_provenance"]["lane_keys"]["mmio"] = "P10-L18"
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:survey_provenance.lane_keys.mmio" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_lane_key_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["exact_checks"] = ["zig build test --build-file zigux/tests/phase10_build.zig --summary all"]
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if f"closure_manifest:exact_checks:{FREEZE_BOUNDARY_CHECK}" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_exact_check_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["roadmap_parity_scoreboard"]["mmio_wrappers"]["evidence"] = ["drivers/virtio/virtio_mmio.zig"]
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:mmio_wrappers.evidence" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_mmio_evidence_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["blocked_transport_gaps"][MMIO_MANIFEST_PATH] = "phase10-mmio-queue-reset-helper"
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:blocked_transport_gaps.mmio" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_blocked_gap_marker_missing")

    print("PHASE10_MMIO_FREEZE_BOUNDARY=pass")
    print("PHASE10_MMIO_FREEZE_BOUNDARY_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 10 MMIO freeze-boundary parity inside the shared closure packet.")
    parser.add_argument("--self-test", action="store_true", help="Run synthetic drift checks against temporary manifests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_MMIO_FREEZE_BOUNDARY=fail")
        print("MISSING_PHASE10_MMIO_FREEZE_BOUNDARY_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_MMIO_FREEZE_BOUNDARY_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_MMIO_FREEZE_BOUNDARY=fail")
        print("MISSING_PHASE10_MMIO_FREEZE_BOUNDARY_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_MMIO_FREEZE_BOUNDARY_MARKERS_END")
        return 1

    print("PHASE10_MMIO_FREEZE_BOUNDARY=pass")
    print("PHASE10_MMIO_FREEZE_BOUNDARY_REQUIRED_FILE_COUNT=2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
