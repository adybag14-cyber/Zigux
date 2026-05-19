#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

FREEZE_MAP_GOVERNANCE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
PARITY_SCORECARD_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
INDEFINITE_C_POLICY_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")

ANCHORS = (
    {
        "anchor": "kernel/sched/core.c",
        "archive_path": "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
        "decision_record_id": "phase15-kernel-sched-core-blocked-posture",
        "lane_owner": "Architecture Council",
        "required_approver_set": "Architecture Council + PMO / Release Management",
        "rollback_owner": "Architecture Council + PMO / Release Management",
        "blocker": "blocked_no_bounded_scheduler_seam",
        "benchmark_notes": "pending_until_bounded_scheduler_seam_exists",
        "rationale_fragment": "no bounded scheduler seam",
    },
    {
        "anchor": "mm/page_alloc.c",
        "archive_path": "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
        "decision_record_id": "phase15-mm-page-alloc-blocked-posture",
        "lane_owner": "Architecture Council",
        "required_approver_set": "Architecture Council + Validation and Perf Team",
        "rollback_owner": "Architecture Council + Validation and Perf Team",
        "blocker": "blocked_no_bounded_allocator_seam",
        "benchmark_notes": "pending_until_bounded_allocator_seam_exists",
        "rationale_fragment": "no bounded allocator seam",
    },
    {
        "anchor": "kernel/rcu/tree.c",
        "archive_path": "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md",
        "decision_record_id": "phase15-kernel-rcu-tree-blocked-posture",
        "lane_owner": "ABI and Runtime Team",
        "required_approver_set": "Architecture Council + ABI and Runtime Team",
        "rollback_owner": "Architecture Council + ABI and Runtime Team",
        "blocker": "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
        "benchmark_notes": "pending_until_rcu_followup_is_narrower_than_freeze_boundary",
        "rationale_fragment": "wider than the allowed seam",
    },
    {
        "anchor": "net/core/skbuff.c",
        "archive_path": "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md",
        "decision_record_id": "phase15-net-core-skbuff-blocked-posture",
        "lane_owner": "Shared Subsystems Pod",
        "required_approver_set": "Architecture Council + Shared Subsystems Pod",
        "rollback_owner": "Architecture Council + Shared Subsystems Pod",
        "blocker": "blocked_packet_lifetime_boundary_still_too_wide",
        "benchmark_notes": "pending_until_skbuff_followup_is_narrower_than_lifetime_boundary",
        "rationale_fragment": "packet-lifetime boundary",
    },
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    freeze_map_governance = _read_text(root / FREEZE_MAP_GOVERNANCE_PATH)
    parity_scorecard = _read_text(root / PARITY_SCORECARD_PATH)
    indefinite_c_policy = _read_text(root / INDEFINITE_C_POLICY_PATH)
    review_process = _read_text(root / REVIEW_PROCESS_PATH)

    failures: list[str] = []

    if "current-master-readback-2026-05-19" not in freeze_map_governance:
        failures.append("freeze-map governance note is missing the current dated readback marker")

    if "current-master-readback-2026-05-19" not in parity_scorecard:
        failures.append("parity scorecard is missing the current dated readback marker")

    for anchor in ANCHORS:
        archive_path = Path(anchor["archive_path"])
        if not (root / archive_path).exists():
            failures.append(f"evidence archive is missing from repo: `{archive_path.as_posix()}`")
            continue

        archive = _read_text(root / archive_path)

        for required_marker in (
            anchor["anchor"],
            anchor["archive_path"],
            anchor["decision_record_id"],
            anchor["lane_owner"],
            anchor["required_approver_set"],
            anchor["rollback_owner"],
            anchor["blocker"],
            anchor["benchmark_notes"],
            "current-master-readback-2026-05-19",
            "Documentation/zigux/phase15-parity-scorecard.md",
            "Documentation/zigux/phase15-indefinite-c-policy.md",
            "Documentation/zigux/phase15-architecture-council-review-process.md",
            "retired_from_active_discussion",
            "narrower_followup_answers_blocker",
            "evidence_packet_stale_or_contradictory",
            "ownership_or_validation_changed",
            "zig test zigux/tests/phase15_freeze_map_governance.zig",
        ):
            if required_marker not in archive:
                failures.append(
                    f"evidence archive `{archive_path.as_posix()}` is missing required marker: {required_marker}"
                )

        if anchor["rationale_fragment"] not in archive:
            failures.append(
                f"evidence archive `{archive_path.as_posix()}` is missing the rationale fragment `{anchor['rationale_fragment']}`"
            )

        if anchor["archive_path"] not in freeze_map_governance:
            failures.append(
                f"freeze-map governance note is missing the archive path `{anchor['archive_path']}`"
            )

        if anchor["blocker"] not in freeze_map_governance:
            failures.append(
                f"freeze-map governance note is missing the blocker `{anchor['blocker']}`"
            )

        if anchor["archive_path"] not in parity_scorecard:
            failures.append(
                f"parity scorecard is missing the decision record path `{anchor['archive_path']}`"
            )

        if anchor["blocker"] not in parity_scorecard:
            failures.append(
                f"parity scorecard is missing the blocker `{anchor['blocker']}`"
            )

    if "required approver set" not in indefinite_c_policy:
        failures.append("indefinite-C policy note is missing the required approver set marker")

    if "automatic return-to-blocked trigger" not in review_process:
        failures.append("review-process note is missing the automatic return-to-blocked trigger marker")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_root(root: Path) -> None:
    _write(
        root / FREEZE_MAP_GOVERNANCE_PATH,
        """# Phase 15 Freeze-Map Governance

- surveyed against dated current-master readback marker `current-master-readback-2026-05-19`
- `blocked_no_bounded_scheduler_seam`
- `blocked_no_bounded_allocator_seam`
- `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- `blocked_packet_lifetime_boundary_still_too_wide`
- `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`
- `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`
- `Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md`
- `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`
""",
    )
    _write(
        root / PARITY_SCORECARD_PATH,
        """# Phase 15 Parity Scorecard

- surveyed against dated current-master readback marker `current-master-readback-2026-05-19`
- `blocked_no_bounded_scheduler_seam`
- `blocked_no_bounded_allocator_seam`
- `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- `blocked_packet_lifetime_boundary_still_too_wide`
- `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`
- `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`
- `Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md`
- `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`
""",
    )
    _write(
        root / INDEFINITE_C_POLICY_PATH,
        """# Phase 15 Indefinite-C Policy

- required approver set
""",
    )
    _write(
        root / REVIEW_PROCESS_PATH,
        """# Phase 15 Architecture Council Review Process

- automatic return-to-blocked trigger
""",
    )

    for anchor in ANCHORS:
        _write(
            root / Path(anchor["archive_path"]),
            f"""# Archive

- `{anchor["decision_record_id"]}`
- `current-master-readback-2026-05-19`
- `{anchor["anchor"]}`
- `{anchor["archive_path"]}`
- `{anchor["lane_owner"]}`
- `{anchor["required_approver_set"]}`
- `{anchor["rollback_owner"]}`
- `{anchor["blocker"]}`
- `{anchor["benchmark_notes"]}`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `retired_from_active_discussion`
- `narrower_followup_answers_blocker`
- `evidence_packet_stale_or_contradictory`
- `ownership_or_validation_changed`
- `zig test zigux/tests/phase15_freeze_map_governance.zig`
- `{anchor["rationale_fragment"]}`
""",
        )


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase15-evidence-archive-") as tmp:
        root = Path(tmp)
        _sample_root(root)
        failures = collect_failures(root)
        if failures:
            raise SystemExit(
                "PHASE15_EVIDENCE_ARCHIVE_ALIGNMENT_SELF_TEST=fail\n"
                + "\n".join(failures)
            )

    print("PHASE15_EVIDENCE_ARCHIVE_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_EVIDENCE_ARCHIVE_ALIGNMENT_SELF_TEST_CASES={len(ANCHORS)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("Phase 15 evidence archive alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
