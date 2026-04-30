#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")

FILES = [
    "scripts/zigux/validate-phase15.py",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_readiness_gate.zig",
]

MAKE_MARKERS = [
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "scripts/zigux/validate-phase15.py",
    "phase15-test:",
    "$(ZIG) build test --build-file zigux/tests/phase15_build.zig",
    "phase15: phase15-validate phase15-test",
]

WORKFLOW_MARKERS = [
    "Run Phase 15 governance tests",
    "make -C zigux phase15",
]

SURVEY_MARKERS = [
    "## Current Repo Readiness",
    "## Readiness Gate",
    "make -C zigux phase15",
    "zig build test --build-file zigux/tests/phase15_build.zig",
]

BUILD_MARKERS = [
    "phase15-freeze-map-governance-tests",
    "phase15-parity-scorecard-tests",
    "phase15-architecture-council-review-process-tests",
    "phase15-indefinite-c-policy-tests",
    "phase15-readiness-gate-tests",
    "phase15-handoff-next-steps-tests",
]

REVIEW_PROCESS_MARKERS = [
    "## Trigger Conditions",
    "## Required Review Packet",
    "## Decision Buckets",
    "## Reopen Trigger Catalog",
    "## Reopen Evidence Matrix",
    "## Roadmap Handoff Evidence",
    "## Maintenance-Mode Handoff",
    "automatic return-to-blocked trigger",
    "indefinite-C policy link or applicability note",
    "trigger-specific refreshed evidence by path",
    "current bounded lane:",
]

CHECKLIST_MARKERS = [
    "current roadmap phase",
    "written rationale",
    "does the packet name the automatic return-to-blocked trigger",
    "trigger-specific refreshed evidence by path",
    "does the packet refresh both the current lane owner and the rollback owner before active review resumes?",
    "retained discussion state, the indefinite-C policy link or explicit non-applicability note, and the reopen triggers explicit",
]

REQUIRED_REVIEW_PACKET_FIELDS = [
    "linux anchor path",
    "phase",
    "current status bucket",
    "requested decision bucket",
    "decision record ID",
    "owner",
    "rollback owner",
    "validation gate summary",
    "evidence archive path",
    "latest blocker disposition",
    "benchmark notes",
    "replay command",
    "retained discussion state",
    "automatic return-to-blocked trigger",
    "indefinite-C policy link or applicability note",
    "reopen triggers",
    "trigger-specific refreshed evidence by path",
    "parity scorecard link or blocker record",
    "explicit non-goals",
    "written rationale",
]

OWNERSHIP_EVIDENCE_FIELDS = [
    "owner",
    "rollback owner",
    "validation gate summary",
    "evidence archive path",
    "latest blocker disposition",
    "benchmark notes",
    "replay command",
    "retained discussion state",
    "automatic return-to-blocked trigger",
    "indefinite-C policy link or applicability note",
    "reopen triggers",
    "parity scorecard link or blocker record",
]

DECISION_BUCKETS = [
    "keep_in_c",
    "study_only_followup",
    "bounded_dual_implementation",
    "defer_or_reject",
]

REOPEN_TRIGGER_CATALOG = [
    "narrower_followup_answers_blocker",
    "evidence_packet_stale_or_contradictory",
    "ownership_or_validation_changed",
]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str) -> dict[str, object]:
    return json.loads(text(path))


missing_files = [path for path in FILES if not (ROOT / path).exists()]
if missing_files:
    print("PHASE15_VALIDATION=fail")
    print("MISSING_PHASE15_FILES_START")
    for path in missing_files:
        print(path)
    print("MISSING_PHASE15_FILES_END")
    sys.exit(1)

missing: list[str] = []
for name, source, markers in [
    ("make", text("zigux/Makefile"), MAKE_MARKERS),
    ("workflow", text(".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS),
    ("survey", text("Documentation/zigux/phase15-readiness-gate-survey.md"), SURVEY_MARKERS),
    ("build", text("zigux/tests/phase15_build.zig"), BUILD_MARKERS),
    ("review_process", text("Documentation/zigux/phase15-architecture-council-review-process.md"), REVIEW_PROCESS_MARKERS),
    ("checklist", text("Documentation/zigux/review-checklist.md"), CHECKLIST_MARKERS),
]:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")

manifest = load_json("zigux/tests/phase15_readiness_gate_manifest.json")
if manifest.get("phase") != "Phase 15":
    missing.append("manifest:phase")
lane_key = manifest.get("lane_key")
if lane_key != "P15-L06":
    missing.append("manifest:lane_key")
surveyed_commit = manifest.get("surveyed_commit")
if surveyed_commit != "ef7b33b6922d05e5ef514fb4efa588316ce6dda8":
    missing.append("manifest:surveyed_commit")

repo_evidence = manifest.get("repo_evidence")
if not isinstance(repo_evidence, dict):
    missing.append("manifest:repo_evidence")
else:
    for key in [
        "freeze_map_present",
        "review_checklist_present",
        "review_process_present",
        "parity_scorecard_present",
        "indefinite_c_policy_present",
        "handoff_next_steps_present",
        "phase15_build_present",
        "phase15_make_target_present",
        "shared_ci_phase15_present",
    ]:
        if repo_evidence.get(key) is not True:
            missing.append(f"manifest:repo_evidence:{key}")
    if repo_evidence.get("phase15_replay_green_on_current_master") is not True:
        missing.append("manifest:repo_evidence:phase15_replay_green_on_current_master")
    if repo_evidence.get("deep_core_status_change_ready") is not False:
        missing.append("manifest:repo_evidence:deep_core_status_change_ready")

remaining_gaps = manifest.get("remaining_gaps")
expected_gaps = {
    "phase15-deep-core-status-change-blocker": {
        "status": "blocked_on_stay_in_c_evidence",
        "zigux_destination": "Documentation/zigux/phase15-parity-scorecard.md",
        "phrases": [
            "freeze-in-C posture",
        ],
    },
}
if not isinstance(remaining_gaps, list) or len(remaining_gaps) != len(expected_gaps):
    missing.append("manifest:remaining_gaps")
else:
    seen_gap_ids: set[str] = set()
    for gap in remaining_gaps:
        if not isinstance(gap, dict):
            missing.append("manifest:remaining_gaps:shape")
            continue
        gap_id = gap.get("id")
        if not isinstance(gap_id, str):
            missing.append("manifest:remaining_gaps:id")
            continue
        expected = expected_gaps.get(gap_id)
        if expected is None:
            missing.append(f"manifest:remaining_gaps:unexpected:{gap_id}")
            continue
        seen_gap_ids.add(gap_id)
        if gap.get("status") != expected["status"]:
            missing.append(f"manifest:remaining_gaps:status:{gap_id}")
        if gap.get("zigux_destination") != expected["zigux_destination"]:
            missing.append(f"manifest:remaining_gaps:zigux_destination:{gap_id}")
        why_now = gap.get("why_now")
        if not isinstance(why_now, str):
            missing.append(f"manifest:remaining_gaps:why_now:{gap_id}")
            continue
        for phrase in expected["phrases"]:
            if phrase not in why_now:
                missing.append(f"manifest:remaining_gaps:why_now:{gap_id}:{phrase}")
    for gap_id in expected_gaps:
        if gap_id not in seen_gap_ids:
            missing.append(f"manifest:remaining_gaps:missing:{gap_id}")

review_process_manifest = load_json("zigux/tests/phase15_architecture_council_review_process_manifest.json")
if review_process_manifest.get("phase") != "Phase 15":
    missing.append("review_process_manifest:phase")
review_process_lane_key = review_process_manifest.get("lane_key")
if not isinstance(review_process_lane_key, str) or not review_process_lane_key.startswith("P15-L"):
    missing.append("review_process_manifest:lane_key")
review_process_commit = review_process_manifest.get("surveyed_commit")
if not isinstance(review_process_commit, str) or not HEX40.fullmatch(review_process_commit):
    missing.append("review_process_manifest:surveyed_commit")
if review_process_manifest.get("roadmap_requirement") != "Architecture Council review process":
    missing.append("review_process_manifest:roadmap_requirement")
if review_process_manifest.get("current_approval_state") != "no_freeze_map_status_change_approved":
    missing.append("review_process_manifest:current_approval_state")

approval_evidence_fields = review_process_manifest.get("approval_evidence_fields")
if approval_evidence_fields != [
    "requested decision bucket",
    "decision record ID",
    "no Architecture Council approval claim",
]:
    missing.append("review_process_manifest:approval_evidence_fields")

ownership_evidence_fields = review_process_manifest.get("ownership_evidence_fields")
if ownership_evidence_fields != OWNERSHIP_EVIDENCE_FIELDS:
    missing.append("review_process_manifest:ownership_evidence_fields")

required_review_packet_fields = review_process_manifest.get("required_review_packet_fields")
if required_review_packet_fields != REQUIRED_REVIEW_PACKET_FIELDS:
    missing.append("review_process_manifest:required_review_packet_fields")

decision_buckets = review_process_manifest.get("decision_buckets")
if decision_buckets != DECISION_BUCKETS:
    missing.append("review_process_manifest:decision_buckets")

reopen_trigger_catalog = review_process_manifest.get("reopen_trigger_catalog")
if reopen_trigger_catalog != REOPEN_TRIGGER_CATALOG:
    missing.append("review_process_manifest:reopen_trigger_catalog")

if review_process_manifest.get("ownership_refresh_trigger") != "ownership_or_validation_changed":
    missing.append("review_process_manifest:ownership_refresh_trigger")
if review_process_manifest.get("ownership_refresh_fields") != ["owner", "rollback owner"]:
    missing.append("review_process_manifest:ownership_refresh_fields")

handoff = review_process_manifest.get("handoff")
if not isinstance(handoff, dict):
    missing.append("review_process_manifest:handoff")
else:
    if handoff.get("current_mode") != "maintenance_mode":
        missing.append("review_process_manifest:handoff:current_mode")
    if handoff.get("replay_commands") != [
        "zig build test --build-file zigux/tests/phase15_build.zig",
        "make -C zigux phase15",
    ]:
        missing.append("review_process_manifest:handoff:replay_commands")
    if handoff.get("blocker_posture_requirement") != "deep_core_blocker_posture_change":
        missing.append("review_process_manifest:handoff:blocker_posture_requirement")

handoff_evidence = review_process_manifest.get("handoff_evidence")
if not isinstance(handoff_evidence, dict):
    missing.append("review_process_manifest:handoff_evidence")
else:
    if handoff_evidence.get("roadmap_source") != "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md#phase-15-full-parity-blockers-and-long-term-governance":
        missing.append("review_process_manifest:handoff_evidence:roadmap_source")
    current_repo_handoff = handoff_evidence.get("current_repo_handoff")
    if not isinstance(current_repo_handoff, str) or "Documentation/zigux/phase15-indefinite-c-policy.md" not in current_repo_handoff:
        missing.append("review_process_manifest:handoff_evidence:current_repo_handoff")
    current_bounded_lane = handoff_evidence.get("current_bounded_lane")
    if not isinstance(current_bounded_lane, str) or "current no-approval posture" not in current_bounded_lane:
        missing.append("review_process_manifest:handoff_evidence:current_bounded_lane")

review_process_gaps = review_process_manifest.get("gaps")
if not isinstance(review_process_gaps, list) or len(review_process_gaps) < 15:
    missing.append("review_process_manifest:gaps")
else:
    gap_ids = {
        gap.get("id")
        for gap in review_process_gaps
        if isinstance(gap, dict) and isinstance(gap.get("id"), str)
    }
    for required_gap in [
        "phase15-architecture-council-review-process-doc",
        "phase15-ownership-refresh-gate",
        "phase15-automatic-return-to-blocked-gate",
        "phase15-indefinite-c-policy-review-gate",
        "phase15-review-process-reopen-evidence-matrix-gate",
    ]:
        if required_gap not in gap_ids:
            missing.append(f"review_process_manifest:gaps:{required_gap}")

if missing:
    print("PHASE15_VALIDATION=fail")
    print("PHASE15_VALIDATION_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE15_VALIDATION_MISSING_END")
    sys.exit(1)

print("PHASE15_VALIDATION=pass")
print(f"PHASE15_REQUIRED_FILE_COUNT={len(FILES)}")
print(
    "PHASE15_REQUIRED_MARKER_COUNT="
    f"{len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(SURVEY_MARKERS) + len(BUILD_MARKERS)}"
)
print("PHASE15_REMAINING_BLOCKERS=phase15-deep-core-status-change-blocker")
