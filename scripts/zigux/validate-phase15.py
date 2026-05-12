#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

FILES = [
    "scripts/zigux/validate-phase15.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "zigux/tests/README.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_freeze_map_manifest.json",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate.zig",
]

MAKE_MARKERS = [
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py --self-test",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/validate-phase15.py",
    "phase15-test:",
    "$(ZIG) build test --build-file zigux/tests/phase15_build.zig",
    "phase15: phase15-validate phase15-test",
]

WORKFLOW_MARKERS = [
    "Validate Phase 15 governance packet",
    "make -C zigux phase15-validate",
    "Run Phase 15 governance tests",
    "make -C zigux phase15-test",
]

DOCS_README_MARKERS = [
    "Phase 15 notes",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "zigux/tests/phase15_build.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "no Architecture Council approval is recorded yet",
    "named reopen trigger",
    "deep-core blocker-posture change",
]

SCRIPTS_README_MARKERS = [
    "Phase 15 flow",
    "validate-phase15.py",
    "check-phase15-review-process-handoff.py",
    "check-phase15-scripts-readme-alignment.py",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15",
]

TESTS_README_MARKERS = [
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate.zig",
]

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 15 governance packet",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "scripts/zigux/validate-phase15.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_readiness_gate.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "no-approval-yet posture",
]

READINESS_SURVEY_MARKERS = [
    "PHASE15_LANE_KEY=P15-L01",
    "The packet remains parked.",
    "no Architecture Council approval is currently recorded",
    "validator-first route stays explicit through `python3 scripts/zigux/validate-phase15.py` and `make -C zigux phase15-validate`",
    "shared replay route stays explicit through `zigux/tests/phase15_build.zig`",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "make -C zigux phase15-test",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase15.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "`make -C zigux phase15` packet still matches the current no-approval-yet maintenance-mode blocker posture",
    "no-approval-yet maintenance-mode blocker posture",
    "the remaining blocker is still `phase15-deep-core-status-change-blocker`",
    "phase15-docs-root-summary-alignment",
    "Later repo movement still requires a fresh bounded provenance refresh",
]

READINESS_MANIFEST_REL = "zigux/tests/phase15_readiness_gate_manifest.json"
FREEZE_MAP_MANIFEST_REL = "zigux/tests/phase15_freeze_map_manifest.json"
PARITY_SCORECARD_REL = "zigux/tests/phase15_parity_scorecard.json"
READINESS_CHECKERS = [
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
]
READINESS_BOOL_FIELDS = [
    "phase15_validate_target_present",
    "phase15_test_target_present",
    "shared_ci_phase15_present",
    "phase15_replay_green_on_current_master",
]
EXPECTED_FREEZE_IN_C_TARGETS = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
]
EXPECTED_STUDY_ONLY_TARGETS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]
EXPECTED_BLOCKED_STATUS_CHANGE_COUNT = len(EXPECTED_FREEZE_IN_C_TARGETS)


def _read(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_markers(name: str, source: str, markers: list[str], missing: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")


def _load_json(root: Path, rel: str, label: str, missing: list[str]) -> dict | None:
    try:
        value = json.loads(_read(root, rel))
    except json.JSONDecodeError:
        missing.append(f"{label}:json_decode")
        return None
    if not isinstance(value, dict):
        missing.append(f"{label}:root_object")
        return None
    return value


def _validate_readiness_manifest(root: Path, missing: list[str]) -> None:
    manifest = json.loads(_read(root, READINESS_MANIFEST_REL))
    repo_evidence = manifest.get("repo_evidence")
    if not isinstance(repo_evidence, dict):
        missing.append("readiness_manifest:repo_evidence")
        return

    for field in READINESS_BOOL_FIELDS:
        if repo_evidence.get(field) is not True:
            missing.append(f"readiness_manifest:{field}")

    checkers = manifest.get("phase15_validate_checkers")
    if checkers != READINESS_CHECKERS:
        missing.append("readiness_manifest:phase15_validate_checkers")


def _validate_phase15_governance_manifests(root: Path, missing: list[str]) -> None:
    freeze_manifest = _load_json(root, FREEZE_MAP_MANIFEST_REL, "phase15_freeze_map_manifest", missing)
    parity_scorecard = _load_json(root, PARITY_SCORECARD_REL, "phase15_parity_scorecard", missing)
    if freeze_manifest is None or parity_scorecard is None:
        return

    if freeze_manifest.get("freeze_in_c_targets") != EXPECTED_FREEZE_IN_C_TARGETS:
        missing.append("phase15_freeze_map_manifest:freeze_in_c_targets")
    if freeze_manifest.get("study_only_targets") != EXPECTED_STUDY_ONLY_TARGETS:
        missing.append("phase15_freeze_map_manifest:study_only_targets")

    blocker_ownership = freeze_manifest.get("blocker_ownership")
    if not isinstance(blocker_ownership, list):
        missing.append("phase15_freeze_map_manifest:blocker_ownership")
        blocker_anchors: list[str | None] = []
    else:
        blocker_anchors = [item.get("anchor") if isinstance(item, dict) else None for item in blocker_ownership]
        if blocker_anchors != EXPECTED_FREEZE_IN_C_TARGETS:
            missing.append("phase15_freeze_map_manifest:blocker_ownership")

    if freeze_manifest.get("surveyed_commit") != parity_scorecard.get("surveyed_commit"):
        missing.append("phase15_governance_manifests:surveyed_commit")

    posture = parity_scorecard.get("posture")
    if not isinstance(posture, dict):
        missing.append("phase15_parity_scorecard:posture")
    else:
        if posture.get("architecture_council_status_change_approval_recorded") is not False:
            missing.append("phase15_parity_scorecard:posture.architecture_council_status_change_approval_recorded")

    metrics = parity_scorecard.get("metrics")
    if not isinstance(metrics, dict):
        missing.append("phase15_parity_scorecard:metrics")
    else:
        if metrics.get("active_freeze_in_c_anchor_count") != len(EXPECTED_FREEZE_IN_C_TARGETS):
            missing.append("phase15_parity_scorecard:metrics.active_freeze_in_c_anchor_count")
        if metrics.get("blocked_status_change_anchor_count") != EXPECTED_BLOCKED_STATUS_CHANGE_COUNT:
            missing.append("phase15_parity_scorecard:metrics.blocked_status_change_anchor_count")
        if metrics.get("architecture_council_status_change_approval_count") != 0:
            missing.append("phase15_parity_scorecard:metrics.architecture_council_status_change_approval_count")

    anchors = parity_scorecard.get("anchors")
    if not isinstance(anchors, list):
        missing.append("phase15_parity_scorecard:anchors")
        return

    anchor_paths = [item.get("path") if isinstance(item, dict) else None for item in anchors]
    if anchor_paths != EXPECTED_FREEZE_IN_C_TARGETS:
        missing.append("phase15_parity_scorecard:anchors")

    if blocker_anchors == EXPECTED_FREEZE_IN_C_TARGETS and len(anchors) == len(blocker_ownership):
        for score_anchor, freeze_anchor in zip(anchors, blocker_ownership):
            if not isinstance(score_anchor, dict) or not isinstance(freeze_anchor, dict):
                missing.append("phase15_governance_manifests:anchor_alignment")
                break
            evidence_archive = score_anchor.get("evidence_archive")
            if not isinstance(evidence_archive, dict):
                missing.append("phase15_governance_manifests:anchor_alignment")
                break
            if (
                score_anchor.get("path") != freeze_anchor.get("anchor")
                or score_anchor.get("required_approver_set") != freeze_anchor.get("required_approver_set")
                or score_anchor.get("rollback_owner") != freeze_anchor.get("rollback_owner")
                or evidence_archive.get("latest_blocker_disposition") != freeze_anchor.get("latest_blocker_disposition")
            ):
                missing.append("phase15_governance_manifests:anchor_alignment")
                break


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    _require_markers("make", _read(root, "zigux/Makefile"), MAKE_MARKERS, missing_markers)
    _require_markers(
        "workflow",
        _read(root, ".github/workflows/zigux-bootstrap.yml"),
        WORKFLOW_MARKERS,
        missing_markers,
    )
    _require_markers(
        "docs_readme",
        _read(root, "Documentation/zigux/README.md"),
        DOCS_README_MARKERS,
        missing_markers,
    )
    _require_markers(
        "scripts_readme",
        _read(root, "scripts/zigux/README.md"),
        SCRIPTS_README_MARKERS,
        missing_markers,
    )
    _require_markers(
        "tests_readme",
        _read(root, "zigux/tests/README.md"),
        TESTS_README_MARKERS,
        missing_markers,
    )
    _require_markers(
        "review_checklist",
        _read(root, "Documentation/zigux/review-checklist.md"),
        REVIEW_CHECKLIST_MARKERS,
        missing_markers,
    )
    _require_markers(
        "readiness_survey",
        _read(root, "Documentation/zigux/phase15-readiness-gate-survey.md"),
        READINESS_SURVEY_MARKERS,
        missing_markers,
    )
    _validate_readiness_manifest(root, missing_markers)
    _validate_phase15_governance_manifests(root, missing_markers)
    return [], missing_markers


def _baseline_docs_readme() -> str:
    return "\n".join(
        (
            "# Zigux Documentation",
            "Phase 15 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-freeze-map-governance.md` - `Documentation/zigux/phase15-architecture-council-review-process.md` - `Documentation/zigux/phase15-parity-scorecard.md` - `Documentation/zigux/phase15-indefinite-c-policy.md` - `Documentation/zigux/phase15-readiness-gate-survey.md` - `Documentation/zigux/phase15-handoff-next-steps-survey.md` - `Documentation/zigux/phase15-governance-lane-sequencing.md` - `zigux/tests/phase15_build.zig` - `make -C zigux phase15-validate` - `make -C zigux phase15-test` - `make -C zigux phase15` now keep the current freeze-map, dedicated freeze-map-governance note, Architecture Council review-process, parity-scorecard, dedicated indefinite-C policy note, the parked readiness-gate survey, the parked handoff-next-steps survey, the governance-lane owner map, and the stay-in-C governance packet reviewable through the shipped validator-first route, the shared build replay, and the full Linux-style Phase 15 lane instead of widening into ad hoc deep-core status claims.",
            "- the current bounded Phase 15 decision is not whether a freeze-in-C anchor is ready for a direct Zigux port; no Architecture Council approval is recorded yet, so the next follow-up should wait for a named reopen trigger or a real deep-core blocker-posture change before opening another governance slice.",
            "",
        )
    )


def _phase15_freeze_map_manifest_fixture() -> dict:
    return {
        "lane_key": "P15-L04",
        "phase": "Phase 15",
        "surveyed_commit": "current-master-readback-2026-05-11",
        "surveyed_commit_mode": "dated_master_readback",
        "anchor": "Documentation/zigux/freeze-map.md",
        "freeze_in_c_targets": EXPECTED_FREEZE_IN_C_TARGETS,
        "study_only_targets": EXPECTED_STUDY_ONLY_TARGETS,
        "blocker_ownership": [
            {
                "anchor": "kernel/sched/core.c",
                "required_approver_set": "Architecture Council + PMO / Release Management",
                "rollback_owner": "Architecture Council + PMO / Release Management",
                "latest_blocker_disposition": "blocked_no_bounded_scheduler_seam",
            },
            {
                "anchor": "mm/page_alloc.c",
                "required_approver_set": "Architecture Council + Validation and Perf Team",
                "rollback_owner": "Architecture Council + Validation and Perf Team",
                "latest_blocker_disposition": "blocked_no_bounded_allocator_seam",
            },
            {
                "anchor": "kernel/rcu/tree.c",
                "required_approver_set": "Architecture Council + ABI and Runtime Team",
                "rollback_owner": "Architecture Council + ABI and Runtime Team",
                "latest_blocker_disposition": "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
            },
            {
                "anchor": "net/core/skbuff.c",
                "required_approver_set": "Architecture Council + Shared Subsystems Pod",
                "rollback_owner": "Architecture Council + Shared Subsystems Pod",
                "latest_blocker_disposition": "blocked_packet_lifetime_boundary_still_too_wide",
            },
        ],
    }


def _phase15_parity_scorecard_fixture() -> dict:
    return {
        "surveyed_commit": "current-master-readback-2026-05-11",
        "posture": {
            "architecture_council_status_change_approval_recorded": False,
        },
        "metrics": {
            "active_freeze_in_c_anchor_count": len(EXPECTED_FREEZE_IN_C_TARGETS),
            "blocked_status_change_anchor_count": EXPECTED_BLOCKED_STATUS_CHANGE_COUNT,
            "architecture_council_status_change_approval_count": 0,
        },
        "anchors": [
            {
                "path": "kernel/sched/core.c",
                "required_approver_set": "Architecture Council + PMO / Release Management",
                "rollback_owner": "Architecture Council + PMO / Release Management",
                "evidence_archive": {
                    "latest_blocker_disposition": "blocked_no_bounded_scheduler_seam",
                },
            },
            {
                "path": "mm/page_alloc.c",
                "required_approver_set": "Architecture Council + Validation and Perf Team",
                "rollback_owner": "Architecture Council + Validation and Perf Team",
                "evidence_archive": {
                    "latest_blocker_disposition": "blocked_no_bounded_allocator_seam",
                },
            },
            {
                "path": "kernel/rcu/tree.c",
                "required_approver_set": "Architecture Council + ABI and Runtime Team",
                "rollback_owner": "Architecture Council + ABI and Runtime Team",
                "evidence_archive": {
                    "latest_blocker_disposition": "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
                },
            },
            {
                "path": "net/core/skbuff.c",
                "required_approver_set": "Architecture Council + Shared Subsystems Pod",
                "rollback_owner": "Architecture Council + Shared Subsystems Pod",
                "evidence_archive": {
                    "latest_blocker_disposition": "blocked_packet_lifetime_boundary_still_too_wide",
                },
            },
        ],
    }


def _seed_fixture_tree(root: Path) -> None:
    _write(root, "scripts/zigux/validate-phase15.py", "# stub\n")
    _write(root, "scripts/zigux/check-phase15-scripts-readme-alignment.py", "# stub\n")
    _write(root, "scripts/zigux/check-phase15-review-process-handoff.py", "# stub\n")
    _write(root, "scripts/zigux/README.md", "\n".join(SCRIPTS_README_MARKERS) + "\n")
    _write(root, "Documentation/zigux/README.md", _baseline_docs_readme())
    _write(root, "Documentation/zigux/freeze-map.md", "# freeze map\n")
    _write(root, "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    _write(root, "Documentation/zigux/phase15-freeze-map-governance.md", "# freeze governance\n")
    _write(
        root,
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        "# review process\n",
    )
    _write(root, "Documentation/zigux/phase15-parity-scorecard.md", "# parity\n")
    _write(root, "Documentation/zigux/phase15-indefinite-c-policy.md", "# policy\n")
    _write(
        root,
        "Documentation/zigux/phase15-readiness-gate-survey.md",
        "\n".join(READINESS_SURVEY_MARKERS) + "\n",
    )
    _write(root, "Documentation/zigux/phase15-handoff-next-steps-survey.md", "# handoff\n")
    _write(root, "Documentation/zigux/phase15-governance-lane-sequencing.md", "# lane sequencing\n")
    _write(root, "zigux/tests/README.md", "\n".join(TESTS_README_MARKERS) + "\n")
    _write(
        root,
        ".github/workflows/zigux-bootstrap.yml",
        "\n".join(WORKFLOW_MARKERS) + "\n",
    )
    _write(root, "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")
    for rel in (
        "zigux/tests/phase15_build.zig",
        "zigux/tests/phase15_freeze_map_governance.zig",
        "zigux/tests/phase15_parity_scorecard.zig",
        "zigux/tests/phase15_architecture_council_review_process.zig",
        "zigux/tests/phase15_indefinite_c_policy.zig",
        "zigux/tests/phase15_handoff_next_steps.zig",
        "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
        "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
        "zigux/tests/phase15_governance_lane_sequencing.zig",
        "zigux/tests/phase15_readiness_gate.zig",
    ):
        _write(root, rel, "// stub\n")
    for rel in (
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
        "zigux/tests/phase15_handoff_next_steps_manifest.json",
        "zigux/tests/phase15_indefinite_c_policy.json",
    ):
        _write(root, rel, "{}\n")
    _write(
        root,
        READINESS_MANIFEST_REL,
        json.dumps(
            {
                "repo_evidence": {
                    "phase15_validate_target_present": True,
                    "phase15_test_target_present": True,
                    "shared_ci_phase15_present": True,
                    "phase15_replay_green_on_current_master": True,
                },
                "phase15_validate_checkers": READINESS_CHECKERS,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        root,
        FREEZE_MAP_MANIFEST_REL,
        json.dumps(_phase15_freeze_map_manifest_fixture(), indent=2) + "\n",
    )
    _write(
        root,
        PARITY_SCORECARD_REL,
        json.dumps(_phase15_parity_scorecard_fixture(), indent=2) + "\n",
    )


def _assert_result(
    missing_files: list[str],
    missing_markers: list[str],
    expected_files: list[str],
    expected_markers: list[str],
    label: str,
) -> None:
    if missing_files != expected_files or missing_markers != expected_markers:
        raise SystemExit(
            f"phase15-self-test:{label}:got_files={missing_files}:got_markers={missing_markers}:"
            f"want_files={expected_files}:want_markers={expected_markers}"
        )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_validate_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_fixture_tree(root)
        _assert_result(*validate(root), [], [], "baseline")
        case_count += 1

        docs_rel = "Documentation/zigux/README.md"
        docs_text = _read(root, docs_rel)
        missing_docs_marker = "make -C zigux phase15-validate"
        _write(root, docs_rel, docs_text.replace(missing_docs_marker, "", 1))
        _assert_result(*validate(root), [], [f"docs_readme:{missing_docs_marker}"], "docs_marker")
        _seed_fixture_tree(root)
        case_count += 1

        docs_text = _read(root, docs_rel)
        missing_docs_test_marker = "make -C zigux phase15-test"
        _write(root, docs_rel, docs_text.replace(missing_docs_test_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"docs_readme:{missing_docs_test_marker}"],
            "docs_test_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        docs_text = _read(root, docs_rel)
        missing_docs_readiness_marker = "Documentation/zigux/phase15-readiness-gate-survey.md"
        _write(root, docs_rel, docs_text.replace(missing_docs_readiness_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"docs_readme:{missing_docs_readiness_marker}"],
            "docs_readiness_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        docs_text = _read(root, docs_rel)
        missing_docs_handoff_marker = "Documentation/zigux/phase15-handoff-next-steps-survey.md"
        _write(root, docs_rel, docs_text.replace(missing_docs_handoff_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"docs_readme:{missing_docs_handoff_marker}"],
            "docs_handoff_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        docs_text = _read(root, docs_rel)
        missing_docs_lane_marker = "Documentation/zigux/phase15-governance-lane-sequencing.md"
        _write(root, docs_rel, docs_text.replace(missing_docs_lane_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"docs_readme:{missing_docs_lane_marker}"],
            "docs_lane_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_rel = "Documentation/zigux/review-checklist.md"
        checklist_text = _read(root, checklist_rel)
        missing_checklist_freeze_map_marker = "Documentation/zigux/freeze-map.md"
        _write(root, checklist_rel, checklist_text.replace(missing_checklist_freeze_map_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_checklist_freeze_map_marker}"],
            "review_checklist_freeze_map_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_text = _read(root, checklist_rel)
        missing_checklist_governance_marker = "Documentation/zigux/phase15-freeze-map-governance.md"
        _write(root, checklist_rel, checklist_text.replace(missing_checklist_governance_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_checklist_governance_marker}"],
            "review_checklist_governance_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_text = _read(root, checklist_rel)
        missing_checklist_parity_marker = "Documentation/zigux/phase15-parity-scorecard.md"
        _write(root, checklist_rel, checklist_text.replace(missing_checklist_parity_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_checklist_parity_marker}"],
            "review_checklist_parity_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_text = _read(root, checklist_rel)
        missing_checklist_policy_marker = "Documentation/zigux/phase15-indefinite-c-policy.md"
        _write(root, checklist_rel, checklist_text.replace(missing_checklist_policy_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_checklist_policy_marker}"],
            "review_checklist_policy_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_text = _read(root, checklist_rel)
        missing_checklist_lane_marker = "Documentation/zigux/phase15-governance-lane-sequencing.md"
        _write(root, checklist_rel, checklist_text.replace(missing_checklist_lane_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_checklist_lane_marker}"],
            "review_checklist_lane_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_text = _read(root, checklist_rel)
        missing_handoff_manifest_marker = "zigux/tests/phase15_handoff_next_steps_manifest.json"
        _write(root, checklist_rel, checklist_text.replace(missing_handoff_manifest_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_handoff_manifest_marker}"],
            "review_checklist_handoff_manifest_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_text = _read(root, checklist_rel)
        missing_readiness_manifest_marker = "zigux/tests/phase15_readiness_gate_manifest.json"
        _write(root, checklist_rel, checklist_text.replace(missing_readiness_manifest_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_readiness_manifest_marker}"],
            "review_checklist_readiness_manifest_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_text = _read(root, checklist_rel)
        missing_freeze_governance_zig_marker = "zigux/tests/phase15_freeze_map_governance.zig"
        _write(root, checklist_rel, checklist_text.replace(missing_freeze_governance_zig_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_freeze_governance_zig_marker}"],
            "review_checklist_freeze_governance_zig_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_text = _read(root, checklist_rel)
        missing_policy_json_marker = "zigux/tests/phase15_indefinite_c_policy.json"
        _write(root, checklist_rel, checklist_text.replace(missing_policy_json_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_policy_json_marker}"],
            "review_checklist_policy_json_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_text = _read(root, checklist_rel)
        missing_blocker_evidence_marker = "zigux/tests/phase15_indefinite_c_blocker_evidence.zig"
        _write(root, checklist_rel, checklist_text.replace(missing_blocker_evidence_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_blocker_evidence_marker}"],
            "review_checklist_blocker_evidence_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_text = _read(root, checklist_rel)
        missing_lane_owner_alignment_marker = "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig"
        _write(root, checklist_rel, checklist_text.replace(missing_lane_owner_alignment_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_lane_owner_alignment_marker}"],
            "review_checklist_lane_owner_alignment_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_text = _read(root, checklist_rel)
        missing_governance_lane_zig_marker = "zigux/tests/phase15_governance_lane_sequencing.zig"
        _write(root, checklist_rel, checklist_text.replace(missing_governance_lane_zig_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_governance_lane_zig_marker}"],
            "review_checklist_governance_lane_zig_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        checklist_text = _read(root, checklist_rel)
        missing_phase15_test_marker = "make -C zigux phase15-test"
        _write(
            root,
            checklist_rel,
            checklist_text.replace(missing_phase15_test_marker, "", 1),
        )
        _assert_result(
            *validate(root),
            [],
            [f"review_checklist:{missing_phase15_test_marker}"],
            "review_checklist_phase15_test_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        readiness_rel = "Documentation/zigux/phase15-readiness-gate-survey.md"
        readiness_text = _read(root, readiness_rel)
        missing_readiness_marker = "make -C zigux phase15-test"
        _write(root, readiness_rel, readiness_text.replace(missing_readiness_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"readiness_survey:{missing_readiness_marker}"],
            "readiness_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        readiness_text = _read(root, readiness_rel)
        missing_readiness_scope_marker = "Documentation/zigux/review-checklist.md"
        _write(
            root,
            readiness_rel,
            readiness_text.replace(missing_readiness_scope_marker, "", 1),
        )
        _assert_result(
            *validate(root),
            [],
            [f"readiness_survey:{missing_readiness_scope_marker}"],
            "readiness_scope_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        readiness_text = _read(root, readiness_rel)
        missing_docs_root_marker = "Documentation/zigux/README.md"
        _write(root, readiness_rel, readiness_text.replace(missing_docs_root_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"readiness_survey:{missing_docs_root_marker}"],
            "readiness_docs_root_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        readiness_text = _read(root, readiness_rel)
        missing_handoff_note_marker = "Documentation/zigux/phase15-handoff-next-steps-survey.md"
        _write(root, readiness_rel, readiness_text.replace(missing_handoff_note_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"readiness_survey:{missing_handoff_note_marker}"],
            "readiness_handoff_note_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        readiness_text = _read(root, readiness_rel)
        missing_lane_note_marker = "Documentation/zigux/phase15-governance-lane-sequencing.md"
        _write(root, readiness_rel, readiness_text.replace(missing_lane_note_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"readiness_survey:{missing_lane_note_marker}"],
            "readiness_lane_note_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        readiness_text = _read(root, readiness_rel)
        missing_scripts_alignment_marker = "scripts/zigux/check-phase15-scripts-readme-alignment.py"
        _write(
            root,
            readiness_rel,
            readiness_text.replace(missing_scripts_alignment_marker, "", 1),
        )
        _assert_result(
            *validate(root),
            [],
            [f"readiness_survey:{missing_scripts_alignment_marker}"],
            "readiness_scripts_alignment_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        readiness_text = _read(root, readiness_rel)
        missing_handoff_checker_marker = "scripts/zigux/check-phase15-review-process-handoff.py"
        _write(
            root,
            readiness_rel,
            readiness_text.replace(missing_handoff_checker_marker, "", 1),
        )
        _assert_result(
            *validate(root),
            [],
            [f"readiness_survey:{missing_handoff_checker_marker}"],
            "readiness_handoff_checker_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        tests_readme_rel = "zigux/tests/README.md"
        tests_readme_text = _read(root, tests_readme_rel)
        missing_tests_checklist_marker = "Documentation/zigux/review-checklist.md"
        _write(
            root,
            tests_readme_rel,
            tests_readme_text.replace(missing_tests_checklist_marker, "", 1),
        )
        _assert_result(
            *validate(root),
            [],
            [f"tests_readme:{missing_tests_checklist_marker}"],
            "tests_readme_checklist_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        tests_readme_text = _read(root, tests_readme_rel)
        missing_tests_scripts_alignment_marker = "scripts/zigux/check-phase15-scripts-readme-alignment.py"
        _write(
            root,
            tests_readme_rel,
            tests_readme_text.replace(missing_tests_scripts_alignment_marker, "", 1),
        )
        _assert_result(
            *validate(root),
            [],
            [f"tests_readme:{missing_tests_scripts_alignment_marker}"],
            "tests_readme_scripts_alignment_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        readiness_text = _read(root, readiness_rel)
        missing_tests_readme_marker = "zigux/tests/README.md"
        _write(root, readiness_rel, readiness_text.replace(missing_tests_readme_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"readiness_survey:{missing_tests_readme_marker}"],
            "readiness_tests_readme_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        readiness_text = _read(root, readiness_rel)
        missing_phase15_make_marker = "`make -C zigux phase15` packet still matches the current no-approval-yet maintenance-mode blocker posture"
        _write(root, readiness_rel, readiness_text.replace(missing_phase15_make_marker, "", 1))
        _assert_result(
            *validate(root),
            [],
            [f"readiness_survey:{missing_phase15_make_marker}"],
            "readiness_phase15_make_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        readiness_text = _read(root, readiness_rel)
        missing_alignment_blocker_marker = "phase15-docs-root-summary-alignment"
        _write(
            root,
            readiness_rel,
            readiness_text.replace(missing_alignment_blocker_marker, "", 1),
        )
        _assert_result(
            *validate(root),
            [],
            [f"readiness_survey:{missing_alignment_blocker_marker}"],
            "readiness_alignment_blocker_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        make_rel = "zigux/Makefile"
        make_text = _read(root, make_rel)
        missing_make_marker = "scripts/zigux/check-phase15-review-process-handoff.py --self-test"
        _write(root, make_rel, make_text.replace(missing_make_marker + "\n", "", 1))
        _assert_result(*validate(root), [], [f"make:{missing_make_marker}"], "make_marker")
        _seed_fixture_tree(root)
        case_count += 1

        manifest_text = json.loads(_read(root, READINESS_MANIFEST_REL))
        manifest_text["repo_evidence"]["phase15_validate_target_present"] = False
        _write(root, READINESS_MANIFEST_REL, json.dumps(manifest_text, indent=2) + "\n")
        _assert_result(
            *validate(root),
            [],
            ["readiness_manifest:phase15_validate_target_present"],
            "manifest_validate_target_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest_text = json.loads(_read(root, READINESS_MANIFEST_REL))
        manifest_text["phase15_validate_checkers"] = [READINESS_CHECKERS[0]]
        _write(root, READINESS_MANIFEST_REL, json.dumps(manifest_text, indent=2) + "\n")
        _assert_result(
            *validate(root),
            [],
            ["readiness_manifest:phase15_validate_checkers"],
            "manifest_checker_pair_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        freeze_manifest = _phase15_freeze_map_manifest_fixture()
        freeze_manifest["freeze_in_c_targets"] = EXPECTED_FREEZE_IN_C_TARGETS[:-1]
        _write(root, FREEZE_MAP_MANIFEST_REL, json.dumps(freeze_manifest, indent=2) + "\n")
        _assert_result(
            *validate(root),
            [],
            ["phase15_freeze_map_manifest:freeze_in_c_targets"],
            "freeze_map_targets_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        freeze_manifest = _phase15_freeze_map_manifest_fixture()
        freeze_manifest["blocker_ownership"][0]["anchor"] = "kernel/sched/core.zig"
        _write(root, FREEZE_MAP_MANIFEST_REL, json.dumps(freeze_manifest, indent=2) + "\n")
        _assert_result(
            *validate(root),
            [],
            ["phase15_freeze_map_manifest:blocker_ownership"],
            "freeze_map_blocker_ownership_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        parity_scorecard = _phase15_parity_scorecard_fixture()
        parity_scorecard["surveyed_commit"] = "current-master-readback-2026-05-10"
        _write(root, PARITY_SCORECARD_REL, json.dumps(parity_scorecard, indent=2) + "\n")
        _assert_result(
            *validate(root),
            [],
            ["phase15_governance_manifests:surveyed_commit"],
            "governance_surveyed_commit_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        parity_scorecard = _phase15_parity_scorecard_fixture()
        parity_scorecard["metrics"]["architecture_council_status_change_approval_count"] = 1
        _write(root, PARITY_SCORECARD_REL, json.dumps(parity_scorecard, indent=2) + "\n")
        _assert_result(
            *validate(root),
            [],
            ["phase15_parity_scorecard:metrics.architecture_council_status_change_approval_count"],
            "parity_scorecard_approval_count_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        parity_scorecard = _phase15_parity_scorecard_fixture()
        parity_scorecard["anchors"][0]["required_approver_set"] = "Architecture Council"
        _write(root, PARITY_SCORECARD_REL, json.dumps(parity_scorecard, indent=2) + "\n")
        _assert_result(
            *validate(root),
            [],
            ["phase15_governance_manifests:anchor_alignment"],
            "governance_anchor_alignment_marker",
        )
        _seed_fixture_tree(root)
        case_count += 1

        missing_file = "zigux/tests/phase15_handoff_next_steps.zig"
        (root / missing_file).unlink()
        _assert_result(*validate(root), [missing_file], [], "missing_file")
        case_count += 1

    print("PHASE15_VALIDATE_SELF_TEST=pass")
    print(f"PHASE15_VALIDATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the parked Phase 15 governance packet surfaces."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(args.root)
    if missing_files:
        print("PHASE15_VALIDATION=fail")
        print("MISSING_PHASE15_FILES_START")
        for path in missing_files:
            print(path)
        print("MISSING_PHASE15_FILES_END")
        return 1

    if missing_markers:
        print("PHASE15_VALIDATION=fail")
        print("PHASE15_VALIDATION_MISSING_START")
        for item in missing_markers:
            print(item)
        print("PHASE15_VALIDATION_MISSING_END")
        return 1

    print("PHASE15_VALIDATION=pass")
    print(f"PHASE15_REQUIRED_FILE_COUNT={len(FILES)}")
    print(
        "PHASE15_REQUIRED_MARKER_COUNT="
        + str(
            len(MAKE_MARKERS)
            + len(WORKFLOW_MARKERS)
            + len(DOCS_README_MARKERS)
            + len(SCRIPTS_README_MARKERS)
            + len(TESTS_README_MARKERS)
            + len(REVIEW_CHECKLIST_MARKERS)
            + len(READINESS_SURVEY_MARKERS)
            + len(READINESS_BOOL_FIELDS)
            + len(READINESS_CHECKERS)
            + 8
        )
    )
    print("PHASE15_REMAINING_BLOCKERS=phase15-deep-core-status-change-blocker")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
