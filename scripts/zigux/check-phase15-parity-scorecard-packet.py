#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
SCORECARD_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
SCORECARD_SURVEY_PATH = Path("Documentation/zigux/phase15-parity-scorecard-survey.md")
GOVERNANCE_LANE_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
HANDOFF_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_GAP_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
JSON_PATH = Path("zigux/tests/phase15_parity_scorecard.json")
ZIG_PATH = Path("zigux/tests/phase15_parity_scorecard.zig")

EXPECTED_LANE_KEY = "P15-L03"
EXPECTED_SLICE = "parity-scorecard-baseline"
EXPECTED_READBACK = "current-master-readback-2026-05-25"
EXPECTED_ROLE = "blocked_posture_accounting_not_port_readiness"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _line_containing(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line
    return None


def _load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    required_paths = (
        FREEZE_MAP_PATH,
        REVIEW_CHECKLIST_PATH,
        SCORECARD_PATH,
        SCORECARD_SURVEY_PATH,
        GOVERNANCE_LANE_PATH,
        HANDOFF_PATH,
        SHARED_GAP_PATH,
        JSON_PATH,
        ZIG_PATH,
    )
    for rel in required_paths:
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures

    freeze_map = _read_text(root / FREEZE_MAP_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    scorecard = _read_text(root / SCORECARD_PATH)
    survey = _read_text(root / SCORECARD_SURVEY_PATH)
    governance_lane = _read_text(root / GOVERNANCE_LANE_PATH)
    handoff = _read_text(root / HANDOFF_PATH)
    shared_gap = _read_text(root / SHARED_GAP_PATH)
    manifest = _load_manifest(root / JSON_PATH)
    zig_replay = _read_text(root / ZIG_PATH)

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("slice") != EXPECTED_SLICE:
        failures.append(f"slice:{manifest.get('slice')!r}")
    if manifest.get("surveyed_commit") != EXPECTED_READBACK:
        failures.append(f"surveyed_commit:{manifest.get('surveyed_commit')!r}")
    if manifest.get("posture", {}).get("scorecard_role") != EXPECTED_ROLE:
        failures.append(f"scorecard_role:{manifest.get('posture', {}).get('scorecard_role')!r}")

    metrics = manifest.get("metrics", {})
    metric_pairs = (
        ("active_freeze_in_c_anchor_count", "active freeze-in-C anchor count"),
        ("blocked_status_change_anchor_count", "blocked status-change anchor count"),
        ("phase15_governance_only_blocker_anchor_count", "anchors blocked entirely within Phase 15 governance evidence"),
        ("phase14_coupled_blocker_anchor_count", "Phase 14 coupled blocker anchor count"),
        ("anchors_still_blocked_on_prior_phase_bridge_evidence", "anchors still blocked on prior-phase bridge evidence"),
        ("study_only_anchors_tracked_outside_scorecard", "study-only anchors tracked outside this scorecard"),
        ("architecture_council_status_change_approval_count", "Architecture Council approvals recorded for status change"),
    )
    for json_key, doc_label in metric_pairs:
        rendered = f"{doc_label}: `{metrics.get(json_key)}`"
        if rendered not in scorecard:
            failures.append(f"scorecard metric drift:{json_key}")

    for marker in (
        EXPECTED_LANE_KEY,
        EXPECTED_SLICE,
        EXPECTED_READBACK,
        EXPECTED_ROLE,
        "validator-first reminder route is directly readable on current `master` through `python3 scripts/zigux/validate-phase15.py`",
        "shared replay build route is directly readable on current `master` through `zigux/tests/phase15_build.zig` and `zig build test --build-file zigux/tests/phase15_build.zig`",
        "python3 scripts/zigux/check-phase15-docs-readme-alignment.py",
        "python3 scripts/zigux/check-phase15-scripts-readme-alignment.py",
        "python3 scripts/zigux/check-phase15-tests-readme-alignment.py",
        "python3 scripts/zigux/check-phase15-review-process-handoff.py",
        "python3 scripts/zigux/check-phase15-shared-summary-gap.py",
        "zig test zigux/tests/phase15_parity_scorecard.zig",
        "zig test zigux/tests/phase15_freeze_map_governance.zig",
    ):
        if marker not in scorecard:
            failures.append(f"scorecard missing marker:{marker}")

    survey_markers = (
        EXPECTED_READBACK,
        "scripts/zigux/validate-phase15.py",
        "zigux/tests/phase15_build.zig",
        "the dedicated parity-scorecard packet itself aligned on current `master`",
        "`Documentation/zigux/phase15-governance-lane-sequencing.md` still carries the older dedicated-build-gap wording",
        "`phase15-validator-first-route-materialized`",
        "`phase15-shared-build-route-materialized`",
    )
    for marker in survey_markers:
        if marker not in survey:
            failures.append(f"survey missing marker:{marker}")

    governance_markers = (
        "`Documentation/zigux/phase15-parity-scorecard.md`, `zigux/tests/phase15_parity_scorecard.json`, and `zigux/tests/phase15_parity_scorecard.zig` own blocked-posture accounting",
        "`zigux/tests/phase15_build.zig` is now directly materialized",
        "refresh the parity scorecard only if a blocker posture, owner, approver set, or evidence path changed",
    )
    for marker in governance_markers:
        if marker not in governance_lane:
            failures.append(f"governance lane missing marker:{marker}")

    handoff_markers = (
        "`Documentation/zigux/phase15-parity-scorecard.md`",
        "`Documentation/zigux/phase15-parity-scorecard-survey.md`",
        "`zigux/tests/phase15_parity_scorecard.json`",
        "`zigux/tests/phase15_parity_scorecard.zig`",
        "the dedicated parity-scorecard packet itself aligned on current `master`",
    )
    for marker in handoff_markers:
        if marker not in handoff:
            failures.append(f"handoff missing marker:{marker}")

    shared_gap_markers = (
        "`Documentation/zigux/phase15-parity-scorecard-survey.md`",
        "`zigux/tests/phase15_parity_scorecard.json`",
        "`zigux/tests/phase15_parity_scorecard.zig`",
        "`Documentation/zigux/phase15-parity-scorecard.md`",
        "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    )
    for marker in shared_gap_markers:
        if marker not in shared_gap:
            failures.append(f"shared-gap missing marker:{marker}")

    checklist_line = _line_containing(
        review_checklist,
        "if a freeze-map anchor is entering Architecture Council status review",
    )
    if checklist_line is None:
        failures.append("review-checklist missing Architecture Council prompt")
    else:
        for marker in (
            "required approver set",
            "rollback owner",
            "evidence archive path",
            "Documentation/zigux/phase15-architecture-council-review-process.md",
            "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            "Documentation/zigux/phase15-indefinite-c-policy.md",
        ):
            if marker not in checklist_line:
                failures.append(f"review-checklist boundary drift:{marker}")

    study_only_line = _line_containing(
        review_checklist,
        "if a shared reminder surface summarizes the study-only freeze-map anchors",
    )
    if study_only_line is None:
        failures.append("review-checklist missing study-only anchor prompt")
    else:
        for marker in (
            "Documentation/zigux/freeze-map.md",
            "Documentation/zigux/phase15-study-only-anchor-accounting.md",
            "kernel/workqueue.c",
            "kernel/trace/ring_buffer.c",
        ):
            if marker not in study_only_line:
                failures.append(f"review-checklist study-only drift:{marker}")

    if metrics.get("study_only_anchors_tracked_outside_scorecard") != 2:
        failures.append("manifest study-only anchor count drift")
    if metrics.get("blocked_status_change_anchor_count") != 4:
        failures.append("manifest blocked anchor count drift")
    if metrics.get("architecture_council_status_change_approval_count") != 0:
        failures.append("manifest approval count drift")

    anchors = manifest.get("anchors", [])
    expected_freeze = [
        "kernel/sched/core.c",
        "mm/page_alloc.c",
        "kernel/rcu/tree.c",
        "net/core/skbuff.c",
    ]
    for anchor_path in expected_freeze:
        if f"`{anchor_path}`" not in freeze_map:
            failures.append(f"freeze-map missing freeze anchor:{anchor_path}")
    for anchor_path in ("kernel/workqueue.c", "kernel/trace/ring_buffer.c"):
        if f"`{anchor_path}`" not in freeze_map:
            failures.append(f"freeze-map missing study-only anchor:{anchor_path}")

    if len(anchors) != len(expected_freeze):
        failures.append(f"manifest anchor count:{len(anchors)}")
    for anchor in anchors:
        path = anchor.get("path")
        if not path:
            failures.append("manifest anchor missing path")
            continue
        if f"`{path}`" not in freeze_map:
            failures.append(f"freeze-map parity anchor drift:{path}")
        if path not in scorecard:
            failures.append(f"scorecard anchor drift:{path}")
        if path not in survey:
            failures.append(f"survey anchor drift:{path}")
        if path not in zig_replay:
            failures.append(f"zig replay anchor drift:{path}")

        current_blocker = anchor.get("current_blocker")
        required_approver_set = anchor.get("required_approver_set")
        decision_record_path = anchor.get("evidence_archive", {}).get("decision_record_path")
        replay_command = anchor.get("evidence_archive", {}).get("replay_command")
        benchmark_notes = anchor.get("evidence_archive", {}).get("benchmark_notes_status")

        for doc, label in (
            (scorecard, "scorecard"),
            (zig_replay, "zig replay"),
        ):
            for marker, kind in (
                (current_blocker, "blocker"),
                (required_approver_set, "required approver set"),
                (decision_record_path, "decision record path"),
                (replay_command, "replay command"),
                (benchmark_notes, "benchmark notes"),
            ):
                if marker and marker not in doc:
                    failures.append(f"{label} anchor {kind} drift:{path}")

    for marker in (
        '"lane_key": "P15-L03"',
        '"surveyed_commit": "current-master-readback-2026-05-25"',
        '"architecture_council_status_change_approval_count": 0',
    ):
        if marker not in zig_replay:
            failures.append(f"zig replay missing literal:{marker}")

    return failures


def _sample_manifest() -> str:
    payload = {
        "status": "parity_scorecard_slice_landed",
        "lane_key": EXPECTED_LANE_KEY,
        "slice": EXPECTED_SLICE,
        "provenance_mode": "dated_master_readback",
        "surveyed_commit": EXPECTED_READBACK,
        "posture": {
            "architecture_council_status_change_approval_recorded": False,
            "scorecard_role": EXPECTED_ROLE,
        },
        "metrics": {
            "active_freeze_in_c_anchor_count": 4,
            "blocked_status_change_anchor_count": 4,
            "phase15_governance_only_blocker_anchor_count": 2,
            "phase14_coupled_blocker_anchor_count": 2,
            "anchors_still_blocked_on_prior_phase_bridge_evidence": 2,
            "study_only_anchors_tracked_outside_scorecard": 2,
            "architecture_council_status_change_approval_count": 0,
        },
        "anchors": [
            {
                "path": "kernel/sched/core.c",
                "required_approver_set": "Architecture Council + PMO / Release Management",
                "current_blocker": "blocked_no_bounded_scheduler_seam",
                "evidence_archive": {
                    "decision_record_path": "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
                    "replay_command": "zig test zigux/tests/phase15_freeze_map_governance.zig",
                    "benchmark_notes_status": "pending_until_bounded_scheduler_seam_exists",
                },
            },
            {
                "path": "mm/page_alloc.c",
                "required_approver_set": "Architecture Council + Validation and Perf Team",
                "current_blocker": "blocked_no_bounded_allocator_seam",
                "evidence_archive": {
                    "decision_record_path": "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
                    "replay_command": "zig test zigux/tests/phase15_freeze_map_governance.zig",
                    "benchmark_notes_status": "pending_until_bounded_allocator_seam_exists",
                },
            },
            {
                "path": "kernel/rcu/tree.c",
                "required_approver_set": "Architecture Council + ABI and Runtime Team",
                "current_blocker": "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
                "evidence_archive": {
                    "decision_record_path": "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md",
                    "replay_command": "zig test zigux/tests/phase15_freeze_map_governance.zig",
                    "benchmark_notes_status": "pending_until_rcu_followup_is_narrower_than_freeze_boundary",
                },
            },
            {
                "path": "net/core/skbuff.c",
                "required_approver_set": "Architecture Council + Shared Subsystems Pod",
                "current_blocker": "blocked_packet_lifetime_boundary_still_too_wide",
                "evidence_archive": {
                    "decision_record_path": "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md",
                    "replay_command": "zig test zigux/tests/phase15_freeze_map_governance.zig",
                    "benchmark_notes_status": "pending_until_skbuff_followup_is_narrower_than_lifetime_boundary",
                },
            },
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

## Freeze In C Initially
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
"""


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

- if a freeze-map anchor is entering Architecture Council status review, does this checklist keep the shared entry-review prompt explicit, including the required approver set, rollback owner, and evidence archive path, while Documentation/zigux/phase15-architecture-council-review-process.md and Documentation/zigux/phase15-architecture-council-decision-record-template.md remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details, and Documentation/zigux/phase15-indefinite-c-policy.md remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording?
- if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through Documentation/zigux/freeze-map.md and Documentation/zigux/phase15-study-only-anchor-accounting.md so kernel/workqueue.c and kernel/trace/ring_buffer.c stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?
"""


def _sample_scorecard() -> str:
    return """# Phase 15 Parity Scorecard

- `PHASE15_LANE_KEY=P15-L03`
- `PHASE15_SLICE=parity-scorecard-baseline`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-25`
- `PHASE15_SCORECARD_ROLE=blocked_posture_accounting_not_port_readiness`

- active freeze-in-C anchor count: `4`
- blocked status-change anchor count: `4`
- anchors blocked entirely within Phase 15 governance evidence: `2`
- Phase 14 coupled blocker anchor count: `2`
- anchors still blocked on prior-phase bridge evidence: `2`
- study-only anchors tracked outside this scorecard: `2`
- Architecture Council approvals recorded for status change: `0`

## Current reminder route

- python3 scripts/zigux/check-phase15-docs-readme-alignment.py
- python3 scripts/zigux/check-phase15-scripts-readme-alignment.py
- python3 scripts/zigux/check-phase15-tests-readme-alignment.py
- python3 scripts/zigux/check-phase15-review-process-handoff.py
- python3 scripts/zigux/check-phase15-shared-summary-gap.py
- zig test zigux/tests/phase15_parity_scorecard.zig
- anchor-level blocker evidence stays reviewable through `zig test zigux/tests/phase15_freeze_map_governance.zig`
- validator-first reminder route is directly readable on current `master` through `python3 scripts/zigux/validate-phase15.py`
- shared replay build route is directly readable on current `master` through `zigux/tests/phase15_build.zig` and `zig build test --build-file zigux/tests/phase15_build.zig`

### `kernel/sched/core.c`
- required approver set: `Architecture Council + PMO / Release Management`
- current blocker: `blocked_no_bounded_scheduler_seam`
- decision record path: `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`
- benchmark notes status: `pending_until_bounded_scheduler_seam_exists`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`

### `mm/page_alloc.c`
- required approver set: `Architecture Council + Validation and Perf Team`
- current blocker: `blocked_no_bounded_allocator_seam`
- decision record path: `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`
- benchmark notes status: `pending_until_bounded_allocator_seam_exists`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`

### `kernel/rcu/tree.c`
- required approver set: `Architecture Council + ABI and Runtime Team`
- current blocker: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- decision record path: `Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md`
- benchmark notes status: `pending_until_rcu_followup_is_narrower_than_freeze_boundary`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`

### `net/core/skbuff.c`
- required approver set: `Architecture Council + Shared Subsystems Pod`
- current blocker: `blocked_packet_lifetime_boundary_still_too_wide`
- decision record path: `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`
- benchmark notes status: `pending_until_skbuff_followup_is_narrower_than_lifetime_boundary`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`

## Next bounded step

Keep the scorecard parked until one of the named reopen triggers fits the evidence, the blocker posture changes, or the direct reminder-route wording, machine-readable companion inventory, and current-master wrapper-gap or workflow-gap inventory drift enough that the aggregate metrics or anchor records need another truthfulness refresh.
"""


def _sample_survey() -> str:
    return """# Phase 15 Parity Scorecard Survey

- surveyed against dated current-master readback marker `current-master-readback-2026-05-25`
- the dedicated parity-scorecard packet itself aligned on current `master`
- `Documentation/zigux/phase15-governance-lane-sequencing.md` still carries the older dedicated-build-gap wording
- `phase15-validator-first-route-materialized`
- `phase15-shared-build-route-materialized`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`
"""


def _sample_governance_lane() -> str:
    return """# Phase 15 Governance Lane Sequencing

- `Documentation/zigux/phase15-parity-scorecard.md`, `zigux/tests/phase15_parity_scorecard.json`, and `zigux/tests/phase15_parity_scorecard.zig` own blocked-posture accounting
- `zigux/tests/phase15_build.zig` is now directly materialized
- refresh the parity scorecard only if a blocker posture, owner, approver set, or evidence path changed
"""


def _sample_handoff() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-parity-scorecard-survey.md`
- `zigux/tests/phase15_parity_scorecard.json`
- `zigux/tests/phase15_parity_scorecard.zig`
- the dedicated parity-scorecard packet itself aligned on current `master`
"""


def _sample_shared_gap() -> str:
    return """# Phase 15 Shared Summary Gap

- `Documentation/zigux/phase15-parity-scorecard-survey.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `zigux/tests/phase15_parity_scorecard.json`
- `zigux/tests/phase15_parity_scorecard.zig`
"""


def _sample_zig_replay() -> str:
    return """const std = @import(\"std\");

test \"phase 15 parity scorecard manifest keeps the blocked posture explicit\" {
    _ = std.testing;
    _ = \"lane_key\\\": \\\"P15-L03\\\"\";
    _ = \"surveyed_commit\\\": \\\"current-master-readback-2026-05-25\\\"\";
    _ = \"architecture_council_status_change_approval_count\\\": 0\";
    _ = \"kernel/sched/core.c\";
    _ = \"mm/page_alloc.c\";
    _ = \"kernel/rcu/tree.c\";
    _ = \"net/core/skbuff.c\";
    _ = \"blocked_no_bounded_scheduler_seam\";
    _ = \"blocked_no_bounded_allocator_seam\";
    _ = \"blocked_phase14_followup_still_wider_than_allowed_rcu_seam\";
    _ = \"blocked_packet_lifetime_boundary_still_too_wide\";
    _ = \"Architecture Council + PMO / Release Management\";
    _ = \"Architecture Council + Validation and Perf Team\";
    _ = \"Architecture Council + ABI and Runtime Team\";
    _ = \"Architecture Council + Shared Subsystems Pod\";
    _ = \"Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md\";
    _ = \"Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md\";
    _ = \"Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md\";
    _ = \"Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md\";
    _ = \"pending_until_bounded_scheduler_seam_exists\";
    _ = \"pending_until_bounded_allocator_seam_exists\";
    _ = \"pending_until_rcu_followup_is_narrower_than_freeze_boundary\";
    _ = \"pending_until_skbuff_followup_is_narrower_than_lifetime_boundary\";
    _ = \"zig test zigux/tests/phase15_freeze_map_governance.zig\";
}
"""


def write_fixture_root(root: Path) -> None:
    _write(root / FREEZE_MAP_PATH, _sample_freeze_map())
    _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
    _write(root / SCORECARD_PATH, _sample_scorecard())
    _write(root / SCORECARD_SURVEY_PATH, _sample_survey())
    _write(root / GOVERNANCE_LANE_PATH, _sample_governance_lane())
    _write(root / HANDOFF_PATH, _sample_handoff())
    _write(root / SHARED_GAP_PATH, _sample_shared_gap())
    _write(root / JSON_PATH, _sample_manifest())
    _write(root / ZIG_PATH, _sample_zig_replay())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_parity_scorecard_packet_") as tmp_dir:
        base = Path(tmp_dir)

        root = base / "baseline"
        write_fixture_root(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        survey_root = base / "survey"
        write_fixture_root(survey_root)
        _write(
            survey_root / SCORECARD_SURVEY_PATH,
            _sample_survey().replace("`phase15-shared-build-route-materialized`\n", "", 1),
        )
        failures = collect_failures(survey_root)
        if failures != ["survey missing marker:`phase15-shared-build-route-materialized`"]:
            raise AssertionError(f"unexpected survey failure: {failures}")
        case_count += 1

        checklist_root = base / "checklist"
        write_fixture_root(checklist_root)
        _write(
            checklist_root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace("rollback owner, ", "", 1),
        )
        failures = collect_failures(checklist_root)
        if failures != ["review-checklist boundary drift:rollback owner"]:
            raise AssertionError(f"unexpected checklist failure: {failures}")
        case_count += 1

        zig_root = base / "zig"
        write_fixture_root(zig_root)
        _write(
            zig_root / ZIG_PATH,
            _sample_zig_replay().replace("blocked_packet_lifetime_boundary_still_too_wide", "", 1),
        )
        failures = collect_failures(zig_root)
        if failures != ["zig replay anchor blocker drift:net/core/skbuff.c"]:
            raise AssertionError(f"unexpected zig failure: {failures}")
        case_count += 1

        shared_root = base / "shared"
        write_fixture_root(shared_root)
        _write(
            shared_root / SHARED_GAP_PATH,
            _sample_shared_gap().replace("`Documentation/zigux/phase15-parity-scorecard.md`\n", "", 1),
        )
        failures = collect_failures(shared_root)
        if failures != ["shared-gap missing marker:`Documentation/zigux/phase15-parity-scorecard.md`"]:
            raise AssertionError(f"unexpected shared-gap failure: {failures}")
        case_count += 1

    print("PHASE15_PARITY_SCORECARD_PACKET_SELF_TEST=pass")
    print(f"PHASE15_PARITY_SCORECARD_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 parity-scorecard packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 parity-scorecard packet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
