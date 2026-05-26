#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-24"

EXPECTED_ANCHORS = (
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
)
EXPECTED_STUDY_ONLY = (
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
)

REQUIRED_SURVEY_MARKERS = (
    f"PHASE15_STATUS={EXPECTED_STATUS}",
    f"PHASE15_LANE_KEY={EXPECTED_LANE_KEY}",
    f"PHASE15_SLICE={EXPECTED_SLICE}",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    f"surveyed against dated current-master readback marker `{EXPECTED_SURVEYED_COMMIT}`",
    "role: keep one dedicated reviewable crosswalk for the four freeze-in-C anchors",
    "What was still missing as a standalone reviewable surface was the direct survey",
    "Current `master` directly materializes the owner packet that governs these anchors through:",
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
    "`zigux/tests/phase15_build.zig` is still not directly materialized on current `master`",
    "`zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15`",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "`Documentation/zigux/phase14-rcu-tree-survey.md` still records blocked `phase14-rcu-tree-bridge-blocker`",
    "`Documentation/zigux/phase14-skbuff-bridge-survey.md` still records live blocker `phase14-skbuff-live-ownership-blocker`",
    "`Documentation/zigux/phase14-core-boundary-traceability.md` still keeps skbuff in retained-in-C posture",
)

FORBIDDEN_SURVEY_MARKERS = (
    "current-master-readback-2026-05-25",
    "`scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig` are both present",
    "`zigux/tests/phase15_build.zig` is now directly materialized",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _makefile_has_target(root: Path, target: str) -> bool:
    return f"\n{target}:" in ("\n" + _read_text(root / MAKEFILE_PATH))


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

    for marker in FORBIDDEN_SURVEY_MARKERS:
        if marker in survey:
            failures.append(f"survey:forbidden_marker:{marker}")

    for anchor in EXPECTED_ANCHORS:
        if f"`{anchor}`" not in survey:
            failures.append(f"survey:missing_anchor:`{anchor}`")
        if f"`{anchor}`" not in freeze_map:
            failures.append(f"freeze_map:missing_anchor:`{anchor}`")
        if f"`{anchor}`" not in governance:
            failures.append(f"governance:missing_anchor:`{anchor}`")

    for anchor in EXPECTED_STUDY_ONLY:
        marker = f"`{anchor}`"
        if marker not in survey:
            failures.append(f"survey:missing_study_only_anchor:{marker}")
        if marker not in freeze_map:
            failures.append(f"freeze_map:missing_study_only_anchor:{marker}")

    if "`Documentation/zigux/phase15-deep-core-blocker-survey.md`" not in freeze_map:
        failures.append("freeze_map:missing_deep_core_survey_marker")
    if "`Documentation/zigux/phase15-deep-core-blocker-survey.md`" not in handoff:
        failures.append("handoff:missing_deep_core_survey_marker")
    if "`Documentation/zigux/phase15-deep-core-blocker-survey.md`" not in shared_gap:
        failures.append("shared_gap:missing_deep_core_survey_marker")

    if "`scripts/zigux/validate-phase15.py`" not in readiness:
        failures.append("readiness:missing_validator_marker")
    if "`zigux/tests/phase15_build.zig`" not in readiness:
        failures.append("readiness:missing_build_marker")
    if "the dedicated shared-build companion" not in parity_survey:
        failures.append("parity_survey:missing_shared_build_marker")

    if "phase14-rcu-tree-bridge-blocker" not in rcu_survey:
        failures.append("rcu_survey:missing_blocker_marker")
    if "phase14-skbuff-live-ownership-blocker" not in skbuff_survey:
        failures.append("skbuff_survey:missing_blocker_marker")
    if "retained-in-C posture" not in traceability:
        failures.append("traceability:missing_retained_in_c_marker")

    if _makefile_has_target(root, "phase15-validate"):
        failures.append("makefile:unexpected_phase15_validate_target")
    if _makefile_has_target(root, "phase15-test"):
        failures.append("makefile:unexpected_phase15_test_target")
    if _makefile_has_target(root, "phase15"):
        failures.append("makefile:unexpected_phase15_target")

    return failures


def _sample_survey() -> str:
    anchors = "\n".join(f"- `{anchor}`" for anchor in EXPECTED_ANCHORS)
    study_only = "\n".join(f"- `{anchor}`" for anchor in EXPECTED_STUDY_ONLY)
    return f"""# Phase 15 Deep-Core Blocker Survey

## Status

- `PHASE15_STATUS={EXPECTED_STATUS}`
- `PHASE15_LANE_KEY={EXPECTED_LANE_KEY}`
- `PHASE15_SLICE={EXPECTED_SLICE}`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{EXPECTED_SURVEYED_COMMIT}`
- role: keep one dedicated reviewable crosswalk for the four freeze-in-C anchors

## Why this note exists

What was still missing as a standalone reviewable surface was the direct survey.

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

The same reread still shows the broader shared-build and wrapper surfaces as current gaps:

- `zigux/tests/phase15_build.zig` is still not directly materialized on current `master`
- `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15`
- no Architecture Council approval is currently recorded for a freeze-map status change

## Deep-core blockers versus roadmap and repo reality

{anchors}

- `Documentation/zigux/phase14-rcu-tree-survey.md` still records blocked `phase14-rcu-tree-bridge-blocker`
- `Documentation/zigux/phase14-skbuff-bridge-survey.md` still records live blocker `phase14-skbuff-live-ownership-blocker`
- `Documentation/zigux/phase14-core-boundary-traceability.md` still keeps skbuff in retained-in-C posture

## Study-only boundary context

{study_only}
"""


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- `Documentation/zigux/phase15-deep-core-blocker-survey.md`
"""


def _sample_governance() -> str:
    anchors = "\n".join(f"- `{anchor}`" for anchor in EXPECTED_ANCHORS)
    return f"""# Phase 15 Freeze-Map Governance

{anchors}
"""


def _sample_readiness() -> str:
    return """# Phase 15 Readiness Gate Survey

- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
"""


def _sample_handoff() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/phase15-deep-core-blocker-survey.md`
"""


def _sample_shared_gap() -> str:
    return """# Phase 15 Shared Summary Gap

- `Documentation/zigux/phase15-deep-core-blocker-survey.md`
"""


def _sample_parity_survey() -> str:
    return """# Phase 15 Parity Scorecard Survey

- the dedicated shared-build companion
"""


def _sample_rcu_survey() -> str:
    return """# Phase 14 RCU Tree Survey

- phase14-rcu-tree-bridge-blocker
"""


def _sample_skbuff_survey() -> str:
    return """# Phase 14 Skbuff Bridge Survey

- phase14-skbuff-live-ownership-blocker
"""


def _sample_traceability() -> str:
    return """# Phase 14 Core Boundary Traceability

- retained-in-C posture
"""


def _seed_repo(root: Path) -> None:
    _write(root / SURVEY_PATH, _sample_survey())
    _write(root / FREEZE_MAP_PATH, _sample_freeze_map())
    _write(root / FREEZE_GOVERNANCE_PATH, _sample_governance())
    _write(root / READINESS_PATH, _sample_readiness())
    _write(root / HANDOFF_PATH, _sample_handoff())
    _write(root / SHARED_GAP_PATH, _sample_shared_gap())
    _write(root / PARITY_SURVEY_PATH, _sample_parity_survey())
    _write(root / VALIDATOR_PATH, "#!/usr/bin/env python3\n")
    _write(root / BUILD_PATH, 'const std = @import("std");\n')
    _write(root / MAKEFILE_PATH, "phase14-validate:\n\t@true\n")
    _write(root / RCU_SURVEY_PATH, _sample_rcu_survey())
    _write(root / SKBUFF_SURVEY_PATH, _sample_skbuff_survey())
    _write(root / TRACEABILITY_PATH, _sample_traceability())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_deep_core_blocker_survey_") as tmp_dir:
        root = Path(tmp_dir)

        baseline = root / "baseline"
        _seed_repo(baseline)
        failures = collect_failures(baseline)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_marker_root = root / "missing_marker"
        _seed_repo(missing_marker_root)
        _write(
            missing_marker_root / SURVEY_PATH,
            _sample_survey().replace(
                "- `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_marker_root)
        expected = [
            "survey:missing_marker:`zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")
        case_count += 1

        forbidden_marker_root = root / "forbidden_marker"
        _seed_repo(forbidden_marker_root)
        _write(
            forbidden_marker_root / SURVEY_PATH,
            _sample_survey() + "- `zigux/tests/phase15_build.zig` is now directly materialized\n",
        )
        failures = collect_failures(forbidden_marker_root)
        expected = [
            "survey:forbidden_marker:`zigux/tests/phase15_build.zig` is now directly materialized"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected forbidden-marker failure: {failures}")
        case_count += 1

        missing_path_root = root / "missing_path"
        _seed_repo(missing_path_root)
        (missing_path_root / HANDOFF_PATH).unlink()
        failures = collect_failures(missing_path_root)
        expected = [f"missing_required_path:{HANDOFF_PATH}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-path failure: {failures}")
        case_count += 1

        rcu_root = root / "rcu"
        _seed_repo(rcu_root)
        _write(rcu_root / RCU_SURVEY_PATH, "# Phase 14 RCU Tree Survey\n")
        failures = collect_failures(rcu_root)
        expected = ["rcu_survey:missing_blocker_marker"]
        if failures != expected:
            raise AssertionError(f"unexpected rcu failure: {failures}")
        case_count += 1

        make_root = root / "make"
        _seed_repo(make_root)
        _write(make_root / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(make_root)
        expected = ["makefile:unexpected_phase15_validate_target"]
        if failures != expected:
            raise AssertionError(f"unexpected make-target failure: {failures}")
        case_count += 1

    print("PHASE15_DEEP_CORE_BLOCKER_SURVEY_SELF_TEST=pass")
    print(f"PHASE15_DEEP_CORE_BLOCKER_SURVEY_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 deep-core blocker survey stays aligned with its current owner packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run the synthetic self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_DEEP_CORE_BLOCKER_SURVEY=pass")
    print(f"PHASE15_DEEP_CORE_BLOCKER_SURVEY_ANCHOR_COUNT={len(EXPECTED_ANCHORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
