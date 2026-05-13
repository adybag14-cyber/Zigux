#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

NOTE_PATH = "Documentation/zigux/phase15-architecture-council-review-process.md"
POLICY_PATH = "Documentation/zigux/phase15-indefinite-c-policy.md"
MANIFEST_PATH = "zigux/tests/phase15_architecture_council_review_process_manifest.json"
LANE_NOTE_PATH = "Documentation/zigux/phase15-governance-lane-sequencing.md"
VALIDATOR_PATH = "scripts/zigux/validate-phase15.py"
DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
FREEZE_MAP_MANIFEST_PATH = "zigux/tests/phase15_freeze_map_manifest.json"
PARITY_SCORECARD_PATH = "zigux/tests/phase15_parity_scorecard.json"
READINESS_MANIFEST_PATH = "zigux/tests/phase15_readiness_gate_manifest.json"
PARITY_SCORECARD_SURVEY_PATH = "Documentation/zigux/phase15-parity-scorecard-survey.md"
SHARED_SUMMARY_GAP_CHECKER = "scripts/zigux/check-phase15-shared-summary-gap.py"
EXPECTED_MANIFEST_LANE_KEY = "P15-L08"
EXPECTED_MANIFEST_PHASE = "Phase 15"
EXPECTED_ROADMAP_REQUIREMENT = "Architecture Council review process"
EXPECTED_MANIFEST_ANCHOR = NOTE_PATH
HISTORICAL_CONTINUITY_MARKER = (
    "historical continuity for this parked maintenance surface still points back to `P15-L06`"
)
START_WITH_SCRIPTS_README_MARKER = (
    "starting with scripts/zigux/README.md as the smallest remaining "
    "parity-scorecard-survey reminder before widening into zigux/tests/README.md"
)
NOTE_START_WITH_SCRIPTS_README_MARKER = (
    "Start that shared-summary follow-through with `scripts/zigux/README.md` as the "
    "smallest remaining parity-scorecard-survey reminder before widening into "
    "`zigux/tests/README.md`."
)
RUN_SHARED_SUMMARY_GAP_CHECKER_FIRST_MARKER = (
    "run python3 scripts/zigux/check-phase15-shared-summary-gap.py first"
)

NOTE_MARKERS = (
    "## Trigger Conditions",
    "## Required Review Packet",
    "## Decision Buckets",
    "## Reopen Trigger Catalog",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "Keep the Phase 15 governance lane in maintenance mode.",
    PARITY_SCORECARD_SURVEY_PATH,
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "## Next bounded step",
    "shared-summaries",
    "broader scripts-root or tests-root reminder drift routed through the shared-summary companion lane",
    NOTE_START_WITH_SCRIPTS_README_MARKER,
)

NOTE_MAINTENANCE_CLOSURE_MARKERS = (
    "shared docs-root maintenance undercount is",
    "broader scripts-root and tests-root parity-scorecard-survey undercount",
    "that remaining drift stays owned by the shared-summary companion lane rather than this packet-local review-process note",
)

POLICY_MARKERS = (
    "required approver set",
    "retained discussion state",
    "named reopen-trigger catalog item",
    "trigger-specific evidence refresh",
    "There is no silent exception path around the indefinite-C policy.",
    "The only allowed exception is an Architecture Council reopen request",
    "the existing blocker remains recorded",
    "narrower_followup_answers_blocker",
    "evidence_packet_stale_or_contradictory",
    "ownership_or_validation_changed",
)

LANE_NOTE_MARKERS = (
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    HISTORICAL_CONTINUITY_MARKER,
    "scripts/zigux/validate-phase15.py",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)

VALIDATOR_MARKERS = ("scripts/zigux/check-phase15-review-process-handoff.py",)

DOCS_README_MARKERS = (
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "no Architecture Council approval is recorded yet",
    "named reopen trigger",
    "deep-core blocker-posture change",
)

REVIEW_CHECKLIST_MARKERS = (
    "Architecture Council decision",
    "parity scorecard evidence or blocker state explicit",
    "Architecture Council review record linked",
    "current status bucket plus requested decision bucket explicit",
    "decision record ID, lane owner, required approver set, rollback owner, validation gate summary, evidence archive path, latest blocker disposition, benchmark notes, replay command, rollback threshold, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, explicit non-goals, and written rationale explicit",
    "retained discussion state, the current blocker, and reopen triggers explicit",
)

SCRIPTS_README_MARKERS = ("check-phase15-review-process-handoff.py",)

TESTS_README_PACKET_MARKERS = (
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "without implying any Architecture Council approval for a freeze-map status change",
)

REQUIRED_REVIEW_PACKET_FIELDS = (
    "linux anchor path",
    "phase",
    "current status bucket",
    "requested decision bucket",
    "decision record ID",
    "owner",
    "required approver set",
    "rollback owner",
    "validation gate summary",
    "evidence archive path",
    "latest blocker disposition",
    "benchmark notes",
    "replay command",
    "rollback threshold",
    "retained discussion state",
    "reopen triggers",
    "parity scorecard link or blocker record",
    "indefinite-C policy link or non-applicability note",
    "explicit non-goals",
    "written rationale",
)

OWNERSHIP_EVIDENCE_FIELDS = (
    "owner",
    "required approver set",
    "rollback owner",
    "validation gate summary",
    "evidence archive path",
    "latest blocker disposition",
    "benchmark notes",
    "replay command",
    "rollback threshold",
    "retained discussion state",
    "reopen triggers",
    "parity scorecard link or blocker record",
    "indefinite-C policy link or non-applicability note",
)

TRIGGER_CONDITIONS = (
    "freeze-map list change",
    "freeze-map status-bucket change",
    "bounded dual-implementation request for a deep-core study target",
    "contradictory validation needing a written council decision",
)

REOPEN_TRIGGER_CATALOG = (
    "narrower_followup_answers_blocker",
    "evidence_packet_stale_or_contradictory",
    "ownership_or_validation_changed",
)

DECISION_BUCKETS = (
    "keep_in_c",
    "study_only_followup",
    "bounded_dual_implementation",
    "defer_or_reject",
)

HANDOFF_REPLAY_COMMANDS = (
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
)

HANDOFF_NEXT_STEP_MARKERS = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    PARITY_SCORECARD_SURVEY_PATH,
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    RUN_SHARED_SUMMARY_GAP_CHECKER_FIRST_MARKER,
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "shared-summaries",
    START_WITH_SCRIPTS_README_MARKER,
    "broader scripts-root or tests-root reminder drift routed through the shared-summary companion lane",
)

EXPECTED_FREEZE_IN_C_TARGETS = (
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_text_markers(text: str, markers: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            issues.append(f"{prefix}:missing:{marker}")


def _require_items(items: list[str], markers: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for marker in markers:
        if marker not in items:
            issues.append(f"{prefix}:missing:{marker}")


def _require_json_object(value: object, prefix: str, issues: list[str]) -> dict:
    if not isinstance(value, dict):
        issues.append(f"{prefix}:missing:object")
        return {}
    return value


def _validate_governance_alignment(
    review_manifest: dict,
    freeze_manifest: dict,
    parity_scorecard: dict,
    readiness_manifest: dict,
    issues: list[str],
) -> None:
    if review_manifest.get("current_approval_state") != "no_freeze_map_status_change_approved":
        issues.append("manifest:approval_state_mismatch")
    if review_manifest.get("lane_key") != EXPECTED_MANIFEST_LANE_KEY:
        issues.append("manifest:lane_key")
    if review_manifest.get("phase") != EXPECTED_MANIFEST_PHASE:
        issues.append("manifest:phase")
    if review_manifest.get("roadmap_requirement") != EXPECTED_ROADMAP_REQUIREMENT:
        issues.append("manifest:roadmap_requirement")
    if review_manifest.get("anchor") != EXPECTED_MANIFEST_ANCHOR:
        issues.append("manifest:anchor")

    readiness = _require_json_object(readiness_manifest, "readiness_manifest", issues)
    if readiness.get("surveyed_commit_mode") != "dated_master_readback":
        issues.append("readiness_manifest:surveyed_commit_mode")

    posture = _require_json_object(parity_scorecard.get("posture"), "parity_scorecard:posture", issues)
    if posture.get("architecture_council_status_change_approval_recorded") is not False:
        issues.append("parity_scorecard:approval_posture_mismatch")

    metrics = _require_json_object(parity_scorecard.get("metrics"), "parity_scorecard:metrics", issues)
    if metrics.get("architecture_council_status_change_approval_count") != 0:
        issues.append("parity_scorecard:approval_count_mismatch")

    freeze_targets = freeze_manifest.get("freeze_in_c_targets")
    if freeze_targets != list(EXPECTED_FREEZE_IN_C_TARGETS):
        issues.append("freeze_map_manifest:freeze_in_c_targets")

    freeze_blockers = freeze_manifest.get("blocker_ownership")
    anchors = parity_scorecard.get("anchors")
    if not isinstance(freeze_blockers, list):
        issues.append("freeze_map_manifest:blocker_ownership")
        freeze_blockers = []
    if not isinstance(anchors, list):
        issues.append("parity_scorecard:anchors")
        anchors = []

    freeze_map = {item.get("anchor"): item for item in freeze_blockers if isinstance(item, dict)}
    parity_map = {item.get("path"): item for item in anchors if isinstance(item, dict)}
    freeze_paths = [item.get("anchor") for item in freeze_blockers if isinstance(item, dict)]
    parity_paths = [item.get("path") for item in anchors if isinstance(item, dict)]
    if freeze_paths != list(EXPECTED_FREEZE_IN_C_TARGETS):
        issues.append("freeze_map_manifest:blocker_ownership")
    if parity_paths != list(EXPECTED_FREEZE_IN_C_TARGETS):
        issues.append("parity_scorecard:anchors")

    for anchor in EXPECTED_FREEZE_IN_C_TARGETS:
        freeze_entry = freeze_map.get(anchor)
        parity_entry = parity_map.get(anchor)
        if not isinstance(freeze_entry, dict) or not isinstance(parity_entry, dict):
            continue
        parity_archive = _require_json_object(
            parity_entry.get("evidence_archive"),
            f"parity_scorecard:evidence_archive:{anchor}",
            issues,
        )
        if parity_entry.get("lane_owner") != freeze_entry.get("owner"):
            issues.append(f"governance_alignment:owner:{anchor}")
        if parity_entry.get("required_approver_set") != freeze_entry.get("required_approver_set"):
            issues.append(f"governance_alignment:required_approver_set:{anchor}")
        if parity_entry.get("rollback_owner") != freeze_entry.get("rollback_owner"):
            issues.append(f"governance_alignment:rollback_owner:{anchor}")
        if parity_entry.get("current_blocker") != freeze_entry.get("latest_blocker_disposition"):
            issues.append(f"governance_alignment:current_blocker:{anchor}")
        if parity_archive.get("latest_blocker_disposition") != freeze_entry.get("latest_blocker_disposition"):
            issues.append(f"governance_alignment:evidence_archive.latest_blocker_disposition:{anchor}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    required_files = (
        NOTE_PATH,
        POLICY_PATH,
        MANIFEST_PATH,
        LANE_NOTE_PATH,
        VALIDATOR_PATH,
        DOCS_README_PATH,
        REVIEW_CHECKLIST_PATH,
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
        FREEZE_MAP_MANIFEST_PATH,
        PARITY_SCORECARD_PATH,
        READINESS_MANIFEST_PATH,
        PARITY_SCORECARD_SURVEY_PATH,
    )
    for rel in required_files:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    note_text = _read(root / NOTE_PATH)
    _require_text_markers(note_text, NOTE_MARKERS, "note", issues)
    _require_text_markers(note_text, NOTE_MAINTENANCE_CLOSURE_MARKERS, "note", issues)
    _require_text_markers(_read(root / POLICY_PATH), POLICY_MARKERS, "policy", issues)
    _require_text_markers(_read(root / LANE_NOTE_PATH), LANE_NOTE_MARKERS, "lane_note", issues)
    _require_text_markers(_read(root / VALIDATOR_PATH), VALIDATOR_MARKERS, "validator", issues)
    _require_text_markers(_read(root / DOCS_README_PATH), DOCS_README_MARKERS, "docs_readme", issues)
    _require_text_markers(_read(root / REVIEW_CHECKLIST_PATH), REVIEW_CHECKLIST_MARKERS, "review_checklist", issues)
    _require_text_markers(_read(root / SCRIPTS_README_PATH), SCRIPTS_README_MARKERS, "scripts_readme", issues)
    _require_text_markers(_read(root / TESTS_README_PATH), TESTS_README_PACKET_MARKERS, "tests_readme", issues)

    review_manifest = json.loads(_read(root / MANIFEST_PATH))
    freeze_manifest = json.loads(_read(root / FREEZE_MAP_MANIFEST_PATH))
    parity_scorecard = json.loads(_read(root / PARITY_SCORECARD_PATH))
    readiness_manifest = json.loads(_read(root / READINESS_MANIFEST_PATH))

    _require_items(
        review_manifest.get("ownership_evidence_fields", []),
        OWNERSHIP_EVIDENCE_FIELDS,
        "manifest_ownership_evidence_fields",
        issues,
    )
    _require_items(
        review_manifest.get("required_review_packet_fields", []),
        REQUIRED_REVIEW_PACKET_FIELDS,
        "manifest_required_review_packet_fields",
        issues,
    )
    _require_items(
        review_manifest.get("trigger_conditions", []),
        TRIGGER_CONDITIONS,
        "manifest_trigger_conditions",
        issues,
    )
    _require_items(
        review_manifest.get("reopen_trigger_catalog", []),
        REOPEN_TRIGGER_CATALOG,
        "manifest_reopen_trigger_catalog",
        issues,
    )
    _require_items(
        review_manifest.get("decision_buckets", []),
        DECISION_BUCKETS,
        "manifest_decision_buckets",
        issues,
    )

    handoff = review_manifest.get("handoff")
    if not isinstance(handoff, dict):
        issues.append("manifest:missing:handoff")
        return issues
    if handoff.get("current_mode") != "maintenance_mode":
        issues.append("manifest:handoff_current_mode_mismatch")
    _require_items(
        handoff.get("replay_commands", []),
        HANDOFF_REPLAY_COMMANDS,
        "manifest_handoff_replay_commands",
        issues,
    )
    next_step = handoff.get("next_step")
    if not isinstance(next_step, str):
        issues.append("manifest:missing:handoff.next_step")
    else:
        _require_text_markers(next_step, HANDOFF_NEXT_STEP_MARKERS, "manifest_handoff_next_step", issues)

    _validate_governance_alignment(
        review_manifest,
        freeze_manifest,
        parity_scorecard,
        readiness_manifest,
        issues,
    )

    return issues


def _seed_fixture_tree(root: Path) -> None:
    _write(root / NOTE_PATH, "\n".join(NOTE_MARKERS + NOTE_MAINTENANCE_CLOSURE_MARKERS) + "\n")
    _write(root / POLICY_PATH, "\n".join(POLICY_MARKERS) + "\n")
    _write(root / LANE_NOTE_PATH, "\n".join(LANE_NOTE_MARKERS) + "\n")
    _write(root / VALIDATOR_PATH, "\n".join(VALIDATOR_MARKERS) + "\n")
    _write(root / DOCS_README_PATH, "\n".join(DOCS_README_MARKERS) + "\n")
    _write(root / REVIEW_CHECKLIST_PATH, "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    _write(root / SCRIPTS_README_PATH, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    _write(root / TESTS_README_PATH, "\n".join(TESTS_README_PACKET_MARKERS) + "\n")
    _write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": EXPECTED_MANIFEST_LANE_KEY,
                "phase": EXPECTED_MANIFEST_PHASE,
                "surveyed_commit": "current-master-readback-2026-05-12",
                "roadmap_requirement": EXPECTED_ROADMAP_REQUIREMENT,
                "anchor": EXPECTED_MANIFEST_ANCHOR,
                "current_approval_state": "no_freeze_map_status_change_approved",
                "ownership_evidence_fields": list(OWNERSHIP_EVIDENCE_FIELDS),
                "required_review_packet_fields": list(REQUIRED_REVIEW_PACKET_FIELDS),
                "trigger_conditions": list(TRIGGER_CONDITIONS),
                "reopen_trigger_catalog": list(REOPEN_TRIGGER_CATALOG),
                "decision_buckets": list(DECISION_BUCKETS),
                "handoff": {
                    "current_mode": "maintenance_mode",
                    "replay_commands": list(HANDOFF_REPLAY_COMMANDS),
                    "next_step": " ".join(HANDOFF_NEXT_STEP_MARKERS),
                },
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        root / FREEZE_MAP_MANIFEST_PATH,
        json.dumps(
            {
                "surveyed_commit": "current-master-readback-2026-05-12",
                "freeze_in_c_targets": list(EXPECTED_FREEZE_IN_C_TARGETS),
                "blocker_ownership": [
                    {
                        "anchor": "kernel/sched/core.c",
                        "owner": "Architecture Council",
                        "required_approver_set": "Architecture Council + PMO / Release Management",
                        "rollback_owner": "Architecture Council + PMO / Release Management",
                        "latest_blocker_disposition": "blocked_no_bounded_scheduler_seam",
                    },
                    {
                        "anchor": "mm/page_alloc.c",
                        "owner": "Architecture Council",
                        "required_approver_set": "Architecture Council + Validation and Perf Team",
                        "rollback_owner": "Architecture Council + Validation and Perf Team",
                        "latest_blocker_disposition": "blocked_no_bounded_allocator_seam",
                    },
                    {
                        "anchor": "kernel/rcu/tree.c",
                        "owner": "ABI and Runtime Team",
                        "required_approver_set": "Architecture Council + ABI and Runtime Team",
                        "rollback_owner": "Architecture Council + ABI and Runtime Team",
                        "latest_blocker_disposition": "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
                    },
                    {
                        "anchor": "net/core/skbuff.c",
                        "owner": "Shared Subsystems Pod",
                        "required_approver_set": "Architecture Council + Shared Subsystems Pod",
                        "rollback_owner": "Architecture Council + Shared Subsystems Pod",
                        "latest_blocker_disposition": "blocked_packet_lifetime_boundary_still_too_wide",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        root / PARITY_SCORECARD_PATH,
        json.dumps(
            {
                "surveyed_commit": "current-master-readback-2026-05-12",
                "posture": {
                    "architecture_council_status_change_approval_recorded": False,
                },
                "metrics": {
                    "architecture_council_status_change_approval_count": 0,
                },
                "anchors": [
                    {
                        "path": "kernel/sched/core.c",
                        "lane_owner": "Architecture Council",
                        "required_approver_set": "Architecture Council + PMO / Release Management",
                        "rollback_owner": "Architecture Council + PMO / Release Management",
                        "current_blocker": "blocked_no_bounded_scheduler_seam",
                        "evidence_archive": {
                            "latest_blocker_disposition": "blocked_no_bounded_scheduler_seam",
                        },
                    },
                    {
                        "path": "mm/page_alloc.c",
                        "lane_owner": "Architecture Council",
                        "required_approver_set": "Architecture Council + Validation and Perf Team",
                        "rollback_owner": "Architecture Council + Validation and Perf Team",
                        "current_blocker": "blocked_no_bounded_allocator_seam",
                        "evidence_archive": {
                            "latest_blocker_disposition": "blocked_no_bounded_allocator_seam",
                        },
                    },
                    {
                        "path": "kernel/rcu/tree.c",
                        "lane_owner": "ABI and Runtime Team",
                        "required_approver_set": "Architecture Council + ABI and Runtime Team",
                        "rollback_owner": "Architecture Council + ABI and Runtime Team",
                        "current_blocker": "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
                        "evidence_archive": {
                            "latest_blocker_disposition": "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
                        },
                    },
                    {
                        "path": "net/core/skbuff.c",
                        "lane_owner": "Shared Subsystems Pod",
                        "required_approver_set": "Architecture Council + Shared Subsystems Pod",
                        "rollback_owner": "Architecture Council + Shared Subsystems Pod",
                        "current_blocker": "blocked_packet_lifetime_boundary_still_too_wide",
                        "evidence_archive": {
                            "latest_blocker_disposition": "blocked_packet_lifetime_boundary_still_too_wide",
                        },
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        root / READINESS_MANIFEST_PATH,
        json.dumps(
            {
                "surveyed_commit_mode": "dated_master_readback",
                "surveyed_commit": "current-master-readback-2026-05-12",
            },
            indent=2,
        )
        + "\n",
    )
    _write(root / PARITY_SCORECARD_SURVEY_PATH, "# parity scorecard survey\n")


def _assert_only(issues: list[str], expected: list[str], label: str) -> None:
    if issues != expected:
        got = ",".join(issues) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase15-review-process-handoff-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_review_process_handoff_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_fixture_tree(root)
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        note_path = root / NOTE_PATH
        _write(note_path, _read(note_path).replace("## Decision Buckets\n", "", 1))
        _assert_only(validate(root), ["note:missing:## Decision Buckets"], "missing_note_marker")
        _seed_fixture_tree(root)
        case_count += 1

        note_path = root / NOTE_PATH
        _write(note_path, _read(note_path).replace(PARITY_SCORECARD_SURVEY_PATH + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"note:missing:{PARITY_SCORECARD_SURVEY_PATH}"],
            "missing_note_parity_scorecard_survey_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        note_path = root / NOTE_PATH
        _write(
            note_path,
            _read(note_path).replace(
                "shared docs-root maintenance undercount is\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            ["note:missing:shared docs-root maintenance undercount is"],
            "missing_note_maintenance_handoff_closure_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        note_path = root / NOTE_PATH
        _write(
            note_path,
            _read(note_path).replace(
                "broader scripts-root and tests-root parity-scorecard-survey undercount\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            ["note:missing:broader scripts-root and tests-root parity-scorecard-survey undercount"],
            "missing_note_shared_summary_alignment_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        note_path = root / NOTE_PATH
        _write(
            note_path,
            _read(note_path).replace(NOTE_START_WITH_SCRIPTS_README_MARKER + "\n", "", 1),
        )
        _assert_only(
            validate(root),
            [f"note:missing:{NOTE_START_WITH_SCRIPTS_README_MARKER}"],
            "missing_note_start_with_scripts_readme_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        lane_note_path = root / LANE_NOTE_PATH
        _write(
            lane_note_path,
            _read(lane_note_path).replace(HISTORICAL_CONTINUITY_MARKER + "\n", "", 1),
        )
        _assert_only(
            validate(root),
            [f"lane_note:missing:{HISTORICAL_CONTINUITY_MARKER}"],
            "missing_lane_note_historical_continuity_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        docs_readme_path = root / DOCS_README_PATH
        _write(
            docs_readme_path,
            _read(docs_readme_path).replace("Documentation/zigux/phase15-readiness-gate-survey.md\n", "", 1),
        )
        _assert_only(
            validate(root),
            ["docs_readme:missing:Documentation/zigux/phase15-readiness-gate-survey.md"],
            "missing_docs_readme_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        review_checklist_path = root / REVIEW_CHECKLIST_PATH
        _write(
            review_checklist_path,
            _read(review_checklist_path).replace("Architecture Council review record linked\n", "", 1),
        )
        _assert_only(
            validate(root),
            ["review_checklist:missing:Architecture Council review record linked"],
            "missing_review_checklist_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        tests_readme_path = root / TESTS_README_PATH
        _write(
            tests_readme_path,
            _read(tests_readme_path).replace("Documentation/zigux/freeze-map.md\n", "", 1),
        )
        _assert_only(
            validate(root),
            ["tests_readme:missing:Documentation/zigux/freeze-map.md"],
            "missing_tests_readme_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["ownership_evidence_fields"].remove("required approver set")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_ownership_evidence_fields:missing:required approver set"],
            "missing_manifest_ownership_field",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["required_review_packet_fields"].remove("required approver set")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_required_review_packet_fields:missing:required approver set"],
            "missing_manifest_field",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["lane_key"] = "P15-L06"
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest:lane_key"],
            "manifest_lane_key_alignment",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["anchor"] = "Documentation/zigux/freeze-map.md"
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest:anchor"],
            "manifest_anchor_alignment",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["handoff"]["replay_commands"].remove("make -C zigux phase15-test")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_handoff_replay_commands:missing:make -C zigux phase15-test"],
            "missing_manifest_handoff_phase15_test",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["handoff"]["next_step"] = manifest["handoff"]["next_step"].replace("Documentation/zigux/review-checklist.md ", "", 1)
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_handoff_next_step:missing:Documentation/zigux/review-checklist.md"],
            "missing_handoff_review_checklist_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["handoff"]["next_step"] = manifest["handoff"]["next_step"].replace(PARITY_SCORECARD_SURVEY_PATH + " ", "", 1)
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _assert_only(
            validate(root),
            [f"manifest_handoff_next_step:missing:{PARITY_SCORECARD_SURVEY_PATH}"],
            "missing_handoff_parity_scorecard_survey_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["handoff"]["next_step"] = manifest["handoff"]["next_step"].replace(
            RUN_SHARED_SUMMARY_GAP_CHECKER_FIRST_MARKER + " ",
            "",
            1,
        )
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _assert_only(
            validate(root),
            [f"manifest_handoff_next_step:missing:{RUN_SHARED_SUMMARY_GAP_CHECKER_FIRST_MARKER}"],
            "missing_handoff_run_shared_summary_gap_checker_first_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["handoff"]["next_step"] = manifest["handoff"]["next_step"].replace(
            START_WITH_SCRIPTS_README_MARKER + " ",
            "",
            1,
        )
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _assert_only(
            validate(root),
            [f"manifest_handoff_next_step:missing:{START_WITH_SCRIPTS_README_MARKER}"],
            "missing_handoff_start_with_scripts_readme_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        readiness_manifest = json.loads(_read(root / READINESS_MANIFEST_PATH))
        readiness_manifest["surveyed_commit"] = "current-master-readback-2026-05-13"
        _write(root / READINESS_MANIFEST_PATH, json.dumps(readiness_manifest, indent=2) + "\n")
        _assert_only(
            validate(root),
            [],
            "decoupled_readiness_surveyed_commit",
        )
        _seed_fixture_tree(root)
        case_count += 1

        readiness_manifest = json.loads(_read(root / READINESS_MANIFEST_PATH))
        readiness_manifest["surveyed_commit_mode"] = "exact_head"
        _write(root / READINESS_MANIFEST_PATH, json.dumps(readiness_manifest, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["readiness_manifest:surveyed_commit_mode"],
            "readiness_surveyed_commit_mode",
        )
        _seed_fixture_tree(root)
        case_count += 1

        parity_scorecard = json.loads(_read(root / PARITY_SCORECARD_PATH))
        parity_scorecard["posture"]["architecture_council_status_change_approval_recorded"] = True
        _write(root / PARITY_SCORECARD_PATH, json.dumps(parity_scorecard, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["parity_scorecard:approval_posture_mismatch"],
            "approval_posture_alignment",
        )
        _seed_fixture_tree(root)
        case_count += 1

        parity_scorecard = json.loads(_read(root / PARITY_SCORECARD_PATH))
        parity_scorecard["metrics"]["architecture_council_status_change_approval_count"] = 1
        _write(root / PARITY_SCORECARD_PATH, json.dumps(parity_scorecard, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["parity_scorecard:approval_count_mismatch"],
            "approval_count_alignment",
        )
        _seed_fixture_tree(root)
        case_count += 1

        parity_scorecard = json.loads(_read(root / PARITY_SCORECARD_PATH))
        parity_scorecard["anchors"][2]["lane_owner"] = "Architecture Council"
        _write(root / PARITY_SCORECARD_PATH, json.dumps(parity_scorecard, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["governance_alignment:owner:kernel/rcu/tree.c"],
            "owner_alignment",
        )
        _seed_fixture_tree(root)
        case_count += 1

        freeze_manifest = json.loads(_read(root / FREEZE_MAP_MANIFEST_PATH))
        freeze_manifest["blocker_ownership"][3]["required_approver_set"] = "Architecture Council"
        _write(root / FREEZE_MAP_MANIFEST_PATH, json.dumps(freeze_manifest, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["governance_alignment:required_approver_set:net/core/skbuff.c"],
            "approver_alignment",
        )
        _seed_fixture_tree(root)
        case_count += 1

        freeze_manifest = json.loads(_read(root / FREEZE_MAP_MANIFEST_PATH))
        freeze_manifest["freeze_in_c_targets"] = list(EXPECTED_FREEZE_IN_C_TARGETS[:-1])
        _write(root / FREEZE_MAP_MANIFEST_PATH, json.dumps(freeze_manifest, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["freeze_map_manifest:freeze_in_c_targets"],
            "freeze_map_targets",
        )
        _seed_fixture_tree(root)
        case_count += 1

        (root / REVIEW_CHECKLIST_PATH).unlink()
        _assert_only(
            validate(root),
            [f"missing_file:{REVIEW_CHECKLIST_PATH}"],
            "missing_review_checklist_file",
        )
        case_count += 1

    print("PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST=pass")
    print(f"PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the dedicated Phase 15 Architecture Council review-process handoff aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE15_REVIEW_PROCESS_HANDOFF=fail")
        print("PHASE15_REVIEW_PROCESS_HANDOFF_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE15_REVIEW_PROCESS_HANDOFF_ISSUES_END")
        return 1

    print("PHASE15_REVIEW_PROCESS_HANDOFF=pass")
    print(
        "PHASE15_REVIEW_PROCESS_HANDOFF_MARKER_COUNT="
        f"{len(NOTE_MARKERS) + len(NOTE_MAINTENANCE_CLOSURE_MARKERS) + len(POLICY_MARKERS) + len(LANE_NOTE_MARKERS) + len(VALIDATOR_MARKERS) + len(DOCS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_PACKET_MARKERS) + len(OWNERSHIP_EVIDENCE_FIELDS) + len(REQUIRED_REVIEW_PACKET_FIELDS) + len(TRIGGER_CONDITIONS) + len(REOPEN_TRIGGER_CATALOG) + len(DECISION_BUCKETS) + len(HANDOFF_REPLAY_COMMANDS) + len(HANDOFF_NEXT_STEP_MARKERS) + 15}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())