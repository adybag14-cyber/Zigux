#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile


def read_text(path: Path, *, mode_label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path}: invalid UTF-8 for {mode_label} mode") from exc


def canonical_json(path: Path):
    try:
        return json.loads(read_text(path, mode_label="json"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}:{exc.lineno}:{exc.colno}: {exc.msg}") from exc


def sha256_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_artifacts(mode: str, expected: Path, actual: Path) -> tuple[bool, dict[str, object]]:
    details: dict[str, object] = {
        "mode": mode,
        "expected": str(expected),
        "actual": str(actual),
    }

    if not expected.exists() or not actual.exists():
        details["expected_exists"] = expected.exists()
        details["actual_exists"] = actual.exists()
        return False, details

    if mode == "text":
        try:
            expected_value = read_text(expected, mode_label="text")
        except ValueError as exc:
            details["expected_text_error"] = str(exc)
            return False, details
        try:
            actual_value = read_text(actual, mode_label="text")
        except ValueError as exc:
            details["actual_text_error"] = str(exc)
            return False, details
    elif mode == "json":
        try:
            expected_value = canonical_json(expected)
        except ValueError as exc:
            details["expected_json_error"] = str(exc)
            return False, details
        try:
            actual_value = canonical_json(actual)
        except ValueError as exc:
            details["actual_json_error"] = str(exc)
            return False, details
    elif mode == "sha256":
        expected_value = sha256_digest(expected)
        actual_value = sha256_digest(actual)
    else:
        raise ValueError(f"unsupported artifact diff mode: {mode}")

    if mode == "sha256":
        details["expected_sha256"] = expected_value
        details["actual_sha256"] = actual_value

    return expected_value == actual_value, details


def render_result_lines(matched: bool, details: dict[str, object]) -> list[str]:
    lines = ["ARTIFACT_DIFF=pass" if matched else "ARTIFACT_DIFF=fail"]
    if "mode" in details:
        lines.append(f"MODE={details['mode']}")
    if "expected" in details:
        lines.append(f"EXPECTED={details['expected']}")
    if "actual" in details:
        lines.append(f"ACTUAL={details['actual']}")

    if matched:
        if "expected_sha256" in details:
            lines.append(f"SHA256={details['expected_sha256']}")
        return lines

    if "expected_exists" in details:
        lines.append(f"EXPECTED_EXISTS={details['expected_exists']}")
    if "actual_exists" in details:
        lines.append(f"ACTUAL_EXISTS={details['actual_exists']}")
    if "expected_text_error" in details:
        lines.append(f"EXPECTED_TEXT_ERROR={details['expected_text_error']}")
    if "actual_text_error" in details:
        lines.append(f"ACTUAL_TEXT_ERROR={details['actual_text_error']}")
    if "expected_json_error" in details:
        lines.append(f"EXPECTED_JSON_ERROR={details['expected_json_error']}")
    if "actual_json_error" in details:
        lines.append(f"ACTUAL_JSON_ERROR={details['actual_json_error']}")
    if "expected_sha256" in details:
        lines.append(f"EXPECTED_SHA256={details['expected_sha256']}")
    if "actual_sha256" in details:
        lines.append(f"ACTUAL_SHA256={details['actual_sha256']}")
    return lines


def emit_result(matched: bool, details: dict[str, object]) -> int:
    for line in render_result_lines(matched, details):
        print(line)
    return 0 if matched else 1


def capture_emit_result(matched: bool, details: dict[str, object]) -> tuple[int, list[str]]:
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        exit_code = emit_result(matched, details)
    return exit_code, stream.getvalue().splitlines()


EXPECTED_SELF_TEST_CASES = [
    "text_pass",
    "text_mismatch",
    "text_invalid_utf8_expected",
    "text_invalid_utf8_actual",
    "text_invalid_utf8_both",
    "json_pass",
    "json_mismatch",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "json_invalid_utf8_expected",
    "json_invalid_utf8_actual",
    "json_invalid_utf8_both",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "sha256_pass",
    "sha256_drift",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "sha256_missing_expected",
    "sha256_missing_actual",
    "sha256_missing_both",
    "invalid_mode_rejected",
]


def assert_self_test_catalog_shape() -> None:
    if len(set(EXPECTED_SELF_TEST_CASES)) != len(EXPECTED_SELF_TEST_CASES):
        raise AssertionError(
            f"artifact-diff self-test cases must stay unique: {EXPECTED_SELF_TEST_CASES}"
        )


def assert_detail_shape(
    details: dict[str, object],
    *,
    mode: str,
    expected: Path,
    actual: Path,
    expected_exists: bool | None = None,
    actual_exists: bool | None = None,
    expected_text_error: bool = False,
    actual_text_error: bool = False,
    expected_json_error: bool = False,
    actual_json_error: bool = False,
    sha256: bool = False,
) -> None:
    assert details["mode"] == mode
    assert details["expected"] == str(expected)
    assert details["actual"] == str(actual)

    shape_expectations = {
        "expected_exists": expected_exists is not None,
        "actual_exists": actual_exists is not None,
        "expected_text_error": expected_text_error,
        "actual_text_error": actual_text_error,
        "expected_json_error": expected_json_error,
        "actual_json_error": actual_json_error,
        "expected_sha256": sha256,
        "actual_sha256": sha256,
    }
    for key, should_exist in shape_expectations.items():
        assert (key in details) is should_exist, (key, details)

    if expected_exists is not None:
        assert details["expected_exists"] is expected_exists
    if actual_exists is not None:
        assert details["actual_exists"] is actual_exists


def assert_repeatable_case(
    mode: str,
    expected: Path,
    actual: Path,
    expected_matched: bool,
    expected_lines: list[str],
    *,
    repeat_count: int = 2,
) -> None:
    if repeat_count < 1:
        raise ValueError(f"repeat_count must be positive, got {repeat_count}")

    expected_exit_code = 0 if expected_matched else 1
    for _ in range(repeat_count):
        matched, details = compare_artifacts(mode, expected, actual)
        assert matched is expected_matched
        assert render_result_lines(matched, details) == expected_lines
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == expected_exit_code
        assert lines == expected_lines


def run_self_test() -> int:
    assert_self_test_catalog_shape()
    covered_cases: list[str] = []

    with tempfile.TemporaryDirectory(prefix="zigux_artifact_diff_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        text_a = tmp_dir / "text-a.txt"
        text_b = tmp_dir / "text-b.txt"
        invalid_text = tmp_dir / "text-invalid.txt"
        other_invalid_text = tmp_dir / "text-other-invalid.txt"
        json_a = tmp_dir / "json-a.json"
        json_b = tmp_dir / "json-b.json"
        invalid_json = tmp_dir / "json-invalid.json"
        other_invalid_json = tmp_dir / "json-other-invalid.json"
        invalid_json_utf8 = tmp_dir / "json-invalid-utf8.json"
        other_invalid_json_utf8 = tmp_dir / "json-other-invalid-utf8.json"
        blob_a = tmp_dir / "blob-a.bin"
        blob_b = tmp_dir / "blob-b.bin"
        missing = tmp_dir / "missing.txt"
        other_missing = tmp_dir / "other-missing.txt"

        text_a.write_text("alpha\nbeta\n", encoding="utf-8", newline="\n")
        text_b.write_text("alpha\nbeta\n", encoding="utf-8", newline="\n")
        matched, details = compare_artifacts("text", text_a, text_b)
        assert matched
        assert_detail_shape(details, mode="text", expected=text_a, actual=text_b)
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=pass",
            "MODE=text",
            f"EXPECTED={text_a}",
            f"ACTUAL={text_b}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 0
        assert lines == render_result_lines(matched, details)
        covered_cases.append("text_pass")
        assert_repeatable_case(
            "text",
            text_a,
            text_b,
            True,
            render_result_lines(matched, details),
        )

        text_b.write_text("alpha\nBETA\n", encoding="utf-8", newline="\n")
        matched, details = compare_artifacts("text", text_a, text_b)
        assert not matched
        assert_detail_shape(details, mode="text", expected=text_a, actual=text_b)
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=text",
            f"EXPECTED={text_a}",
            f"ACTUAL={text_b}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("text_mismatch")
        assert_repeatable_case(
            "text",
            text_a,
            text_b,
            False,
            render_result_lines(matched, details),
        )

        invalid_text.write_bytes(b"alpha\xffbeta")
        matched, details = compare_artifacts("text", invalid_text, text_a)
        assert not matched
        assert_detail_shape(
            details,
            mode="text",
            expected=invalid_text,
            actual=text_a,
            expected_text_error=True,
        )
        assert details["expected_text_error"] == f"{invalid_text}: invalid UTF-8 for text mode"
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=text",
            f"EXPECTED={invalid_text}",
            f"ACTUAL={text_a}",
            f"EXPECTED_TEXT_ERROR={details['expected_text_error']}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("text_invalid_utf8_expected")
        assert_repeatable_case(
            "text",
            invalid_text,
            text_a,
            False,
            render_result_lines(matched, details),
        )

        matched, details = compare_artifacts("text", text_a, invalid_text)
        assert not matched
        assert_detail_shape(
            details,
            mode="text",
            expected=text_a,
            actual=invalid_text,
            actual_text_error=True,
        )
        assert details["actual_text_error"] == f"{invalid_text}: invalid UTF-8 for text mode"
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=text",
            f"EXPECTED={text_a}",
            f"ACTUAL={invalid_text}",
            f"ACTUAL_TEXT_ERROR={details['actual_text_error']}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("text_invalid_utf8_actual")
        assert_repeatable_case(
            "text",
            text_a,
            invalid_text,
            False,
            render_result_lines(matched, details),
        )

        other_invalid_text.write_bytes(b"\xfeomega")
        matched, details = compare_artifacts("text", invalid_text, other_invalid_text)
        assert not matched
        assert_detail_shape(
            details,
            mode="text",
            expected=invalid_text,
            actual=other_invalid_text,
            expected_text_error=True,
        )
        assert details["expected_text_error"] == f"{invalid_text}: invalid UTF-8 for text mode"
        assert "actual_text_error" not in details
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=text",
            f"EXPECTED={invalid_text}",
            f"ACTUAL={other_invalid_text}",
            f"EXPECTED_TEXT_ERROR={details['expected_text_error']}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("text_invalid_utf8_both")
        assert_repeatable_case(
            "text",
            invalid_text,
            other_invalid_text,
            False,
            render_result_lines(matched, details),
        )

        json_a.write_text('{"alpha": 1, "beta": [2, 3]}\n', encoding="utf-8", newline="\n")
        json_b.write_text('{\n  "beta": [2, 3],\n  "alpha": 1\n}\n', encoding="utf-8", newline="\n")
        matched, details = compare_artifacts("json", json_a, json_b)
        assert matched
        assert_detail_shape(details, mode="json", expected=json_a, actual=json_b)
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=pass",
            "MODE=json",
            f"EXPECTED={json_a}",
            f"ACTUAL={json_b}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 0
        assert lines == render_result_lines(matched, details)
        covered_cases.append("json_pass")
        assert_repeatable_case(
            "json",
            json_a,
            json_b,
            True,
            render_result_lines(matched, details),
        )

        json_b.write_text('{"alpha": 1, "beta": [2, 4]}\n', encoding="utf-8", newline="\n")
        matched, details = compare_artifacts("json", json_a, json_b)
        assert not matched
        assert_detail_shape(details, mode="json", expected=json_a, actual=json_b)
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=json",
            f"EXPECTED={json_a}",
            f"ACTUAL={json_b}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("json_mismatch")
        assert_repeatable_case(
            "json",
            json_a,
            json_b,
            False,
            render_result_lines(matched, details),
        )

        invalid_json.write_text('{"alpha": 1,\n', encoding="utf-8", newline="\n")
        matched, details = compare_artifacts("json", invalid_json, json_a)
        assert not matched
        assert_detail_shape(
            details,
            mode="json",
            expected=invalid_json,
            actual=json_a,
            expected_json_error=True,
        )
        assert str(invalid_json) in details["expected_json_error"]
        assert "line 2 column 1" not in details["expected_json_error"]
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=json",
            f"EXPECTED={invalid_json}",
            f"ACTUAL={json_a}",
            f"EXPECTED_JSON_ERROR={details['expected_json_error']}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("json_invalid_expected")
        assert_repeatable_case(
            "json",
            invalid_json,
            json_a,
            False,
            render_result_lines(matched, details),
        )

        matched, details = compare_artifacts("json", json_a, invalid_json)
        assert not matched
        assert_detail_shape(
            details,
            mode="json",
            expected=json_a,
            actual=invalid_json,
            actual_json_error=True,
        )
        assert str(invalid_json) in details["actual_json_error"]
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=json",
            f"EXPECTED={json_a}",
            f"ACTUAL={invalid_json}",
            f"ACTUAL_JSON_ERROR={details['actual_json_error']}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("json_invalid_actual")
        assert_repeatable_case(
            "json",
            json_a,
            invalid_json,
            False,
            render_result_lines(matched, details),
        )

        other_invalid_json.write_text('{"beta": [1,\n', encoding="utf-8", newline="\n")
        matched, details = compare_artifacts("json", invalid_json, other_invalid_json)
        assert not matched
        assert_detail_shape(
            details,
            mode="json",
            expected=invalid_json,
            actual=other_invalid_json,
            expected_json_error=True,
        )
        assert str(invalid_json) in details["expected_json_error"]
        assert "actual_json_error" not in details
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=json",
            f"EXPECTED={invalid_json}",
            f"ACTUAL={other_invalid_json}",
            f"EXPECTED_JSON_ERROR={details['expected_json_error']}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("json_invalid_both")
        assert_repeatable_case(
            "json",
            invalid_json,
            other_invalid_json,
            False,
            render_result_lines(matched, details),
        )

        invalid_json_utf8.write_bytes(b'{"alpha":"\xff"}')
        matched, details = compare_artifacts("json", invalid_json_utf8, json_a)
        assert not matched
        assert_detail_shape(
            details,
            mode="json",
            expected=invalid_json_utf8,
            actual=json_a,
            expected_json_error=True,
        )
        assert details["expected_json_error"] == f"{invalid_json_utf8}: invalid UTF-8 for json mode"
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=json",
            f"EXPECTED={invalid_json_utf8}",
            f"ACTUAL={json_a}",
            f"EXPECTED_JSON_ERROR={details['expected_json_error']}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("json_invalid_utf8_expected")
        assert_repeatable_case(
            "json",
            invalid_json_utf8,
            json_a,
            False,
            render_result_lines(matched, details),
        )

        matched, details = compare_artifacts("json", json_a, invalid_json_utf8)
        assert not matched
        assert_detail_shape(
            details,
            mode="json",
            expected=json_a,
            actual=invalid_json_utf8,
            actual_json_error=True,
        )
        assert details["actual_json_error"] == f"{invalid_json_utf8}: invalid UTF-8 for json mode"
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=json",
            f"EXPECTED={json_a}",
            f"ACTUAL={invalid_json_utf8}",
            f"ACTUAL_JSON_ERROR={details['actual_json_error']}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("json_invalid_utf8_actual")
        assert_repeatable_case(
            "json",
            json_a,
            invalid_json_utf8,
            False,
            render_result_lines(matched, details),
        )

        other_invalid_json_utf8.write_bytes(b'{"beta":"\xfe"}')
        matched, details = compare_artifacts("json", invalid_json_utf8, other_invalid_json_utf8)
        assert not matched
        assert_detail_shape(
            details,
            mode="json",
            expected=invalid_json_utf8,
            actual=other_invalid_json_utf8,
            expected_json_error=True,
        )
        assert details["expected_json_error"] == f"{invalid_json_utf8}: invalid UTF-8 for json mode"
        assert "actual_json_error" not in details
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=json",
            f"EXPECTED={invalid_json_utf8}",
            f"ACTUAL={other_invalid_json_utf8}",
            f"EXPECTED_JSON_ERROR={details['expected_json_error']}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("json_invalid_utf8_both")
        assert_repeatable_case(
            "json",
            invalid_json_utf8,
            other_invalid_json_utf8,
            False,
            render_result_lines(matched, details),
        )

        matched, details = compare_artifacts("json", missing, json_a)
        assert not matched
        assert_detail_shape(
            details,
            mode="json",
            expected=missing,
            actual=json_a,
            expected_exists=False,
            actual_exists=True,
        )
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=json",
            f"EXPECTED={missing}",
            f"ACTUAL={json_a}",
            "EXPECTED_EXISTS=False",
            "ACTUAL_EXISTS=True",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("json_missing_expected")
        assert_repeatable_case(
            "json",
            missing,
            json_a,
            False,
            render_result_lines(matched, details),
        )

        matched, details = compare_artifacts("json", json_a, missing)
        assert not matched
        assert_detail_shape(
            details,
            mode="json",
            expected=json_a,
            actual=missing,
            expected_exists=True,
            actual_exists=False,
        )
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=json",
            f"EXPECTED={json_a}",
            f"ACTUAL={missing}",
            "EXPECTED_EXISTS=True",
            "ACTUAL_EXISTS=False",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("json_missing_actual")
        assert_repeatable_case(
            "json",
            json_a,
            missing,
            False,
            render_result_lines(matched, details),
        )

        matched, details = compare_artifacts("json", missing, other_missing)
        assert not matched
        assert_detail_shape(
            details,
            mode="json",
            expected=missing,
            actual=other_missing,
            expected_exists=False,
            actual_exists=False,
        )
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=json",
            f"EXPECTED={missing}",
            f"ACTUAL={other_missing}",
            "EXPECTED_EXISTS=False",
            "ACTUAL_EXISTS=False",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("json_missing_both")
        assert_repeatable_case(
            "json",
            missing,
            other_missing,
            False,
            render_result_lines(matched, details),
        )

        blob_a.write_bytes(b"zigux-artifact-diff")
        blob_b.write_bytes(b"zigux-artifact-diff")
        matched, details = compare_artifacts("sha256", blob_a, blob_b)
        assert matched
        assert_detail_shape(details, mode="sha256", expected=blob_a, actual=blob_b, sha256=True)
        assert details["expected_sha256"] == details["actual_sha256"]
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=pass",
            "MODE=sha256",
            f"EXPECTED={blob_a}",
            f"ACTUAL={blob_b}",
            f"SHA256={details['expected_sha256']}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 0
        assert lines == render_result_lines(matched, details)
        covered_cases.append("sha256_pass")
        assert_repeatable_case(
            "sha256",
            blob_a,
            blob_b,
            True,
            render_result_lines(matched, details),
        )

        blob_b.write_bytes(b"zigux-artifact-DRIFT")
        matched, details = compare_artifacts("sha256", blob_a, blob_b)
        assert not matched
        assert_detail_shape(details, mode="sha256", expected=blob_a, actual=blob_b, sha256=True)
        assert details["expected_sha256"] != details["actual_sha256"]
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=sha256",
            f"EXPECTED={blob_a}",
            f"ACTUAL={blob_b}",
            f"EXPECTED_SHA256={details['expected_sha256']}",
            f"ACTUAL_SHA256={details['actual_sha256']}",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("sha256_drift")
        assert_repeatable_case(
            "sha256",
            blob_a,
            blob_b,
            False,
            render_result_lines(matched, details),
        )

        matched, details = compare_artifacts("text", missing, text_a)
        assert not matched
        assert_detail_shape(
            details,
            mode="text",
            expected=missing,
            actual=text_a,
            expected_exists=False,
            actual_exists=True,
        )
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=text",
            f"EXPECTED={missing}",
            f"ACTUAL={text_a}",
            "EXPECTED_EXISTS=False",
            "ACTUAL_EXISTS=True",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("text_missing_expected")
        assert_repeatable_case(
            "text",
            missing,
            text_a,
            False,
            render_result_lines(matched, details),
        )

        matched, details = compare_artifacts("text", text_a, missing)
        assert not matched
        assert_detail_shape(
            details,
            mode="text",
            expected=text_a,
            actual=missing,
            expected_exists=True,
            actual_exists=False,
        )
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=text",
            f"EXPECTED={text_a}",
            f"ACTUAL={missing}",
            "EXPECTED_EXISTS=True",
            "ACTUAL_EXISTS=False",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("text_missing_actual")
        assert_repeatable_case(
            "text",
            text_a,
            missing,
            False,
            render_result_lines(matched, details),
        )

        matched, details = compare_artifacts("text", missing, other_missing)
        assert not matched
        assert_detail_shape(
            details,
            mode="text",
            expected=missing,
            actual=other_missing,
            expected_exists=False,
            actual_exists=False,
        )
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=text",
            f"EXPECTED={missing}",
            f"ACTUAL={other_missing}",
            "EXPECTED_EXISTS=False",
            "ACTUAL_EXISTS=False",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("text_missing_both")
        assert_repeatable_case(
            "text",
            missing,
            other_missing,
            False,
            render_result_lines(matched, details),
        )

        matched, details = compare_artifacts("sha256", missing, blob_a)
        assert not matched
        assert_detail_shape(
            details,
            mode="sha256",
            expected=missing,
            actual=blob_a,
            expected_exists=False,
            actual_exists=True,
        )
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=sha256",
            f"EXPECTED={missing}",
            f"ACTUAL={blob_a}",
            "EXPECTED_EXISTS=False",
            "ACTUAL_EXISTS=True",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("sha256_missing_expected")
        assert_repeatable_case(
            "sha256",
            missing,
            blob_a,
            False,
            render_result_lines(matched, details),
        )

        matched, details = compare_artifacts("sha256", blob_a, missing)
        assert not matched
        assert_detail_shape(
            details,
            mode="sha256",
            expected=blob_a,
            actual=missing,
            expected_exists=True,
            actual_exists=False,
        )
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=sha256",
            f"EXPECTED={blob_a}",
            f"ACTUAL={missing}",
            "EXPECTED_EXISTS=True",
            "ACTUAL_EXISTS=False",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("sha256_missing_actual")
        assert_repeatable_case(
            "sha256",
            blob_a,
            missing,
            False,
            render_result_lines(matched, details),
        )

        matched, details = compare_artifacts("sha256", missing, other_missing)
        assert not matched
        assert_detail_shape(
            details,
            mode="sha256",
            expected=missing,
            actual=other_missing,
            expected_exists=False,
            actual_exists=False,
        )
        assert render_result_lines(matched, details) == [
            "ARTIFACT_DIFF=fail",
            "MODE=sha256",
            f"EXPECTED={missing}",
            f"ACTUAL={other_missing}",
            "EXPECTED_EXISTS=False",
            "ACTUAL_EXISTS=False",
        ]
        exit_code, lines = capture_emit_result(matched, details)
        assert exit_code == 1
        assert lines == render_result_lines(matched, details)
        covered_cases.append("sha256_missing_both")
        assert_repeatable_case(
            "sha256",
            missing,
            other_missing,
            False,
            render_result_lines(matched, details),
        )

        try:
            compare_artifacts("yaml", text_a, text_b)
        except ValueError as exc:
            assert str(exc) == "unsupported artifact diff mode: yaml"
        else:
            raise AssertionError("expected compare_artifacts() to reject unsupported modes")
        covered_cases.append("invalid_mode_rejected")

    if covered_cases != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(
            "artifact-diff self-test case catalog drifted: "
            f"expected {EXPECTED_SELF_TEST_CASES}, got {covered_cases}"
        )

    print("ARTIFACT_DIFF_SELF_TEST=pass")
    print(f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(EXPECTED_SELF_TEST_CASES)}")
    print("ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(EXPECTED_SELF_TEST_CASES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two artifacts in a stable mode.")
    parser.add_argument("--mode", choices=["text", "json", "sha256"])
    parser.add_argument("--self-test", action="store_true", help="Run built-in deterministic comparison checks.")
    parser.add_argument("expected", nargs="?")
    parser.add_argument("actual", nargs="?")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.mode is None or args.expected is None or args.actual is None:
        parser.error("--mode, expected, and actual are required unless --self-test is set")

    matched, details = compare_artifacts(args.mode, Path(args.expected), Path(args.actual))
    return emit_result(matched, details)


if __name__ == "__main__":
    raise SystemExit(main())
