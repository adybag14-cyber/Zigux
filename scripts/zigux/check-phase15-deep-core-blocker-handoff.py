#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase15-deep-core-blocker-survey.md")
HANDOFF_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SEQUENCING_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
RCU_SURVEY_PATH = Path("Documentation/zigux/phase14-rcu-tree-survey.md")
SKBUFF_SURVEY_PATH = Path("Documentation/zigux/phase14-skbuff-bridge-survey.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_FILES = (
    SURVEY_PATH,
    HANDOFF_PATH,
    SEQUENCING_PATH,
    FREEZE_MAP_PATH,
    RCU_SURVEY_PATH,
    SKBUFF_SURVEY_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
)

SURVEY_MARKERS = (
    "PHASE15_STATUS=deep_core_blocker_survey_landed",
    "PHASE15_LANE_KEY=P15-L01",
    "`kernel/sched/core.c`",
    "`mm/page_alloc.c`",
    "`kernel/rcu/tree.c`",
    "`net/core/skbuff.c`",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`scripts/zigux/validate-phase15.py`",
    "`Documentation/zigux/phase14-rcu-tree-survey.md`",
    "`Documentation/zigux/phase14-skbuff-bridge-survey.md`",
    "`zigux/tests/phase15_build.zig` is still not directly materialized on current `master`",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
)

HANDOFF_MARKERS = (
    "`Documentation/zigux/phase15-deep-core-blocker-survey.md`",
    "The dedicated deep-core blocker survey `Documentation/zigux/phase15-deep-core-blocker-survey.md` is also directly materialized on current `master`",
    "keep the landed `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`",
)

SEQUENCING_MARKERS = (
    "`Documentation/zigux/phase15-deep-core-blocker-survey.md` owns the dedicated roadmap-versus-current-master crosswalk",
    "`Documentation/zigux/phase15-deep-core-blocker-survey.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`scripts/zigux/validate-phase15.py`",
)

VALIDATOR_MARKERS = (
    '"Documentation/zigux/phase15-deep-core-blocker-survey.md"',
    '"Documentation/zigux/phase15-governance-lane-sequencing.md"',
    '"Documentation/zigux/phase15-handoff-next-steps-survey.md"',
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase15-validate:",
    "phase15-test:",
    "\nphase15:",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    survey = _read(root / SURVEY_PATH)
    handoff = _read(root / HANDOFF_PATH)
    sequencing = _read(root / SEQUENCING_PATH)
    validator = _read(root / VALIDATOR_PATH)
    makefile = _read(root / MAKEFILE_PATH)

    for marker in SURVEY_MARKERS:
        if marker not in survey:
            failures.append(f"survey:missing:{marker}")
    for marker in HANDOFF_MARKERS:
        if marker not in handoff:
            failures.append(f"handoff:missing:{marker}")
    for marker in SEQUENCING_MARKERS:
        if marker not in sequencing:
            failures.append(f"sequencing:missing:{marker}")
    for marker in VALIDATOR_MARKERS:
        if marker not in validator:
            failures.append(f"validator:missing:{marker}")
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        if marker in makefile:
            failures.append(f"makefile:unexpected_phase15_route:{marker}")

    return failures


def write_sample_root(root: Path) -> None:
    _write(
        root / SURVEY_PATH,
        """# Phase 15 Deep-Core Blocker Survey

- PHASE15_STATUS=deep_core_blocker_survey_landed
- PHASE15_LANE_KEY=P15-L01
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `scripts/zigux/validate-phase15.py`
- `Documentation/zigux/phase14-rcu-tree-survey.md`
- `Documentation/zigux/phase14-skbuff-bridge-survey.md`
- `zigux/tests/phase15_build.zig` is still not directly materialized on current `master`
- no Architecture Council approval is currently recorded for a freeze-map status change
""",
    )
    _write(
        root / HANDOFF_PATH,
        """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/phase15-deep-core-blocker-survey.md`
- The dedicated deep-core blocker survey `Documentation/zigux/phase15-deep-core-blocker-survey.md` is also directly materialized on current `master`
- keep the landed `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`
""",
    )
    _write(
        root / SEQUENCING_PATH,
        """# Phase 15 Governance Lane Sequencing

- `Documentation/zigux/phase15-deep-core-blocker-survey.md` owns the dedicated roadmap-versus-current-master crosswalk
- `Documentation/zigux/phase15-deep-core-blocker-survey.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `scripts/zigux/validate-phase15.py`
""",
    )
    _write(root / FREEZE_MAP_PATH, "# freeze map\n")
    _write(root / RCU_SURVEY_PATH, "# rcu survey\n")
    _write(root / SKBUFF_SURVEY_PATH, "# skbuff survey\n")
    _write(
        root / VALIDATOR_PATH,
        """#!/usr/bin/env python3
EXPECTED_DIRECT_PACKET_PATHS = [
    \"Documentation/zigux/phase15-deep-core-blocker-survey.md\",
    \"Documentation/zigux/phase15-governance-lane-sequencing.md\",
    \"Documentation/zigux/phase15-handoff-next-steps-survey.md\",
]
""",
    )
    _write(root / MAKEFILE_PATH, "phase2-validate:\n\t@true\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_deep_core_blocker_handoff_") as tmp_dir:
        root = Path(tmp_dir)

        baseline = root / "baseline"
        write_sample_root(baseline)
        failures = collect_failures(baseline)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        survey_root = root / "survey"
        write_sample_root(survey_root)
        _write(
            survey_root / SURVEY_PATH,
            _read(survey_root / SURVEY_PATH).replace(
                "`Documentation/zigux/phase15-handoff-next-steps-survey.md`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(survey_root)
        expected = [
            "survey:missing:`Documentation/zigux/phase15-handoff-next-steps-survey.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected survey failure: {failures}")
        case_count += 1

        handoff_root = root / "handoff"
        write_sample_root(handoff_root)
        _write(
            handoff_root / HANDOFF_PATH,
            _read(handoff_root / HANDOFF_PATH).replace(
                "The dedicated deep-core blocker survey `Documentation/zigux/phase15-deep-core-blocker-survey.md` is also directly materialized on current `master`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(handoff_root)
        expected = [
            "handoff:missing:The dedicated deep-core blocker survey `Documentation/zigux/phase15-deep-core-blocker-survey.md` is also directly materialized on current `master`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected handoff failure: {failures}")
        case_count += 1

        sequencing_root = root / "sequencing"
        write_sample_root(sequencing_root)
        _write(
            sequencing_root / SEQUENCING_PATH,
            _read(sequencing_root / SEQUENCING_PATH).replace(
                "`scripts/zigux/validate-phase15.py`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(sequencing_root)
        expected = ["sequencing:missing:`scripts/zigux/validate-phase15.py`"]
        if failures != expected:
            raise AssertionError(f"unexpected sequencing failure: {failures}")
        case_count += 1

        validator_root = root / "validator"
        write_sample_root(validator_root)
        _write(
            validator_root / VALIDATOR_PATH,
            _read(validator_root / VALIDATOR_PATH).replace(
                '    \"Documentation/zigux/phase15-deep-core-blocker-survey.md\",\n',
                "",
                1,
            ),
        )
        failures = collect_failures(validator_root)
        expected = [
            'validator:missing:"Documentation/zigux/phase15-deep-core-blocker-survey.md"'
        ]
        if failures != expected:
            raise AssertionError(f"unexpected validator failure: {failures}")
        case_count += 1

        makefile_root = root / "makefile"
        write_sample_root(makefile_root)
        _write(makefile_root / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(makefile_root)
        expected = ["makefile:unexpected_phase15_route:phase15-validate:"]
        if failures != expected:
            raise AssertionError(f"unexpected makefile failure: {failures}")
        case_count += 1

    print("PHASE15_DEEP_CORE_BLOCKER_HANDOFF_SELF_TEST=pass")
    print(f"PHASE15_DEEP_CORE_BLOCKER_HANDOFF_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 deep-core blocker handoff packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run synthetic self-test coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like sample root for manual checker replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE15_DEEP_CORE_BLOCKER_HANDOFF_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        print("PHASE15_DEEP_CORE_BLOCKER_HANDOFF=fail")
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_DEEP_CORE_BLOCKER_HANDOFF=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
