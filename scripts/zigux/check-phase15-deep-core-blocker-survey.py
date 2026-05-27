#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SURVEY_NOTE_PATH = Path("Documentation/zigux/phase15-deep-core-blocker-survey.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
FREEZE_GOVERNANCE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
PARITY_SCORECARD_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
INDEFINITE_POLICY_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
STUDY_ONLY_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
READINESS_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
LANE_SEQ_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
HANDOFF_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_GAP_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
FREEZE_MAP_REPLAY_PATH = Path("zigux/tests/phase15_freeze_map_governance.zig")
PARITY_REPLAY_PATH = Path("zigux/tests/phase15_parity_scorecard.zig")
LANE_OWNER_REPLAY_PATH = Path("zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig")
BUILD_REPLAY_PATH = Path("zigux/tests/phase15_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
RCU_SURVEY_PATH = Path("Documentation/zigux/phase14-rcu-tree-survey.md")
SKBUFF_SURVEY_PATH = Path("Documentation/zigux/phase14-skbuff-bridge-survey.md")

CURRENT_READBACK = "current-master-readback-2026-05-27"

REQUIRED_PRESENT_PATHS = (
    SURVEY_NOTE_PATH,
    FREEZE_MAP_PATH,
    FREEZE_GOVERNANCE_PATH,
    PARITY_SCORECARD_PATH,
    REVIEW_PROCESS_PATH,
    INDEFINITE_POLICY_PATH,
    STUDY_ONLY_PATH,
    READINESS_PATH,
    LANE_SEQ_PATH,
    HANDOFF_PATH,
    SHARED_GAP_PATH,
    VALIDATOR_PATH,
    FREEZE_MAP_REPLAY_PATH,
    PARITY_REPLAY_PATH,
    LANE_OWNER_REPLAY_PATH,
    BUILD_REPLAY_PATH,
    MAKEFILE_PATH,
    RCU_SURVEY_PATH,
    SKBUFF_SURVEY_PATH,
)

REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=deep_core_blocker_survey_landed",
    "PHASE15_LANE_KEY=P15-L01",
    "PHASE15_SLICE=roadmap_vs_repo_reality_deep_core_blocker_crosswalk",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    f"surveyed against dated current-master readback marker `{CURRENT_READBACK}`",
    "The roadmap keeps these four anchors in the active freeze-in-C set",
    "`kernel/sched/core.c`",
    "`mm/page_alloc.c`",
    "`kernel/rcu/tree.c`",
    "`net/core/skbuff.c`",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_freeze_map_governance.zig`",
    "`zigux/tests/phase15_parity_scorecard.zig`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "`zigux/tests/phase15_build.zig`",
    "`zigux/tests/phase15_build.zig` is directly materialized on current `master` as the shared Phase 15 governance replay companion",
    "`zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15`",
    "blocked_no_bounded_scheduler_seam",
    "blocked_no_bounded_allocator_seam",
    "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
    "blocked_packet_lifetime_boundary_still_too_wide",
    "keep the anchor frozen until a bounded scheduler seam exists",
    "keep the anchor frozen until a bounded allocator seam exists",
    "keep the anchor frozen until a narrower-than-freeze RCU seam exists",
    "keep the anchor frozen until a narrower-than-lifetime skbuff seam exists",
    "Study-only boundary context",
    "reopen only when one of these packet-local conditions becomes true:",
    "a freeze-in-C anchor changes blocker disposition, owner, approver set, or evidence path",
    "the broader wrapper routes or shared-CI Phase 15 route return on current `master`",
    "This note does not claim:",
    "an Architecture Council approval for any freeze-map status change",
    "a direct Zig bridge or dual implementation for any deep-core freeze-in-C anchor",
)

REQUIRED_REPLAY_COMMANDS = (
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
    "zig build test --build-file zigux/tests/phase15_build.zig",
)

REQUIRED_RCU_MARKERS = (
    "phase14-rcu-tree-bridge-blocker",
    "freeze-in-C posture",
)

REQUIRED_SKBUFF_MARKERS = (
    "phase14-skbuff-live-ownership-blocker",
    "retained-in-C posture",
)

REQUIRED_MAKEFILE_ABSENT = (
    "phase15-validate:",
    "phase15-test:",
    "phase15:",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in REQUIRED_PRESENT_PATHS:
        if not (root / rel).exists():
            failures.append(f"repo:missing_required_path:{rel.as_posix()}")
    if failures:
        return failures

    survey = _read(root / SURVEY_NOTE_PATH)
    rcu_survey = _read(root / RCU_SURVEY_PATH)
    skbuff_survey = _read(root / SKBUFF_SURVEY_PATH)
    makefile = _read(root / MAKEFILE_PATH)

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in survey:
            failures.append(f"survey:missing_marker:{marker}")

    for command in REQUIRED_REPLAY_COMMANDS:
        if command not in survey:
            failures.append(f"survey:missing_replay_command:{command}")

    for marker in REQUIRED_RCU_MARKERS:
        if marker not in rcu_survey:
            failures.append(f"rcu_survey:missing_marker:{marker}")

    for marker in REQUIRED_SKBUFF_MARKERS:
        if marker not in skbuff_survey:
            failures.append(f"skbuff_survey:missing_marker:{marker}")

    for marker in REQUIRED_MAKEFILE_ABSENT:
        if marker in makefile:
            failures.append(f"makefile:unexpected_phase15_route:{marker}")

    return failures


def _sample_survey_note() -> str:
    replay_lines = "\n".join(f"  - `{cmd}`" for cmd in REQUIRED_REPLAY_COMMANDS)
    return f"""# Phase 15 Deep-Core Blocker Survey

## Status

- `PHASE15_STATUS=deep_core_blocker_survey_landed`
- `PHASE15_LANE_KEY=P15-L01`
- `PHASE15_SLICE=roadmap_vs_repo_reality_deep_core_blocker_crosswalk`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{CURRENT_READBACK}`
- role: keep one dedicated reviewable crosswalk for the four freeze-in-C anchors so the current blocker posture can be read directly against the roadmap, the freeze-map packet, the directly materialized shared build companion, and the adjacent Phase 14 evidence without implying a status change, a wrapper-route recovery, or deep-core port readiness

## Roadmap basis

The roadmap keeps these four anchors in the active freeze-in-C set:

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

The same roadmap keeps these two neighboring deep-core areas as study-only boundary context rather than freeze-in-C scorecard rows:

- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Current repo reality packet

Current `master` directly materializes the owner packet that governs these anchors through:

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
- `zigux/tests/phase15_build.zig`

The same reread now shows the shared build companion as directly materialized while the broader wrapper and shared-CI surfaces remain current gaps:

- `zigux/tests/phase15_build.zig` is directly materialized on current `master` as the shared Phase 15 governance replay companion
- `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15`
- no Architecture Council approval is currently recorded for a freeze-map status change

## Deep-core blockers versus roadmap and repo reality

### `kernel/sched/core.c`

- current blocker: `blocked_no_bounded_scheduler_seam`
- next honest posture: keep the anchor frozen until a bounded scheduler seam exists

### `mm/page_alloc.c`

- current blocker: `blocked_no_bounded_allocator_seam`
- next honest posture: keep the anchor frozen until a bounded allocator seam exists

### `kernel/rcu/tree.c`

- current blocker: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- next honest posture: keep the anchor frozen until a narrower-than-freeze RCU seam exists

### `net/core/skbuff.c`

- current blocker: `blocked_packet_lifetime_boundary_still_too_wide`
- next honest posture: keep the anchor frozen until a narrower-than-lifetime skbuff seam exists

## Study-only boundary context

`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain relevant to deep-core governance, but they stay outside the blocked status-change scorecard tracked here.

## Maintenance-Mode Handoff

- reopen only when one of these packet-local conditions becomes true:
{replay_lines}
- a freeze-in-C anchor changes blocker disposition, owner, approver set, or evidence path
- the broader wrapper routes or shared-CI Phase 15 route return on current `master`

## Non-goals

This note does not claim:

- an Architecture Council approval for any freeze-map status change
- a direct Zig bridge or dual implementation for any deep-core freeze-in-C anchor
"""


def _sample_rcu_survey() -> str:
    return """# Phase 14 RCU Tree Survey

- blocked by `phase14-rcu-tree-bridge-blocker`
- That is still a freeze-in-C posture, not a review-ready bridge seam.
"""


def _sample_skbuff_survey() -> str:
    return """# Phase 14 skbuff Bridge Survey

- live blocker `phase14-skbuff-live-ownership-blocker`
- retained-in-C posture remains explicit here
"""


def _seed_repo(root: Path) -> None:
    _write(root / SURVEY_NOTE_PATH, _sample_survey_note())
    _write(root / RCU_SURVEY_PATH, _sample_rcu_survey())
    _write(root / SKBUFF_SURVEY_PATH, _sample_skbuff_survey())
    _write(root / MAKEFILE_PATH, "phase14-validate:\n\t@true\n")

    placeholder_paths = (
        FREEZE_MAP_PATH,
        FREEZE_GOVERNANCE_PATH,
        PARITY_SCORECARD_PATH,
        REVIEW_PROCESS_PATH,
        INDEFINITE_POLICY_PATH,
        STUDY_ONLY_PATH,
        READINESS_PATH,
        LANE_SEQ_PATH,
        HANDOFF_PATH,
        SHARED_GAP_PATH,
        VALIDATOR_PATH,
        FREEZE_MAP_REPLAY_PATH,
        PARITY_REPLAY_PATH,
        LANE_OWNER_REPLAY_PATH,
        BUILD_REPLAY_PATH,
    )
    for rel in placeholder_paths:
        _write(root / rel, "present\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_deep_core_blocker_survey_") as tmpdir:
        root = Path(tmpdir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        cases = (
            ("missing_note_marker", SURVEY_NOTE_PATH, "blocked_no_bounded_scheduler_seam", "survey:missing_marker:blocked_no_bounded_scheduler_seam"),
            ("missing_replay", SURVEY_NOTE_PATH, "python3 scripts/zigux/check-phase15-shared-summary-gap.py", "survey:missing_replay_command:python3 scripts/zigux/check-phase15-shared-summary-gap.py"),
            ("missing_rcu_marker", RCU_SURVEY_PATH, "phase14-rcu-tree-bridge-blocker", "rcu_survey:missing_marker:phase14-rcu-tree-bridge-blocker"),
            ("missing_skbuff_marker", SKBUFF_SURVEY_PATH, "phase14-skbuff-live-ownership-blocker", "skbuff_survey:missing_marker:phase14-skbuff-live-ownership-blocker"),
            ("unexpected_make_route", MAKEFILE_PATH, "phase14-validate:", "makefile:unexpected_phase15_route:phase15-validate:"),
        )

        for name, rel, needle, expected in cases:
            case_root = root / name
            _seed_repo(case_root)
            if rel == MAKEFILE_PATH:
                _write(case_root / rel, "phase15-validate:\n\t@true\n")
            else:
                text = _read(case_root / rel)
                _write(case_root / rel, text.replace(needle, "", 1))
            failures = collect_failures(case_root)
            if failures != [expected]:
                raise AssertionError(f"unexpected failures for {name}: {failures}")
            case_count += 1

    print("PHASE15_DEEP_CORE_BLOCKER_SURVEY_SELF_TEST=pass")
    print(f"PHASE15_DEEP_CORE_BLOCKER_SURVEY_SELF_TEST_CASES={case_count}")
    return 0


def write_sample_root(root: Path) -> None:
    _seed_repo(root)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 deep-core blocker survey stays aligned with its landed governance packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root to check")
    parser.add_argument("--self-test", action="store_true", help="run synthetic self-tests")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like sample root for replaying the checker",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE15_DEEP_CORE_BLOCKER_SURVEY_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_DEEP_CORE_BLOCKER_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
