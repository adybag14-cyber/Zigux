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
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_freeze_map_manifest.json",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_readiness_gate.zig",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_docs_root_reviewability.zig",
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
    "only remaining blocked work is the deep-core status-change evidence",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
]

SCRIPTS_README_MARKERS = [
    "Phase 15 flow",
    "validate-phase15.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15",
    "zig build test --build-file zigux/tests/phase15_build.zig",
]

TESTS_README_MARKERS = [
    "Phase 15 guidance",
    "zigux/tests/phase15_build.zig",
    "scripts/zigux/validate-phase15.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15",
    "blocked deep-core status-change posture",
]

FREEZE_MAP_NOTE_MARKERS = [
    "PHASE15_LANE_KEY=arch-council",
    "## Roadmap versus repo reality",
    "## Current blocker posture",
    "phase15-deep-core-status-change-blocker",
    "make -C zigux phase15",
    "zig build test --build-file zigux/tests/phase15_build.zig",
]

REVIEW_PROCESS_MARKERS = [
    "## Trigger Conditions",
    "## Required Review Packet",
    "## Decision Buckets",
    "## Reopen Trigger Catalog",
    "## Reopen Evidence Matrix",
    "## Current Approval Posture",
    "## Roadmap Handoff Evidence",
    "## Maintenance-Mode Handoff",
    "no Architecture Council approval is currently recorded",
    "current approval evidence is explicit negative evidence rather than silence",
    "current ownership evidence is explicit in both the scorecard and the anchor templates",
    "requested decision bucket: pending_no_request",
    "decision record ID: pending_no_architecture_council_request",
    "no Architecture Council approval claim",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
]

SURVEY_MARKERS = [
    "## Current Repo Readiness",
    "## Readiness Gate",
    "make -C zigux phase15",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "docs-root Phase 15 summary now matches the dedicated readiness and handoff packet",
    "phase15-docs-root-summary-alignment",
]

HANDOFF_MARKERS = [
    "PHASE15_LANE_KEY=P15-Y08",
    "## Current Handoff Surface",
    "## Open Handoff Gaps",
    "## Pending Next Steps",
    "## Maintenance Handoff Contract",
    "docs-root release evidence now matches the dedicated maintenance packet",
    "phase15-docs-root-summary-alignment",
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
    "phase15-docs-root-reviewability-tests",
]

HANDOFF_TEST_MARKERS = [
    'try std.testing.expectEqualStrings("P15-Y08", manifest.lane_key);',
    "phase15-deep-core-status-change-blocker",
    "make -C zigux phase15",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "docs_root_phase15_summary_aligned",
]

DOCS_ROOT_REVIEWABILITY_MARKERS = [
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "only remaining blocked work is the deep-core status-change evidence",
    "docs-root Phase 15 summary now matches the dedicated readiness and handoff packet",
    "phase15-docs-root-summary-alignment",
]

REVIEW_PROCESS_APPROVAL_FIELDS = [
    "requested decision bucket",
    "decision record ID",
    "no Architecture Council approval claim",
]

REVIEW_PROCESS_APPROVAL_PATHS = [
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
    "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
    "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md",
    "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md",
]

REVIEW_PROCESS_OWNERSHIP_FIELDS = [
    "owner",
    "rollback owner",
    "validation gate summary",
    "evidence archive path",
    "latest blocker disposition",
    "benchmark notes",
    "replay command",
    "retained discussion state",
    "automatic return-to-blocked trigger",
    "rollback threshold",
    "indefinite-C policy link or applicability note",
    "reopen triggers",
    "parity scorecard link or blocker record",
]

REVIEW_PROCESS_OWNERSHIP_PATHS = [
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
    "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
    "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md",
    "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md",
]

REVIEW_PROCESS_TRIGGER_CONDITIONS = [
    "freeze-map list change",
    "freeze-map status-bucket change",
    "bounded dual-implementation request for a deep-core study target",
    "contradictory validation needing a written council decision",
]

REVIEW_PROCESS_REQUIRED_FIELDS = [
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
    "rollback threshold",
    "indefinite-C policy link or applicability note",
    "reopen triggers",
    "trigger-specific refreshed evidence by path",
    "parity scorecard link or blocker record",
    "explicit non-goals",
    "written rationale",
]

REVIEW_PROCESS_REOPEN_TRIGGER_CATALOG = [
    "narrower_followup_answers_blocker",
    "evidence_packet_stale_or_contradictory",
    "ownership_or_validation_changed",
]

REVIEW_PROCESS_DECISION_BUCKETS = [
    "keep_in_c",
    "study_only_followup",
    "bounded_dual_implementation",
    "defer_or_reject",
]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str):
    return json.loads(text(path))


missing = []


def require(condition: bool, key: str) -> None:
    if not condition:
        missing.append(key)


def require_markers(name: str, source: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")


def require_true(mapping, prefix: str, keys: list[str]) -> None:
    for key in keys:
        if mapping.get(key) is not True:
            missing.append(f"{prefix}:{key}")


def require_false(mapping, prefix: str, keys: list[str]) -> None:
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
require_markers("scripts_readme", text("scripts/zigux/README.md"), SCRIPTS_README_MARKERS)
require_markers("tests_readme", text("zigux/tests/README.md"), TESTS_README_MARKERS)
require_markers(
    "freeze_map_note",
    text("Documentation/zigux/phase15-freeze-map-governance.md"),
    FREEZE_MAP_NOTE_MARKERS,
)
require_markers(
    "review_process_note",
    text("Documentation/zigux/phase15-architecture-council-review-process.md"),
    REVIEW_PROCESS_MARKERS,
)
require_markers("survey", text("Documentation/zigux/phase15-readiness-gate-survey.md"), SURVEY_MARKERS)
require_markers("handoff", text("Documentation/zigux/phase15-handoff-next-steps-survey.md"), HANDOFF_MARKERS)
require_markers("handoff_test", text("zigux/tests/phase15_handoff_next_steps.zig"), HANDOFF_TEST_MARKERS)
require_markers("docs_root_reviewability", text("zigux/tests/phase15_docs_root_reviewability.zig"), DOCS_ROOT_REVIEWABILITY_MARKERS)
require_markers("build", text("zigux/tests/phase15_build.zig"), BUILD_MARKERS)

freeze_map_manifest = load_json("zigux/tests/phase15_freeze_map_manifest.json")
require(freeze_map_manifest.get("phase") == "Phase 15", "freeze_map_manifest:phase")
require(freeze_map_manifest.get("lane_key") == "arch-council", "freeze_map_manifest:lane_key")
require(
    isinstance(freeze_map_manifest.get("surveyed_commit"), str)
    and HEX40.fullmatch(freeze_map_manifest["surveyed_commit"]),
    "freeze_map_manifest:surveyed_commit",
)
require(
    freeze_map_manifest.get("anchor") == "Documentation/zigux/freeze-map.md",
    "freeze_map_manifest:anchor",
)
require(
    freeze_map_manifest.get("roadmap_freeze_in_c_targets")
    == freeze_map_manifest.get("freeze_in_c_targets"),
    "freeze_map_manifest:freeze_in_c_targets",
)
require(
    freeze_map_manifest.get("roadmap_study_only_targets")
    == freeze_map_manifest.get("study_only_targets"),
    "freeze_map_manifest:study_only_targets",
)
current_blockers = freeze_map_manifest.get("current_blockers")
require(isinstance(current_blockers, list) and len(current_blockers) == 4, "freeze_map_manifest:current_blockers")
governance_requirements = freeze_map_manifest.get("governance_requirements")
require(
    isinstance(governance_requirements, list)
    and {item.get("id") for item in governance_requirements} == {
        "freeze-map-council-decision",
        "freeze-map-lane-ownership",
        "freeze-map-parity-gate",
        "freeze-map-rollback-threshold",
        "freeze-map-stay-in-c-policy",
        "freeze-map-stay-in-c-closeout",
    },
    "freeze_map_manifest:governance_requirements",
)
freeze_map_gaps = freeze_map_manifest.get("gaps")
require(isinstance(freeze_map_gaps, list) and len(freeze_map_gaps) >= 1, "freeze_map_manifest:gaps")
if isinstance(freeze_map_gaps, list):
    blocked_gaps = [gap for gap in freeze_map_gaps if gap.get("id") == "phase15-deep-core-status-change-blocker"]
    require(len(blocked_gaps) == 1, "freeze_map_manifest:deep_core_gap")
    if len(blocked_gaps) == 1:
        gap = blocked_gaps[0]
        require(gap.get("status") == "blocked_on_stay_in_c_evidence", "freeze_map_manifest:deep_core_gap:status")
        require(
            gap.get("zigux_destination") == "Documentation/zigux/phase15-parity-scorecard.md",
            "freeze_map_manifest:deep_core_gap:zigux_destination",
        )

readiness_manifest = load_json("zigux/tests/phase15_readiness_gate_manifest.json")
require(readiness_manifest.get("phase") == "Phase 15", "manifest:phase")
require(readiness_manifest.get("lane_key") == "P15-L01", "manifest:lane_key")
require(readiness_manifest.get("surveyed_commit") == "b5f64cf3306b706ea93cc9d3de769d545849b2d4", "manifest:surveyed_commit")
repo_evidence = readiness_manifest.get("repo_evidence", {})
require_true(repo_evidence, "manifest:repo_evidence", [
    "freeze_map_present", "review_checklist_present", "review_process_present", "parity_scorecard_present",
    "indefinite_c_policy_present", "handoff_next_steps_present", "phase15_build_present",
    "phase15_make_target_present", "shared_ci_phase15_present", "phase15_replay_green_on_current_master",
    "docs_root_phase15_summary_aligned",
])
require_false(repo_evidence, "manifest:repo_evidence", ["deep_core_status_change_ready"])
remaining_gaps = readiness_manifest.get("remaining_gaps")
require(isinstance(remaining_gaps, list) and len(remaining_gaps) == 1, "manifest:remaining_gaps")
if isinstance(remaining_gaps, list) and len(remaining_gaps) == 1:
    gap = remaining_gaps[0]
    require(gap.get("id") == "phase15-deep-core-status-change-blocker", "manifest:remaining_gaps:id")
    require(gap.get("status") == "blocked_on_stay_in_c_evidence", "manifest:remaining_gaps:status")
    require(gap.get("zigux_destination") == "Documentation/zigux/phase15-parity-scorecard.md", "manifest:remaining_gaps:zigux_destination")

handoff_manifest = load_json("zigux/tests/phase15_handoff_next_steps_manifest.json")
require(handoff_manifest.get("phase") == "Phase 15", "handoff_manifest:phase")
require(handoff_manifest.get("lane_key") == "P15-Y08", "handoff_manifest:lane_key")
require(handoff_manifest.get("surveyed_commit") == "b5f64cf3306b706ea93cc9d3de769d545849b2d4", "handoff_manifest:surveyed_commit")
handoff_repo_evidence = handoff_manifest.get("repo_evidence", {})
require_true(handoff_repo_evidence, "handoff_manifest:repo_evidence", [
    "freeze_map_governance_present", "review_process_present", "parity_scorecard_present",
    "indefinite_c_policy_present", "readiness_gate_present", "phase15_build_present",
    "phase15_make_target_present", "shared_ci_phase15_present", "docs_index_handoff_pointer_present",
    "docs_root_reviewability_guard_present", "phase15_replay_green_on_current_master",
    "docs_root_phase15_summary_aligned",
])
require_false(handoff_repo_evidence, "handoff_manifest:repo_evidence", ["deep_core_status_change_ready"])
open_handoff_gaps = handoff_manifest.get("open_handoff_gaps")
require(isinstance(open_handoff_gaps, list) and len(open_handoff_gaps) == 1, "handoff_manifest:open_handoff_gaps")
if isinstance(open_handoff_gaps, list) and len(open_handoff_gaps) == 1:
    gap = open_handoff_gaps[0]
    require(gap.get("id") == "phase15-deep-core-status-change-blocker", "handoff_manifest:open_handoff_gaps:id")
    require(gap.get("status") == "blocked_on_stay_in_c_evidence", "handoff_manifest:open_handoff_gaps:status")

review_process_manifest = load_json("zigux/tests/phase15_architecture_council_review_process_manifest.json")
require(review_process_manifest.get("phase") == "Phase 15", "review_process_manifest:phase")
require(review_process_manifest.get("lane_key") == "P15-L07", "review_process_manifest:lane_key")
require(
    isinstance(review_process_manifest.get("surveyed_commit"), str)
    and HEX40.fullmatch(review_process_manifest["surveyed_commit"]),
    "review_process_manifest:surveyed_commit",
)
require(
    review_process_manifest.get("roadmap_requirement") == "Architecture Council review process",
    "review_process_manifest:roadmap_requirement",
)
require(
    review_process_manifest.get("anchor") == "Documentation/zigux/phase15-architecture-council-review-process.md",
    "review_process_manifest:anchor",
)
require(
    review_process_manifest.get("current_approval_state") == "no_freeze_map_status_change_approved",
    "review_process_manifest:current_approval_state",
)
require(
    review_process_manifest.get("approval_evidence_fields") == REVIEW_PROCESS_APPROVAL_FIELDS,
    "review_process_manifest:approval_evidence_fields",
)
require(
    review_process_manifest.get("approval_evidence_paths") == REVIEW_PROCESS_APPROVAL_PATHS,
    "review_process_manifest:approval_evidence_paths",
)
require(
    review_process_manifest.get("ownership_evidence_fields") == REVIEW_PROCESS_OWNERSHIP_FIELDS,
    "review_process_manifest:ownership_evidence_fields",
)
require(
    review_process_manifest.get("ownership_evidence_paths") == REVIEW_PROCESS_OWNERSHIP_PATHS,
    "review_process_manifest:ownership_evidence_paths",
)
require(
    review_process_manifest.get("trigger_conditions") == REVIEW_PROCESS_TRIGGER_CONDITIONS,
    "review_process_manifest:trigger_conditions",
)
require(
    review_process_manifest.get("required_review_packet_fields") == REVIEW_PROCESS_REQUIRED_FIELDS,
    "review_process_manifest:required_review_packet_fields",
)
require(
    review_process_manifest.get("reopen_trigger_catalog") == REVIEW_PROCESS_REOPEN_TRIGGER_CATALOG,
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
require(
    review_process_manifest.get("decision_buckets") == REVIEW_PROCESS_DECISION_BUCKETS,
    "review_process_manifest:decision_buckets",
)

review_process_handoff_evidence = review_process_manifest.get("handoff_evidence", {})
require(
    review_process_handoff_evidence.get("roadmap_source")
    == "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md#phase-15-full-parity-blockers-and-long-term-governance",
    "review_process_manifest:handoff_evidence:roadmap_source",
)
require(
    "freeze map" in review_process_handoff_evidence.get("roadmap_handoff", "")
    and "parity scorecard" in review_process_handoff_evidence.get("roadmap_handoff", "")
    and "indefinite-C policy" in review_process_handoff_evidence.get("roadmap_handoff", ""),
    "review_process_manifest:handoff_evidence:roadmap_handoff",
)
require(
    review_process_handoff_evidence.get("bootstrap_ledger_anchor")
    == "docs(zigux): add documentation root, review checklist, and freeze map",
    "review_process_manifest:handoff_evidence:bootstrap_ledger_anchor",
)
require(
    "Documentation/zigux/README.md" in review_process_handoff_evidence.get("current_repo_handoff", "")
    and "Documentation/zigux/phase15-indefinite-c-policy.md" in review_process_handoff_evidence.get("current_repo_handoff", "")
    and "Documentation/zigux/phase15-handoff-next-steps-survey.md" in review_process_handoff_evidence.get("current_repo_handoff", "")
    and "zigux/tests/phase15_build.zig" in review_process_handoff_evidence.get("current_repo_handoff", "")
    and "make -C zigux phase15" in review_process_handoff_evidence.get("current_repo_handoff", ""),
    "review_process_manifest:handoff_evidence:current_repo_handoff",
)
require(
    review_process_manifest["lane_key"] in review_process_handoff_evidence.get("current_bounded_lane", "")
    and "governance, approval, and ownership evidence verification" in review_process_handoff_evidence.get("current_bounded_lane", "")
    and "current parked maintenance-mode Phase 15 packet" in review_process_handoff_evidence.get("current_bounded_lane", "")
    and "neighboring governance slices" in review_process_handoff_evidence.get("current_bounded_lane", ""),
    "review_process_manifest:handoff_evidence:current_bounded_lane",
)
require(
    "named reopen triggers" in review_process_handoff_evidence.get("maintenance_mode_next_step", "")
    and "shared Phase 15 replay drift" in review_process_handoff_evidence.get("maintenance_mode_next_step", "")
    and "deep-core blocker posture" in review_process_handoff_evidence.get("maintenance_mode_next_step", ""),
    "review_process_manifest:handoff_evidence:maintenance_mode_next_step",
)

review_process_handoff = review_process_manifest.get("handoff", {})
require(review_process_handoff.get("current_mode") == "maintenance_mode", "review_process_manifest:handoff:current_mode")
require(
    review_process_handoff.get("replay_commands") == [
        "zig build test --build-file zigux/tests/phase15_build.zig",
        "make -C zigux phase15",
    ],
    "review_process_manifest:handoff:replay_commands",
)
require(
    review_process_handoff.get("blocker_posture_requirement") == "deep_core_blocker_posture_change",
    "review_process_manifest:handoff:blocker_posture_requirement",
)
require(
    "named reopen triggers" in review_process_handoff.get("next_step", "")
    and "shared Phase 15 replay drift" in review_process_handoff.get("next_step", "")
    and "deep-core blocker posture" in review_process_handoff.get("next_step", ""),
    "review_process_manifest:handoff:next_step",
)

review_process_gaps = review_process_manifest.get("gaps")
require(isinstance(review_process_gaps, list) and len(review_process_gaps) == 19, "review_process_manifest:gaps")
if isinstance(review_process_gaps, list):
    gap_ids = {gap.get("id") for gap in review_process_gaps}
    require(
        {
            "phase15-review-process-lane-identity-provenance-refresh",
            "phase15-review-process-indefinite-c-evidence-path-sync",
            "phase15-review-process-ownership-evidence-rollback-threshold-sync",
        }.issubset(gap_ids),
        "review_process_manifest:required_gap_ids",
    )

review_process_note = text("Documentation/zigux/phase15-architecture-council-review-process.md")
require(
    f"PHASE15_LANE_KEY={review_process_manifest.get('lane_key')}" in review_process_note,
    "review_process_note:lane_key",
)
require(
    f"survey provenance refreshed against verified `master` head `{review_process_manifest.get('surveyed_commit')}`"
    in review_process_note,
    "review_process_note:surveyed_commit",
)
require(
    f"current bounded lane: `{review_process_manifest.get('lane_key')}`" in review_process_note,
    "review_process_note:current_bounded_lane",
)

scorecard_manifest = load_json("zigux/tests/phase15_parity_scorecard.json")
require(scorecard_manifest.get("phase") == "Phase 15", "scorecard_manifest:phase")
require(scorecard_manifest.get("lane_key") == "P15-L12", "scorecard_manifest:lane_key")

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
    "PHASE15_REQUIRED_MARKER_COUNT=" + str(
        len(MAKE_MARKERS)
        + len(WORKFLOW_MARKERS)
        + len(README_MARKERS)
        + len(SCRIPTS_README_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(FREEZE_MAP_NOTE_MARKERS)
        + len(REVIEW_PROCESS_MARKERS)
        + len(SURVEY_MARKERS)
        + len(HANDOFF_MARKERS)
        + len(HANDOFF_TEST_MARKERS)
        + len(DOCS_ROOT_REVIEWABILITY_MARKERS)
        + len(BUILD_MARKERS)
    )
)
print("PHASE15_REMAINING_BLOCKERS=phase15-deep-core-status-change-blocker")