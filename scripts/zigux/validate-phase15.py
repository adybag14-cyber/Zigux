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
    "Documentation/zigux/README.md",
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
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_readiness_gate.zig",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
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

README_MARKERS = [
    "Phase 15 notes",
    "remaining broader replay drift on current `master`",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
]

SURVEY_MARKERS = [
    "## Current Repo Readiness",
    "## Readiness Gate",
    "make -C zigux phase15",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "docs-root Phase 15 summary still says the handoff includes remaining broader replay drift",
    "phase15-docs-root-summary-drift-blocker",
]

HANDOFF_MARKERS = [
    "## Current Handoff Surface",
    "## Open Handoff Gaps",
    "## Pending Next Steps",
    "## Maintenance Handoff Contract",
    "broader shared replay is green on current `master`",
    "phase15-deep-core-status-change-blocker",
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


missing: list[str] = []


def require(condition: bool, key: str) -> None:
    if not condition:
        missing.append(key)


def require_markers(name: str, source: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")


def require_true(mapping: dict[str, object], prefix: str, keys: list[str]) -> None:
    for key in keys:
        if mapping.get(key) is not True:
            missing.append(f"{prefix}:{key}")


def require_false(mapping: dict[str, object], prefix: str, keys: list[str]) -> None:
    for key in keys:
        if mapping.get(key) is not False:
            missing.append(f"{prefix}:{key}")


missing_files = [path for path in FILES if not (ROOT / path).exists()]
if missing_files:
    print("PHASE15_VALIDATION=fail")
    print("MISSING_PHASE15_FILES_START")
    for path in missing_files:
        print(path)
    print("MISSING_PHASE15_FILES_END")
    sys.exit(1)

require_markers("make", text("zigux/Makefile"), MAKE_MARKERS)
require_markers("workflow", text(".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS)
require_markers("readme", text("Documentation/zigux/README.md"), README_MARKERS)
require_markers("survey", text("Documentation/zigux/phase15-readiness-gate-survey.md"), SURVEY_MARKERS)
require_markers("handoff", text("Documentation/zigux/phase15-handoff-next-steps-survey.md"), HANDOFF_MARKERS)
require_markers("build", text("zigux/tests/phase15_build.zig"), BUILD_MARKERS)
require_markers(
    "review_process",
    text("Documentation/zigux/phase15-architecture-council-review-process.md"),
    REVIEW_PROCESS_MARKERS,
)
require_markers("checklist", text("Documentation/zigux/review-checklist.md"), CHECKLIST_MARKERS)

readiness_manifest = load_json("zigux/tests/phase15_readiness_gate_manifest.json")
require(readiness_manifest.get("phase") == "Phase 15", "manifest:phase")
require(readiness_manifest.get("lane_key") == "P15-L01", "manifest:lane_key")
require(
    readiness_manifest.get("surveyed_commit") == "ef7b33b6922d05e5ef514fb4efa588316ce6dda8",
    "manifest:surveyed_commit",
)

repo_evidence = readiness_manifest.get("repo_evidence")
if not isinstance(repo_evidence, dict):
    missing.append("manifest:repo_evidence")
else:
    require_true(
        repo_evidence,
        "manifest:repo_evidence",
        [
            "freeze_map_present",
            "review_checklist_present",
            "review_process_present",
            "parity_scorecard_present",
            "indefinite_c_policy_present",
            "handoff_next_steps_present",
            "phase15_build_present",
            "phase15_make_target_present",
            "shared_ci_phase15_present",
            "phase15_replay_green_on_current_master",
        ],
    )
    require_false(
        repo_evidence,
        "manifest:repo_evidence",
        ["docs_root_phase15_summary_aligned", "deep_core_status_change_ready"],
    )

remaining_gaps = readiness_manifest.get("remaining_gaps")
expected_readiness_gaps = {
    "phase15-docs-root-summary-drift-blocker": (
        "blocked_on_release_evidence_alignment",
        "Documentation/zigux/README.md",
        ["docs-root Phase 15 summary", "remaining broader replay drift"],
    ),
    "phase15-deep-core-status-change-blocker": (
        "blocked_on_stay_in_c_evidence",
        "Documentation/zigux/phase15-parity-scorecard.md",
        ["freeze-in-C posture"],
    ),
}
if not isinstance(remaining_gaps, list) or len(remaining_gaps) != 2:
    missing.append("manifest:remaining_gaps")
else:
    seen_gap_ids: set[str] = set()
    for gap in remaining_gaps:
        if not isinstance(gap, dict):
            missing.append("manifest:remaining_gaps:shape")
            continue
        gap_id = gap.get("id")
        if not isinstance(gap_id, str) or gap_id not in expected_readiness_gaps:
            missing.append(f"manifest:remaining_gaps:unexpected:{gap_id}")
            continue
        seen_gap_ids.add(gap_id)
        expected_status, expected_destination, phrases = expected_readiness_gaps[gap_id]
        require(gap.get("status") == expected_status, f"manifest:remaining_gaps:status:{gap_id}")
        require(
            gap.get("zigux_destination") == expected_destination,
            f"manifest:remaining_gaps:zigux_destination:{gap_id}",
        )
        why_now = gap.get("why_now")
        if not isinstance(why_now, str):
            missing.append(f"manifest:remaining_gaps:why_now:{gap_id}")
            continue
        for phrase in phrases:
            require(phrase in why_now, f"manifest:remaining_gaps:why_now:{gap_id}:{phrase}")
    for gap_id in expected_readiness_gaps:
        require(gap_id in seen_gap_ids, f"manifest:remaining_gaps:missing:{gap_id}")

scorecard_manifest = load_json("zigux/tests/phase15_parity_scorecard.json")
require(scorecard_manifest.get("phase") == "Phase 15", "scorecard_manifest:phase")
require(scorecard_manifest.get("lane_key") == "P15-L09", "scorecard_manifest:lane_key")
require(
    scorecard_manifest.get("surveyed_commit") == "90d95d183d1072f1e8a030eec05e1e60abf443ac",
    "scorecard_manifest:surveyed_commit",
)

scorecard_handoff = scorecard_manifest.get("handoff_evidence")
if not isinstance(scorecard_handoff, dict):
    missing.append("scorecard_manifest:handoff_evidence")
else:
    require(
        scorecard_handoff.get("roadmap_source")
        == "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md#phase-15-full-parity-blockers-and-long-term-governance",
        "scorecard_manifest:handoff_evidence:roadmap_source",
    )
    require(
        scorecard_handoff.get("roadmap_requirements")
        == [
            "freeze map",
            "Architecture Council review process",
            "parity scorecard",
            "policy for code that remains in C indefinitely",
        ],
        "scorecard_manifest:handoff_evidence:roadmap_requirements",
    )
    current_repo_handoff = scorecard_handoff.get("current_repo_handoff")
    if not isinstance(current_repo_handoff, str):
        missing.append("scorecard_manifest:handoff_evidence:current_repo_handoff")
    else:
        for phrase in [
            "Documentation/zigux/README.md",
            "Documentation/zigux/phase15-handoff-next-steps-survey.md",
            "make -C zigux phase15",
            "shared bootstrap workflow replay",
        ]:
            require(
                phrase in current_repo_handoff,
                f"scorecard_manifest:handoff_evidence:current_repo_handoff:{phrase}",
            )
    maintenance_mode_next_step = scorecard_handoff.get("maintenance_mode_next_step")
    if not isinstance(maintenance_mode_next_step, str):
        missing.append("scorecard_manifest:handoff_evidence:maintenance_mode_next_step")
    else:
        for phrase in ["named reopen triggers", "deep-core blocker posture"]:
            require(
                phrase in maintenance_mode_next_step,
                f"scorecard_manifest:handoff_evidence:maintenance_mode_next_step:{phrase}",
            )

scorecard_gap = scorecard_manifest.get("current_parity_tracking_gap")
if not isinstance(scorecard_gap, dict):
    missing.append("scorecard_manifest:current_parity_tracking_gap")
else:
    require(
        scorecard_gap.get("roadmap_requirement") == "parity scorecard",
        "scorecard_manifest:current_parity_tracking_gap:roadmap_requirement",
    )
    current_gap = scorecard_gap.get("current_gap")
    if not isinstance(current_gap, str):
        missing.append("scorecard_manifest:current_parity_tracking_gap:current_gap")
    else:
        for phrase in ["lane identity", "surveyed-master provenance", "roadmap wording", "replay-backed evidence packet"]:
            require(
                phrase in current_gap,
                f"scorecard_manifest:current_parity_tracking_gap:current_gap:{phrase}",
            )
    repo_state = scorecard_gap.get("repo_state")
    if not isinstance(repo_state, str):
        missing.append("scorecard_manifest:current_parity_tracking_gap:repo_state")
    else:
        for phrase in ["Documentation/zigux/README.md", "phase15_build.zig", "make -C zigux phase15"]:
            require(
                phrase in repo_state,
                f"scorecard_manifest:current_parity_tracking_gap:repo_state:{phrase}",
            )
    closure_signal = scorecard_gap.get("closure_signal")
    require(
        isinstance(closure_signal, str) and "parity-tracking gap" in closure_signal,
        "scorecard_manifest:current_parity_tracking_gap:closure_signal",
    )
    remaining_blocker = scorecard_gap.get("remaining_blocker")
    require(
        isinstance(remaining_blocker, str) and "deep-core status-change blocker" in remaining_blocker,
        "scorecard_manifest:current_parity_tracking_gap:remaining_blocker",
    )

scorecard_repo_evidence = scorecard_manifest.get("repo_evidence")
if not isinstance(scorecard_repo_evidence, dict):
    missing.append("scorecard_manifest:repo_evidence")
else:
    require_true(
        scorecard_repo_evidence,
        "scorecard_manifest:repo_evidence",
        [
            "freeze_map_present",
            "review_checklist_present",
            "phase15_review_process_note_present",
            "phase15_indefinite_c_policy_note_present",
            "phase15_readme_reviewability_present",
            "phase15_scorecard_note_present",
            "phase15_evidence_archive_templates_present",
            "phase15_anchor_owner_tracking_present",
            "phase15_scorecard_test_present",
            "phase15_scorecard_manifest_present",
            "phase15_build_present",
            "phase15_make_target_present",
            "phase15_workflow_replay_present",
        ],
    )

scorecard_gaps = scorecard_manifest.get("gaps")
if not isinstance(scorecard_gaps, list):
    missing.append("scorecard_manifest:gaps")
else:
    scorecard_gap_ids = {
        gap.get("id")
        for gap in scorecard_gaps
        if isinstance(gap, dict) and isinstance(gap.get("id"), str)
    }
    for gap_id in [
        "phase15-roadmap-handoff-evidence-followup",
        "phase15-maintenance-mode-handoff-sync",
        "phase15-scorecard-review-packet-field-sync",
        "phase15-deep-core-status-change-blocker",
    ]:
        require(gap_id in scorecard_gap_ids, f"scorecard_manifest:gaps:{gap_id}")

scorecard_metrics = scorecard_manifest.get("scorecard_metrics")
if not isinstance(scorecard_metrics, dict):
    missing.append("scorecard_manifest:scorecard_metrics")
else:
    require(scorecard_metrics.get("landed_scorecard_gaps") == 19, "scorecard_manifest:scorecard_metrics:landed_scorecard_gaps")
    require(scorecard_metrics.get("blocked_scorecard_gaps") == 1, "scorecard_manifest:scorecard_metrics:blocked_scorecard_gaps")
    require(scorecard_metrics.get("repo_evidence_checks_green") == 15, "scorecard_manifest:scorecard_metrics:repo_evidence_checks_green")

review_process_manifest = load_json("zigux/tests/phase15_architecture_council_review_process_manifest.json")
require(review_process_manifest.get("phase") == "Phase 15", "review_process_manifest:phase")
review_process_lane_key = review_process_manifest.get("lane_key")
require(
    isinstance(review_process_lane_key, str) and review_process_lane_key.startswith("P15-L"),
    "review_process_manifest:lane_key",
)
review_process_commit = review_process_manifest.get("surveyed_commit")
require(
    isinstance(review_process_commit, str) and HEX40.fullmatch(review_process_commit),
    "review_process_manifest:surveyed_commit",
)
require(
    review_process_manifest.get("roadmap_requirement") == "Architecture Council review process",
    "review_process_manifest:roadmap_requirement",
)
require(
    review_process_manifest.get("current_approval_state") == "no_freeze_map_status_change_approved",
    "review_process_manifest:current_approval_state",
)
require(
    review_process_manifest.get("approval_evidence_fields")
    == ["requested decision bucket", "decision record ID", "no Architecture Council approval claim"],
    "review_process_manifest:approval_evidence_fields",
)
require(
    review_process_manifest.get("ownership_evidence_fields") == OWNERSHIP_EVIDENCE_FIELDS,
    "review_process_manifest:ownership_evidence_fields",
)
require(
    review_process_manifest.get("required_review_packet_fields") == REQUIRED_REVIEW_PACKET_FIELDS,
    "review_process_manifest:required_review_packet_fields",
)
require(
    review_process_manifest.get("decision_buckets") == DECISION_BUCKETS,
    "review_process_manifest:decision_buckets",
)
require(
    review_process_manifest.get("reopen_trigger_catalog") == REOPEN_TRIGGER_CATALOG,
    "review_process_manifest:reopen_trigger_catalog",
)
require(
    review_process_manifest.get("ownership_refresh_trigger") == "ownership_or_validation_changed",
    "review_process_manifest:ownership_refresh_trigger",
)
require(
    review_process_manifest.get("ownership_refresh_fields") == ["owner", "rollback owner"],
    "review_process_manifest:ownership_refresh_fields",
)

handoff = review_process_manifest.get("handoff")
if not isinstance(handoff, dict):
    missing.append("review_process_manifest:handoff")
else:
    require(handoff.get("current_mode") == "maintenance_mode", "review_process_manifest:handoff:current_mode")
    require(
        handoff.get("replay_commands")
        == ["zig build test --build-file zigux/tests/phase15_build.zig", "make -C zigux phase15"],
        "review_process_manifest:handoff:replay_commands",
    )
    require(
        handoff.get("blocker_posture_requirement") == "deep_core_blocker_posture_change",
        "review_process_manifest:handoff:blocker_posture_requirement",
    )

handoff_evidence = review_process_manifest.get("handoff_evidence")
if not isinstance(handoff_evidence, dict):
    missing.append("review_process_manifest:handoff_evidence")
else:
    require(
        handoff_evidence.get("roadmap_source")
        == "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md#phase-15-full-parity-blockers-and-long-term-governance",
        "review_process_manifest:handoff_evidence:roadmap_source",
    )
    current_repo_handoff = handoff_evidence.get("current_repo_handoff")
    require(
        isinstance(current_repo_handoff, str)
        and "Documentation/zigux/phase15-indefinite-c-policy.md" in current_repo_handoff,
        "review_process_manifest:handoff_evidence:current_repo_handoff",
    )
    current_bounded_lane = handoff_evidence.get("current_bounded_lane")
    require(
        isinstance(current_bounded_lane, str) and "current no-approval posture" in current_bounded_lane,
        "review_process_manifest:handoff_evidence:current_bounded_lane",
    )

review_process_gaps = review_process_manifest.get("gaps")
if not isinstance(review_process_gaps, list) or len(review_process_gaps) < 15:
    missing.append("review_process_manifest:gaps")
else:
    review_gap_ids = {
        gap.get("id")
        for gap in review_process_gaps
        if isinstance(gap, dict) and isinstance(gap.get("id"), str)
    }
    for gap_id in [
        "phase15-architecture-council-review-process-doc",
        "phase15-ownership-refresh-gate",
        "phase15-automatic-return-to-blocked-gate",
        "phase15-indefinite-c-policy-review-gate",
        "phase15-review-process-reopen-evidence-matrix-gate",
    ]:
        require(gap_id in review_gap_ids, f"review_process_manifest:gaps:{gap_id}")

handoff_manifest = load_json("zigux/tests/phase15_handoff_next_steps_manifest.json")
require(handoff_manifest.get("phase") == "Phase 15", "handoff_manifest:phase")
require(handoff_manifest.get("lane_key") == "P15-L12", "handoff_manifest:lane_key")
require(
    handoff_manifest.get("surveyed_commit") == "ef7b33b6922d05e5ef514fb4efa588316ce6dda8",
    "handoff_manifest:surveyed_commit",
)

handoff_repo_evidence = handoff_manifest.get("repo_evidence")
if not isinstance(handoff_repo_evidence, dict):
    missing.append("handoff_manifest:repo_evidence")
else:
    require_true(
        handoff_repo_evidence,
        "handoff_manifest:repo_evidence",
        [
            "freeze_map_governance_present",
            "review_process_present",
            "parity_scorecard_present",
            "indefinite_c_policy_present",
            "readiness_gate_present",
            "phase15_build_present",
            "phase15_make_target_present",
            "shared_ci_phase15_present",
            "docs_index_handoff_pointer_present",
            "phase15_replay_green_on_current_master",
        ],
    )
    require_false(
        handoff_repo_evidence,
        "handoff_manifest:repo_evidence",
        ["deep_core_status_change_ready"],
    )

open_handoff_gaps = handoff_manifest.get("open_handoff_gaps")
if not isinstance(open_handoff_gaps, list) or len(open_handoff_gaps) != 1:
    missing.append("handoff_manifest:open_handoff_gaps")
else:
    gap = open_handoff_gaps[0]
    if not isinstance(gap, dict):
        missing.append("handoff_manifest:open_handoff_gaps:shape")
    else:
        require(gap.get("id") == "phase15-deep-core-status-change-blocker", "handoff_manifest:open_handoff_gaps:id")
        require(
            gap.get("status") == "blocked_on_stay_in_c_evidence",
            "handoff_manifest:open_handoff_gaps:status",
        )
        require(
            gap.get("zigux_destination") == "Documentation/zigux/phase15-parity-scorecard.md",
            "handoff_manifest:open_handoff_gaps:zigux_destination",
        )
        why_now = gap.get("why_now")
        require(
            isinstance(why_now, str) and "freeze-in-C posture" in why_now,
            "handoff_manifest:open_handoff_gaps:why_now",
        )

pending_next_steps = handoff_manifest.get("pending_next_steps")
if not isinstance(pending_next_steps, list) or len(pending_next_steps) != 2:
    missing.append("handoff_manifest:pending_next_steps")
else:
    require(
        isinstance(pending_next_steps[0], str) and "shared Phase 15 replay drifts again" in pending_next_steps[0],
        "handoff_manifest:pending_next_steps:0",
    )
    require(
        isinstance(pending_next_steps[1], str) and "make -C zigux phase15" in pending_next_steps[1],
        "handoff_manifest:pending_next_steps:1",
    )

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
    f"{len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(README_MARKERS) + len(SURVEY_MARKERS) + len(HANDOFF_MARKERS) + len(BUILD_MARKERS)}"
)
print(
    "PHASE15_REMAINING_BLOCKERS="
    "phase15-docs-root-summary-drift-blocker,phase15-deep-core-status-change-blocker"
)
