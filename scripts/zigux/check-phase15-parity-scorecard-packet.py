#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SCORECARD_NOTE_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
SCORECARD_JSON_PATH = Path("zigux/tests/phase15_parity_scorecard.json")
SCORECARD_ZIG_PATH = Path("zigux/tests/phase15_parity_scorecard.zig")
FREEZE_MAP_GOVERNANCE_ZIG_PATH = Path("zigux/tests/phase15_freeze_map_governance.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

DIRECT_PACKET_PATHS = (
    str(SCORECARD_NOTE_PATH),
    str(SCORECARD_JSON_PATH),
    str(SCORECARD_ZIG_PATH),
)

DIRECT_REMINDER_ROUTE_PATHS = (
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "scripts/zigux/validate-phase15.py",
    str(SCORECARD_ZIG_PATH),
    str(FREEZE_MAP_GOVERNANCE_ZIG_PATH),
)

DIRECT_REMINDER_ROUTE_MARKERS = {
    "scripts/zigux/check-phase15-docs-readme-alignment.py": "`python3 scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py": "`python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`",
    "scripts/zigux/check-phase15-tests-readme-alignment.py": "`python3 scripts/zigux/check-phase15-tests-readme-alignment.py`",
    "scripts/zigux/check-phase15-review-process-handoff.py": "`python3 scripts/zigux/check-phase15-review-process-handoff.py`",
    "scripts/zigux/check-phase15-shared-summary-gap.py": "`python3 scripts/zigux/check-phase15-shared-summary-gap.py`",
    "scripts/zigux/validate-phase15.py": "`python3 scripts/zigux/validate-phase15.py`",
    str(SCORECARD_ZIG_PATH): "`zig test zigux/tests/phase15_parity_scorecard.zig`",
    str(FREEZE_MAP_GOVERNANCE_ZIG_PATH): "`zig test zigux/tests/phase15_freeze_map_governance.zig`",
}

BROADER_GAP_PATHS = (
    "zigux/tests/phase15_build.zig",
)

BROADER_GAP_ROUTE_MARKERS = (
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
)

STATIC_REQUIRED_MARKERS = (
    "PHASE15_STATUS=parity_scorecard_slice_landed",
    "PHASE15_SCORECARD_ROLE=blocked_posture_accounting_not_port_readiness",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "the scorecard remains an honest blocker-accounting packet, not a port-readiness claim",
    "validator-first reminder route is directly readable on current `master` through `python3 scripts/zigux/validate-phase15.py`",
    "shared replay build route remains a repo-reality gap on current `master` through `zigux/tests/phase15_build.zig` and `zig build test --build-file zigux/tests/phase15_build.zig`",
    "current `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15` targets, so the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes remain wrapper-gap vocabulary rather than shipped reminder-route evidence",
    "Keep the scorecard parked until one of the named reopen triggers fits the evidence, the blocker posture changes, or the direct reminder-route wording, machine-readable companion inventory, and current-master shared-build or wrapper-gap inventory drift enough that the aggregate metrics or anchor records need another truthfulness refresh.",
)

STALE_TEXT_MARKERS = (
    "current-master-readback-2026-05-17",
    "current-master-readback-2026-05-18",
    "current `master` still returns missing for `scripts/zigux/validate-phase15.py`",
    "ready for a direct Zigux port claim",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _metric_lines(manifest: dict) -> tuple[str, ...]:
    metrics = manifest["metrics"]
    return (
        f"active freeze-in-C anchor count: `{metrics['active_freeze_in_c_anchor_count']}`",
        f"blocked status-change anchor count: `{metrics['blocked_status_change_anchor_count']}`",
        f"anchors blocked entirely within Phase 15 governance evidence: `{metrics['phase15_governance_only_blocker_anchor_count']}`",
        f"Phase 14 coupled blocker anchor count: `{metrics['phase14_coupled_blocker_anchor_count']}`",
        f"anchors still blocked on prior-phase bridge evidence: `{metrics['anchors_still_blocked_on_prior_phase_bridge_evidence']}`",
        f"study-only anchors tracked outside this scorecard: `{metrics['study_only_anchors_tracked_outside_scorecard']}`",
        f"Architecture Council approvals recorded for status change: `{metrics['architecture_council_status_change_approval_count']}`",
    )


def collect_failures(root: Path) -> list[str]:
    note = _read_text(root / SCORECARD_NOTE_PATH)
    manifest = _read_json(root / SCORECARD_JSON_PATH)
    failures: list[str] = []

    dynamic_required_markers = (
        f"PHASE15_LANE_KEY={manifest['lane_key']}",
        f"PHASE15_SLICE={manifest['slice']}",
        f"surveyed against dated current-master readback marker `{manifest['surveyed_commit']}`",
        manifest["posture"]["scorecard_role"],
    )

    for marker in STATIC_REQUIRED_MARKERS + dynamic_required_markers + _metric_lines(manifest):
        if marker not in note:
            failures.append(f"scorecard_note:missing_marker:{marker}")

    for rel in DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in note:
            failures.append(f"scorecard_note:missing_direct_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_path:{rel}")

    for rel in DIRECT_REMINDER_ROUTE_PATHS:
        marker = DIRECT_REMINDER_ROUTE_MARKERS[rel]
        if marker not in note:
            failures.append(f"scorecard_note:missing_route_path:{marker}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_route_path:{rel}")

    for rel in BROADER_GAP_PATHS:
        if f"`{rel}`" not in note:
            failures.append(f"scorecard_note:missing_gap_path:`{rel}`")
        if (root / rel).exists():
            failures.append(f"repo:gap_path_returned:{rel}")

    for route in BROADER_GAP_ROUTE_MARKERS:
        if f"`{route}`" not in note:
            failures.append(f"scorecard_note:missing_gap_route:`{route}`")

    makefile = _read_text(root / MAKEFILE_PATH) if (root / MAKEFILE_PATH).exists() else ""
    for target in ("phase15-validate:", "phase15-test:", "\nphase15:"):
        if target in makefile:
            failures.append(f"makefile:unexpected_phase15_target:{target.strip()}")

    for anchor in manifest["anchors"]:
        for key in (
            "path",
            "lane_owner",
            "phase",
            "current_status_bucket",
            "required_approver_set",
            "validation_gate_summary",
            "rollback_owner",
            "current_blocker",
            "next_honest_posture",
        ):
            value = anchor[key]
            if value not in note:
                failures.append(f"scorecard_note:missing_anchor_field:{key}:{value}")
        archive = anchor["evidence_archive"]
        for key in (
            "decision_record_path",
            "benchmark_notes_status",
            "replay_command",
            "latest_blocker_disposition",
        ):
            value = archive[key]
            if value not in note:
                failures.append(f"scorecard_note:missing_archive_field:{key}:{value}")
        for linked_evidence in archive["linked_evidence"]:
            if linked_evidence not in note:
                failures.append(f"scorecard_note:missing_linked_evidence:{linked_evidence}")

    if manifest["posture"]["architecture_council_status_change_approval_recorded"]:
        failures.append("manifest:unexpected_status_change_approval_recorded")

    for marker in STALE_TEXT_MARKERS:
        if marker in note:
            failures.append(f"scorecard_note:stale_marker:{marker}")

    return failures


def _sample_manifest() -> dict:
    return {
        "status": "parity_scorecard_slice_landed",
        "lane_key": "P15-L03",
        "slice": "parity-scorecard-baseline",
        "provenance_mode": "dated_master_readback",
        "surveyed_commit": "current-master-readback-2026-05-22",
        "posture": {
            "architecture_council_status_change_approval_recorded": False,
            "scorecard_role": "blocked_posture_accounting_not_port_readiness",
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
                "lane_owner": "Architecture Council",
                "phase": "Phase 15",
                "current_status_bucket": "freeze_in_c",
                "required_approver_set": "Architecture Council + PMO / Release Management",
                "validation_gate_summary": "Phase 15 parity scorecard plus Architecture Council reopen record",
                "rollback_owner": "Architecture Council + PMO / Release Management",
                "current_blocker": "blocked_no_bounded_scheduler_seam",
                "evidence_archive": {
                    "decision_record_path": "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
                    "linked_evidence": [
                        "Documentation/zigux/freeze-map.md",
                        "Documentation/zigux/phase15-freeze-map-governance.md",
                        "Documentation/zigux/phase15-architecture-council-review-process.md",
                    ],
                    "benchmark_notes_status": "pending_until_bounded_scheduler_seam_exists",
                    "replay_command": "zig test zigux/tests/phase15_freeze_map_governance.zig",
                    "latest_blocker_disposition": "blocked_no_bounded_scheduler_seam",
                },
                "next_honest_posture": "keep the anchor frozen until a bounded scheduler seam exists and a reopen trigger is recorded",
            },
            {
                "path": "mm/page_alloc.c",
                "lane_owner": "Architecture Council",
                "phase": "Phase 15",
                "current_status_bucket": "freeze_in_c",
                "required_approver_set": "Architecture Council + Validation and Perf Team",
                "validation_gate_summary": "Phase 15 parity scorecard plus Architecture Council reopen record",
                "rollback_owner": "Architecture Council + Validation and Perf Team",
                "current_blocker": "blocked_no_bounded_allocator_seam",
                "evidence_archive": {
                    "decision_record_path": "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
                    "linked_evidence": [
                        "Documentation/zigux/freeze-map.md",
                        "Documentation/zigux/phase15-freeze-map-governance.md",
                        "Documentation/zigux/phase15-architecture-council-review-process.md",
                    ],
                    "benchmark_notes_status": "pending_until_bounded_allocator_seam_exists",
                    "replay_command": "zig test zigux/tests/phase15_freeze_map_governance.zig",
                    "latest_blocker_disposition": "blocked_no_bounded_allocator_seam",
                },
                "next_honest_posture": "keep the anchor frozen until a bounded allocator seam exists and a reopen trigger is recorded",
            },
            {
                "path": "kernel/rcu/tree.c",
                "lane_owner": "ABI and Runtime Team",
                "phase": "Phase 15",
                "current_status_bucket": "freeze_in_c",
                "required_approver_set": "Architecture Council + ABI and Runtime Team",
                "validation_gate_summary": "Phase 15 parity scorecard plus Architecture Council reopen record",
                "rollback_owner": "Architecture Council + ABI and Runtime Team",
                "current_blocker": "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
                "evidence_archive": {
                    "decision_record_path": "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md",
                    "linked_evidence": [
                        "Documentation/zigux/freeze-map.md",
                        "Documentation/zigux/phase15-freeze-map-governance.md",
                        "Documentation/zigux/phase14-rcu-tree-survey.md",
                    ],
                    "benchmark_notes_status": "pending_until_rcu_followup_is_narrower_than_freeze_boundary",
                    "replay_command": "zig test zigux/tests/phase15_freeze_map_governance.zig",
                    "latest_blocker_disposition": "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
                },
                "next_honest_posture": "keep the anchor frozen until a narrower-than-freeze RCU follow-up exists and a reopen trigger is recorded",
            },
            {
                "path": "net/core/skbuff.c",
                "lane_owner": "Shared Subsystems Pod",
                "phase": "Phase 15",
                "current_status_bucket": "freeze_in_c",
                "required_approver_set": "Architecture Council + Shared Subsystems Pod",
                "validation_gate_summary": "Phase 15 parity scorecard plus Architecture Council reopen record",
                "rollback_owner": "Architecture Council + Shared Subsystems Pod",
                "current_blocker": "blocked_packet_lifetime_boundary_still_too_wide",
                "evidence_archive": {
                    "decision_record_path": "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md",
                    "linked_evidence": [
                        "Documentation/zigux/freeze-map.md",
                        "Documentation/zigux/phase15-freeze-map-governance.md",
                        "Documentation/zigux/phase14-skbuff-bridge-survey.md",
                        "Documentation/zigux/phase14-core-boundary-traceability.md",
                    ],
                    "benchmark_notes_status": "pending_until_skbuff_followup_is_narrower_than_lifetime_boundary",
                    "replay_command": "zig test zigux/tests/phase15_freeze_map_governance.zig",
                    "latest_blocker_disposition": "blocked_packet_lifetime_boundary_still_too_wide",
                },
                "next_honest_posture": "keep the anchor frozen until a narrower-than-lifetime skbuff follow-up exists and a reopen trigger is recorded",
            },
        ],
    }


def _sample_note() -> str:
    manifest = _sample_manifest()
    metrics = manifest["metrics"]
    direct_packet = "\n".join(f"- `{rel}`" for rel in DIRECT_PACKET_PATHS)
    return f"""# Phase 15 Parity Scorecard

This note records the bounded Phase 15 parity-accounting surface for the freeze-in-C anchors that remain blocked from a direct Zigux status change.

## Status

- `PHASE15_STATUS=parity_scorecard_slice_landed`
- `PHASE15_LANE_KEY={manifest['lane_key']}`
- `PHASE15_SLICE={manifest['slice']}`
- `PHASE15_PROVENANCE_MODE={manifest['provenance_mode']}`
- `PHASE15_SCORECARD_ROLE={manifest['posture']['scorecard_role']}`
- surveyed against dated current-master readback marker `{manifest['surveyed_commit']}`
- no Architecture Council approval is currently recorded for a freeze-map status change
- the scorecard remains an honest blocker-accounting packet, not a port-readiness claim

## Current direct packet

{direct_packet}

## Aggregate Metrics

- active freeze-in-C anchor count: `{metrics['active_freeze_in_c_anchor_count']}`
- blocked status-change anchor count: `{metrics['blocked_status_change_anchor_count']}`
- anchors blocked entirely within Phase 15 governance evidence: `{metrics['phase15_governance_only_blocker_anchor_count']}`
- Phase 14 coupled blocker anchor count: `{metrics['phase14_coupled_blocker_anchor_count']}`
- anchors still blocked on prior-phase bridge evidence: `{metrics['anchors_still_blocked_on_prior_phase_bridge_evidence']}`
- study-only anchors tracked outside this scorecard: `{metrics['study_only_anchors_tracked_outside_scorecard']}`
- Architecture Council approvals recorded for status change: `{metrics['architecture_council_status_change_approval_count']}`

## Current reminder route

- the current checker-backed reminder route exists through `python3 scripts/zigux/check-phase15-docs-readme-alignment.py`, `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`, `python3 scripts/zigux/check-phase15-tests-readme-alignment.py`, `python3 scripts/zigux/check-phase15-review-process-handoff.py`, `python3 scripts/zigux/check-phase15-shared-summary-gap.py`, and `zig test zigux/tests/phase15_parity_scorecard.zig`
- the machine-readable blocked-posture companion stays explicit through `zigux/tests/phase15_parity_scorecard.json` while the dedicated Zig replay stays reviewable through `zig test zigux/tests/phase15_parity_scorecard.zig`
- anchor-level blocker evidence stays reviewable through `zig test zigux/tests/phase15_freeze_map_governance.zig`
- validator-first reminder route is directly readable on current `master` through `python3 scripts/zigux/validate-phase15.py`
- shared replay build route remains a repo-reality gap on current `master` through `zigux/tests/phase15_build.zig` and `zig build test --build-file zigux/tests/phase15_build.zig`
- current `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15` targets, so the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes remain wrapper-gap vocabulary rather than shipped reminder-route evidence

## Anchor Scorecard

### `kernel/sched/core.c`
- lane owner: `Architecture Council`
- phase: `Phase 15`
- current status bucket: `freeze_in_c`
- required approver set: `Architecture Council + PMO / Release Management`
- validation gate summary: `Phase 15 parity scorecard plus Architecture Council reopen record`
- rollback owner: `Architecture Council + PMO / Release Management`
- current blocker: `blocked_no_bounded_scheduler_seam`
- decision record path: `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`
- linked evidence: `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`
- benchmark-notes status: `pending_until_bounded_scheduler_seam_exists`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`
- next honest posture: `keep the anchor frozen until a bounded scheduler seam exists and a reopen trigger is recorded`

### `mm/page_alloc.c`
- lane owner: `Architecture Council`
- phase: `Phase 15`
- current status bucket: `freeze_in_c`
- required approver set: `Architecture Council + Validation and Perf Team`
- validation gate summary: `Phase 15 parity scorecard plus Architecture Council reopen record`
- rollback owner: `Architecture Council + Validation and Perf Team`
- current blocker: `blocked_no_bounded_allocator_seam`
- decision record path: `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`
- linked evidence: `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`
- benchmark-notes status: `pending_until_bounded_allocator_seam_exists`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`
- next honest posture: `keep the anchor frozen until a bounded allocator seam exists and a reopen trigger is recorded`

### `kernel/rcu/tree.c`
- lane owner: `ABI and Runtime Team`
- phase: `Phase 15`
- current status bucket: `freeze_in_c`
- required approver set: `Architecture Council + ABI and Runtime Team`
- validation gate summary: `Phase 15 parity scorecard plus Architecture Council reopen record`
- rollback owner: `Architecture Council + ABI and Runtime Team`
- current blocker: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- decision record path: `Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md`
- linked evidence: `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase14-rcu-tree-survey.md`
- benchmark-notes status: `pending_until_rcu_followup_is_narrower_than_freeze_boundary`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`
- next honest posture: `keep the anchor frozen until a narrower-than-freeze RCU follow-up exists and a reopen trigger is recorded`

### `net/core/skbuff.c`
- lane owner: `Shared Subsystems Pod`
- phase: `Phase 15`
- current status bucket: `freeze_in_c`
- required approver set: `Architecture Council + Shared Subsystems Pod`
- validation gate summary: `Phase 15 parity scorecard plus Architecture Council reopen record`
- rollback owner: `Architecture Council + Shared Subsystems Pod`
- current blocker: `blocked_packet_lifetime_boundary_still_too_wide`
- decision record path: `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`
- linked evidence: `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`
- benchmark-notes status: `pending_until_skbuff_followup_is_narrower_than_lifetime_boundary`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`
- next honest posture: `keep the anchor frozen until a narrower-than-lifetime skbuff follow-up exists and a reopen trigger is recorded`

## Next bounded step

Keep the scorecard parked until one of the named reopen triggers fits the evidence, the blocker posture changes, or the direct reminder-route wording, machine-readable companion inventory, and current-master shared-build or wrapper-gap inventory drift enough that the aggregate metrics or anchor records need another truthfulness refresh.
"""


def _seed_repo(root: Path) -> None:
    _write(root / SCORECARD_NOTE_PATH, _sample_note())
    _write(root / SCORECARD_JSON_PATH, json.dumps(_sample_manifest(), indent=2) + "\n")
    _write(root / MAKEFILE_PATH, "phase2-toolchain:\n\t@true\n")
    for rel in DIRECT_REMINDER_ROUTE_PATHS:
        _write(root / rel, "present\n")
    for rel in DIRECT_PACKET_PATHS:
        if rel in (str(SCORECARD_NOTE_PATH), str(SCORECARD_JSON_PATH)):
            continue
        _write(root / rel, "present\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_parity_scorecard_packet_") as tmpdir:
        root = Path(tmpdir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        metric_root = root / "metric"
        _seed_repo(metric_root)
        _write(
            metric_root / SCORECARD_NOTE_PATH,
            _sample_note().replace(
                "- blocked status-change anchor count: `4`\n",
                "- blocked status-change anchor count: `3`\n",
                1,
            ),
        )
        failures = collect_failures(metric_root)
        expected = ["scorecard_note:missing_marker:blocked status-change anchor count: `4`"]
        if failures != expected:
            raise AssertionError(f"unexpected metric failure: {failures}")
        case_count += 1

        route_root = root / "route"
        _seed_repo(route_root)
        _write(
            route_root / SCORECARD_NOTE_PATH,
            _sample_note().replace("`python3 scripts/zigux/check-phase15-shared-summary-gap.py`", "", 1),
        )
        failures = collect_failures(route_root)
        expected = ["scorecard_note:missing_route_path:`python3 scripts/zigux/check-phase15-shared-summary-gap.py`"]
        if failures != expected:
            raise AssertionError(f"unexpected route failure: {failures}")
        case_count += 1

        returned_gap_root = root / "returned_gap"
        _seed_repo(returned_gap_root)
        _write(returned_gap_root / BROADER_GAP_PATHS[0], "present\n")
        failures = collect_failures(returned_gap_root)
        expected = ["repo:gap_path_returned:zigux/tests/phase15_build.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected returned-gap failure: {failures}")
        case_count += 1

        anchor_root = root / "anchor"
        _seed_repo(anchor_root)
        _write(
            anchor_root / SCORECARD_NOTE_PATH,
            _sample_note().replace("- current blocker: `blocked_packet_lifetime_boundary_still_too_wide`\n", "", 1),
        )
        failures = collect_failures(anchor_root)
        expected = [
            "scorecard_note:missing_anchor_field:current_blocker:blocked_packet_lifetime_boundary_still_too_wide",
            "scorecard_note:missing_archive_field:latest_blocker_disposition:blocked_packet_lifetime_boundary_still_too_wide",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected anchor failure: {failures}")
        case_count += 1

        stale_root = root / "stale"
        _seed_repo(stale_root)
        _write(
            stale_root / SCORECARD_NOTE_PATH,
            _sample_note().replace(
                "validator-first reminder route is directly readable on current `master` through `python3 scripts/zigux/validate-phase15.py`",
                "current `master` still returns missing for `scripts/zigux/validate-phase15.py`",
                1,
            ),
        )
        failures = collect_failures(stale_root)
        expected = [
            "scorecard_note:missing_marker:validator-first reminder route is directly readable on current `master` through `python3 scripts/zigux/validate-phase15.py`",
            "scorecard_note:missing_route_path:`python3 scripts/zigux/validate-phase15.py`",
            "scorecard_note:stale_marker:current `master` still returns missing for `scripts/zigux/validate-phase15.py`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-marker failure: {failures}")
        case_count += 1

    print("PHASE15_PARITY_SCORECARD_PACKET_SELF_TEST=pass")
    print(f"PHASE15_PARITY_SCORECARD_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 parity scorecard packet still matches the current blocker-accounting posture."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_PARITY_SCORECARD_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
