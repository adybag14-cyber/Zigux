#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HELPER_REL = Path("scripts") / "zigux" / "artifact_diff.py"

HELP_LINES = [
    "usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test]",
    " [expected] [actual]",
    "",
    "Compare two artifacts in a stable mode.",
    "",
    "positional arguments:",
    " expected",
    " actual",
    "",
    "options:",
    " -h, --help show this help message and exit",
    " --mode {text,json,bytes}",
    " --self-test Run built-in deterministic comparison checks.",
]
MISSING_ARGUMENT_ERROR = (
    "usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test] "
    "[expected] [actual] artifact_diff.py: error: --mode, expected, and actual "
    "are required unless --self-test is set"
)
INVALID_MODE_ERROR = (
    "usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test] "
    "[expected] [actual] artifact_diff.py: error: argument --mode: invalid "
    "choice: 'yaml' (choose from text, json, bytes)"
)
HELPER_SELF_TEST_CASES = [
    "text_pass",
    "text_mismatch",
    "json_pass",
    "json_mismatch",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "bytes_pass",
    "bytes_drift",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "bytes_missing_expected",
    "bytes_missing_actual",
    "bytes_missing_both",
    "legacy_sha256_alias",
    "invalid_mode_rejected",
]
HELPER_SELF_TEST_LINES = [
    "ARTIFACT_DIFF_SELF_TEST=pass",
    f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(HELPER_SELF_TEST_CASES)}",
    "ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(HELPER_SELF_TEST_CASES),
]

BASE_CONTRACT_CASES = [
    "helper_self_test",
    "cli_help_output",
    "cli_missing_required_args",
    "cli_missing_actual_operand",
    "cli_invalid_mode",
    "text_pass",
    "text_mismatch",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "json_pass",
    "json_mismatch",
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
]
REPEAT_CONTRACT_CASES = [
    "helper_self_test_repeat",
    "cli_help_output_repeat",
    "text_pass_repeat",
    "json_mismatch_repeat",
    "sha256_drift_repeat",
]
ALL_CONTRACT_CASES = BASE_CONTRACT_CASES + REPEAT_CONTRACT_CASES
REVIEW_NOTE_MARKERS = [
    "host-side artifact-diff tooling contract",
    "owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`",
    "rollback owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`",
]
SELF_TEST_CASES = [
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


def run_helper(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / HELPER_REL), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=root,
    )


def normalize_stderr(stderr: str) -> str:
    return " ".join(stderr.split())


def assert_lines(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def extract_value(lines: list[str], prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :]
    raise AssertionError(f"missing line with prefix {prefix!r}: {lines}")


def parse_catalog(lines: list[str], count_prefix: str, cases_prefix: str) -> list[str]:
    count = int(extract_value(lines, count_prefix))
    cases_text = extract_value(lines, cases_prefix)
    cases = [] if not cases_text else cases_text.split(",")
    if len(cases) != count:
        raise AssertionError(f"count/list drift for {count_prefix}: {count} vs {cases}")
    if len(set(cases)) != len(cases):
        raise AssertionError(f"duplicate cases for {cases_prefix}: {cases}")
    return cases


def expected_contract_lines() -> list[str]:
    return [
        "ARTIFACT_DIFF_CONTRACT=pass",
        f"ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={len(BASE_CONTRACT_CASES)}",
        "ARTIFACT_DIFF_CONTRACT_BASE_CASES=" + ",".join(BASE_CONTRACT_CASES),
        f"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(REPEAT_CONTRACT_CASES)}",
        "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=" + ",".join(REPEAT_CONTRACT_CASES),
        f"ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(ALL_CONTRACT_CASES)}",
        "ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(ALL_CONTRACT_CASES),
    ]


def assert_helper_self_test_output(lines: list[str]) -> None:
    assert_lines(lines, HELPER_SELF_TEST_LINES, "helper self-test")
    cases = parse_catalog(
        lines,
        "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=",
        "ARTIFACT_DIFF_SELF_TEST_CASES=",
    )
    if cases != HELPER_SELF_TEST_CASES:
        raise AssertionError("helper self-test catalog drifted")


def assert_contract_output(lines: list[str]) -> None:
    expected = expected_contract_lines()
    assert_lines(lines, expected, "contract summary")
    if parse_catalog(
        lines,
        "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_BASE_CASES=",
    ) != BASE_CONTRACT_CASES:
        raise AssertionError("base contract catalog drifted")
    if parse_catalog(
        lines,
        "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=",
    ) != REPEAT_CONTRACT_CASES:
        raise AssertionError("repeat contract catalog drifted")
    if parse_catalog(
        lines,
        "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_CASES=",
    ) != ALL_CONTRACT_CASES:
        raise AssertionError("full contract catalog drifted")


def run_case(
    root: Path,
    args: list[str],
    *,
    expected_exit: int,
    expected_lines: list[str],
    repeat_count: int = 1,
) -> list[str]:
    last_lines: list[str] | None = None
    for attempt in range(repeat_count):
        completed = run_helper(root, args)
        lines = completed.stdout.splitlines()
        if completed.returncode != expected_exit:
            raise AssertionError(
                f"attempt {attempt + 1}: expected exit {expected_exit}, got {completed.returncode}"
            )
        if completed.stderr:
            raise AssertionError(f"attempt {attempt + 1}: unexpected stderr {completed.stderr!r}")
        assert_lines(lines, expected_lines, f"attempt {attempt + 1}")
        last_lines = lines
    assert last_lines is not None
    return last_lines


def run_error_case(
    root: Path,
    args: list[str],
    *,
    expected_exit: int,
    expected_stdout: list[str],
    expected_stderr: str,
    repeat_count: int = 1,
) -> None:
    for attempt in range(repeat_count):
        completed = run_helper(root, args)
        stdout = completed.stdout.splitlines()
        stderr = normalize_stderr(completed.stderr)
        if completed.returncode != expected_exit:
            raise AssertionError(
                f"attempt {attempt + 1}: expected exit {expected_exit}, got {completed.returncode}"
            )
        assert_lines(stdout, expected_stdout, f"attempt {attempt + 1} stdout")
        if stderr != expected_stderr:
            raise AssertionError(
                f"attempt {attempt + 1}: expected stderr {expected_stderr!r}, got {stderr!r}"
            )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def expected_json_error(label: str, path: Path) -> str:
    return (
        f"{label}_JSON_ERROR={path}:2:1: "
        "Expecting property name enclosed in double quotes"
    )


def assert_review_note_markers(markers: list[str]) -> None:
    if markers != REVIEW_NOTE_MARKERS:
        raise AssertionError(f"review-note marker drifted: {markers}")
    if len(set(markers)) != len(markers):
        raise AssertionError(f"review-note markers must stay unique: {markers}")


def run_check(root: Path) -> int:
    assert_helper_self_test_output(
        run_case(root, ["--self-test"], expected_exit=0, expected_lines=HELPER_SELF_TEST_LINES, repeat_count=2)
    )
    run_case(root, ["-h"], expected_exit=0, expected_lines=HELP_LINES, repeat_count=2)
    run_error_case(
        root,
        [],
        expected_exit=2,
        expected_stdout=[],
        expected_stderr=MISSING_ARGUMENT_ERROR,
        repeat_count=2,
    )

    with tempfile.TemporaryDirectory(prefix="zigux_artifact_diff_contract_") as tmp_dir:
        tmp = Path(tmp_dir)
        expected = tmp / "expected.txt"
        actual = tmp / "actual.txt"
        missing = tmp / "missing.txt"
        other_missing = tmp / "other-missing.txt"
        expected_json = tmp / "expected.json"
        actual_json = tmp / "actual.json"
        actual_json_mismatch = tmp / "actual-mismatch.json"
        invalid_expected_json = tmp / "expected-invalid.json"
        invalid_actual_json = tmp / "actual-invalid.json"
        blob_a = tmp / "blob-a.bin"
        blob_b = tmp / "blob-b.bin"

        write_text(expected, "alpha\nbeta\n")
        write_text(actual, "alpha\nbeta\n")

        run_error_case(
            root,
            ["--mode", "text", str(expected)],
            expected_exit=2,
            expected_stdout=[],
            expected_stderr=MISSING_ARGUMENT_ERROR,
            repeat_count=2,
        )
        run_error_case(
            root,
            ["--mode", "yaml", str(expected), str(actual)],
            expected_exit=2,
            expected_stdout=[],
            expected_stderr=INVALID_MODE_ERROR,
            repeat_count=2,
        )

        blob_a.write_bytes(b"zigux-artifact-diff")
        blob_b.write_bytes(b"zigux-artifact-diff")

        run_case(
            root,
            ["--mode", "text", str(expected), str(actual)],
            expected_exit=0,
            expected_lines=[
                "ARTIFACT_DIFF=pass",
                "MODE=text",
                f"EXPECTED={expected}",
                f"ACTUAL={actual}",
            ],
            repeat_count=2,
        )

        write_text(actual, "alpha\nBETA\n")
        run_case(
            root,
            ["--mode", "text", str(expected), str(actual)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=text",
                f"EXPECTED={expected}",
                f"ACTUAL={actual}",
            ],
        )
        write_text(actual, "alpha\nbeta\n")

        run_case(
            root,
            ["--mode", "text", str(missing), str(actual)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=text",
                f"EXPECTED={missing}",
                f"ACTUAL={actual}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=True",
            ],
        )
        run_case(
            root,
            ["--mode", "text", str(expected), str(missing)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=text",
                f"EXPECTED={expected}",
                f"ACTUAL={missing}",
                "EXPECTED_EXISTS=True",
                "ACTUAL_EXISTS=False",
            ],
        )
        run_case(
            root,
            ["--mode", "text", str(missing), str(other_missing)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=text",
                f"EXPECTED={missing}",
                f"ACTUAL={other_missing}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=False",
            ],
        )

        write_text(expected_json, '{"alpha": 1, "beta": [2, 3]}\n')
        write_text(actual_json, '{\n  "beta": [2, 3],\n  "alpha": 1\n}\n')
        write_text(actual_json_mismatch, '{"alpha": 1, "beta": [2, 4]}\n')
        write_text(invalid_expected_json, '{"alpha": 1,\n')
        write_text(invalid_actual_json, '{"alpha": 1,\n')

        run_case(
            root,
            ["--mode", "json", str(expected_json), str(actual_json)],
            expected_exit=0,
            expected_lines=[
                "ARTIFACT_DIFF=pass",
                "MODE=json",
                f"EXPECTED={expected_json}",
                f"ACTUAL={actual_json}",
            ],
        )
        run_case(
            root,
            ["--mode", "json", str(expected_json), str(actual_json_mismatch)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={expected_json}",
                f"ACTUAL={actual_json_mismatch}",
            ],
            repeat_count=2,
        )
        run_case(
            root,
            ["--mode", "json", str(missing), str(actual_json)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={missing}",
                f"ACTUAL={actual_json}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=True",
            ],
        )
        run_case(
            root,
            ["--mode", "json", str(expected_json), str(missing)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={expected_json}",
                f"ACTUAL={missing}",
                "EXPECTED_EXISTS=True",
                "ACTUAL_EXISTS=False",
            ],
        )
        run_case(
            root,
            ["--mode", "json", str(missing), str(other_missing)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={missing}",
                f"ACTUAL={other_missing}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=False",
            ],
        )
        run_case(
            root,
            ["--mode", "json", str(invalid_expected_json), str(actual_json)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={invalid_expected_json}",
                f"ACTUAL={actual_json}",
                expected_json_error("EXPECTED", invalid_expected_json),
            ],
        )
        run_case(
            root,
            ["--mode", "json", str(expected_json), str(invalid_actual_json)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={expected_json}",
                f"ACTUAL={invalid_actual_json}",
                expected_json_error("ACTUAL", invalid_actual_json),
            ],
        )
        run_case(
            root,
            ["--mode", "json", str(invalid_expected_json), str(invalid_actual_json)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={invalid_expected_json}",
                f"ACTUAL={invalid_actual_json}",
                expected_json_error("EXPECTED", invalid_expected_json),
            ],
        )

        run_case(
            root,
            ["--mode", "sha256", str(blob_a), str(blob_b)],
            expected_exit=0,
            expected_lines=[
                "ARTIFACT_DIFF=pass",
                "MODE=bytes",
                f"EXPECTED={blob_a}",
                f"ACTUAL={blob_b}",
                "SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576",
            ],
        )
        run_case(
            root,
            ["--mode", "sha256", str(missing), str(blob_b)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=bytes",
                f"EXPECTED={missing}",
                f"ACTUAL={blob_b}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=True",
            ],
        )
        run_case(
            root,
            ["--mode", "sha256", str(blob_a), str(missing)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=bytes",
                f"EXPECTED={blob_a}",
                f"ACTUAL={missing}",
                "EXPECTED_EXISTS=True",
                "ACTUAL_EXISTS=False",
            ],
        )
        run_case(
            root,
            ["--mode", "sha256", str(missing), str(other_missing)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=bytes",
                f"EXPECTED={missing}",
                f"ACTUAL={other_missing}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=False",
            ],
        )

        blob_b.write_bytes(b"zigux-artifact-DRIFT")
        run_case(
            root,
            ["--mode", "sha256", str(blob_a), str(blob_b)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=bytes",
                f"EXPECTED={blob_a}",
                f"ACTUAL={blob_b}",
                "EXPECTED_SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576",
                "ACTUAL_SHA256=bfc83f8f1f4369ce3cfabfdff0699ae3bf7a15b89f1702b690e56c6f35f1ee94",
            ],
            repeat_count=2,
        )

    for line in expected_contract_lines():
        print(line)
    return 0


def expect_assertion(label: str, callback) -> None:
    try:
        callback()
    except AssertionError:
        return
    raise AssertionError(f"expected AssertionError for {label}")


def run_self_test() -> int:
    covered: list[str] = []

    if len(set(BASE_CONTRACT_CASES)) != len(BASE_CONTRACT_CASES):
        raise AssertionError("base cases must stay unique")
    if len(set(REPEAT_CONTRACT_CASES)) != len(REPEAT_CONTRACT_CASES):
        raise AssertionError("repeat cases must stay unique")
    if len(set(ALL_CONTRACT_CASES)) != len(ALL_CONTRACT_CASES):
        raise AssertionError("full contract cases must stay unique")
    if ALL_CONTRACT_CASES != BASE_CONTRACT_CASES + REPEAT_CONTRACT_CASES:
        raise AssertionError("full contract packet must stay base+repeat")
    if len(set(SELF_TEST_CASES)) != len(SELF_TEST_CASES):
        raise AssertionError("self-test cases must stay unique")
    covered.append("catalog_shape")

    assert_review_note_markers(list(REVIEW_NOTE_MARKERS))
    covered.append("review_note_marker_round_trip")

    bad_owner = list(REVIEW_NOTE_MARKERS)
    bad_owner[1] = "owner: `stale owner marker`"
    expect_assertion("review_note_owner_marker_drift", lambda: assert_review_note_markers(bad_owner))
    covered.append("review_note_owner_marker_drift")

    bad_marker = list(REVIEW_NOTE_MARKERS)
    bad_marker[0] = "host-side artifact-diff stale contract"
    expect_assertion("review_note_marker_drift", lambda: assert_review_note_markers(bad_marker))
    covered.append("review_note_marker_drift")

    assert_lines(HELP_LINES, HELP_LINES, "help round trip")
    covered.append("cli_help_round_trip")

    bad_help = list(HELP_LINES)
    bad_help[11] = " --mode {text,json,sha256}"
    expect_assertion("cli_help_line_drift", lambda: assert_lines(bad_help, HELP_LINES, "help drift"))
    covered.append("cli_help_line_drift")

    if "are required unless --self-test is set" not in MISSING_ARGUMENT_ERROR:
        raise AssertionError("missing-argument parser contract drifted")
    covered.append("cli_missing_argument_parser_round_trip")

    expect_assertion(
        "cli_missing_argument_parser_stderr_drift",
        lambda: (
            None
            if MISSING_ARGUMENT_ERROR
            == MISSING_ARGUMENT_ERROR.replace("required unless", "needed unless")
            else (_ for _ in ()).throw(AssertionError("stderr drift"))
        ),
    )
    covered.append("cli_missing_argument_parser_stderr_drift")

    if "choice: 'yaml' (choose from text, json, bytes)" not in INVALID_MODE_ERROR:
        raise AssertionError("invalid-mode parser contract drifted")
    covered.append("cli_invalid_mode_parser_round_trip")

    expect_assertion(
        "cli_invalid_mode_parser_stderr_drift",
        lambda: (
            None
            if INVALID_MODE_ERROR == INVALID_MODE_ERROR.replace("'yaml'", "'yml'")
            else (_ for _ in ()).throw(AssertionError("stderr drift"))
        ),
    )
    covered.append("cli_invalid_mode_parser_stderr_drift")

    assert_helper_self_test_output(HELPER_SELF_TEST_LINES)
    covered.append("helper_summary_round_trip")

    assert_contract_output(expected_contract_lines())
    covered.append("contract_summary_round_trip")

    bad_status = list(HELPER_SELF_TEST_LINES)
    bad_status[0] = "ARTIFACT_DIFF_SELF_TEST=fail"
    expect_assertion("helper_summary_status_drift", lambda: assert_helper_self_test_output(bad_status))
    covered.append("helper_summary_status_drift")

    bad_count = list(HELPER_SELF_TEST_LINES)
    bad_count[1] = "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=19"
    expect_assertion("helper_summary_count_drift", lambda: assert_helper_self_test_output(bad_count))
    covered.append("helper_summary_count_drift")

    duplicate_cases = list(HELPER_SELF_TEST_CASES)
    duplicate_cases[-1] = duplicate_cases[0]
    expect_assertion(
        "helper_summary_duplicate_case_drift",
        lambda: assert_helper_self_test_output(
            [
                "ARTIFACT_DIFF_SELF_TEST=pass",
                f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(duplicate_cases)}",
                "ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(duplicate_cases),
            ]
        ),
    )
    covered.append("helper_summary_duplicate_case_drift")

    reordered_cases = [HELPER_SELF_TEST_CASES[1], HELPER_SELF_TEST_CASES[0], *HELPER_SELF_TEST_CASES[2:]]
    expect_assertion(
        "helper_summary_case_order_drift",
        lambda: assert_helper_self_test_output(
            [
                "ARTIFACT_DIFF_SELF_TEST=pass",
                f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(reordered_cases)}",
                "ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(reordered_cases),
            ]
        ),
    )
    covered.append("helper_summary_case_order_drift")

    bad_contract_status = expected_contract_lines()
    bad_contract_status[0] = "ARTIFACT_DIFF_CONTRACT=fail"
    expect_assertion("contract_summary_status_drift", lambda: assert_contract_output(bad_contract_status))
    covered.append("contract_summary_status_drift")

    bad_base_count = expected_contract_lines()
    bad_base_count[1] = "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=22"
    expect_assertion("contract_summary_base_count_drift", lambda: assert_contract_output(bad_base_count))
    covered.append("contract_summary_base_count_drift")

    bad_base_order = expected_contract_lines()
    swapped = [BASE_CONTRACT_CASES[1], BASE_CONTRACT_CASES[0], *BASE_CONTRACT_CASES[2:]]
    bad_base_order[2] = "ARTIFACT_DIFF_CONTRACT_BASE_CASES=" + ",".join(swapped)
    expect_assertion("contract_summary_base_case_order_drift", lambda: assert_contract_output(bad_base_order))
    covered.append("contract_summary_base_case_order_drift")

    bad_repeat_count = expected_contract_lines()
    bad_repeat_count[3] = "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=4"
    expect_assertion("contract_summary_repeat_count_drift", lambda: assert_contract_output(bad_repeat_count))
    covered.append("contract_summary_repeat_count_drift")

    bad_repeat_order = expected_contract_lines()
    repeat_swapped = [REPEAT_CONTRACT_CASES[1], REPEAT_CONTRACT_CASES[0], *REPEAT_CONTRACT_CASES[2:]]
    bad_repeat_order[4] = "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=" + ",".join(repeat_swapped)
    expect_assertion("contract_summary_repeat_case_order_drift", lambda: assert_contract_output(bad_repeat_order))
    covered.append("contract_summary_repeat_case_order_drift")

    bad_case_count = expected_contract_lines()
    bad_case_count[5] = "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27"
    expect_assertion("contract_summary_case_count_drift", lambda: assert_contract_output(bad_case_count))
    covered.append("contract_summary_case_count_drift")

    duplicate_all = list(ALL_CONTRACT_CASES)
    duplicate_all[-1] = duplicate_all[0]
    bad_duplicate = expected_contract_lines()
    bad_duplicate[6] = "ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(duplicate_all)
    expect_assertion("contract_summary_duplicate_case_drift", lambda: assert_contract_output(bad_duplicate))
    covered.append("contract_summary_duplicate_case_drift")

    reordered_all = [ALL_CONTRACT_CASES[1], ALL_CONTRACT_CASES[0], *ALL_CONTRACT_CASES[2:]]
    bad_order = expected_contract_lines()
    bad_order[6] = "ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(reordered_all)
    expect_assertion("contract_summary_case_order_drift", lambda: assert_contract_output(bad_order))
    covered.append("contract_summary_case_order_drift")

    if covered != SELF_TEST_CASES:
        raise AssertionError(f"checker self-test catalog drifted: {covered}")

    print("ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass")
    print(f"ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print("ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the published artifact-diff helper contract and summary shapes."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if args.self_test:
        return run_self_test()
    return run_check(root)


if __name__ == "__main__":
    raise SystemExit(main())
