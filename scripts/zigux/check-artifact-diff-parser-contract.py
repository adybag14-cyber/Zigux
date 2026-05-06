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
    "cli_missing_required_args",
    "cli_missing_actual_operand",
    "cli_invalid_mode",
]

EXPECTED_SELF_TEST_CASES = [
    "catalog_shape",
    "summary_round_trip",
    "summary_status_drift",
    "summary_count_drift",
    "summary_duplicate_case_drift",
    "summary_case_order_drift",
]


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
        f"ARTIFACT_DIFF_PARSER_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}",
        "ARTIFACT_DIFF_PARSER_CONTRACT_CASES=" + ",".join(EXPECTED_CONTRACT_CASES),
    ]


def extract_output_value(lines: list[str], prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :]
    raise AssertionError(f"missing output line with prefix {prefix!r}: {lines}")


def assert_summary_output(lines: list[str]) -> None:
    if extract_output_value(lines, "ARTIFACT_DIFF_PARSER_CONTRACT=") != "pass":
        raise AssertionError(f"unexpected parser-contract status: {lines}")

    count_text = extract_output_value(lines, "ARTIFACT_DIFF_PARSER_CONTRACT_CASE_COUNT=")
    try:
        expected_count = int(count_text)
    except ValueError as exc:
        raise AssertionError(f"invalid case count {count_text!r}") from exc

    cases_text = extract_output_value(lines, "ARTIFACT_DIFF_PARSER_CONTRACT_CASES=")
    cases = [] if not cases_text else cases_text.split(",")
    if len(cases) != expected_count:
        raise AssertionError(f"count/list drift: count={expected_count} cases={cases}")
    if len(set(cases)) != len(cases):
        raise AssertionError(f"duplicate parser-contract cases: {cases}")
    if cases != EXPECTED_CONTRACT_CASES:
        raise AssertionError(
            "parser-contract catalog drifted: "
            f"expected {EXPECTED_CONTRACT_CASES}, got {cases}"
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
    if len(set(EXPECTED_SELF_TEST_CASES)) != len(EXPECTED_SELF_TEST_CASES):
        raise AssertionError(
            f"parser-contract self-test cases must stay unique: {EXPECTED_SELF_TEST_CASES}"
        )

    covered_cases: list[str] = []
    covered_cases.append("catalog_shape")

    assert_summary_output(expected_summary_lines())
    covered_cases.append("summary_round_trip")

    bad_status_lines = expected_summary_lines()
    bad_status_lines[0] = "ARTIFACT_DIFF_PARSER_CONTRACT=fail"
    expect_assertion("summary_status_drift", lambda: assert_summary_output(bad_status_lines))
    covered_cases.append("summary_status_drift")

    bad_count_lines = expected_summary_lines()
    bad_count_lines[1] = "ARTIFACT_DIFF_PARSER_CONTRACT_CASE_COUNT=2"
    expect_assertion("summary_count_drift", lambda: assert_summary_output(bad_count_lines))
    covered_cases.append("summary_count_drift")

    bad_duplicate_lines = expected_summary_lines()
    bad_duplicate_lines[2] = (
        "ARTIFACT_DIFF_PARSER_CONTRACT_CASES="
        "cli_missing_required_args,cli_missing_required_args,cli_invalid_mode"
    )
    expect_assertion(
        "summary_duplicate_case_drift", lambda: assert_summary_output(bad_duplicate_lines)
    )
    covered_cases.append("summary_duplicate_case_drift")

    bad_order_lines = expected_summary_lines()
    bad_order_lines[2] = (
        "ARTIFACT_DIFF_PARSER_CONTRACT_CASES="
        "cli_invalid_mode,cli_missing_actual_operand,cli_missing_required_args"
    )
    expect_assertion("summary_case_order_drift", lambda: assert_summary_output(bad_order_lines))
    covered_cases.append("summary_case_order_drift")

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
        description="Check deterministic stderr-only parser failure paths for artifact_diff.py."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated summary-shape checks without replaying the live parser errors.",
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
