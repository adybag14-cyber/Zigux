#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

FREEZE_MAP_REL = "Documentation/zigux/freeze-map.md"
FREEZE_GOVERNANCE_REL = "Documentation/zigux/phase15-freeze-map-governance.md"

ARCHIVES = (
    {
        "key": "kernel_sched_core",
        "path": "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
        "anchor": "kernel/sched/core.c",
        "decision_record_id": "phase15-kernel-sched-core-blocked-posture",
        "owner": "Architecture Council",
        "approvers": "Architecture Council + PMO / Release Management",
        "rollback_owner": "Architecture Council + PMO / Release Management",
        "blocker": "blocked_no_bounded_scheduler_seam",
        "benchmark_notes": "pending_until_bounded_scheduler_seam_exists",
        "extra_links": (),
        "non_goals": "this archive does not approve a status change or claim that a bounded scheduler seam already exists",
        "rationale": "current master still has no bounded scheduler seam, so the honest posture remains freeze-in-C with blocker accounting only",
        "next_step": "Keep this anchor blocked until a bounded scheduler seam exists and a named reopen trigger is recorded with fresh linked evidence.",
    },
    {
        "key": "mm_page_alloc",
        "path": "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
        "anchor": "mm/page_alloc.c",
        "decision_record_id": "phase15-mm-page-alloc-blocked-posture",
        "owner": "Architecture Council",
        "approvers": "Architecture Council + Validation and Perf Team",
        "rollback_owner": "Architecture Council + Validation and Perf Team",
        "blocker": "blocked_no_bounded_allocator_seam",
        "benchmark_notes": "pending_until_bounded_allocator_seam_exists",
        "extra_links": (),
        "non_goals": "this archive does not approve a status change or claim that a bounded allocator seam already exists",
        "rationale": "current master still has no bounded allocator seam, so the honest posture remains freeze-in-C with blocker accounting only",
        "next_step": "Keep this anchor blocked until a bounded allocator seam exists and a named reopen trigger is recorded with fresh linked evidence.",
    },
    {
        "key": "kernel_rcu_tree",
        "path": "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md",
        "anchor": "kernel/rcu/tree.c",
        "decision_record_id": "phase15-kernel-rcu-tree-blocked-posture",
        "owner": "ABI and Runtime Team",
        "approvers": "Architecture Council + ABI and Runtime Team",
        "rollback_owner": "Architecture Council + ABI and Runtime Team",
        "blocker": "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
        "benchmark_notes": "pending_until_rcu_followup_is_narrower_than_freeze_boundary",
        "extra_links": ("Documentation/zigux/phase14-rcu-tree-survey.md",),
        "non_goals": "this archive does not approve a status change or claim that an RCU follow-up is already narrower than the freeze boundary",
        "rationale": "current master still treats the carried Phase 14 RCU follow-up as wider than the allowed seam, so the honest posture remains freeze-in-C with blocker accounting only",
        "next_step": "Keep this anchor blocked until a narrower-than-freeze RCU follow-up exists and a named reopen trigger is recorded with fresh linked evidence.",
    },
    {
        "key": "net_core_skbuff",
        "path": "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md",
        "anchor": "net/core/skbuff.c",
        "decision_record_id": "phase15-net-core-skbuff-blocked-posture",
        "owner": "Shared Subsystems Pod",
        "approvers": "Architecture Council + Shared Subsystems Pod",
        "rollback_owner": "Architecture Council + Shared Subsystems Pod",
        "blocker": "blocked_packet_lifetime_boundary_still_too_wide",
        "benchmark_notes": "pending_until_skbuff_followup_is_narrower_than_lifetime_boundary",
        "extra_links": (
            "Documentation/zigux/phase14-skbuff-bridge-survey.md",
            "Documentation/zigux/phase14-core-boundary-traceability.md",
        ),
        "non_goals": "this archive does not approve a status change or claim that a skbuff follow-up is already narrower than the packet-lifetime boundary",
        "rationale": "current master still treats the surviving skbuff packet as review-first and too wide at the packet-lifetime boundary, so the honest posture remains freeze-in-C with blocker accounting only",
        "next_step": "Keep this anchor blocked until a narrower-than-lifetime skbuff follow-up exists and a named reopen trigger is recorded with fresh linked evidence.",
    },
)

REQUIRED_FILES = (
    FREEZE_MAP_REL,
    FREEZE_GOVERNANCE_REL,
    *(archive["path"] for archive in ARCHIVES),
)

FREEZE_MAP_MARKERS = (
    "freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`",
    "evidence archive path",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

FREEZE_GOVERNANCE_MARKERS = (
    "`PHASE15_STATUS=governance_slice_landed`",
    "`PHASE15_LANE_KEY=P15-L04`",
    "`PHASE15_SLICE=freeze-map-route-gap-truthfulness-refresh`",
    "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
    "surveyed against dated current-master readback marker `current-master-readback-2026-05-22`",
    "`zigux/tests/phase15_freeze_map_manifest.json`",
    "`zigux/tests/phase15_freeze_map_governance.zig`",
    "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_build.zig`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "`zigux/Makefile`",
    "direct Zig bridge or port claims for a freeze-in-C anchor stay blocked",
    "the freeze-map anchor set and study-only scope therefore stay unchanged on current `master`",
)

ARCHIVE_COMMON_MARKERS = (
    "`PHASE=Phase 15`",
    "`LANE_KEY=P15-L03`",
    "`SURVEYED_COMMIT=current-master-readback-2026-05-22`",
    "`REVIEW_STATUS=blocked_review`",
    "current Architecture Council status-change approval: `not_recorded`",
    "roadmap phase: `Phase 15`",
    "current status bucket: `freeze_in_c`",
    "requested decision bucket: `none_recorded_on_current_master`",
    "validation gate summary: `Phase 15 parity scorecard plus Architecture Council reopen record`",
    "replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`",
    "rollback threshold: `no rollback threshold is recorded because no status-change approval exists on current master`",
    "automatic return-to-blocked trigger: `stale, contradictory, or broadened evidence immediately returns the anchor to blocked posture`",
    "`retired_from_active_discussion` state: `retired_from_active_discussion` for the current maintenance-only stay-in-C posture",
    "`narrower_followup_answers_blocker`",
    "`evidence_packet_stale_or_contradictory`",
    "`ownership_or_validation_changed`",
    "trigger-specific evidence refresh: `required before any later reopen request`",
    "governance lane sequencing link or explicit scope note: `Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "study-only anchor accounting link or explicit freeze-map-anchor confirmation: `this anchor remains one of the four freeze-in-C anchors recorded in Documentation/zigux/freeze-map.md and is not part of the study-only inventory in Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "parity scorecard link or blocker record: `Documentation/zigux/phase15-parity-scorecard.md`",
    "indefinite-C policy link or explicit non-applicability note: `Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    freeze_map = _read(root / FREEZE_MAP_REL)
    for marker in FREEZE_MAP_MARKERS:
        if marker not in freeze_map:
            failures.append(f"freeze_map:missing:{marker}")

    governance = _read(root / FREEZE_GOVERNANCE_REL)
    for marker in FREEZE_GOVERNANCE_MARKERS:
        if marker not in governance:
            failures.append(f"governance:missing:{marker}")

    for archive in ARCHIVES:
        archive_path = archive["path"]
        archive_text = _read(root / archive_path)

        if f"`{archive_path}`" not in governance:
            failures.append(f"governance:missing:`{archive_path}`")
        if archive["blocker"] not in governance:
            failures.append(f"governance:missing:{archive['blocker']}")

        for marker in ARCHIVE_COMMON_MARKERS:
            if marker not in archive_text:
                failures.append(f"{archive['key']}:missing:{marker}")

        specific_markers = (
            f"`DECISION_RECORD_ID={archive['decision_record_id']}`",
            f"exact Linux anchor path: `{archive['anchor']}`",
            f"lane owner: `{archive['owner']}`",
            f"required approver set: `{archive['approvers']}`",
            f"rollback owner: `{archive['rollback_owner']}`",
            f"evidence archive path: `{archive_path}`",
            f"latest blocker disposition: `{archive['blocker']}`",
            f"benchmark notes: `{archive['benchmark_notes']}`",
            f"the current blocker: `{archive['blocker']}`",
            f"explicit non-goals: `{archive['non_goals']}`",
            f"written rationale: `{archive['rationale']}`",
            archive["next_step"],
        )
        for marker in specific_markers:
            if marker not in archive_text:
                failures.append(f"{archive['key']}:missing:{marker}")

        for link in archive["extra_links"]:
            if f"`{link}`" not in archive_text:
                failures.append(f"{archive['key']}:missing:`{link}`")

    return failures


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

- freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, and keep the exact Linux anchor path, current roadmap phase, lane owner, rollback owner, current status bucket, requested decision bucket, decision record ID, required approver set, validation gate summary, evidence archive path, latest blocker disposition, automatic return-to-blocked trigger, benchmark notes, replay command, rollback threshold, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, governance lane sequencing link or explicit scope note, study-only anchor accounting link or explicit freeze-map-anchor confirmation, explicit non-goals, and written rationale explicit beside those minimum lane fields
- study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md` so the `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` inventory does not drift from this file
"""


def _sample_governance() -> str:
    return """# Phase 15 Freeze-Map Governance

- `PHASE15_STATUS=governance_slice_landed`
- `PHASE15_LANE_KEY=P15-L04`
- `PHASE15_SLICE=freeze-map-route-gap-truthfulness-refresh`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-22`
- direct lane-owned boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `zigux/tests/phase15_freeze_map_manifest.json`
  - `zigux/tests/phase15_freeze_map_governance.zig`
- adjacent governance inputs that still shape this packet's truthfulness checks:
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase15-study-only-anchor-accounting.md`
  - `Documentation/zigux/phase15-shared-summary-gap.md`
  - `zigux/tests/README.md`
  - `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
  - `scripts/zigux/validate-phase15.py`
  - `zigux/tests/phase15_build.zig`
  - `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
  - `zigux/Makefile`
- direct Zig bridge or port claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change
- `kernel/sched/core.c`: evidence archive path `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`; latest blocker disposition `blocked_no_bounded_scheduler_seam`
- `mm/page_alloc.c`: evidence archive path `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`; latest blocker disposition `blocked_no_bounded_allocator_seam`
- `kernel/rcu/tree.c`: evidence archive path `Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md`; latest blocker disposition `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- `net/core/skbuff.c`: evidence archive path `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`; latest blocker disposition `blocked_packet_lifetime_boundary_still_too_wide`
- the freeze-map anchor set and study-only scope therefore stay unchanged on current `master`
"""


def _sample_archive(archive: dict[str, object]) -> str:
    extra_links = "".join(f"  - `{link}`\n" for link in archive["extra_links"])
    return f"""# Phase 15 Evidence Archive: `{archive['anchor']}`

## Record Metadata

- `DECISION_RECORD_ID={archive['decision_record_id']}`
- `PHASE=Phase 15`
- `LANE_KEY=P15-L03`
- `SURVEYED_COMMIT=current-master-readback-2026-05-22`
- `REVIEW_STATUS=blocked_review`
- current Architecture Council status-change approval: `not_recorded`

## Anchor And Ownership

- exact Linux anchor path: `{archive['anchor']}`
- roadmap phase: `Phase 15`
- lane owner: `{archive['owner']}`
- current status bucket: `freeze_in_c`
- requested decision bucket: `none_recorded_on_current_master`
- required approver set: `{archive['approvers']}`
- rollback owner: `{archive['rollback_owner']}`

## Validation And Evidence

- validation gate summary: `Phase 15 parity scorecard plus Architecture Council reopen record`
- evidence archive path: `{archive['path']}`
- latest blocker disposition: `{archive['blocker']}`
- benchmark notes: `{archive['benchmark_notes']}`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`
- rollback threshold: `no rollback threshold is recorded because no status-change approval exists on current master`

## Stay-In-C Posture

- retained `freeze_in_c` decision: `the anchor remains in C as the current product source of truth`
- the current blocker: `{archive['blocker']}`
- automatic return-to-blocked trigger: `stale, contradictory, or broadened evidence immediately returns the anchor to blocked posture`
- `retired_from_active_discussion` state: `retired_from_active_discussion` for the current maintenance-only stay-in-C posture
- reopen triggers:
  - `narrower_followup_answers_blocker`
  - `evidence_packet_stale_or_contradictory`
  - `ownership_or_validation_changed`
- trigger-specific evidence refresh: `required before any later reopen request`

## Supporting Context

- governance lane sequencing link or explicit scope note: `Documentation/zigux/phase15-governance-lane-sequencing.md`
- study-only anchor accounting link or explicit freeze-map-anchor confirmation: `this anchor remains one of the four freeze-in-C anchors recorded in Documentation/zigux/freeze-map.md and is not part of the study-only inventory in Documentation/zigux/phase15-study-only-anchor-accounting.md`
- parity scorecard link or blocker record: `Documentation/zigux/phase15-parity-scorecard.md`
- indefinite-C policy link or explicit non-applicability note: `Documentation/zigux/phase15-indefinite-c-policy.md`
- linked governance notes:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
{extra_links}  - `Documentation/zigux/phase15-architecture-council-review-process.md`
- explicit non-goals: `{archive['non_goals']}`
- written rationale: `{archive['rationale']}`

## Next Bounded Step

{archive['next_step']}
"""


def write_sample_root(root: Path) -> None:
    _write(root / FREEZE_MAP_REL, _sample_freeze_map())
    _write(root / FREEZE_GOVERNANCE_REL, _sample_governance())
    for archive in ARCHIVES:
        _write(root / archive["path"], _sample_archive(archive))


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_evidence_archive_packet_") as tmpdir:
        root = Path(tmpdir)
        write_sample_root(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        case_root = root / "missing_freeze_map_marker"
        write_sample_root(case_root)
        _write(
            case_root / FREEZE_MAP_REL,
            _sample_freeze_map().replace("evidence archive path", "archive field", 1),
        )
        failures = collect_failures(case_root)
        if failures != ["freeze_map:missing:evidence archive path"]:
            raise AssertionError(f"unexpected freeze-map failure: {failures}")
        case_count += 1

        case_root = root / "missing_governance_marker"
        write_sample_root(case_root)
        _write(
            case_root / FREEZE_GOVERNANCE_REL,
            _sample_governance().replace(
                "`zigux/tests/phase15_freeze_map_governance.zig`\n", "", 1
            ),
        )
        failures = collect_failures(case_root)
        expected = ["governance:missing:`zigux/tests/phase15_freeze_map_governance.zig`"]
        if failures != expected:
            raise AssertionError(f"unexpected governance failure: {failures}")
        case_count += 1

        case_root = root / "missing_archive_path"
        write_sample_root(case_root)
        archive_file = case_root / ARCHIVES[2]["path"]
        archive_file.unlink()
        failures = collect_failures(case_root)
        expected = [f"missing_file:{ARCHIVES[2]['path']}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-file failure: {failures}")
        case_count += 1

        case_root = root / "missing_archive_marker"
        write_sample_root(case_root)
        archive = ARCHIVES[3]
        _write(
            case_root / archive["path"],
            _sample_archive(archive).replace(
                f"latest blocker disposition: `{archive['blocker']}`\n", "", 1
            ),
        )
        failures = collect_failures(case_root)
        expected = [f"{archive['key']}:missing:latest blocker disposition: `{archive['blocker']}`"]
        if failures != expected:
            raise AssertionError(f"unexpected archive-marker failure: {failures}")
        case_count += 1

        case_root = root / "missing_extra_link"
        write_sample_root(case_root)
        archive = ARCHIVES[2]
        _write(
            case_root / archive["path"],
            _sample_archive(archive).replace(
                f"  - `{archive['extra_links'][0]}`\n", "", 1
            ),
        )
        failures = collect_failures(case_root)
        expected = [f"{archive['key']}:missing:`{archive['extra_links'][0]}`"]
        if failures != expected:
            raise AssertionError(f"unexpected extra-link failure: {failures}")
        case_count += 1

        case_root = root / "missing_next_step"
        write_sample_root(case_root)
        archive = ARCHIVES[0]
        _write(
            case_root / archive["path"],
            _sample_archive(archive).replace(archive["next_step"], "", 1),
        )
        failures = collect_failures(case_root)
        expected = [f"{archive['key']}:missing:{archive['next_step']}"]
        if failures != expected:
            raise AssertionError(f"unexpected next-step failure: {failures}")
        case_count += 1

    print("PHASE15_EVIDENCE_ARCHIVE_PACKET_SELF_TEST=pass")
    print(f"PHASE15_EVIDENCE_ARCHIVE_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 freeze-in-C evidence-archive packet stays aligned with the current freeze-map governance packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the Phase 15 freeze-map packet",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in synthetic checker tests",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a synthetic packet root to the given directory",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 evidence-archive packet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
