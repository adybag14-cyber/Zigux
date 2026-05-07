#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"

EXPECTED_CONTRACT_CASES = [
    "cli_help",
    "cli_help_repeat",
    "cli_missing_required_args",
    "cli_missing_actual_operand",
    "cli_invalid_mode",
]
REPEAT_CONTRACT_CASES = [
    "cli_help_repeat",
]
BASE_CONTRACT_CASES = [
    case for case in EXPECTED_CONTRACT_CASES if case not in REPEAT_CONTRACT_CASES
]

EXPECTED_SELF_TEST_CASES = [
    "catalog_shape",
    "summary_round_trip",
    "base_summary_round_trip",
    "repeat_summary_round_trip",
    "summary_status_drift",
    "summary_count_drift",
    "summary_duplicate_case_drift",
    "summary_case_order_drift",
    "base_summary_count_drift",
    "base_summary_case_order_drift",
    "repeat_summary_count_drift",
    "repeat_summary_case_order_drift",
]


def run_contract_case(
    args: list[str],
    expected_exit: int,
    expected_stdout_lines: list[str],
    *,
    expected_stderr_lines: list[str] | None = None,
    repeat_count: int = 1,
) -> None:
    if repeat_count < 1:
        raise ValueError(f"repeat_count must be positive, got {repeat_count}")

    for attempt in range(1, repeat_count + 1):
        completed = subprocess.run(
            [sys.executable, str(ARTIFACT_DIFF), *args],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        stdout_lines = completed.stdout.splitlines()
        stderr_lines = completed.stderr.splitlines()
        if completed.returncode != expected_exit:
            raise AssertionError(
                f"attempt {attempt}: expected exit {expected_exit}, got {completed.returncode}: "
                f"stdout={stdout_lines} stderr={stderr_lines}"
            )
        if stdout_lines != expected_stdout_lines:
            raise AssertionError(f"attempt {attempt}: unexpected stdout lines: {stdout_lines}")
        if expected_stderr_lines is not None and stderr_lines != expected_stderr_lines:
            raise AssertionError(
                f"attempt {attempt}: unexpected stderr lines: expected {expected_stderr_lines}, got {stderr_lines}"
            )


def run_error_contract_case(
    args: list[str],
    expected_exit: int,
    expected_stdout_lines: list[str],
    *,
    expected_stderr_normalized: str,
    repeat_count: int = 1,
) -> None:
    if repeat_count < 1:
        raise ValueError(f"repeat_count must be positive, got {repeat_count}")

    for attempt in range(1, repeat_count + 1):
        completed = subprocess.run(
            [sys.executable, str(ARTIFACT_DIFF), *args],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        stdout_lines = completed.stdout.splitlines()
        stderr_lines = completed.stderr.splitlines()
        normalized_stderr = " ".join(completed.stderr.split())
        if completed.returncode != expected_exit:
            raise AssertionError(
                f"attempt {attempt}: expected exit {expected_exit}, got {completed.returncode}: "
                f"stdout={stdout_lines} stderr={stderr_lines}"
            )
        if stdout_lines != expected_stdout_lines:
            raise AssertionError(f"attempt {attempt}: unexpected stdout lines: {stdout_lines}")
        if not stderr_lines:
            raise AssertionError(f"attempt {attempt}: expected parser stderr output, got none")
        if normalized_stderr != expected_stderr_normalized:
            raise AssertionError(
                f"attempt {attempt}: unexpected normalized parser stderr: "
                f"expected {expected_stderr_normalized!r}, got {normalized_stderr!r}"
            )


def expected_summary_lines() -> list[str]:
    return [
        "ARTIFACT_DIFF_PARSER_CONTRACT=pass",
        f"ARTIFACT_DIFF_PARSER_CONTRACT_BASE_CASE_COUNT={len(BASE_CONTRACT_CASES)}",
        "ARTIFACT_DIFF_PARSER_CONTRACT_BASE_CASES=" + ",".join(BASE_CONTRACT_CASES),
        f"ARTIFACT_DIFF_PARSER_CONTRACT_REPEAT_CASE_COUNT={len(REPEAT_CONTRACT_CASES)}",
        "ARTIFACT_DIFF_PARSER_CONTRACT_REPEAT_CASES=" + ",".join(REPEAT_CONTRACT_CASES),
        f"ARTIFACT_DIFF_PARSER_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}",
        "ARTIFACT_DIFF_PARSER_CONTRACT_CASES=" + ",".join(EXPECTED_CONTRACT_CASES),
    ]


def extract_output_value(lines: list[str], prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :]
    raise AssertionError(f"missing output line with prefix {prefix!r}: {lines}")


def parse_case_catalog(lines: list[str], count_prefix: str, cases_prefix: str) -> list[str]:
    count_text = extract_output_value(lines, count_prefix)
    try:
        expected_count = int(count_text)
    except ValueError as exc:
        raise AssertionError(f"invalid case count {count_text!r}") from exc

    cases_text = extract_output_value(lines, cases_prefix)
    cases = [] if not cases_text else cases_text.split(",")
    if len(cases) != expected_count:
        raise AssertionError(f"count/list drift: count={expected_count} cases={cases}")
    if len(set(cases)) != len(cases):
        raise AssertionError(f"duplicate parser-contract cases: {cases}")
    return cases


def assert_summary_output(lines: list[str]) -> None:
    if extract_output_value(lines, "ARTIFACT_DIFF_PARSER_CONTRACT=") != "pass":
        raise AssertionError(f"unexpected parser-contract status: {lines}")

    base_cases = parse_case_catalog(
        lines,
        "ARTIFACT_DIFF_PARSER_CONTRACT_BASE_CASE_COUNT=",
        "ARTIFACT_DIFF_PARSER_CONTRACT_BASE_CASES=",
    )
    if base_cases != BASE_CONTRACT_CASES:
        raise AssertionError(
            "parser-contract base catalog drifted: "
            f"expected {BASE_CONTRACT_CASES}, got {base_cases}"
        )

    repeat_cases = parse_case_catalog(
        lines,
        "ARTIFACT_DIFF_PARSER_CONTRACT_REPEAT_CASE_COUNT=",
        "ARTIFACT_DIFF_PARSER_CONTRACT_REPEAT_CASES=",
    )
    if repeat_cases != REPEAT_CONTRACT_CASES:
        raise AssertionError(
            "parser-contract repeat catalog drifted: "
            f"expected {REPEAT_CONTRACT_CASES}, got {repeat_cases}"
        )

    all_cases = parse_case_catalog(
        lines,
        "ARTIFACT_DIFF_PARSER_CONTRACT_CASE_COUNT=",
        "ARTIFACT_DIFF_PARSER_CONTRACT_CASES=",
    )
    if all_cases != EXPECTED_CONTRACT_CASES:
        raise AssertionError(
            "parser-contract catalog drifted: "
            f"expected {EXPECTED_CONTRACT_CASES}, got {all_cases}"
        )


def expect_assertion(label: str, callback) -> None:
    try:
        callback()
    except AssertionError:
        return
    raise AssertionError(f"expected AssertionError for self-test case {label}")


def run_self_test() -> int:
    if len(set(EXPECTED_CONTRACT_CASES)) != len(EXPECTED_CONTRACT_CASES):
        raise AssertionError(
            f"parser-contract cases must stay unique: {EXPECTED_CONTRACT_CASES}"
        )
    if len(set(REPEAT_CONTRACT_CASES)) != len(REPEAT_CONTRACT_CASES):
        raise AssertionError(
            f"parser-contract repeat cases must stay unique: {REPEAT_CONTRACT_CASES}"
        )
    if len(BASE_CONTRACT_CASES) + len(REPEAT_CONTRACT_CASES) != len(
        EXPECTED_CONTRACT_CASES
    ):
        raise AssertionError(
            "parser-contract base and repeat partitions drifted: "
            f"base={BASE_CONTRACT_CASES} repeat={REPEAT_CONTRACT_CASES} "
            f"all={EXPECTED_CONTRACT_CASES}"
        )
    if len(set(EXPECTED_SELF_TEST_CASES)) != len(EXPECTED_SELF_TEST_CASES):
        raise AssertionError(
            f"parser-contract self-test cases must stay unique: {EXPECTED_SELF_TEST_CASES}"
        )

    covered_cases: list[str] = []
    covered_cases.append("catalog_shape")

    assert_summary_output(expected_summary_lines())
    covered_cases.append("summary_round_trip")
    covered_cases.append("base_summary_round_trip")
    covered_cases.append("repeat_summary_round_trip")

    bad_status_lines = expected_summary_lines()
    bad_status_lines[0] = "ARTIFACT_DIFF_PARSER_CONTRACT=fail"
    expect_assertion("summary_status_drift", lambda: assert_summary_output(bad_status_lines))
    covered_cases.append("summary_status_drift")

    bad_count_lines = expected_summary_lines()
    bad_count_lines[5] = "ARTIFACT_DIFF_PARSER_CONTRACT_CASE_COUNT=4"
    expect_assertion("summary_count_drift", lambda: assert_summary_output(bad_count_lines))
    covered_cases.append("summary_count_drift")

    bad_duplicate_lines = expected_summary_lines()
    bad_duplicate_lines[6] = (
        "ARTIFACT_DIFF_PARSER_CONTRACT_CASES="
        "cli_help,cli_help,cli_missing_required_args,cli_missing_actual_operand,cli_invalid_mode"
    )
    expect_assertion(
        "summary_duplicate_case_drift", lambda: assert_summary_output(bad_duplicate_lines)
    )
    covered_cases.append("summary_duplicate_case_drift")

    bad_order_lines = expected_summary_lines()
    bad_order_lines[6] = (
        "ARTIFACT_DIFF_PARSER_CONTRACT_CASES="
        "cli_invalid_mode,cli_help,cli_help_repeat,cli_missing_required_args,cli_missing_actual_operand"
    )
    expect_assertion("summary_case_order_drift", lambda: assert_summary_output(bad_order_lines))
    covered_cases.append("summary_case_order_drift")

    bad_base_count_lines = expected_summary_lines()
    bad_base_count_lines[1] = "ARTIFACT_DIFF_PARSER_CONTRACT_BASE_CASE_COUNT=3"
    expect_assertion(
        "base_summary_count_drift", lambda: assert_summary_output(bad_base_count_lines)
    )
    covered_cases.append("base_summary_count_drift")

    bad_base_case_order_lines = expected_summary_lines()
    bad_base_case_order_lines[2] = (
        "ARTIFACT_DIFF_PARSER_CONTRACT_BASE_CASES="
        "cli_missing_required_args,cli_help,cli_missing_actual_operand,cli_invalid_mode"
    )
    expect_assertion(
        "base_summary_case_order_drift",
        lambda: assert_summary_output(bad_base_case_order_lines),
    )
    covered_cases.append("base_summary_case_order_drift")

    bad_repeat_count_lines = expected_summary_lines()
    bad_repeat_count_lines[3] = "ARTIFACT_DIFF_PARSER_CONTRACT_REPEAT_CASE_COUNT=2"
    expect_assertion(
        "repeat_summary_count_drift", lambda: assert_summary_output(bad_repeat_count_lines)
    )
    covered_cases.append("repeat_summary_count_drift")

    bad_repeat_case_order_lines = expected_summary_lines()
    bad_repeat_case_order_lines[4] = (
        "ARTIFACT_DIFF_PARSER_CONTRACT_REPEAT_CASES=cli_missing_actual_operand"
    )
    expect_assertion(
        "repeat_summary_case_order_drift",
        lambda: assert_summary_output(bad_repeat_case_order_lines),
    )
    covered_cases.append("repeat_summary_case_order_drift")

    if covered_cases != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(
            "parser-contract self-test case catalog drifted: "
            f"expected {EXPECTED_SELF_TEST_CASES}, got {covered_cases}"
        )

    print("ARTIFACT_DIFF_PARSER_CONTRACT_SELF_TEST=pass")
    print(f"ARTIFACT_DIFF_PARSER_CONTRACT_SELF_TEST_CASE_COUNT={len(EXPECTED_SELF_TEST_CASES)}")
    print("ARTIFACT_DIFF_PARSER_CONTRACT_SELF_TEST_CASES=" + ",".join(EXPECTED_SELF_TEST_CASES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check deterministic parser-owned CLI surfaces for artifact_diff.py."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated summary-shape checks without replaying the live parser surfaces.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    run_self_test()

    with tempfile.TemporaryDirectory(prefix="zigux_artifact_diff_parser_contract_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        expected = tmp_dir / "expected.txt"
        actual = tmp_dir / "actual.txt"
        expected.write_text("alpha\n", encoding="utf-8", newline="\n")
        actual.write_text("alpha\n", encoding="utf-8", newline="\n")

        run_contract_case(
            ["-h"],
            0,
            [
                "usage: artifact_diff.py [-h] [--mode {text,json,sha256}] [--self-test]",
                "                        [expected] [actual]",
                "",
                "Compare two artifacts in a stable mode.",
                "",
                "positional arguments:",
                "  expected",
                "  actual",
                "",
                "options:",
                "  -h, --help            show this help message and exit",
                "  --mode {text,json,sha256}",
                "  --self-test           Run built-in deterministic comparison checks.",
            ],
            expected_stderr_lines=[],
            repeat_count=2,
        )

        run_error_contract_case(
            [],
            2,
            [],
            expected_stderr_normalized=(
                "usage: artifact_diff.py [-h] [--mode {text,json,sha256}] [--self-test] "
                "[expected] [actual] artifact_diff.py: error: --mode, expected, and actual are "
                "required unless --self-test is set"
            ),
            repeat_count=2,
        )

        run_error_contract_case(
            ["--mode", "text", str(expected)],
            2,
            [],
            expected_stderr_normalized=(
                "usage: artifact_diff.py [-h] [--mode {text,json,sha256}] [--self-test] "
                "[expected] [actual] artifact_diff.py: error: --mode, expected, and actual are "
                "required unless --self-test is set"
            ),
            repeat_count=2,
        )

        run_error_contract_case(
            ["--mode", "yaml", str(expected), str(actual)],
            2,
            [],
            expected_stderr_normalized=(
                "usage: artifact_diff.py [-h] [--mode {text,json,sha256}] [--self-test] "
                "[expected] [actual] artifact_diff.py: error: argument --mode: invalid choice: "
                "'yaml' (choose from text, json, sha256)"
            ),
            repeat_count=2,
        )

    for line in expected_summary_lines():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
