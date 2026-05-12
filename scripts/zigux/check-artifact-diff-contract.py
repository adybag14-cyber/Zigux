#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"
ARTIFACT_DIFF_NOTE = ROOT / "Documentation" / "zigux" / "artifact-diff.md"

EXPECTED_CONTRACT_CASES = [
    "helper_self_test",
    "helper_self_test_repeat",
    "cli_help_output",
    "cli_help_output_repeat",
    "cli_missing_required_args",
    "cli_missing_actual_operand",
    "cli_invalid_mode",
    "text_pass",
    "text_pass_repeat",
    "text_mismatch",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "json_pass",
    "json_mismatch",
    "json_mismatch_repeat",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "sha256_pass",
    "sha256_missing_expected",
    "sha256_missing_actual",
    "sha256_missing_both",
    "sha256_drift",
    "sha256_drift_repeat",
]
REPEAT_CONTRACT_CASES = [
    "helper_self_test_repeat",
    "cli_help_output_repeat",
    "text_pass_repeat",
    "json_mismatch_repeat",
    "sha256_drift_repeat",
]
BASE_CONTRACT_CASES = [
    case for case in EXPECTED_CONTRACT_CASES if case not in REPEAT_CONTRACT_CASES
]
REQUIRED_REVIEW_NOTE_MARKERS = [
    "- owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`",
    "- rollback owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`",
    "- fallback rule: if `scripts/zigux/artifact_diff.py` regresses, keep the committed expected artifact plus the current authoritative C or documented replay command as the source of truth until the helper contract is repaired",
    "- review rule: any change to the helper's emitted `ARTIFACT_DIFF=*`, `MODE=*`, `EXPECTED=*`, `ACTUAL=*`, `SHA256=*`, `EXPECTED_EXISTS=*`, `ACTUAL_EXISTS=*`, `EXPECTED_JSON_ERROR=*`, or `ACTUAL_JSON_ERROR=*` lines must update this note in the same change so the published host-side artifact packet stays reviewable",
    "- deterministic replay entrypoint: `python3 scripts/zigux/check-artifact-diff-contract.py` is the reviewable contract rerun for the shared host-side helper and should stay aligned with the outward line rules below",
    "- deterministic survey entrypoint: `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py` must keep the helper self-test catalog, the contract summary catalog, and the repeat-case packet aligned with this note and the shared validator packet",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_JSON_INVALID` must prove malformed JSON fails without inventing digest or exists markers",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_MISSING` must prove missing-path failures emit only the EXISTS markers",
    "- deterministic checker catalog: `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_BASE_CASES`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES`, `ARTIFACT_DIFF_CONTRACT_CASE_COUNT`, and `ARTIFACT_DIFF_CONTRACT_CASES` must stay aligned with the published contract replay packet",
    "- deterministic checker self-test catalog: `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES` must stay aligned with the isolated stale-catalog and review-note drift coverage",
]

EXPECTED_SELF_TEST_CASES = [
    "catalog_shape",
    "review_note_marker_round_trip",
    "review_note_owner_marker_drift",
    "review_note_marker_drift",
    "cli_help_round_trip",
    "cli_help_line_drift",
    "cli_missing_argument_parser_round_trip",
    "cli_missing_argument_parser_stderr_drift",
    "cli_invalid_mode_parser_round_trip",
    "cli_invalid_mode_parser_stderr_drift",
    "helper_summary_round_trip",
    "contract_summary_round_trip",
    "helper_summary_status_drift",
    "helper_summary_count_drift",
    "helper_summary_duplicate_case_drift",
    "helper_summary_case_order_drift",
    "contract_summary_status_drift",
    "contract_summary_base_count_drift",
    "contract_summary_base_case_order_drift",
    "contract_summary_repeat_count_drift",
    "contract_summary_repeat_case_order_drift",
    "contract_summary_case_count_drift",
    "contract_summary_duplicate_case_drift",
    "contract_summary_case_order_drift",
]


def run_contract_case(
    args: list[str],
    expected_exit: int,
    expected_lines: list[str],
    *,
    repeat_count: int = 1,
) -> list[str]:
    if repeat_count < 1:
        raise ValueError(f"repeat_count must be positive, got {repeat_count}")

    final_lines: list[str] | None = None
    for attempt in range(1, repeat_count + 1):
        completed = subprocess.run(
            [sys.executable, str(ARTIFACT_DIFF), *args],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        lines = completed.stdout.splitlines()
        if completed.returncode != expected_exit:
            raise AssertionError(
                f"attempt {attempt}: expected exit {expected_exit}, got {completed.returncode}: {lines}"
            )
        if lines != expected_lines:
            raise AssertionError(f"attempt {attempt}: unexpected output lines: {lines}")
        if completed.stderr:
            raise AssertionError(f"attempt {attempt}: unexpected stderr: {completed.stderr!r}")
        final_lines = lines
    assert final_lines is not None
    return final_lines


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
                f"attempt {attempt}: expected exit {expected_exit}, got {completed.returncode}: stdout={stdout_lines} stderr={stderr_lines}"
            )
        assert_output_lines(stdout_lines, expected_stdout_lines, f"attempt {attempt} parser")
        if not stderr_lines:
            raise AssertionError(
                f"attempt {attempt}: expected parser stderr output, got none"
            )
        assert_parser_error_contract(
            stdout_lines,
            normalized_stderr,
            expected_stderr_normalized=expected_stderr_normalized,
            label=f"attempt {attempt} parser",
        )


def assert_contract_catalog_shape() -> None:
    if len(set(EXPECTED_CONTRACT_CASES)) != len(EXPECTED_CONTRACT_CASES):
        raise AssertionError(
            f"artifact-diff contract cases must stay unique: {EXPECTED_CONTRACT_CASES}"
        )
    if len(set(REPEAT_CONTRACT_CASES)) != len(REPEAT_CONTRACT_CASES):
        raise AssertionError(
            f"artifact-diff repeat contract cases must stay unique: {REPEAT_CONTRACT_CASES}"
        )
    missing_repeat_cases = [
        case for case in REPEAT_CONTRACT_CASES if case not in EXPECTED_CONTRACT_CASES
    ]
    if missing_repeat_cases:
        raise AssertionError(
            "artifact-diff repeat contract cases drifted outside the published catalog: "
            f"{missing_repeat_cases}"
        )
    if len(BASE_CONTRACT_CASES) + len(REPEAT_CONTRACT_CASES) != len(
        EXPECTED_CONTRACT_CASES
    ):
        raise AssertionError(
            "artifact-diff base and repeat case partition drifted: "
            f"base={BASE_CONTRACT_CASES} repeat={REPEAT_CONTRACT_CASES} all={EXPECTED_CONTRACT_CASES}"
        )


def assert_self_test_catalog_shape() -> None:
    if len(set(EXPECTED_SELF_TEST_CASES)) != len(EXPECTED_SELF_TEST_CASES):
        raise AssertionError(
            f"artifact-diff contract self-test cases must stay unique: {EXPECTED_SELF_TEST_CASES}"
        )


def assert_review_note_markers(note_text: str) -> None:
    missing_markers = [
        marker for marker in REQUIRED_REVIEW_NOTE_MARKERS if marker not in note_text
    ]
    if missing_markers:
        raise AssertionError(
            "artifact-diff review note missing required markers: "
            f"{missing_markers}"
        )


def helper_self_test_expected_lines() -> list[str]:
    return [
        "ARTIFACT_DIFF_SELF_TEST=pass",
        "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=19",
        (
            "ARTIFACT_DIFF_SELF_TEST_CASES="
            "text_pass,text_mismatch,json_pass,json_mismatch,"
            "json_invalid_expected,json_invalid_actual,json_invalid_both,"
            "json_missing_expected,json_missing_actual,json_missing_both,"
            "sha256_pass,sha256_drift,text_missing_expected,text_missing_actual,"
            "text_missing_both,sha256_missing_expected,sha256_missing_actual,"
            "sha256_missing_both,invalid_mode_rejected"
        ),
    ]


def expected_help_lines() -> list[str]:
    return [
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
    ]


MISSING_ARGUMENT_ERROR_NORMALIZED = (
    "usage: artifact_diff.py [-h] [--mode {text,json,sha256}] [--self-test] "
    "[expected] [actual] artifact_diff.py: error: --mode, expected, and actual "
    "are required unless --self-test is set"
)

INVALID_MODE_ERROR_NORMALIZED = (
    "usage: artifact_diff.py [-h] [--mode {text,json,sha256}] [--self-test] "
    "[expected] [actual] artifact_diff.py: error: argument --mode: invalid "
    "choice: 'yaml' (choose from text, json, sha256)"
)


def assert_output_lines(lines: list[str], expected_lines: list[str], label: str) -> None:
    if lines != expected_lines:
        raise AssertionError(
            f"unexpected {label} lines: expected {expected_lines}, got {lines}"
        )



def assert_parser_error_contract(
    stdout_lines: list[str],
    normalized_stderr: str,
    *,
    expected_stderr_normalized: str,
    label: str,
) -> None:
    assert_output_lines(stdout_lines, [], f"{label} stdout")
    if normalized_stderr != expected_stderr_normalized:
        raise AssertionError(
            f"unexpected {label} stderr: expected {expected_stderr_normalized!r}, got {normalized_stderr!r}"
        )


def extract_output_value(lines: list[str], prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :]
    raise AssertionError(f"missing output line with prefix {prefix!r}: {lines}")


def parse_case_catalog(lines: list[str], count_prefix: str, list_prefix: str) -> list[str]:
    count_text = extract_output_value(lines, count_prefix)
    try:
        expected_count = int(count_text)
    except ValueError as exc:
        raise AssertionError(
            f"invalid integer for {count_prefix!r}: {count_text!r}"
        ) from exc
    cases_text = extract_output_value(lines, list_prefix)
    cases = [] if not cases_text else cases_text.split(",")
    if len(cases) != expected_count:
        raise AssertionError(
            f"count/list drift for {count_prefix!r} and {list_prefix!r}: count={expected_count} cases={cases}"
        )
    if len(set(cases)) != len(cases):
        raise AssertionError(f"duplicate cases in {list_prefix!r}: {cases}")
    return cases


def assert_helper_self_test_output(lines: list[str]) -> None:
    if extract_output_value(lines, "ARTIFACT_DIFF_SELF_TEST=") != "pass":
        raise AssertionError(f"unexpected helper self-test status: {lines}")
    cases = parse_case_catalog(
        lines,
        "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=",
        "ARTIFACT_DIFF_SELF_TEST_CASES=",
    )
    expected_cases = helper_self_test_expected_lines()[2].split("=", 1)[1].split(",")
    if cases != expected_cases:
        raise AssertionError(
            "artifact-diff helper self-test catalog drifted: "
            f"expected {expected_cases}, got {cases}"
        )


def expected_contract_summary_lines() -> list[str]:
    return [
        "ARTIFACT_DIFF_CONTRACT=pass",
        f"ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={len(BASE_CONTRACT_CASES)}",
        "ARTIFACT_DIFF_CONTRACT_BASE_CASES=" + ",".join(BASE_CONTRACT_CASES),
        f"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(REPEAT_CONTRACT_CASES)}",
        "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=" + ",".join(REPEAT_CONTRACT_CASES),
        f"ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}",
        "ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(EXPECTED_CONTRACT_CASES),
    ]


def assert_contract_output(lines: list[str]) -> None:
    if extract_output_value(lines, "ARTIFACT_DIFF_CONTRACT=") != "pass":
        raise AssertionError(f"unexpected contract status: {lines}")
    base_cases = parse_case_catalog(
        lines,
        "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_BASE_CASES=",
    )
    if base_cases != BASE_CONTRACT_CASES:
        raise AssertionError(
            f"artifact-diff base contract catalog drifted: expected {BASE_CONTRACT_CASES}, got {base_cases}"
        )
    repeat_cases = parse_case_catalog(
        lines,
        "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=",
    )
    if repeat_cases != REPEAT_CONTRACT_CASES:
        raise AssertionError(
            f"artifact-diff repeat contract catalog drifted: expected {REPEAT_CONTRACT_CASES}, got {repeat_cases}"
        )
    all_cases = parse_case_catalog(
        lines,
        "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_CASES=",
    )
    if all_cases != EXPECTED_CONTRACT_CASES:
        raise AssertionError(
            f"artifact-diff full contract catalog drifted: expected {EXPECTED_CONTRACT_CASES}, got {all_cases}"
        )


def expect_assertion(label: str, callback) -> None:
    try:
        callback()
    except AssertionError:
        return
    raise AssertionError(f"expected AssertionError for self-test case {label}")


def run_self_test() -> int:
    assert_self_test_catalog_shape()
    covered_cases: list[str] = []

    assert_contract_catalog_shape()
    covered_cases.append("catalog_shape")

    assert_review_note_markers("\n".join(REQUIRED_REVIEW_NOTE_MARKERS))
    covered_cases.append("review_note_marker_round_trip")

    expect_assertion(
        "review_note_owner_marker_drift",
        lambda: assert_review_note_markers("\n".join(REQUIRED_REVIEW_NOTE_MARKERS[1:])),
    )
    covered_cases.append("review_note_owner_marker_drift")

    expect_assertion(
        "review_note_marker_drift",
        lambda: assert_review_note_markers("\n".join(REQUIRED_REVIEW_NOTE_MARKERS[:3] + REQUIRED_REVIEW_NOTE_MARKERS[4:])),
    )
    covered_cases.append("review_note_marker_drift")

    assert_output_lines(expected_help_lines(), expected_help_lines(), "cli_help")
    covered_cases.append("cli_help_round_trip")

    bad_help_lines = expected_help_lines()
    bad_help_lines[11] = "  --mode {text,json}"
    expect_assertion(
        "cli_help_line_drift",
        lambda: assert_output_lines(bad_help_lines, expected_help_lines(), "cli_help"),
    )
    covered_cases.append("cli_help_line_drift")

    assert_parser_error_contract(
        [],
        MISSING_ARGUMENT_ERROR_NORMALIZED,
        expected_stderr_normalized=MISSING_ARGUMENT_ERROR_NORMALIZED,
        label="cli_missing_argument_parser",
    )
    covered_cases.append("cli_missing_argument_parser_round_trip")

    expect_assertion(
        "cli_missing_argument_parser_stderr_drift",
        lambda: assert_parser_error_contract(
            [],
            MISSING_ARGUMENT_ERROR_NORMALIZED.replace(
                "unless --self-test is set",
                "unless --self-test is passed",
            ),
            expected_stderr_normalized=MISSING_ARGUMENT_ERROR_NORMALIZED,
            label="cli_missing_argument_parser",
        ),
    )
    covered_cases.append("cli_missing_argument_parser_stderr_drift")

    assert_parser_error_contract(
        [],
        INVALID_MODE_ERROR_NORMALIZED,
        expected_stderr_normalized=INVALID_MODE_ERROR_NORMALIZED,
        label="cli_invalid_mode_parser",
    )
    covered_cases.append("cli_invalid_mode_parser_round_trip")

    expect_assertion(
        "cli_invalid_mode_parser_stderr_drift",
        lambda: assert_parser_error_contract(
            [],
            INVALID_MODE_ERROR_NORMALIZED.replace("choice", "option"),
            expected_stderr_normalized=INVALID_MODE_ERROR_NORMALIZED,
            label="cli_invalid_mode_parser",
        ),
    )
    covered_cases.append("cli_invalid_mode_parser_stderr_drift")

    assert_helper_self_test_output(helper_self_test_expected_lines())
    covered_cases.append("helper_summary_round_trip")

    assert_contract_output(expected_contract_summary_lines())
    covered_cases.append("contract_summary_round_trip")

    bad_helper_status_lines = helper_self_test_expected_lines()
    bad_helper_status_lines[0] = "ARTIFACT_DIFF_SELF_TEST=fail"
    expect_assertion(
        "helper_summary_status_drift",
        lambda: assert_helper_self_test_output(bad_helper_status_lines),
    )
    covered_cases.append("helper_summary_status_drift")

    bad_helper_count_lines = helper_self_test_expected_lines()
    bad_helper_count_lines[1] = "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=18"
    expect_assertion(
        "helper_summary_count_drift",
        lambda: assert_helper_self_test_output(bad_helper_count_lines),
    )
    covered_cases.append("helper_summary_count_drift")

    bad_helper_duplicate_lines = helper_self_test_expected_lines()
    bad_helper_duplicate_lines[2] = (
        "ARTIFACT_DIFF_SELF_TEST_CASES="
        "text_pass,text_pass,json_pass,json_mismatch,json_invalid_expected,"
        "json_invalid_actual,json_invalid_both,json_missing_expected,"
        "json_missing_actual,json_missing_both,sha256_pass,sha256_drift,"
        "text_missing_expected,text_missing_actual,text_missing_both,"
        "sha256_missing_expected,sha256_missing_actual,sha256_missing_both,"
        "invalid_mode_rejected"
    )
    expect_assertion(
        "helper_summary_duplicate_case_drift",
        lambda: assert_helper_self_test_output(bad_helper_duplicate_lines),
    )
    covered_cases.append("helper_summary_duplicate_case_drift")

    bad_helper_case_order_lines = helper_self_test_expected_lines()
    bad_helper_case_order_lines[2] = (
        "ARTIFACT_DIFF_SELF_TEST_CASES="
        "text_mismatch,text_pass,json_pass,json_mismatch,json_invalid_expected,"
        "json_invalid_actual,json_invalid_both,json_missing_expected,"
        "json_missing_actual,json_missing_both,sha256_pass,sha256_drift,"
        "text_missing_expected,text_missing_actual,text_missing_both,"
        "sha256_missing_expected,sha256_missing_actual,sha256_missing_both,"
        "invalid_mode_rejected"
    )
    expect_assertion(
        "helper_summary_case_order_drift",
        lambda: assert_helper_self_test_output(bad_helper_case_order_lines),
    )
    covered_cases.append("helper_summary_case_order_drift")

    bad_contract_status_lines = expected_contract_summary_lines()
    bad_contract_status_lines[0] = "ARTIFACT_DIFF_CONTRACT=fail"
    expect_assertion(
        "contract_summary_status_drift",
        lambda: assert_contract_output(bad_contract_status_lines),
    )
    covered_cases.append("contract_summary_status_drift")

    bad_base_count_lines = expected_contract_summary_lines()
    bad_base_count_lines[1] = "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=22"
    expect_assertion(
        "contract_summary_base_count_drift",
        lambda: assert_contract_output(bad_base_count_lines),
    )
    covered_cases.append("contract_summary_base_count_drift")

    bad_base_case_order_lines = expected_contract_summary_lines()
    bad_base_case_order_lines[2] = (
        "ARTIFACT_DIFF_CONTRACT_BASE_CASES="
        + ",".join(["cli_help_output", "helper_self_test", *BASE_CONTRACT_CASES[2:]])
    )
    expect_assertion(
        "contract_summary_base_case_order_drift",
        lambda: assert_contract_output(bad_base_case_order_lines),
    )
    covered_cases.append("contract_summary_base_case_order_drift")

    bad_repeat_count_lines = expected_contract_summary_lines()
    bad_repeat_count_lines[3] = "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=4"
    expect_assertion(
        "contract_summary_repeat_count_drift",
        lambda: assert_contract_output(bad_repeat_count_lines),
    )
    covered_cases.append("contract_summary_repeat_count_drift")

    bad_repeat_case_order_lines = expected_contract_summary_lines()
    bad_repeat_case_order_lines[4] = (
        "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES="
        + ",".join(["cli_help_output_repeat", "helper_self_test_repeat", *REPEAT_CONTRACT_CASES[2:]])
    )
    expect_assertion(
        "contract_summary_repeat_case_order_drift",
        lambda: assert_contract_output(bad_repeat_case_order_lines),
    )
    covered_cases.append("contract_summary_repeat_case_order_drift")

    bad_case_count_lines = expected_contract_summary_lines()
    bad_case_count_lines[5] = "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27"
    expect_assertion(
        "contract_summary_case_count_drift",
        lambda: assert_contract_output(bad_case_count_lines),
    )
    covered_cases.append("contract_summary_case_count_drift")

    bad_duplicate_case_lines = expected_contract_summary_lines()
    bad_duplicate_case_lines[6] = (
        "ARTIFACT_DIFF_CONTRACT_CASES="
        + ",".join(["helper_self_test", "helper_self_test", *EXPECTED_CONTRACT_CASES[2:]])
    )
    expect_assertion(
        "contract_summary_duplicate_case_drift",
        lambda: assert_contract_output(bad_duplicate_case_lines),
    )
    covered_cases.append("contract_summary_duplicate_case_drift")

    bad_case_order_lines = expected_contract_summary_lines()
    bad_case_order_lines[6] = (
        "ARTIFACT_DIFF_CONTRACT_CASES="
        + ",".join(["helper_self_test_repeat", "helper_self_test", *EXPECTED_CONTRACT_CASES[2:]])
    )
    expect_assertion(
        "contract_summary_case_order_drift",
        lambda: assert_contract_output(bad_case_order_lines),
    )
    covered_cases.append("contract_summary_case_order_drift")

    if covered_cases != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(
            "artifact-diff contract self-test case catalog drifted: "
            f"expected {EXPECTED_SELF_TEST_CASES}, got {covered_cases}"
        )

    print("ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass")
    print(f"ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT={len(EXPECTED_SELF_TEST_CASES)}")
    print("ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=" + ",".join(EXPECTED_SELF_TEST_CASES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the published artifact-diff CLI contract and summary shapes."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker self-tests without replaying the live artifact-diff helper.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    run_self_test()
    assert_contract_catalog_shape()
    try:
        note_text = ARTIFACT_DIFF_NOTE.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise AssertionError(f"missing artifact-diff note: {ARTIFACT_DIFF_NOTE}") from exc
    assert_review_note_markers(note_text)
    covered_cases: list[str] = []

    helper_self_test_lines = run_contract_case(
        ["--self-test"],
        0,
        helper_self_test_expected_lines(),
        repeat_count=2,
    )
    assert_helper_self_test_output(helper_self_test_lines)
    covered_cases.append("helper_self_test")
    covered_cases.append("helper_self_test_repeat")

    run_contract_case(
        ["-h"],
        0,
        expected_help_lines(),
        repeat_count=2,
    )
    covered_cases.append("cli_help_output")
    covered_cases.append("cli_help_output_repeat")

    run_error_contract_case(
        [],
        2,
        [],
        expected_stderr_normalized=MISSING_ARGUMENT_ERROR_NORMALIZED,
        repeat_count=2,
    )
    covered_cases.append("cli_missing_required_args")

    with tempfile.TemporaryDirectory(prefix="zigux_artifact_diff_contract_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        expected = tmp_dir / "expected.txt"
        actual = tmp_dir / "actual.txt"
        missing = tmp_dir / "missing.txt"
        other_missing = tmp_dir / "other-missing.txt"
        expected_json = tmp_dir / "expected.json"
        actual_json = tmp_dir / "actual.json"
        actual_json_mismatch = tmp_dir / "actual-mismatch.json"
        invalid_expected_json = tmp_dir / "expected-invalid.json"
        invalid_actual_json = tmp_dir / "actual-invalid.json"
        blob_a = tmp_dir / "blob-a.bin"
        blob_b = tmp_dir / "blob-b.bin"

        expected.write_text("alpha\nbeta\n", encoding="utf-8", newline="\n")
        actual.write_text("alpha\nbeta\n", encoding="utf-8", newline="\n")

        run_error_contract_case(
            ["--mode", "text", str(expected)],
            2,
            [],
            expected_stderr_normalized=MISSING_ARGUMENT_ERROR_NORMALIZED,
            repeat_count=2,
        )
        covered_cases.append("cli_missing_actual_operand")

        run_error_contract_case(
            ["--mode", "yaml", str(expected), str(actual)],
            2,
            [],
            expected_stderr_normalized=INVALID_MODE_ERROR_NORMALIZED,
            repeat_count=2,
        )
        covered_cases.append("cli_invalid_mode")

        run_contract_case(
            ["--mode", "text", str(expected), str(actual)],
            0,
            [
                "ARTIFACT_DIFF=pass",
                "MODE=text",
                f"EXPECTED={expected}",
                f"ACTUAL={actual}",
            ],
            repeat_count=2,
        )
        covered_cases.append("text_pass")
        covered_cases.append("text_pass_repeat")

        actual.write_text("alpha\nBETA\n", encoding="utf-8", newline="\n")
        run_contract_case(
            ["--mode", "text", str(expected), str(actual)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=text",
                f"EXPECTED={expected}",
                f"ACTUAL={actual}",
            ],
        )
        covered_cases.append("text_mismatch")
        actual.write_text("alpha\nbeta\n", encoding="utf-8", newline="\n")

        run_contract_case(
            ["--mode", "text", str(missing), str(actual)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=text",
                f"EXPECTED={missing}",
                f"ACTUAL={actual}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=True",
            ],
        )
        covered_cases.append("text_missing_expected")

        run_contract_case(
            ["--mode", "text", str(expected), str(missing)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=text",
                f"EXPECTED={expected}",
                f"ACTUAL={missing}",
                "EXPECTED_EXISTS=True",
                "ACTUAL_EXISTS=False",
            ],
        )
        covered_cases.append("text_missing_actual")

        run_contract_case(
            ["--mode", "text", str(missing), str(other_missing)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=text",
                f"EXPECTED={missing}",
                f"ACTUAL={other_missing}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=False",
            ],
        )
        covered_cases.append("text_missing_both")

        expected_json.write_text('{"alpha": 1, "beta": [2, 3]}\n', encoding="utf-8", newline="\n")
        actual_json.write_text('{\n  "beta": [2, 3],\n  "alpha": 1\n}\n', encoding="utf-8", newline="\n")
        actual_json_mismatch.write_text('{"alpha": 1, "beta": [2, 4]}\n', encoding="utf-8", newline="\n")
        invalid_expected_json.write_text('{"alpha": 1,\n', encoding="utf-8", newline="\n")
        invalid_actual_json.write_text('{"alpha": 1,\n', encoding="utf-8", newline="\n")

        run_contract_case(
            ["--mode", "json", str(expected_json), str(actual_json)],
            0,
            [
                "ARTIFACT_DIFF=pass",
                "MODE=json",
                f"EXPECTED={expected_json}",
                f"ACTUAL={actual_json}",
            ],
        )
        covered_cases.append("json_pass")

        run_contract_case(
            ["--mode", "json", str(expected_json), str(actual_json_mismatch)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={expected_json}",
                f"ACTUAL={actual_json_mismatch}",
            ],
            repeat_count=2,
        )
        covered_cases.append("json_mismatch")
        covered_cases.append("json_mismatch_repeat")

        run_contract_case(
            ["--mode", "json", str(missing), str(actual_json)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={missing}",
                f"ACTUAL={actual_json}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=True",
            ],
        )
        covered_cases.append("json_missing_expected")

        run_contract_case(
            ["--mode", "json", str(expected_json), str(missing)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={expected_json}",
                f"ACTUAL={missing}",
                "EXPECTED_EXISTS=True",
                "ACTUAL_EXISTS=False",
            ],
        )
        covered_cases.append("json_missing_actual")

        run_contract_case(
            ["--mode", "json", str(missing), str(other_missing)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={missing}",
                f"ACTUAL={other_missing}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=False",
            ],
        )
        covered_cases.append("json_missing_both")

        run_contract_case(
            ["--mode", "json", str(invalid_expected_json), str(actual_json)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={invalid_expected_json}",
                f"ACTUAL={actual_json}",
                f"EXPECTED_JSON_ERROR={invalid_expected_json}:2:1: Expecting property name enclosed in double quotes",
            ],
        )
        covered_cases.append("json_invalid_expected")

        run_contract_case(
            ["--mode", "json", str(expected_json), str(invalid_actual_json)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={expected_json}",
                f"ACTUAL={invalid_actual_json}",
                f"ACTUAL_JSON_ERROR={invalid_actual_json}:2:1: Expecting property name enclosed in double quotes",
            ],
        )
        covered_cases.append("json_invalid_actual")

        run_contract_case(
            ["--mode", "json", str(invalid_expected_json), str(invalid_actual_json)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={invalid_expected_json}",
                f"ACTUAL={invalid_actual_json}",
                f"EXPECTED_JSON_ERROR={invalid_expected_json}:2:1: Expecting property name enclosed in double quotes",
            ],
        )
        covered_cases.append("json_invalid_both")

        blob_a.write_bytes(b"zigux-artifact-diff")
        blob_b.write_bytes(b"zigux-artifact-diff")
        run_contract_case(
            ["--mode", "sha256", str(blob_a), str(blob_b)],
            0,
            [
                "ARTIFACT_DIFF=pass",
                "MODE=sha256",
                f"EXPECTED={blob_a}",
                f"ACTUAL={blob_b}",
                "SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576",
            ],
        )
        covered_cases.append("sha256_pass")

        run_contract_case(
            ["--mode", "sha256", str(missing), str(blob_b)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=sha256",
                f"EXPECTED={missing}",
                f"ACTUAL={blob_b}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=True",
            ],
        )
        covered_cases.append("sha256_missing_expected")

        run_contract_case(
            ["--mode", "sha256", str(blob_a), str(missing)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=sha256",
                f"EXPECTED={blob_a}",
                f"ACTUAL={missing}",
                "EXPECTED_EXISTS=True",
                "ACTUAL_EXISTS=False",
            ],
        )
        covered_cases.append("sha256_missing_actual")

        run_contract_case(
            ["--mode", "sha256", str(missing), str(other_missing)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=sha256",
                f"EXPECTED={missing}",
                f"ACTUAL={other_missing}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=False",
            ],
        )
        covered_cases.append("sha256_missing_both")

        blob_b.write_bytes(b"zigux-artifact-DRIFT")
        run_contract_case(
            ["--mode", "sha256", str(blob_a), str(blob_b)],
            1,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=sha256",
                f"EXPECTED={blob_a}",
                f"ACTUAL={blob_b}",
                "EXPECTED_SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576",
                "ACTUAL_SHA256=bfc83f8f1f4369ce3cfabfdff0699ae3bf7a15b89f1702b690e56c6f35f1ee94",
            ],
            repeat_count=2,
        )
        covered_cases.append("sha256_drift")
        covered_cases.append("sha256_drift_repeat")

        assert_helper_self_test_output(
            run_contract_case(
                ["--self-test"],
                0,
                helper_self_test_expected_lines(),
            )
        )

    if covered_cases != EXPECTED_CONTRACT_CASES:
        raise AssertionError(
            "artifact-diff contract case catalog drifted: "
            f"expected {EXPECTED_CONTRACT_CASES}, got {covered_cases}"
        )

    summary_lines = expected_contract_summary_lines()
    for line in summary_lines:
        print(line)
    assert_contract_output(summary_lines)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
