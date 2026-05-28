#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase15-deep-core-blocker-survey.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
FREEZE_GOVERNANCE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
READINESS_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
HANDOFF_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_GAP_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
PARITY_SURVEY_PATH = Path("Documentation/zigux/phase15-parity-scorecard-survey.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
BUILD_PATH = Path("zigux/tests/phase15_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
RCU_SURVEY_PATH = Path("Documentation/zigux/phase14-rcu-tree-survey.md")
SKBUFF_SURVEY_PATH = Path("Documentation/zigux/phase14-skbuff-bridge-survey.md")
TRACEABILITY_PATH = Path("Documentation/zigux/phase14-core-boundary-traceability.md")

EXPECTED_LANE_KEY = "P15-L01"
EXPECTED_STATUS = "deep_core_blocker_survey_landed"
EXPECTED_SLICE = "roadmap_vs_repo_reality_deep_core_blocker_crosswalk"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-27"

FREEZE_IN_C_ANCHORS = (
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
)
STUDY_ONLY_ANCHORS = (
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
)

REQUIRED_SURVEY_MARKERS = (
    f"`PHASE15_STATUS={EXPECTED_STATUS}`",
    f"`PHASE15_LANE_KEY={EXPECTED_LANE_KEY}`",
    f"`PHASE15_SLICE={EXPECTED_SLICE}`",
    "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
    f"`{EXPECTED_SURVEYED_COMMIT}`",
    "the current blocker posture can be read directly against the roadmap",
    "shared build companion",
    "directly materialized",
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
    "`zigux/tests/phase15_build.zig` is directly materialized on current `master`",
    "`zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15`",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "`Documentation/zigux/phase14-rcu-tree-survey.md` still records blocked `phase14-rcu-tree-bridge-blocker`",
    "`Documentation/zigux/phase14-skbuff-bridge-survey.md` still records live blocker `phase14-skbuff-live-ownership-blocker`",
    "`Documentation/zigux/phase14-core-boundary-traceability.md` still keeps skbuff in retained-in-C posture",
    "Current blocker: `blocked_no_bounded_scheduler_seam`",
    "Current blocker: `blocked_no_bounded_allocator_seam`",
    "Current blocker: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`",
    "Current blocker: `blocked_packet_lifetime_boundary_still_too_wide`",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _makefile_has_target(root: Path, target: str) -> bool:
    makefile = _read_text(root / MAKEFILE_PATH)
    return f"\n{target}:" in ("\n" + makefile)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    required_paths = (
        SURVEY_PATH,
        FREEZE_MAP_PATH,
        FREEZE_GOVERNANCE_PATH,
        READINESS_PATH,
        HANDOFF_PATH,
        SHARED_GAP_PATH,
        PARITY_SURVEY_PATH,
        VALIDATOR_PATH,
        BUILD_PATH,
        MAKEFILE_PATH,
        RCU_SURVEY_PATH,
        SKBUFF_SURVEY_PATH,
        TRACEABILITY_PATH,
    )
    for rel in required_paths:
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures

    survey = _read_text(root / SURVEY_PATH)
    freeze_map = _read_text(root / FREEZE_MAP_PATH)
    governance = _read_text(root / FREEZE_GOVERNANCE_PATH)
    readiness = _read_text(root / READINESS_PATH)
    handoff = _read_text(root / HANDOFF_PATH)
    shared_gap = _read_text(root / SHARED_GAP_PATH)
    parity_survey = _read_text(root / PARITY_SURVEY_PATH)
    rcu_survey = _read_text(root / RCU_SURVEY_PATH)
    skbuff_survey = _read_text(root / SKBUFF_SURVEY_PATH)
    traceability = _read_text(root / TRACEABILITY_PATH)

    for marker in REQUIRED_SURVEY_MARKERS:
        if marker not in survey:
            failures.append(f"survey:missing_marker:{marker}")

    for anchor in FREEZE_IN_C_ANCHORS:
        quoted = f"`{anchor}`"
        if quoted not in survey:
            failures.append(f"survey:missing_anchor:{quoted}")
        if quoted not in freeze_map:
            failures.append(f"freeze_map:missing_anchor:{quoted}")
        if quoted not in governance:
            failures.append(f"governance:missing_anchor:{quoted}")

    for anchor in STUDY_ONLY_ANCHORS:
        quoted = f"`{anchor}`"
        if quoted not in survey:
            failures.append(f"survey:missing_study_only_anchor:{quoted}")
        if quoted not in freeze_map:
            failures.append(f"freeze_map:missing_study_only_anchor:{quoted}")

    survey_path_marker = "`Documentation/zigux/phase15-deep-core-blocker-survey.md`"
    if survey_path_marker not in handoff:
        failures.append("handoff:missing_deep_core_survey_marker")
    if survey_path_marker not in shared_gap:
        failures.append("shared_gap:missing_deep_core_survey_marker")

    if "`zigux/tests/phase15_build.zig`" not in readiness:
        failures.append("readiness:missing_build_marker")
    if "shared-build companion is now directly readable current-master evidence" not in readiness:
        failures.append("readiness:missing_shared_build_phrase")
    if "shared-build companion" not in parity_survey:
        failures.append("parity_survey:missing_shared_build_phrase")
    if "phase14-rcu-tree-bridge-blocker" not in rcu_survey:
        failures.append("rcu_survey:missing_blocker_marker")
    if "phase14-skbuff-live-ownership-blocker" not in skbuff_survey:
        failures.append("skbuff_survey:missing_blocker_marker")
    if "retained-in-C posture" not in traceability:
        failures.append("traceability:missing_retained_in_c_marker")

    for target in ("phase15-validate", "phase15-test", "phase15"):
        if _makefile_has_target(root, target):
            failures.append(f"makefile:unexpected_target:{target}")

    return failures


def write_sample_root(root: Path) -> None:
    anchors = "\n".join(f"- `{anchor}`" for anchor in FREEZE_IN_C_ANCHORS)
    study_only = "\n".join(f"- `{anchor}`" for anchor in STUDY_ONLY_ANCHORS)
    _write_text(
        root / SURVEY_PATH,
        f"""# Phase 15 Deep-Core Blocker Survey

## Status

- `PHASE15_STATUS={EXPECTED_STATUS}`
- `PHASE15_LANE_KEY={EXPECTED_LANE_KEY}`
- `PHASE15_SLICE={EXPECTED_SLICE}`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{EXPECTED_SURVEYED_COMMIT}`
- role: keep one dedicated reviewable crosswalk so the current blocker posture can be read directly against the roadmap, the freeze-map packet, the directly materialized shared build companion, and the adjacent Phase 14 evidence without implying a status change

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
- `zigux/tests/phase15_build.zig` is directly materialized on current `master`
- `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15`
- no Architecture Council approval is currently recorded for a freeze-map status change

## Deep-core blockers versus roadmap and repo reality

{anchors}

- `Documentation/zigux/phase14-rcu-tree-survey.md` still records blocked `phase14-rcu-tree-bridge-blocker`
- `Documentation/zigux/phase14-skbuff-bridge-survey.md` still records live blocker `phase14-skbuff-live-ownership-blocker`
- `Documentation/zigux/phase14-core-boundary-traceability.md` still keeps skbuff in retained-in-C posture

### `kernel/sched/core.c`
- Current blocker: `blocked_no_bounded_scheduler_seam`

### `mm/page_alloc.c`
- Current blocker: `blocked_no_bounded_allocator_seam`

### `kernel/rcu/tree.c`
- Current blocker: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`

### `net/core/skbuff.c`
- Current blocker: `blocked_packet_lifetime_boundary_still_too_wide`

## Study-only boundary context

{study_only}
""",
    )
    _write_text(
        root / FREEZE_MAP_PATH,
        """# Zigux Freeze Map

## Freeze In C Initially
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
""",
    )
    _write_text(
        root / FREEZE_GOVERNANCE_PATH,
        """# Phase 15 Freeze-Map Governance

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`
""",
    )
    _write_text(
        root / READINESS_PATH,
        """# Phase 15 Readiness Gate Survey

- the dedicated shared-build companion is now directly readable current-master evidence
- the shared build companion is directly materialized inside the current readiness packet
- `zigux/tests/phase15_build.zig`
""",
    )
    _write_text(
        root / HANDOFF_PATH,
        """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/phase15-deep-core-blocker-survey.md`
""",
    )
    _write_text(
        root / SHARED_GAP_PATH,
        """# Phase 15 Shared Summary Gap

- `Documentation/zigux/phase15-deep-core-blocker-survey.md`
""",
    )
    _write_text(
        root / PARITY_SURVEY_PATH,
        """# Phase 15 Parity Scorecard Survey

- the dedicated shared-build companion is no longer missing from the packet
- keep the shared-build companion explicit in the dedicated parity packet
""",
    )
    _write_text(root / VALIDATOR_PATH, "#!/usr/bin/env python3\n")
    _write_text(root / BUILD_PATH, 'const std = @import("std");\n')
    _write_text(root / MAKEFILE_PATH, "phase14-validate:\n\t@true\n")
    _write_text(
        root / RCU_SURVEY_PATH,
        """# Phase 14 RCU Tree Survey

- phase14-rcu-tree-bridge-blocker
""",
    )
    _write_text(
        root / SKBUFF_SURVEY_PATH,
        """# Phase 14 Skbuff Bridge Survey

- phase14-skbuff-live-ownership-blocker
""",
    )
    _write_text(
        root / TRACEABILITY_PATH,
        """# Phase 14 Core Boundary Traceability

- retained-in-C posture
""",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_deep_core_blocker_survey_") as tmp_dir:
        base = Path(tmp_dir)

        baseline = base / "baseline"
        write_sample_root(baseline)
        failures = collect_failures(baseline)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_marker_root = base / "missing_marker"
        write_sample_root(missing_marker_root)
        _write_text(
            missing_marker_root / SURVEY_PATH,
            _read_text(missing_marker_root / SURVEY_PATH).replace(
                "- `zigux/tests/phase15_build.zig` is directly materialized on current `master`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_marker_root)
        expected = ["survey:missing_marker:`zigux/tests/phase15_build.zig` is directly materialized on current `master`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")
        case_count += 1

        missing_path_root = base / "missing_path"
        write_sample_root(missing_path_root)
        (missing_path_root / HANDOFF_PATH).unlink()
        failures = collect_failures(missing_path_root)
        expected = [f"missing_required_path:{HANDOFF_PATH}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-path failure: {failures}")
        case_count += 1

        stale_readiness_root = base / "stale_readiness"
        write_sample_root(stale_readiness_root)
        _write_text(stale_readiness_root / READINESS_PATH, "# Phase 15 Readiness Gate Survey\n")
        failures = collect_failures(stale_readiness_root)
        expected = [
            "readiness:missing_build_marker",
            "readiness:missing_shared_build_phrase",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-readiness failure: {failures}")
        case_count += 1

        rcu_root = base / "rcu"
        write_sample_root(rcu_root)
        _write_text(rcu_root / RCU_SURVEY_PATH, "# Phase 14 RCU Tree Survey\n")
        failures = collect_failures(rcu_root)
        expected = ["rcu_survey:missing_blocker_marker"]
        if failures != expected:
            raise AssertionError(f"unexpected rcu failure: {failures}")
        case_count += 1

        make_root = base / "make"
        write_sample_root(make_root)
        _write_text(make_root / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(make_root)
        expected = ["makefile:unexpected_target:phase15-validate"]
        if failures != expected:
            raise AssertionError(f"unexpected makefile failure: {failures}")
        case_count += 1

    print("PHASE15_DEEP_CORE_BLOCKER_SURVEY_SELF_TEST=pass")
    print(f"PHASE15_DEEP_CORE_BLOCKER_SURVEY_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 deep-core blocker survey stays aligned with current repo reality."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run synthetic self-test coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a small sample tree that satisfies the checker",
    )
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"WROTE_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_DEEP_CORE_BLOCKER_SURVEY=pass")
    print(f"PHASE15_DEEP_CORE_BLOCKER_SURVEY_ANCHOR_COUNT={len(FREEZE_IN_C_ANCHORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
