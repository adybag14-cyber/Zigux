#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
VALIDATOR_PATH = "scripts/zigux/validate-phase14.py"
MAKEFILE_PATH = "zigux/Makefile"

ROLLBACK_AND_GUARDRAIL_CHECKERS = [
    "ROLLBACK_THRESHOLD_SEQUENCING_CHECKER_PATH",
    "SKBUFF_STAY_IN_C_GUARDRAIL_CHECKER_PATH",
    "SKBUFF_COMPILE_ROUTE_CHECKER_PATH",
    "RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH",
    "RCU_COMPILE_ROUTE_CHECKER_PATH",
    "RCU_ROLLBACK_GUARDRAIL_CHECKER_PATH",
]

MAKEFILE_DIRECT_ROLLBACK_GUARDRAILS = [
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test",
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py --self-test",
    "scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py",
    "scripts/zigux/check-phase14-rcu-rollback-guardrail.py --self-test",
    "scripts/zigux/check-phase14-rcu-rollback-guardrail.py",
]

VALIDATOR_REQUIRED_MARKERS = [
    "SUBCHECKER_PATHS = [",
    "run_guardrail_checker(base, rel_path, self_test=True)",
    "run_guardrail_checker(\n                    args.root,",
    "self_test=False",
    "dedicated rollback-threshold sequencing checker",
    "dedicated skbuff stay-in-C",
    "dedicated RCU rollback guardrail",
    "PHASE14_VALIDATOR_SELF_TEST=pass",
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / VALIDATOR_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    validator = root / VALIDATOR_PATH
    if not validator.exists():
        return [f"missing_file:{VALIDATOR_PATH}"]

    text = read_text(validator)
    failures: list[str] = []
    for marker in VALIDATOR_REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing_validator_marker:{marker}")

    for checker_name in ROLLBACK_AND_GUARDRAIL_CHECKERS:
        if checker_name not in text:
            failures.append(f"missing_guardrail_checker_constant:{checker_name}")
            continue
        subchecker_entry = f"    {checker_name},"
        if subchecker_entry not in text:
            failures.append(f"missing_subchecker_entry:{checker_name}")
        required_marker_lookup = f"REQUIRED_MARKERS[{checker_name}]"
        if required_marker_lookup not in text:
            failures.append(f"missing_required_marker_lookup:{checker_name}")

    makefile = root / MAKEFILE_PATH
    if not makefile.exists():
        failures.append(f"missing_file:{MAKEFILE_PATH}")
    else:
        makefile_text = read_text(makefile)
        for marker in MAKEFILE_DIRECT_ROLLBACK_GUARDRAILS:
            if marker not in makefile_text:
                failures.append(f"missing_makefile_rollback_guardrail:{marker}")

    return failures


def write_fixture(root: Path, text: str) -> None:
    target = root / VALIDATOR_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def write_makefile_fixture(root: Path, text: str | None = None) -> None:
    target = root / MAKEFILE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    body = text if text is not None else "\n".join(MAKEFILE_DIRECT_ROLLBACK_GUARDRAILS) + "\n"
    target.write_text(body, encoding="utf-8")


def fixture_validator() -> str:
    checker_block = "\n".join(f"    {name}," for name in ROLLBACK_AND_GUARDRAIL_CHECKERS)
    marker_lookups = "\n".join(
        f"    REQUIRED_MARKERS[{name}][0]," for name in ROLLBACK_AND_GUARDRAIL_CHECKERS
    )
    return f"""SUBCHECKER_PATHS = [
{checker_block}
]

MARKER_CASES = [
{marker_lookups}
]

def run_self_test():
    for rel_path in SUBCHECKER_PATHS:
        run_guardrail_checker(base, rel_path, self_test=True)
    print("PHASE14_VALIDATOR_SELF_TEST=pass")

def main():
    for rel_path in SUBCHECKER_PATHS:
        run_guardrail_checker(
                    args.root,
                    rel_path,
                    self_test=False,
                )

description = "dedicated rollback-threshold sequencing checker, dedicated skbuff stay-in-C guardrail, dedicated RCU rollback guardrail"
"""


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-guardrail-coverage-"))
    try:
        write_fixture(base, fixture_validator())
        write_makefile_fixture(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture should pass but failed: {failures!r}")

        for checker_name in ROLLBACK_AND_GUARDRAIL_CHECKERS:
            write_fixture(base, fixture_validator().replace(f"    {checker_name},\n", "", 1))
            write_makefile_fixture(base)
            expected = f"missing_subchecker_entry:{checker_name}"
            failures = validate(base)
            if expected not in failures:
                raise SystemExit(f"expected {expected!r}, got {failures!r}")

        for marker in MAKEFILE_DIRECT_ROLLBACK_GUARDRAILS:
            write_fixture(base, fixture_validator())
            write_makefile_fixture(base, "\n".join(
                candidate for candidate in MAKEFILE_DIRECT_ROLLBACK_GUARDRAILS if candidate != marker
            ) + "\n")
            expected = f"missing_makefile_rollback_guardrail:{marker}"
            failures = validate(base)
            if expected not in failures:
                raise SystemExit(f"expected {expected!r}, got {failures!r}")

        write_fixture(base, fixture_validator().replace("self_test=False", "", 1))
        write_makefile_fixture(base)
        failures = validate(base)
        if "missing_validator_marker:self_test=False" not in failures:
            raise SystemExit(f"expected self_test=False marker failure, got {failures!r}")

        empty = Path(tempfile.mkdtemp(prefix="phase14-guardrail-coverage-missing-"))
        try:
            failures = validate(empty)
            if failures != [f"missing_file:{VALIDATOR_PATH}"]:
                raise SystemExit(f"expected missing validator failure, got {failures!r}")
        finally:
            shutil.rmtree(empty, ignore_errors=True)

        missing_makefile = Path(tempfile.mkdtemp(prefix="phase14-guardrail-coverage-missing-makefile-"))
        try:
            write_fixture(missing_makefile, fixture_validator())
            failures = validate(missing_makefile)
            if f"missing_file:{MAKEFILE_PATH}" not in failures:
                raise SystemExit(f"expected missing Makefile failure, got {failures!r}")
        finally:
            shutil.rmtree(missing_makefile, ignore_errors=True)

        print("PHASE14_ROLLBACK_GUARDRAIL_COVERAGE_SELF_TEST=pass")
        print(
            "PHASE14_ROLLBACK_GUARDRAIL_COVERAGE_SELF_TEST_CASE_COUNT="
            f"{len(ROLLBACK_AND_GUARDRAIL_CHECKERS) + len(MAKEFILE_DIRECT_ROLLBACK_GUARDRAILS) + 3}"
        )
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 14 validator still runs the rollback-threshold and "
            "guardrail subcheckers in both fixture-backed self-test and live validation modes, "
            "and that the returned Makefile route still directly replays the rollback "
            "threshold plus skbuff/RCU rollback guardrails."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run the fixture-backed self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE14_ROLLBACK_GUARDRAIL_COVERAGE=fail")
        print("PHASE14_ROLLBACK_GUARDRAIL_COVERAGE_DRIFT_START")
        for failure in failures:
            print(failure)
        print("PHASE14_ROLLBACK_GUARDRAIL_COVERAGE_DRIFT_END")
        return 1

    print("PHASE14_ROLLBACK_GUARDRAIL_COVERAGE=pass")
    print(f"PHASE14_ROLLBACK_GUARDRAIL_COVERAGE_CHECKER_COUNT={len(ROLLBACK_AND_GUARDRAIL_CHECKERS)}")
    print(f"PHASE14_ROLLBACK_GUARDRAIL_COVERAGE_MARKER_COUNT={len(VALIDATOR_REQUIRED_MARKERS)}")
    print(f"PHASE14_ROLLBACK_GUARDRAIL_COVERAGE_MAKEFILE_ROUTE_COUNT={len(MAKEFILE_DIRECT_ROLLBACK_GUARDRAILS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())