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

DIRECT_PACKET_PATHS = (
    "Documentation/zigux/phase15-parity-scorecard.md",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_parity_scorecard.zig",
)

DIRECT_REMINDER_ROUTE_PATHS = (
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
)

BROADER_GAP_PATHS = (
    "scripts/zigux/validate-phase15.py",
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
    "the broader validator-first and shared-build route wording through `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` remains repo-reality gap vocabulary on current `master`, not shipped evidence",
    "Keep the scorecard parked until one of the named reopen triggers fits the evidence, the blocker posture changes, or the direct reminder-route wording drifts enough that the aggregate metrics or anchor records need another truthfulness refresh.",
)

STALE_TEXT_MARKERS = (
    "current-master-readback-2026-05-17",
    "Architecture Council approvals recorded for status change: `1`",
    "ready for a direct Zigux port claim",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _metric_lines(manifest: dict) -> tuple[str, ...]:
    metrics = manifest["metrics"]
    return (
        f"active freeze-in-C anchor count: `{metrics['active_freeze_in_c_anchor_count']}`",
        f"blocked status-change anchor count: `{metrics['blocked_status_change_anchor_count']}`",
        "anchors blocked entirely within Phase 15 governance evidence: "
        f"`{metrics['phase15_governance_only_blocker_anchor_count']}`",
        f"Phase 14 coupled blocker anchor count: `{metrics['phase14_coupled_blocker_anchor_count']}`",
        "anchors still blocked on prior-phase bridge evidence: "
        f"`{metrics['anchors_still_blocked_on_prior_phase_bridge_evidence']}`",
        "study-only anchors tracked outside this scorecard: "
        f"`{metrics['study_only_anchors_tracked_outside_scorecard']}`",
        "Architecture Council approvals recorded for status change: "
        f"`{metrics['architecture_council_status_change_approval_count']}`",
    )


def collect_failures(root: Path) -> list[str]:
    note = _read_text(root / SCORECARD_NOTE_PATH)
    manifest = _read_json(root / SCORECARD_JSON_PATH)
    failures: list[str] = []

    lane_key_marker = f"PHASE15_LANE_KEY={manifest['lane_key']}"
    slice_marker = f"PHASE15_SLICE={manifest['slice']}"
    provenance_marker = f"surveyed against dated current-master readback marker `{manifest['surveyed_commit']}`"
    posture_marker = manifest["posture"]["scorecard_role"]

    required_markers = STATIC_REQUIRED_MARKERS + (
        lane_key_marker,
        slice_marker,
        posture_marker,
        provenance_marker,
    ) + _metric_lines(manifest)

    for marker in required_markers:
        if marker not in note:
            failures.append(f"scorecard_note:missing_marker:{marker}")

    for rel in DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in note:
            failures.append(f"scorecard_note:missing_direct_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_path:{rel}")

    for rel in DIRECT_REMINDER_ROUTE_PATHS:
        if f"`{rel}`" not in note:
            failures.append(f"scorecard_note:missing_route_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_route_path:{rel}")

    for rel in BROADER_GAP_PATHS:
        if f"`{rel}`" not in note:
            failures.append(f"scorecard_note:missing_gap_path:`{rel}`")
        if (root / rel).exists():
            failures.append(f"repo:gap_path_returned:{rel}")

    for marker in BROADER_GAP_ROUTE_MARKERS:
        if f"`{marker}`" not in note:
            failures.append(f"scorecard_note:missing_gap_route:`{marker}`")

    for anchor in manifest["anchors"]:
        if anchor["path"] not in note:
            failures.append(f"scorecard_note:missing_anchor:{anchor['path']}")
        if anchor["lane_owner"] not in note:
            failures.append(f"scorecard_note:missing_lane_owner:{anchor['lane_owner']}")
        if anchor["current_blocker"] not in note:
            failures.append(f"scorecard_note:missing_blocker:{anchor['current_blocker']}")

    if manifest["posture"]["architecture_council_status_change_approval_recorded"]:
        failures.append("manifest:unexpected_status_change_approval_recorded")

    for marker in STALE_TEXT_MARKERS:
        if marker in note:
            failures.append(f"scorecard_note:stale_marker:{marker}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest() -> dict:
    return {
        "status": "parity_scorecard_slice_landed",
        "lane_key": "P15-L03",
        "slice": "parity-scorecard-baseline",
        "provenance_mode": "dated_master_readback",
        "surveyed_commit": "current-master-readback-2026-05-18",
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
                "current_blocker": "blocked_no_bounded_scheduler_seam",
            },
            {
                "path": "mm/page_alloc.c",
                "lane_owner": "Architecture Council",
                "current_blocker": "blocked_no_bounded_allocator_seam",
            },
            {
                "path": "kernel/rcu/tree.c",
                "lane_owner": "ABI and Runtime Team",
                "current_blocker": "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
            },
            {
                "path": "net/core/skbuff.c",
                "lane_owner": "Shared Subsystems Pod",
                "current_blocker": "blocked_packet_lifetime_boundary_still_too_wide",
            },
        ],
    }


def _sample_note() -> str:
    manifest = _sample_manifest()
    metrics = manifest["metrics"]
    direct_packet = "\n".join(f"- `{rel}`" for rel in DIRECT_PACKET_PATHS)
    return f"""# Phase 15 Parity Scorecard

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

- the current directly materialized reminder route exists through `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, and `zig test zigux/tests/phase15_parity_scorecard.zig`
- anchor-level blocker evidence stays reviewable through `zig test zigux/tests/phase15_freeze_map_governance.zig`
- the direct reminder-route packet therefore still depends on `zigux/tests/phase15_freeze_map_governance.zig` beside the dedicated scorecard replay
- the broader validator-first and shared-build route wording through `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` remains repo-reality gap vocabulary on current `master`, not shipped evidence

## Anchor Scorecard

- `kernel/sched/core.c` / `Architecture Council` / `blocked_no_bounded_scheduler_seam`
- `mm/page_alloc.c` / `Architecture Council` / `blocked_no_bounded_allocator_seam`
- `kernel/rcu/tree.c` / `ABI and Runtime Team` / `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- `net/core/skbuff.c` / `Shared Subsystems Pod` / `blocked_packet_lifetime_boundary_still_too_wide`

## Next bounded step

Keep the scorecard parked until one of the named reopen triggers fits the evidence, the blocker posture changes, or the direct reminder-route wording drifts enough that the aggregate metrics or anchor records need another truthfulness refresh.
"""


def _seed_repo(root: Path) -> None:
    _write(root / SCORECARD_NOTE_PATH, _sample_note())
    _write(root / SCORECARD_JSON_PATH, json.dumps(_sample_manifest(), indent=2) + "\n")
    for rel in DIRECT_REMINDER_ROUTE_PATHS:
        _write(root / rel, "present\n")
    for rel in DIRECT_PACKET_PATHS:
        if rel in (
            str(SCORECARD_NOTE_PATH),
            str(SCORECARD_JSON_PATH),
        ):
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
            _sample_note().replace("`scripts/zigux/check-phase15-shared-summary-gap.py`", "", 1),
        )
        failures = collect_failures(route_root)
        expected = ["scorecard_note:missing_route_path:`scripts/zigux/check-phase15-shared-summary-gap.py`"]
        if failures != expected:
            raise AssertionError(f"unexpected route failure: {failures}")
        case_count += 1

        returned_gap_root = root / "returned_gap"
        _seed_repo(returned_gap_root)
        _write(returned_gap_root / BROADER_GAP_PATHS[0], "present\n")
        failures = collect_failures(returned_gap_root)
        expected = ["repo:gap_path_returned:scripts/zigux/validate-phase15.py"]
        if failures != expected:
            raise AssertionError(f"unexpected returned-gap failure: {failures}")
        case_count += 1

        anchor_root = root / "anchor"
        _seed_repo(anchor_root)
        _write(
            anchor_root / SCORECARD_NOTE_PATH,
            _sample_note().replace("`net/core/skbuff.c` / `Shared Subsystems Pod` / `blocked_packet_lifetime_boundary_still_too_wide`\n", "", 1),
        )
        failures = collect_failures(anchor_root)
        expected = [
            "scorecard_note:missing_anchor:net/core/skbuff.c",
            "scorecard_note:missing_lane_owner:Shared Subsystems Pod",
            "scorecard_note:missing_blocker:blocked_packet_lifetime_boundary_still_too_wide",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected anchor failure: {failures}")
        case_count += 1

        stale_root = root / "stale"
        _seed_repo(stale_root)
        _write(
            stale_root / SCORECARD_NOTE_PATH,
            _sample_note().replace(
                "current-master-readback-2026-05-18",
                "current-master-readback-2026-05-17",
            ),
        )
        failures = collect_failures(stale_root)
        expected = [
            "scorecard_note:missing_marker:surveyed against dated current-master readback marker `current-master-readback-2026-05-18`",
            "scorecard_note:stale_marker:current-master-readback-2026-05-17",
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
