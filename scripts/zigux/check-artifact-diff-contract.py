#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF_REL = Path("scripts") / "zigux" / "artifact_diff.py"

EXPECTED_CONTRACT_CASES = [
    "helper_self_test",
    "helper_self_test_repeat",
    "cli_help_output",
    "cli_help_output_repeat",
    "cli_missing_required_args",
    "cli_missing_actual_operand",
    "cli_invalid_mode",
    "bytes_family_legacy_sha256_alias_pass",
    "sha256_family_legacy_bytes_mode_rejected",
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

BYTES_HELP_LINES = [
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

SHA256_HELP_LINES = [
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

MISSING_ARGUMENT_ERROR_BY_FAMILY = {
    "bytes": (
        "usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test] "
        "[expected] [actual] artifact_diff.py: error: --mode, expected, and actual "
        "are required unless --self-test is set"
    ),
    "sha256": (
        "usage: artifact_diff.py [-h] [--mode {text,json,sha256}] [--self-test] "
        "[expected] [actual] artifact_diff.py: error: --mode, expected, and actual "
        "are required unless --self-test is set"
    ),
}

INVALID_MODE_ERROR_BY_FAMILY = {
    "bytes": (
        "usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test] "
        "[expected] [actual] artifact_diff.py: error: argument --mode: invalid "
        "choice: 'yaml' (choose from text, json, bytes)"
    ),
    "sha256": (
        "usage: artifact_diff.py [-h] [--mode {text,json,sha256}] [--self-test] "
        "[expected] [actual] artifact_diff.py: error: argument --mode: invalid "
        "choice: 'yaml' (choose from text, json, sha256)"
    ),
}

LEGACY_BOUNDARY_ERROR_BY_FAMILY = {
    "sha256": (
        "usage: artifact_diff.py [-h] [--mode {text,json,sha256}] [--self-test] "
        "[expected] [actual] artifact_diff.py: error: argument --mode: invalid "
        "choice: 'bytes' (choose from text, json, sha256)"
    ),
}

HELP_LINES_BY_FAMILY = {
    "bytes": BYTES_HELP_LINES,
    "sha256": SHA256_HELP_LINES,
}

HELPER_SELF_TEST_LINES_BY_FAMILY = {
    "bytes": [
        "ARTIFACT_DIFF_SELF_TEST=pass",
        "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=20",
        (
            "ARTIFACT_DIFF_SELF_TEST_CASES="
            "text_pass,text_mismatch,json_pass,json_mismatch,"
            "json_invalid_expected,json_invalid_actual,json_invalid_both,"
            "json_missing_expected,json_missing_actual,json_missing_both,"
            "bytes_pass,bytes_drift,text_missing_expected,text_missing_actual,"
            "text_missing_both,bytes_missing_expected,bytes_missing_actual,"
            "bytes_missing_both,legacy_sha256_alias,invalid_mode_rejected"
        ),
    ],
    "sha256": [
        "ARTIFACT_DIFF_SELF_TEST=pass",
        "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=25",
        (
            "ARTIFACT_DIFF_SELF_TEST_CASES="
            "text_pass,text_mismatch,text_invalid_utf8_expected,"
            "text_invalid_utf8_actual,text_invalid_utf8_both,json_pass,"
            "json_mismatch,json_invalid_expected,json_invalid_actual,"
            "json_invalid_both,json_invalid_utf8_expected,"
            "json_invalid_utf8_actual,json_invalid_utf8_both,"
            "json_missing_expected,json_missing_actual,json_missing_both,"
            "sha256_pass,sha256_drift,text_missing_expected,"
            "text_missing_actual,text_missing_both,sha256_missing_expected,"
            "sha256_missing_actual,sha256_missing_both,invalid_mode_rejected"
        ),
    ],
}

HASH_MODE_BY_FAMILY = {
    "bytes": ("bytes", "bytes"),
    "sha256": ("sha256", "sha256"),
}

EXPECTED_SELF_TEST_CASES = [
    "catalog_shape",
    "family_help_bytes_round_trip",
    "family_help_sha256_round_trip",
    "family_detection_bytes",
    "family_detection_sha256",
    "family_detection_unknown_rejected",
    "helper_summary_bytes_round_trip",
    "helper_summary_sha256_round_trip",
    "helper_summary_bytes_drift",
    "helper_summary_sha256_drift",
    "parser_error_bytes_round_trip",
    "parser_error_sha256_round_trip",
    "parser_error_drift",
    "family_boundary_bytes_alias_round_trip",
    "family_boundary_sha256_rejected_round_trip",
    "family_boundary_drift",
    "contract_summary_round_trip",
    "contract_summary_base_count_drift",
    "contract_summary_repeat_count_drift",
    "contract_summary_case_count_drift",
]


def run_helper(args: list[str], *, root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / ARTIFACT_DIFF_REL), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=root,
    )


def normalize_stderr(stderr: str) -> str:
    return " ".join(stderr.split())


def assert_output_lines(lines: list[str], expected_lines: list[str], label: str) -> None:
    if lines != expected_lines:
        raise AssertionError(
            f"unexpected {label} lines: expected {expected_lines}, got {lines}"
        )


def assert_catalog_shape() -> None:
    if len(set(EXPECTED_CONTRACT_CASES)) != len(EXPECTED_CONTRACT_CASES):
        raise AssertionError("artifact-diff contract cases must stay unique")
    if len(set(REPEAT_CONTRACT_CASES)) != len(REPEAT_CONTRACT_CASES):
        raise AssertionError("artifact-diff repeat contract cases must stay unique")
    if len(BASE_CONTRACT_CASES) + len(REPEAT_CONTRACT_CASES) != len(
        EXPECTED_CONTRACT_CASES
    ):
        raise AssertionError("artifact-diff contract case partition drifted")
    if len(set(EXPECTED_SELF_TEST_CASES)) != len(EXPECTED_SELF_TEST_CASES):
        raise AssertionError("artifact-diff checker self-test cases must stay unique")


def detect_helper_family_from_lines(help_lines: list[str]) -> str:
    if help_lines == BYTES_HELP_LINES:
        return "bytes"
    if help_lines == SHA256_HELP_LINES:
        return "sha256"
    raise AssertionError(f"unrecognized artifact-diff help output: {help_lines}")


def detect_helper_family(root: Path) -> str:
    completed = run_helper(["-h"], root=root)
    if completed.returncode != 0:
        raise AssertionError(
            f"artifact-diff help exited {completed.returncode}: {completed.stderr!r}"
        )
    if completed.stderr:
        raise AssertionError(f"artifact-diff help emitted stderr: {completed.stderr!r}")
    return detect_helper_family_from_lines(completed.stdout.splitlines())


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


def parse_case_catalog(lines: list[str], count_prefix: str, list_prefix: str) -> list[str]:
    count_text = extract_output_value(lines, count_prefix)
    cases_text = extract_output_value(lines, list_prefix)
    try:
        expected_count = int(count_text)
    except ValueError as exc:
        raise AssertionError(f"invalid integer for {count_prefix}: {count_text!r}") from exc
    cases = [] if not cases_text else cases_text.split(",")
    if len(cases) != expected_count:
        raise AssertionError(
            f"count/list drift for {count_prefix}: count={expected_count} cases={cases}"
        )
    if len(set(cases)) != len(cases):
        raise AssertionError(f"duplicate catalog cases for {list_prefix}: {cases}")
    return cases


def extract_output_value(lines: list[str], prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :]
    raise AssertionError(f"missing output line with prefix {prefix!r}: {lines}")


def assert_contract_summary_output(lines: list[str]) -> None:
    expected = expected_contract_summary_lines()
    assert_output_lines(lines, expected, "contract_summary")
    base_cases = parse_case_catalog(
        lines,
        "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_BASE_CASES=",
    )
    if base_cases != BASE_CONTRACT_CASES:
        raise AssertionError("artifact-diff base contract catalog drifted")
    repeat_cases = parse_case_catalog(
        lines,
        "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=",
    )
    if repeat_cases != REPEAT_CONTRACT_CASES:
        raise AssertionError("artifact-diff repeat contract catalog drifted")
    all_cases = parse_case_catalog(
        lines,
        "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_CASES=",
    )
    if all_cases != EXPECTED_CONTRACT_CASES:
        raise AssertionError("artifact-diff full contract catalog drifted")


def assert_helper_self_test_output(lines: list[str], *, family: str) -> None:
    expected = HELPER_SELF_TEST_LINES_BY_FAMILY[family]
    assert_output_lines(lines, expected, f"{family}_helper_self_test")
    cases = parse_case_catalog(
        lines,
        "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=",
        "ARTIFACT_DIFF_SELF_TEST_CASES=",
    )
    expected_cases = expected[2].split("=", 1)[1].split(",")
    if cases != expected_cases:
        raise AssertionError(f"{family} helper self-test catalog drifted")


def run_contract_case(
    root: Path,
    args: list[str],
    *,
    expected_exit: int,
    expected_lines: list[str],
    repeat_count: int = 1,
) -> list[str]:
    if repeat_count < 1:
        raise ValueError(f"repeat_count must be positive, got {repeat_count}")
    final_lines: list[str] | None = None
    for attempt in range(1, repeat_count + 1):
        completed = run_helper(args, root=root)
        lines = completed.stdout.splitlines()
        if completed.returncode != expected_exit:
            raise AssertionError(
                f"attempt {attempt}: expected exit {expected_exit}, got {completed.returncode}: {lines}"
            )
        if completed.stderr:
            raise AssertionError(
                f"attempt {attempt}: unexpected stderr: {completed.stderr!r}"
            )
        assert_output_lines(lines, expected_lines, f"attempt {attempt}")
        final_lines = lines
    assert final_lines is not None
    return final_lines


def run_error_contract_case(
    root: Path,
    args: list[str],
    *,
    expected_exit: int,
    expected_stdout_lines: list[str],
    expected_stderr_normalized: str,
    repeat_count: int = 1,
) -> None:
    if repeat_count < 1:
        raise ValueError(f"repeat_count must be positive, got {repeat_count}")
    for attempt in range(1, repeat_count + 1):
        completed = run_helper(args, root=root)
        stdout_lines = completed.stdout.splitlines()
        stderr_normalized = normalize_stderr(completed.stderr)
        if completed.returncode != expected_exit:
            raise AssertionError(
                f"attempt {attempt}: expected exit {expected_exit}, got {completed.returncode}: stdout={stdout_lines} stderr={completed.stderr!r}"
            )
        assert_output_lines(stdout_lines, expected_stdout_lines, f"attempt {attempt} stdout")
        if stderr_normalized != expected_stderr_normalized:
            raise AssertionError(
                f"attempt {attempt}: unexpected stderr: {stderr_normalized!r}"
            )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def expected_json_error_line(label: str, path: Path) -> str:
    return (
        f"{label}_JSON_ERROR={path}:2:1: "
        "Expecting property name enclosed in double quotes"
    )


def expected_sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_check(root: Path) -> int:
    family = detect_helper_family(root)
    help_lines = HELP_LINES_BY_FAMILY[family]
    hash_mode_arg, hash_output_mode = HASH_MODE_BY_FAMILY[family]

    assert_helper_self_test_output(
        run_contract_case(
            root,
            ["--self-test"],
            expected_exit=0,
            expected_lines=HELPER_SELF_TEST_LINES_BY_FAMILY[family],
            repeat_count=2,
        ),
        family=family,
    )

    run_contract_case(
        root,
        ["-h"],
        expected_exit=0,
        expected_lines=help_lines,
        repeat_count=2,
    )

    run_error_contract_case(
        root,
        [],
        expected_exit=2,
        expected_stdout_lines=[],
        expected_stderr_normalized=MISSING_ARGUMENT_ERROR_BY_FAMILY[family],
        repeat_count=2,
    )

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

        write_text(expected, "alpha\nbeta\n")
        write_text(actual, "alpha\nbeta\n")

        run_error_contract_case(
            root,
            ["--mode", "text", str(expected)],
            expected_exit=2,
            expected_stdout_lines=[],
            expected_stderr_normalized=MISSING_ARGUMENT_ERROR_BY_FAMILY[family],
            repeat_count=2,
        )

        run_error_contract_case(
            root,
            ["--mode", "yaml", str(expected), str(actual)],
            expected_exit=2,
            expected_stdout_lines=[],
            expected_stderr_normalized=INVALID_MODE_ERROR_BY_FAMILY[family],
            repeat_count=2,
        )

        blob_a.write_bytes(b"zigux-artifact-diff")
        blob_b.write_bytes(b"zigux-artifact-diff")

        if family == "bytes":
            run_contract_case(
                root,
                ["--mode", "sha256", str(blob_a), str(blob_b)],
                expected_exit=0,
                expected_lines=[
                    "ARTIFACT_DIFF=pass",
                    "MODE=bytes",
                    f"EXPECTED={blob_a}",
                    f"ACTUAL={blob_b}",
                    f"SHA256={expected_sha256_hex(blob_a)}",
                ],
            )
        else:
            run_error_contract_case(
                root,
                ["--mode", "bytes", str(blob_a), str(blob_b)],
                expected_exit=2,
                expected_stdout_lines=[],
                expected_stderr_normalized=LEGACY_BOUNDARY_ERROR_BY_FAMILY[family],
                repeat_count=2,
            )

        run_contract_case(
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
        run_contract_case(
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

        run_contract_case(
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

        run_contract_case(
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

        run_contract_case(
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

        run_contract_case(
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

        run_contract_case(
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

        run_contract_case(
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

        run_contract_case(
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

        run_contract_case(
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

        run_contract_case(
            root,
            ["--mode", "json", str(invalid_expected_json), str(actual_json)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={invalid_expected_json}",
                f"ACTUAL={actual_json}",
                expected_json_error_line("EXPECTED", invalid_expected_json),
            ],
        )

        run_contract_case(
            root,
            ["--mode", "json", str(expected_json), str(invalid_actual_json)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={expected_json}",
                f"ACTUAL={invalid_actual_json}",
                expected_json_error_line("ACTUAL", invalid_actual_json),
            ],
        )

        run_contract_case(
            root,
            ["--mode", "json", str(invalid_expected_json), str(invalid_actual_json)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={invalid_expected_json}",
                f"ACTUAL={invalid_actual_json}",
                expected_json_error_line("EXPECTED", invalid_expected_json),
            ],
        )

        run_contract_case(
            root,
            ["--mode", hash_mode_arg, str(blob_a), str(blob_b)],
            expected_exit=0,
            expected_lines=[
                "ARTIFACT_DIFF=pass",
                f"MODE={hash_output_mode}",
                f"EXPECTED={blob_a}",
                f"ACTUAL={blob_b}",
                f"SHA256={expected_sha256_hex(blob_a)}",
            ],
        )

        run_contract_case(
            root,
            ["--mode", hash_mode_arg, str(missing), str(blob_b)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                f"MODE={hash_output_mode}",
                f"EXPECTED={missing}",
                f"ACTUAL={blob_b}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=True",
            ],
        )

        run_contract_case(
            root,
            ["--mode", hash_mode_arg, str(blob_a), str(missing)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                f"MODE={hash_output_mode}",
                f"EXPECTED={blob_a}",
                f"ACTUAL={missing}",
                "EXPECTED_EXISTS=True",
                "ACTUAL_EXISTS=False",
            ],
        )

        run_contract_case(
            root,
            ["--mode", hash_mode_arg, str(missing), str(other_missing)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                f"MODE={hash_output_mode}",
                f"EXPECTED={missing}",
                f"ACTUAL={other_missing}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=False",
            ],
        )

        blob_b.write_bytes(b"zigux-artifact-DRIFT")
        run_contract_case(
            root,
            ["--mode", hash_mode_arg, str(blob_a), str(blob_b)],
            expected_exit=1,
            expected_lines=[
                "ARTIFACT_DIFF=fail",
                f"MODE={hash_output_mode}",
                f"EXPECTED={blob_a}",
                f"ACTUAL={blob_b}",
                f"EXPECTED_SHA256={expected_sha256_hex(blob_a)}",
                f"ACTUAL_SHA256={expected_sha256_hex(blob_b)}",
            ],
            repeat_count=2,
        )

    summary_lines = expected_contract_summary_lines()
    for line in summary_lines:
        print(line)
    return 0


def expect_assertion(label: str, callback) -> None:
    try:
        callback()
    except AssertionError:
        return
    raise AssertionError(f"expected AssertionError for self-test case {label}")


def run_self_test() -> int:
    covered_cases: list[str] = []
    assert_catalog_shape()
    covered_cases.append("catalog_shape")

    assert_output_lines(BYTES_HELP_LINES, HELP_LINES_BY_FAMILY["bytes"], "bytes_help")
    covered_cases.append("family_help_bytes_round_trip")

    assert_output_lines(SHA256_HELP_LINES, HELP_LINES_BY_FAMILY["sha256"], "sha256_help")
    covered_cases.append("family_help_sha256_round_trip")

    if detect_helper_family_from_lines(BYTES_HELP_LINES) != "bytes":
        raise AssertionError("failed to detect bytes help family")
    covered_cases.append("family_detection_bytes")

    if detect_helper_family_from_lines(SHA256_HELP_LINES) != "sha256":
        raise AssertionError("failed to detect sha256 help family")
    covered_cases.append("family_detection_sha256")

    expect_assertion(
        "family_detection_unknown_rejected",
        lambda: detect_helper_family_from_lines(["usage: artifact_diff.py --mode yaml"]),
    )
    covered_cases.append("family_detection_unknown_rejected")

    assert_helper_self_test_output(
        HELPER_SELF_TEST_LINES_BY_FAMILY["bytes"], family="bytes"
    )
    covered_cases.append("helper_summary_bytes_round_trip")

    assert_helper_self_test_output(
        HELPER_SELF_TEST_LINES_BY_FAMILY["sha256"], family="sha256"
    )
    covered_cases.append("helper_summary_sha256_round_trip")

    bad_bytes_lines = list(HELPER_SELF_TEST_LINES_BY_FAMILY["bytes"])
    bad_bytes_lines[1] = "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=19"
    expect_assertion(
        "helper_summary_bytes_drift",
        lambda: assert_helper_self_test_output(bad_bytes_lines, family="bytes"),
    )
    covered_cases.append("helper_summary_bytes_drift")

    bad_sha256_lines = list(HELPER_SELF_TEST_LINES_BY_FAMILY["sha256"])
    bad_sha256_lines[2] = (
        "ARTIFACT_DIFF_SELF_TEST_CASES="
        "text_mismatch,text_pass,text_invalid_utf8_expected,"
        "text_invalid_utf8_actual,text_invalid_utf8_both,json_pass,"
        "json_mismatch,json_invalid_expected,json_invalid_actual,"
        "json_invalid_both,json_invalid_utf8_expected,"
        "json_invalid_utf8_actual,json_invalid_utf8_both,"
        "json_missing_expected,json_missing_actual,json_missing_both,"
        "sha256_pass,sha256_drift,text_missing_expected,"
        "text_missing_actual,text_missing_both,sha256_missing_expected,"
        "sha256_missing_actual,sha256_missing_both,invalid_mode_rejected"
    )
    expect_assertion(
        "helper_summary_sha256_drift",
        lambda: assert_helper_self_test_output(bad_sha256_lines, family="sha256"),
    )
    covered_cases.append("helper_summary_sha256_drift")

    if "are required unless --self-test is set" not in MISSING_ARGUMENT_ERROR_BY_FAMILY["bytes"]:
        raise AssertionError("bytes missing-argument contract drifted")
    if "are required unless --self-test is set" not in MISSING_ARGUMENT_ERROR_BY_FAMILY["sha256"]:
        raise AssertionError("sha256 missing-argument contract drifted")
    covered_cases.append("parser_error_bytes_round_trip")

    if "sha256" not in INVALID_MODE_ERROR_BY_FAMILY["sha256"]:
        raise AssertionError("sha256 parser error contract drifted")
    covered_cases.append("parser_error_sha256_round_trip")

    expect_assertion(
        "parser_error_drift",
        lambda: assert_output_lines(
            [INVALID_MODE_ERROR_BY_FAMILY["bytes"].replace("bytes", "binary")],
            [INVALID_MODE_ERROR_BY_FAMILY["bytes"]],
            "parser_error",
        ),
    )
    covered_cases.append("parser_error_drift")

    if "legacy_sha256_alias" not in HELPER_SELF_TEST_LINES_BY_FAMILY["bytes"][2]:
        raise AssertionError("bytes family legacy alias marker drifted")
    covered_cases.append("family_boundary_bytes_alias_round_trip")

    if "choice: 'bytes' (choose from text, json, sha256)" not in LEGACY_BOUNDARY_ERROR_BY_FAMILY["sha256"]:
        raise AssertionError("sha256 family bytes rejection drifted")
    covered_cases.append("family_boundary_sha256_rejected_round_trip")

    expect_assertion(
        "family_boundary_drift",
        lambda: assert_output_lines(
            [
                LEGACY_BOUNDARY_ERROR_BY_FAMILY["sha256"].replace(
                    "choice: 'bytes'",
                    "choice: 'binary'",
                )
            ],
            [LEGACY_BOUNDARY_ERROR_BY_FAMILY["sha256"]],
            "family_boundary",
        ),
    )
    covered_cases.append("family_boundary_drift")

    assert_contract_summary_output(expected_contract_summary_lines())
    covered_cases.append("contract_summary_round_trip")

    bad_base_count = expected_contract_summary_lines()
    bad_base_count[1] = "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=24"
    expect_assertion(
        "contract_summary_base_count_drift",
        lambda: assert_contract_summary_output(bad_base_count),
    )
    covered_cases.append("contract_summary_base_count_drift")

    bad_repeat_count = expected_contract_summary_lines()
    bad_repeat_count[3] = "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=4"
    expect_assertion(
        "contract_summary_repeat_count_drift",
        lambda: assert_contract_summary_output(bad_repeat_count),
    )
    covered_cases.append("contract_summary_repeat_count_drift")

    bad_case_count = expected_contract_summary_lines()
    bad_case_count[5] = "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=29"
    expect_assertion(
        "contract_summary_case_count_drift",
        lambda: assert_contract_summary_output(bad_case_count),
    )
    covered_cases.append("contract_summary_case_count_drift")

    if covered_cases != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(
            f"artifact-diff checker self-test catalog drifted: {covered_cases}"
        )

    print("ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass")
    print(f"ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT={len(EXPECTED_SELF_TEST_CASES)}")
    print(
        "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES="
        + ",".join(EXPECTED_SELF_TEST_CASES)
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the published artifact-diff CLI contract and summary shapes."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker self-tests without replaying the live artifact-diff helper.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root that contains scripts/zigux/artifact_diff.py",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if args.self_test:
        return run_self_test()
    return run_check(root)


if __name__ == "__main__":
    raise SystemExit(main())
