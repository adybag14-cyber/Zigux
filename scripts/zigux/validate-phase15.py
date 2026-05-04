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
    "scripts/zigux/check-phase15-review-process-handoff.py",
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
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_readiness_gate.zig",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_evidence_archive_templates.zig",
    "zigux/tests/phase15_docs_root_reviewability.zig",
]

MAKE_MARKERS = [
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "scripts/zigux/check-phase15-review-process-handoff.py --self-test",
    "scripts/zigux/check-phase15-review-process-handoff.py",
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
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-evidence-archives/",
    "python3 scripts/zigux/validate-phase15.py",
    "make -C zigux phase15-validate",
    "zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
]

SCRIPTS_README_MARKERS = [
    "Phase 15 flow",
    "check-phase15-review-process-handoff.py",
    "validate-phase15.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
]

TESTS_README_MARKERS = [
    "Phase 15 guidance",
    "zigux/tests/phase15_build.zig",
    "scripts/zigux/check-phase15-review-process-handoff.py --self-test",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/validate-phase15.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "blocked deep-core status-change posture",
]

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the freeze-map governance packet",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "automatic return-to-blocked trigger",
    "current maintenance-mode handoff aligned",
    "if the change touches the shared Phase 15 maintenance-mode handoff packet",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "zigux/tests/phase15_docs_root_reviewability.zig",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "focused handoff-checker route",
    "named reopen triggers",
    "phase15-deep-core-status-change-blocker",
    "if the change touches the shared Phase 15 Architecture Council review-process packet",
    "indefinite-C policy link or explicit non-applicability note",
]

FREEZE_MAP_NOTE_MARKERS = [
    "PHASE15_LANE_KEY=P15-L04",
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
    "phase15-review-process-freeze-map-governance-handoff-sync",
    "phase15-review-process-scripts-tests-root-handoff-sync",
    "scripts-root validator path",
    "tests-root guidance path",
]

INDEFINITE_POLICY_NOTE_MARKERS = [
    "PHASE15_LANE_KEY=P15-Y04",
    "## Current Policy Gap",
    "## Exception request checklist",
    "## Automatic Return-To-Blocked Rule",
    "## Reopen Evidence Matrix",
    "## Reopen Trigger Catalog",
    "## Maintenance-Mode Handoff",
    "The current roadmap-vs-repo policy gap inside this lane is no longer a missing local governance artifact.",
    "That closes the current policy gap for the roadmap requirement `policy for code that remains in C indefinitely`.",
    "phase15-deep-core-status-change-blocker",
    "make -C zigux phase15",
]

SURVEY_MARKERS = [
    "## Readiness at Reviewed Head",
    "## Readiness Gate",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "python3 scripts/zigux/validate-phase15.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_docs_root_reviewability.zig",
    "docs-root Phase 15 summary now matches the dedicated readiness and handoff packet",
    "Later repo movement still requires a fresh bounded provenance refresh",
    "phase15-docs-root-summary-alignment",
]

HANDOFF_MARKERS = [
    "PHASE15_LANE_KEY=P15-Y08",
    "## Current Handoff Surface",
    "## Open Handoff Gaps",
    "## Pending Next Steps",
    "## Maintenance Handoff Contract",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "python3 scripts/zigux/validate-phase15.py",
    "make -C zigux phase15-validate",
    "zigux/tests/phase15_docs_root_reviewability.zig",
    "docs-root release evidence now matches the dedicated maintenance packet",
    "phase15-docs-root-summary-alignment",
    "reviewed-provenance head for this packet needs refresh",
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
    "phase15-evidence-archive-templates-tests",
]

HANDOFF_TEST_MARKERS = [
    'try std.testing.expectEqualStrings("P15-Y08", manifest.lane_key);',
    "phase15-deep-core-status-change-blocker",
    "make -C zigux phase15",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "docs_root_phase15_summary_aligned_at_reviewed_head",
]

INDEFINITE_POLICY_TEST_MARKERS = [
    'try std.testing.expectEqualStrings("P15-Y04", manifest.lane_key);',
    'try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirement);',
    'try expectContains(policy_note, "## Current Policy Gap");',
    'try expectContains(policy_note, "## Maintenance-Mode Handoff");',
    'try expectContains(policy_note, "phase15-deep-core-status-change-blocker");',
    'try expectContains(policy_note, "That closes the current policy gap for the roadmap requirement `policy for code that remains in C indefinitely`.");',
]

EVIDENCE_ARCHIVE_TEMPLATE_TEST_MARKERS = [
    "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
    "pending_until_bounded_scheduler_seam_exists",
    "blocked_no_bounded_scheduler_seam",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "retained discussion state after closeout: `retired_from_active_discussion`",
    "no Architecture Council approval claim",
]

DOCS_ROOT_REVIEWABILITY_MARKERS = [
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "python3 scripts/zigux/validate-phase15.py",
    "make -C zigux phase15-validate",
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
    "Documentation/zigux/phase15-freeze-map-governance.md",
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
    "Documentation/zigux/phase15-freeze-map-governance.md",
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
    "explicit source-of-truth note",
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

INDEFINITE_C_REQUIREMENT_IDS = {
    "indefinite-c-source-of-truth",
    "indefinite-c-recordkeeping",
    "indefinite-c-allowed-work",
    "indefinite-c-exception-path",
    "indefinite-c-exception-request-checklist",
    "indefinite-c-automatic-return-to-blocked",
    "indefinite-c-reopen-gate",
    "indefinite-c-reopen-evidence-matrix",
    "indefinite-c-reopen-trigger-catalog",
    "indefinite-c-current-gap-survey",
}


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
require_markers("review_checklist", text("Documentation/zigux/review-checklist.md"), REVIEW_CHECKLIST_MARKERS)
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
require_markers(
    "indefinite_policy_note",
    text("Documentation/zigux/phase15-indefinite-c-policy.md"),
    INDEFINITE_POLICY_NOTE_MARKERS,
)
require_markers("survey", text("Documentation/zigux/phase15-readiness-gate-survey.md"), SURVEY_MARKERS)
require_markers("handoff", text("Documentation/zigux/phase15-handoff-next-steps-survey.md"), HANDOFF_MARKERS)
require_markers("handoff_test", text("zigux/tests/phase15_handoff_next_steps.zig"), HANDOFF_TEST_MARKERS)
require_markers(
    "indefinite_policy_test",
    text("zigux/tests/phase15_indefinite_c_policy.zig"),
    INDEFINITE_POLICY_TEST_MARKERS,
)
require_markers(
    "evidence_archive_template_test",
    text("zigux/tests/phase15_evidence_archive_templates.zig"),
    EVIDENCE_ARCHIVE_TEMPLATE_TEST_MARKERS,
)
require_markers("docs_root_reviewability", text("zigux/tests/phase15_docs_root_reviewability.zig"), DOCS_ROOT_REVIEWABILITY_MARKERS)
require_markers("build", text("zigux/tests/phase15_build.zig"), BUILD_MARKERS)

freeze_map_manifest = load_json("zigux/tests/phase15_freeze_map_manifest.json")
require(freeze_map_manifest.get("phase") == "Phase 15", "freeze_map_manifest:phase")
require(freeze_map_manifest.get("lane_key") == "P15-L04", "freeze_map_manifest:lane_key")
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
require(
    isinstance(readiness_manifest.get("surveyed_commit"), str)
    and HEX40.fullmatch(readiness_manifest["surveyed_commit"]),
    "manifest:surveyed_commit",
)
repo_evidence = readiness_manifest.get("repo_evidence", {})
require_true(repo_evidence, "manifest:repo_evidence", [
    "freeze_map_present", "review_checklist_present", "review_process_present", "parity_scorecard_present",
    "indefinite_c_policy_present", "handoff_next_steps_present", "phase15_build_present",
    "phase15_validator_script_present", "phase15_validate_target_present", "phase15_make_target_present",
    "shared_ci_phase15_present", "phase15_replay_green_at_reviewed_head",
    "docs_root_phase15_summary_aligned_at_reviewed_head", "current_master_provenance_refresh_required",
])
require_false(repo_evidence, "manifest:repo_evidence", ["deep_core_status_change_ready"])
remaining_gaps = readiness_manifest.get("remaining_gaps")
require(isinstance(remaining_gaps, list) and len(remaining_gaps) == 1, "manifest:remaining_gaps")
if isinstance(remaining_gaps, list) and len(remaining_gaps) == 1:
    gap = remaining_gaps[0]
    require(gap.get("id") == "phase15-deep-core-status-change-blocker", "manifest:remaining_gaps:id")
    require(gap.get("status") == "blocked_on_stay_in_c_evidence", "manifest:remaining_gaps:status")
    require(gap.get("zigux_destination") == "Documentation/zigux/phase15-parity-scorecard.md", "manifest:remaining_gaps:zigux_destination")
require(
    f"survey provenance last refreshed against reviewed `master` head `{readiness_manifest['surveyed_commit']}`"
    in text("Documentation/zigux/phase15-readiness-gate-survey.md"),
    "manifest:surveyed_commit:readiness_note",
)

handoff_manifest = load_json("zigux/tests/phase15_handoff_next_steps_manifest.json")
require(handoff_manifest.get("phase") == "Phase 15", "handoff_manifest:phase")
require(handoff_manifest.get("lane_key") == "P15-Y08", "handoff_manifest:lane_key")
require(
    isinstance(handoff_manifest.get("surveyed_commit"), str)
    and HEX40.fullmatch(handoff_manifest["surveyed_commit"]),
    "handoff_manifest:surveyed_commit",
)
handoff_repo_evidence = handoff_manifest.get("repo_evidence", {})
require_true(handoff_repo_evidence, "handoff_manifest:repo_evidence", [
    "freeze_map_governance_present", "review_process_present", "parity_scorecard_present",
    "indefinite_c_policy_present", "readiness_gate_present", "phase15_build_present",
    "phase15_make_target_present", "shared_ci_phase15_present", "docs_index_handoff_pointer_present",
    "docs_root_reviewability_guard_present", "phase15_replay_green_at_reviewed_head",
    "docs_root_phase15_summary_aligned_at_reviewed_head", "current_master_provenance_refresh_required",
])
require_false(handoff_repo_evidence, "handoff_manifest:repo_evidence", ["deep_core_status_change_ready"])
open_handoff_gaps = handoff_manifest.get("open_handoff_gaps")
require(isinstance(open_handoff_gaps, list) and len(open_handoff_gaps) == 1, "handoff_manifest:open_handoff_gaps")
if isinstance(open_handoff_gaps, list) and len(open_handoff_gaps) == 1:
    gap = open_handoff_gaps[0]
    require(gap.get("id") == "phase15-deep-core-status-change-blocker", "handoff_manifest:open_handoff_gaps:id")
    require(gap.get("status") == "blocked_on_stay_in_c_evidence", "handoff_manifest:open_handoff_gaps:status")
require(
    f"survey provenance refreshed against published readiness evidence verified at `master` head `{handoff_manifest['surveyed_commit']}`"
    in text("Documentation/zigux/phase15-handoff-next-steps-survey.md"),
    "handoff_manifest:surveyed_commit:handoff_note",
)

review_process_manifest = load_json("zigux/tests/phase15_architecture_council_review_process_manifest.json")
require(review_process_manifest.get("phase") == "Phase 15", "review_process_manifest:phase")
require(review_process_manifest.get("lane_key") == "P15-L08", "review_process_manifest:lane_key")
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
    and "make -C zigux phase15" in review_process_handoff_evidence.get("current_repo_handoff", "")
    and "scripts/zigux/README.md" in review_process_handoff_evidence.get("current_repo_handoff", "")
    and "scripts/zigux/validate-phase15.py" in review_process_handoff_evidence.get("current_repo_handoff", "")
    and "zigux/tests/README.md" in review_process_handoff_evidence.get("current_repo_handoff", ""),
    "review_process_manifest:handoff_evidence:current_repo_handoff",
)
require(
    review_process_manifest["lane_key"] in review_process_handoff_evidence.get("current_bounded_lane", "")
    and "governance, approval, and ownership evidence verification" in review_process_handoff_evidence.get("current_bounded_lane", "")
    and "current parked maintenance-mode Phase 15 packet" in review_process_handoff_evidence.get("current_bounded_lane", "")
    and "scripts-root validator path" in review_process_handoff_evidence.get("current_bounded_lane", "")
    and "tests-root guidance path" in review_process_handoff_evidence.get("current_bounded_lane", "")
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
require(isinstance(review_process_gaps, list) and len(review_process_gaps) == 22, "review_process_manifest:gaps")
if isinstance(review_process_gaps, list):
    gap_ids = {gap.get("id") for gap in review_process_gaps}
    require(
        {
            "phase15-review-process-lane-identity-provenance-refresh",
            "phase15-review-process-indefinite-c-evidence-path-sync",
            "phase15-review-process-ownership-evidence-rollback-threshold-sync",
            "phase15-review-process-freeze-map-governance-handoff-sync",
            "phase15-review-process-scripts-tests-root-handoff-sync",
        }.issubset(gap_ids),
        "review_process_manifest:required_gap_ids",
    )

review_process_note = text("Documentation/zigux/phase15-architecture-council-review-process.md")
require(
    f"PHASE15_LANE_KEY={review_process_manifest.get('lane_key')}" in review_process_note,
    "review_process_note:lane_key",
)
require(
    f"survey provenance last refreshed against reviewed `master` head `{review_process_manifest.get('surveyed_commit')}`"
    in review_process_note,
    "review_process_note:surveyed_commit",
)
require(
    f"current bounded lane: `{review_process_manifest.get('lane_key')}`" in review_process_note,
    "review_process_note:current_bounded_lane",
)

indefinite_c_manifest = load_json("zigux/tests/phase15_indefinite_c_policy.json")
require(indefinite_c_manifest.get("phase") == "Phase 15", "indefinite_c_manifest:phase")
require(indefinite_c_manifest.get("lane_key") == "P15-Y04", "indefinite_c_manifest:lane_key")
require(
    isinstance(indefinite_c_manifest.get("surveyed_commit"), str)
    and HEX40.fullmatch(indefinite_c_manifest["surveyed_commit"]),
    "indefinite_c_manifest:surveyed_commit",
)
require(
    indefinite_c_manifest.get("roadmap_requirement") == "policy for code that remains in C indefinitely",
    "indefinite_c_manifest:roadmap_requirement",
)
require(
    indefinite_c_manifest.get("anchors") == [
        "kernel/sched/core.c",
        "mm/page_alloc.c",
        "kernel/rcu/tree.c",
        "net/core/skbuff.c",
    ],
    "indefinite_c_manifest:anchors",
)
require(
    indefinite_c_manifest.get("supporting_artifacts") == [
        "Documentation/zigux/freeze-map.md",
        "Documentation/zigux/review-checklist.md",
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        "Documentation/zigux/phase15-parity-scorecard.md",
        "Documentation/zigux/phase15-evidence-archives/",
        "Documentation/zigux/README.md",
        "zigux/tests/phase15_build.zig",
        "zigux/Makefile",
    ],
    "indefinite_c_manifest:supporting_artifacts",
)
indefinite_c_requirements = indefinite_c_manifest.get("indefinite_c_requirements")
require(
    isinstance(indefinite_c_requirements, list) and len(indefinite_c_requirements) == 10,
    "indefinite_c_manifest:indefinite_c_requirements",
)
if isinstance(indefinite_c_requirements, list):
    require(
        {item.get("id") for item in indefinite_c_requirements} == INDEFINITE_C_REQUIREMENT_IDS,
        "indefinite_c_manifest:indefinite_c_requirement_ids",
    )
indefinite_c_handoff = indefinite_c_manifest.get("handoff", {})
require(indefinite_c_handoff.get("current_mode") == "maintenance_mode", "indefinite_c_manifest:handoff:current_mode")
require(
    indefinite_c_handoff.get("replay_commands") == [
        "zig build test --build-file zigux/tests/phase15_build.zig",
        "make -C zigux phase15",
    ],
    "indefinite_c_manifest:handoff:replay_commands",
)
require(
    indefinite_c_handoff.get("blocker_posture_requirement") == "deep_core_blocker_posture_change",
    "indefinite_c_manifest:handoff:blocker_posture_requirement",
)
require(
    indefinite_c_handoff.get("next_step")
    == "wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another Phase 15 slice",
    "indefinite_c_manifest:handoff:next_step",
)
indefinite_c_gaps = indefinite_c_manifest.get("gaps")
require(isinstance(indefinite_c_gaps, list) and len(indefinite_c_gaps) == 12, "indefinite_c_manifest:gaps")
if isinstance(indefinite_c_gaps, list):
    gap_ids = {gap.get("id") for gap in indefinite_c_gaps}
    require(
        {
            "phase15-indefinite-c-maintenance-handoff",
            "phase15-indefinite-c-current-gap-survey",
            "phase15-indefinite-c-automatic-return-to-blocked-gate",
            "phase15-indefinite-c-reopen-evidence-matrix",
            "phase15-indefinite-c-reopen-trigger-catalog",
            "phase15-deep-core-status-change-blocker",
        }.issubset(gap_ids),
        "indefinite_c_manifest:required_gap_ids",
    )
    blocked_gaps = [gap for gap in indefinite_c_gaps if gap.get("status") == "blocked_on_stay_in_c_evidence"]
    require(len(blocked_gaps) == 1, "indefinite_c_manifest:blocked_gap_count")
    if len(blocked_gaps) == 1:
        require(
            blocked_gaps[0].get("id") == "phase15-deep-core-status-change-blocker",
            "indefinite_c_manifest:blocked_gap_id",
        )
        require(
            blocked_gaps[0].get("zigux_destination") == "Documentation/zigux/phase15-parity-scorecard.md",
            "indefinite_c_manifest:blocked_gap_destination",
        )

indefinite_c_note = text("Documentation/zigux/phase15-indefinite-c-policy.md")
require(
    f"PHASE15_LANE_KEY={indefinite_c_manifest.get('lane_key')}" in indefinite_c_note,
    "indefinite_c_note:lane_key",
)
require(
    f"survey provenance refreshed against verified `master` head `{indefinite_c_manifest.get('surveyed_commit')}`"
    in indefinite_c_note,
    "indefinite_c_note:surveyed_commit",
)

scorecard_manifest = load_json("zigux/tests/phase15_parity_scorecard.json")
require(scorecard_manifest.get("phase") == "Phase 15", "scorecard_manifest:phase")
require(scorecard_manifest.get("lane_key") == "P15-Y03", "scorecard_manifest:lane_key")

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
        + len(REVIEW_CHECKLIST_MARKERS)
        + len(FREEZE_MAP_NOTE_MARKERS)
        + len(REVIEW_PROCESS_MARKERS)
        + len(INDEFINITE_POLICY_NOTE_MARKERS)
        + len(SURVEY_MARKERS)
        + len(HANDOFF_MARKERS)
        + len(BUILD_MARKERS)
        + len(HANDOFF_TEST_MARKERS)
        + len(INDEFINITE_POLICY_TEST_MARKERS)
        + len(EVIDENCE_ARCHIVE_TEMPLATE_TEST_MARKERS)
        + len(DOCS_ROOT_REVIEWABILITY_MARKERS)
    )
)
print("PHASE15_REMAINING_BLOCKERS=phase15-deep-core-status-change-blocker")
