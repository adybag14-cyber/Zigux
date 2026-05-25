#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase15-deep-core-blocker-survey.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
FREEZE_GOVERNANCE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
PARITY_SCORECARD_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
INDEFINITE_C_POLICY_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
STUDY_ONLY_ACCOUNTING_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
READINESS_SURVEY_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
LANE_SEQUENCING_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
HANDOFF_SURVEY_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_SUMMARY_GAP_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
MAKEFILE_PATH = Path("zigux/Makefile")
FREEZE_REPLAY_PATH = Path("zigux/tests/phase15_freeze_map_governance.zig")
PARITY_REPLAY_PATH = Path("zigux/tests/phase15_parity_scorecard.zig")
INDEFINITE_ALIGNMENT_PATH = Path("zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig")
PHASE15_BUILD_PATH = Path("zigux/tests/phase15_build.zig")
PHASE14_RCU_SURVEY_PATH = Path("Documentation/zigux/phase14-rcu-tree-survey.md")
PHASE14_SKBUFF_SURVEY_PATH = Path("Documentation/zigux/phase14-skbuff-bridge-survey.md")

EXPECTED_REQUIRED_PATHS = (
    SURVEY_PATH,
    FREEZE_MAP_PATH,
    FREEZE_GOVERNANCE_PATH,
    PARITY_SCORECARD_PATH,
    REVIEW_PROCESS_PATH,
    INDEFINITE_C_POLICY_PATH,
    STUDY_ONLY_ACCOUNTING_PATH,
    READINESS_SURVEY_PATH,
    LANE_SEQUENCING_PATH,
    HANDOFF_SURVEY_PATH,
    SHARED_SUMMARY_GAP_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    FREEZE_REPLAY_PATH,
    PARITY_REPLAY_PATH,
    INDEFINITE_ALIGNMENT_PATH,
    PHASE14_RCU_SURVEY_PATH,
    PHASE14_SKBUFF_SURVEY_PATH,
)

REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=deep_core_blocker_survey_landed",
    "PHASE15_LANE_KEY=P15-L01",
    "PHASE15_SLICE=roadmap_vs_repo_reality_deep_core_blocker_crosswalk",
    "surveyed against dated current-master readback marker `current-master-readback-2026-05-24`",
    "- `kernel/sched/core.c`",
    "- `mm/page_alloc.c`",
    "- `kernel/rcu/tree.c`",
    "- `net/core/skbuff.c`",
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
    "- `Documentation/zigux/freeze-map.md`",
    "- `Documentation/zigux/phase15-freeze-map-governance.md`",
    "- `Documentation/zigux/phase15-parity-scorecard.md`",
    "- `Documentation/zigux/phase15-architecture-council-review-process.md`",
    "- `Documentation/zigux/phase15-indefinite-c-policy.md`",
    "- `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "- `Documentation/zigux/phase15-readiness-gate-survey.md`",
    "- `Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "- `Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "- `Documentation/zigux/phase15-shared-summary-gap.md`",
    "- `scripts/zigux/validate-phase15.py`",
    "- `zigux/tests/phase15_freeze_map_governance.zig`",
    "- `zigux/tests/phase15_parity_scorecard.zig`",
    "- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "- `zigux/tests/phase15_build.zig` is still not directly materialized on current `master`",
    "- `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15`",
    "- no Architecture Council approval is currently recorded for a freeze-map status change",
    "- current blocker: `blocked_no_bounded_scheduler_seam`",
    "- current blocker: `blocked_no_bounded_allocator_seam`",
    "- current blocker: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`",
    "- current blocker: `blocked_packet_lifetime_boundary_still_too_wide`",
    "`Documentation/zigux/phase14-rcu-tree-survey.md`",
    "`Documentation/zigux/phase14-skbuff-bridge-survey.md`",
    "python3 scripts/zigux/check-phase15-docs-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "python3 scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-tests-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-review-process-handoff.py",
    "python3 scripts/zigux/check-phase15-handoff-note-alignment.py",
    "python3 scripts/zigux/check-phase15-shared-summary-gap.py",
    "python3 scripts/zigux/check-phase15-readiness-gate-packet.py",
    "python3 scripts/zigux/validate-phase15.py",
    "zig test zigux/tests/phase15_freeze_map_governance.zig",
    "zig test zigux/tests/phase15_parity_scorecard.zig",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _makefile_has_target(root: Path, target: str) -> bool:
    makefile = root / MAKEFILE_PATH
    if not makefile.exists():
        return False
    return f"\n{target}:" in ("\n" + _read_text(makefile))


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in EXPECTED_REQUIRED_PATHS:
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures

    note = _read_text(root / SURVEY_PATH)

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note:
            failures.append(f"missing_note_marker:{marker}")

    if (root / PHASE15_BUILD_PATH).exists():
        failures.append(f"unexpected_materialized_path:{PHASE15_BUILD_PATH}")
    if _makefile_has_target(root, "phase15-validate"):
        failures.append("unexpected_make_target:phase15-validate")
    if _makefile_has_target(root, "phase15-test"):
        failures.append("unexpected_make_target:phase15-test")
    if _makefile_has_target(root, "phase15"):
        failures.append("unexpected_make_target:phase15")

    return failures


def _sample_note() -> str:
    return """# Phase 15 Deep-Core Blocker Survey

## Status

- `PHASE15_STATUS=deep_core_blocker_survey_landed`
- `PHASE15_LANE_KEY=P15-L01`
- `PHASE15_SLICE=roadmap_vs_repo_reality_deep_core_blocker_crosswalk`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-24`

## Roadmap basis

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Current repo reality packet

- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_freeze_map_governance.zig`
- `zigux/tests/phase15_parity_scorecard.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`

- `zigux/tests/phase15_build.zig` is still not directly materialized on current `master`
- `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15`
- no Architecture Council approval is currently recorded for a freeze-map status change

## Deep-core blockers versus roadmap and repo reality

### `kernel/sched/core.c`
- current blocker: `blocked_no_bounded_scheduler_seam`

### `mm/page_alloc.c`
- current blocker: `blocked_no_bounded_allocator_seam`

### `kernel/rcu/tree.c`
- `Documentation/zigux/phase14-rcu-tree-survey.md`
- current blocker: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`

### `net/core/skbuff.c`
- `Documentation/zigux/phase14-skbuff-bridge-survey.md`
- current blocker: `blocked_packet_lifetime_boundary_still_too_wide`

## Maintenance handoff

- `python3 scripts/zigux/check-phase15-docs-readme-alignment.py`
- `python3 scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
- `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`
- `python3 scripts/zigux/check-phase15-tests-readme-alignment.py`
- `python3 scripts/zigux/check-phase15-review-process-handoff.py`
- `python3 scripts/zigux/check-phase15-handoff-note-alignment.py`
- `python3 scripts/zigux/check-phase15-shared-summary-gap.py`
- `python3 scripts/zigux/check-phase15-readiness-gate-packet.py`
- `python3 scripts/zigux/validate-phase15.py`
- `zig test zigux/tests/phase15_freeze_map_governance.zig`
- `zig test zigux/tests/phase15_parity_scorecard.zig`
"""


def write_sample_root(root: Path) -> None:
    _write(root / SURVEY_PATH, _sample_note())
    _write(root / FREEZE_MAP_PATH, "# sample\n")
    _write(root / FREEZE_GOVERNANCE_PATH, "# sample\n")
    _write(root / PARITY_SCORECARD_PATH, "# sample\n")
    _write(root / REVIEW_PROCESS_PATH, "# sample\n")
    _write(root / INDEFINITE_C_POLICY_PATH, "# sample\n")
    _write(root / STUDY_ONLY_ACCOUNTING_PATH, "# sample\n")
    _write(root / READINESS_SURVEY_PATH, "# sample\n")
    _write(root / LANE_SEQUENCING_PATH, "# sample\n")
    _write(root / HANDOFF_SURVEY_PATH, "# sample\n")
    _write(root / SHARED_SUMMARY_GAP_PATH, "# sample\n")
    _write(root / VALIDATOR_PATH, "#!/usr/bin/env python3\n")
    _write(root / MAKEFILE_PATH, "phase14-validate:\n\t@true\n")
    _write(root / FREEZE_REPLAY_PATH, "const std = @import(\"std\");\n")
    _write(root / PARITY_REPLAY_PATH, "const std = @import(\"std\");\n")
    _write(root / INDEFINITE_ALIGNMENT_PATH, "const std = @import(\"std\");\n")
    _write(root / PHASE14_RCU_SURVEY_PATH, "# sample\n")
    _write(root / PHASE14_SKBUFF_SURVEY_PATH, "# sample\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_deep_core_blocker_") as tmp_dir:
        base = Path(tmp_dir)

        root = base / "baseline"
        write_sample_root(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        marker_root = base / "missing_marker"
        write_sample_root(marker_root)
        _write(
            marker_root / SURVEY_PATH,
            _sample_note().replace(
                "- current blocker: `blocked_no_bounded_allocator_seam`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(marker_root)
        expected = [
            "missing_note_marker:- current blocker: `blocked_no_bounded_allocator_seam`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")

        build_root = base / "unexpected_build"
        write_sample_root(build_root)
        _write(build_root / PHASE15_BUILD_PATH, "const std = @import(\"std\");\n")
        failures = collect_failures(build_root)
        expected = [f"unexpected_materialized_path:{PHASE15_BUILD_PATH}"]
        if failures != expected:
            raise AssertionError(f"unexpected build failure: {failures}")

        make_root = base / "unexpected_make_target"
        write_sample_root(make_root)
        _write(make_root / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(make_root)
        expected = ["unexpected_make_target:phase15-validate"]
        if failures != expected:
            raise AssertionError(f"unexpected make-target failure: {failures}")

        validator_root = base / "missing_validator"
        write_sample_root(validator_root)
        (validator_root / VALIDATOR_PATH).unlink()
        failures = collect_failures(validator_root)
        expected = [f"missing_required_path:{VALIDATOR_PATH}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-validator failure: {failures}")

        handoff_root = base / "missing_handoff_checker"
        write_sample_root(handoff_root)
        _write(
            handoff_root / SURVEY_PATH,
            _sample_note().replace(
                "- `python3 scripts/zigux/check-phase15-handoff-note-alignment.py`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(handoff_root)
        expected = [
            "missing_note_marker:python3 scripts/zigux/check-phase15-handoff-note-alignment.py"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-handoff failure: {failures}")

    print("PHASE15_DEEP_CORE_BLOCKER_SURVEY_SELF_TEST=pass")
    print("PHASE15_DEEP_CORE_BLOCKER_SURVEY_SELF_TEST_CASE_COUNT=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the Phase 15 deep-core blocker survey drifts away from the current governance packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root to validate.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a sample root that satisfies this checker.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in self-tests.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"WROTE_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE15_DEEP_CORE_BLOCKER_SURVEY_FAILURE={failure}")
        return 1

    print("PHASE15_DEEP_CORE_BLOCKER_SURVEY=pass")
    print(f"PHASE15_DEEP_CORE_BLOCKER_SURVEY_NOTE={SURVEY_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
