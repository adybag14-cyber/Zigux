#!/usr/bin/env python3
"""Compare two artifacts in a stable mode."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


MODE_CHOICES = ("text", "json", "bytes")
LEGACY_MODE_ALIASES = {"sha256": "bytes"}
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
INVALID_MODE_ERROR_TEMPLATE = (
    "usage: artifact_diff.py [-h] [--mode {{text,json,bytes}}] [--self-test] "
    "[expected] [actual] artifact_diff.py: error: argument --mode: invalid "
    "choice: {value!r} (choose from text, json, bytes)"
)
TOO_MANY_ARGUMENTS_ERROR = (
    "usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test] "
    "[expected] [actual] artifact_diff.py: error: expected exactly two positional "
    "arguments"
)
SELF_TEST_CASES = [
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
    "missing_mode_value_rejected",
    "missing_positional_arguments_rejected",
    "invalid_mode_rejected",
    "extra_positional_rejected",
]


@dataclass(frozen=True)
class ComparisonResult:
    ok: bool
    extra_lines: list[str]


def read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def load_text(path: Path) -> str:
    return read_bytes(path).decode("utf-8")


def format_utf8_error(path: Path, *, side: str, exc: UnicodeDecodeError) -> str:
    return f"{side}_UTF8_ERROR={path}:{exc.start}: {exc.reason}"


def canonical_json_bytes(path: Path, *, side: str) -> tuple[bytes | None, str | None]:
    try:
        text = load_text(path)
    except UnicodeDecodeError as exc:
        return None, format_utf8_error(path, side=side, exc=exc)
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"{side}_JSON_ERROR={path}:{exc.lineno}:{exc.colno}: {exc.msg}"
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8"), None


def missing_lines(expected: Path, actual: Path) -> list[str] | None:
    expected_exists = expected.exists()
    actual_exists = actual.exists()
    if expected_exists and actual_exists:
        return None
    return [
        f"EXPECTED_EXISTS={expected_exists}",
        f"ACTUAL_EXISTS={actual_exists}",
    ]


def compare_text(expected: Path, actual: Path) -> ComparisonResult:
    if read_bytes(expected) == read_bytes(actual):
        return ComparisonResult(ok=True, extra_lines=[])
    return ComparisonResult(ok=False, extra_lines=[])


def compare_json(expected: Path, actual: Path) -> ComparisonResult:
    expected_bytes, expected_error = canonical_json_bytes(expected, side="EXPECTED")
    if expected_error is not None:
        return ComparisonResult(ok=False, extra_lines=[expected_error])
    actual_bytes, actual_error = canonical_json_bytes(actual, side="ACTUAL")
    if actual_error is not None:
        return ComparisonResult(ok=False, extra_lines=[actual_error])
    assert expected_bytes is not None
    assert actual_bytes is not None
    if expected_bytes == actual_bytes:
        return ComparisonResult(ok=True, extra_lines=[])
    return ComparisonResult(ok=False, extra_lines=[])


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(read_bytes(path)).hexdigest()


def compare_bytes(expected: Path, actual: Path) -> ComparisonResult:
    expected_digest = sha256_hex(expected)
    actual_digest = sha256_hex(actual)
    if expected_digest == actual_digest:
        return ComparisonResult(ok=True, extra_lines=[f"SHA256={expected_digest}"])
    return ComparisonResult(
        ok=False,
        extra_lines=[
            f"EXPECTED_SHA256={expected_digest}",
            f"ACTUAL_SHA256={actual_digest}",
        ],
    )


def normalize_mode(mode: str) -> str:
    return LEGACY_MODE_ALIASES.get(mode, mode)


def compare(mode: str, expected: Path, actual: Path) -> ComparisonResult:
    mode = normalize_mode(mode)
    missing = missing_lines(expected, actual)
    if missing is not None:
        return ComparisonResult(ok=False, extra_lines=missing)
    if mode == "text":
        return compare_text(expected, actual)
    if mode == "json":
        return compare_json(expected, actual)
    if mode == "bytes":
        return compare_bytes(expected, actual)
    raise ValueError(f"unsupported mode: {mode}")


def emit_result(status: str, mode: str, expected: Path, actual: Path, extra_lines: list[str]) -> int:
    print(f"ARTIFACT_DIFF={status}")
    print(f"MODE={mode}")
    print(f"EXPECTED={expected}")
    print(f"ACTUAL={actual}")
    for line in extra_lines:
        print(line)
    return 0 if status == "pass" else 1


def run_parser_probe(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, __file__, *args],
        check=False,
        capture_output=True,
        text=True,
    )


def assert_case(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def run_self_test() -> int:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_artifact_diff_") as tmp_dir:
        root = Path(tmp_dir)
        expected = root / "expected.txt"
        actual = root / "actual.txt"
        missing = root / "missing.txt"
        other_missing = root / "other-missing.txt"
        expected_json = root / "expected.json"
        actual_json = root / "actual.json"
        actual_json_mismatch = root / "actual-mismatch.json"
        invalid_expected_json = root / "invalid-expected.json"
        invalid_actual_json = root / "invalid-actual.json"
        invalid_expected_utf8_json = root / "invalid-expected-utf8.json"
        invalid_actual_utf8_json = root / "invalid-actual-utf8.json"
        blob_a = root / "blob-a.bin"
        blob_b = root / "blob-b.bin"

        expected.write_text("alpha\nbeta\n", encoding="utf-8", newline="\n")
        actual.write_text("alpha\nbeta\n", encoding="utf-8", newline="\n")
        assert_case(compare("text", expected, actual).ok, "text_pass")
        covered.append("text_pass")

        actual.write_text("alpha\nBETA\n", encoding="utf-8", newline="\n")
        assert_case(not compare("text", expected, actual).ok, "text_mismatch")
        covered.append("text_mismatch")

        expected_json.write_text('{"alpha": 1, "beta": [2, 3]}\n', encoding="utf-8", newline="\n")
        actual_json.write_text('{\n "beta": [2, 3],\n "alpha": 1\n}\n', encoding="utf-8", newline="\n")
        assert_case(compare("json", expected_json, actual_json).ok, "json_pass")
        covered.append("json_pass")

        actual_json_mismatch.write_text('{"alpha": 1, "beta": [2, 4]}\n', encoding="utf-8", newline="\n")
        assert_case(not compare("json", expected_json, actual_json_mismatch).ok, "json_mismatch")
        covered.append("json_mismatch")

        invalid_expected_json.write_text('{"alpha": 1,\n', encoding="utf-8", newline="\n")
        invalid_actual_json.write_text('{"alpha": 1,\n', encoding="utf-8", newline="\n")
        invalid_expected_utf8_json.write_bytes(b"\xff{\n")
        invalid_actual_utf8_json.write_bytes(b"\xff{\n")
        assert_case(
            compare("json", invalid_expected_json, actual_json).extra_lines
            == [f"EXPECTED_JSON_ERROR={invalid_expected_json}:2:1: Expecting property name enclosed in double quotes"],
            "json_invalid_expected",
        )
        assert_case(
            compare("json", invalid_expected_utf8_json, actual_json).extra_lines
            == [f"EXPECTED_UTF8_ERROR={invalid_expected_utf8_json}:0: invalid start byte"],
            "json_invalid_expected",
        )
        covered.append("json_invalid_expected")

        assert_case(
            compare("json", expected_json, invalid_actual_json).extra_lines
            == [f"ACTUAL_JSON_ERROR={invalid_actual_json}:2:1: Expecting property name enclosed in double quotes"],
            "json_invalid_actual",
        )
        assert_case(
            compare("json", expected_json, invalid_actual_utf8_json).extra_lines
            == [f"ACTUAL_UTF8_ERROR={invalid_actual_utf8_json}:0: invalid start byte"],
            "json_invalid_actual",
        )
        covered.append("json_invalid_actual")

        assert_case(
            compare("json", invalid_expected_json, invalid_actual_json).extra_lines
            == [f"EXPECTED_JSON_ERROR={invalid_expected_json}:2:1: Expecting property name enclosed in double quotes"],
            "json_invalid_both",
        )
        assert_case(
            compare("json", invalid_expected_utf8_json, invalid_actual_utf8_json).extra_lines
            == [f"EXPECTED_UTF8_ERROR={invalid_expected_utf8_json}:0: invalid start byte"],
            "json_invalid_both",
        )
        covered.append("json_invalid_both")

        assert_case(
            compare("json", missing, actual_json).extra_lines == ["EXPECTED_EXISTS=False", "ACTUAL_EXISTS=True"],
            "json_missing_expected",
        )
        covered.append("json_missing_expected")

        assert_case(
            compare("json", expected_json, missing).extra_lines == ["EXPECTED_EXISTS=True", "ACTUAL_EXISTS=False"],
            "json_missing_actual",
        )
        covered.append("json_missing_actual")

        assert_case(
            compare("json", missing, other_missing).extra_lines == ["EXPECTED_EXISTS=False", "ACTUAL_EXISTS=False"],
            "json_missing_both",
        )
        covered.append("json_missing_both")

        blob_a.write_bytes(b"zigux-artifact-diff")
        blob_b.write_bytes(b"zigux-artifact-diff")
        bytes_pass = compare("bytes", blob_a, blob_b)
        assert_case(
            bytes_pass.ok and bytes_pass.extra_lines == ["SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576"],
            "bytes_pass",
        )
        covered.append("bytes_pass")

        blob_b.write_bytes(b"zigux-artifact-DRIFT")
        assert_case(
            compare("bytes", blob_a, blob_b).extra_lines
            == [
                "EXPECTED_SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576",
                "ACTUAL_SHA256=bfc83f8f1f4369ce3cfabfdff0699ae3bf7a15b89f1702b690e56c6f35f1ee94",
            ],
            "bytes_drift",
        )
        covered.append("bytes_drift")

        assert_case(
            compare("text", missing, actual).extra_lines == ["EXPECTED_EXISTS=False", "ACTUAL_EXISTS=True"],
            "text_missing_expected",
        )
        covered.append("text_missing_expected")

        assert_case(
            compare("text", expected, missing).extra_lines == ["EXPECTED_EXISTS=True", "ACTUAL_EXISTS=False"],
            "text_missing_actual",
        )
        covered.append("text_missing_actual")

        assert_case(
            compare("text", missing, other_missing).extra_lines == ["EXPECTED_EXISTS=False", "ACTUAL_EXISTS=False"],
            "text_missing_both",
        )
        covered.append("text_missing_both")

        assert_case(
            compare("bytes", missing, blob_a).extra_lines == ["EXPECTED_EXISTS=False", "ACTUAL_EXISTS=True"],
            "bytes_missing_expected",
        )
        covered.append("bytes_missing_expected")

        assert_case(
            compare("bytes", blob_a, missing).extra_lines == ["EXPECTED_EXISTS=True", "ACTUAL_EXISTS=False"],
            "bytes_missing_actual",
        )
        covered.append("bytes_missing_actual")

        assert_case(
            compare("bytes", missing, other_missing).extra_lines == ["EXPECTED_EXISTS=False", "ACTUAL_EXISTS=False"],
            "bytes_missing_both",
        )
        covered.append("bytes_missing_both")

        legacy_alias = run_parser_probe(["--mode", "sha256", str(blob_a), str(blob_a)])
        assert_case(legacy_alias.returncode == 0, "legacy_sha256_alias")
        assert_case("ARTIFACT_DIFF=pass" in legacy_alias.stdout, "legacy_sha256_alias")
        assert_case("MODE=bytes" in legacy_alias.stdout, "legacy_sha256_alias")
        covered.append("legacy_sha256_alias")

        missing_mode_value = run_parser_probe(["--mode"])
        assert_case(missing_mode_value.returncode == 2, "missing_mode_value_rejected")
        assert_case(
            " ".join(missing_mode_value.stderr.split()) == MISSING_ARGUMENT_ERROR,
            "missing_mode_value_rejected",
        )
        covered.append("missing_mode_value_rejected")

        missing_positionals = run_parser_probe(["--mode", "text"])
        assert_case(missing_positionals.returncode == 2, "missing_positional_arguments_rejected")
        assert_case(
            " ".join(missing_positionals.stderr.split()) == MISSING_ARGUMENT_ERROR,
            "missing_positional_arguments_rejected",
        )
        covered.append("missing_positional_arguments_rejected")

        invalid_mode = run_parser_probe(["--mode", "yaml", str(expected), str(actual)])
        assert_case(invalid_mode.returncode == 2, "invalid_mode_rejected")
        covered.append("invalid_mode_rejected")

        extra_positional = run_parser_probe(
            ["--mode", "text", str(expected), str(actual), str(missing)]
        )
        assert_case(extra_positional.returncode == 2, "extra_positional_rejected")
        assert_case(
            " ".join(extra_positional.stderr.split()) == TOO_MANY_ARGUMENTS_ERROR,
            "extra_positional_rejected",
        )
        covered.append("extra_positional_rejected")

    assert_case(covered == SELF_TEST_CASES, "self_test_case_order")
    print("ARTIFACT_DIFF_SELF_TEST=pass")
    print(f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print("ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:
    if argv == ["--help"] or argv == ["-h"]:
        print("\n".join(HELP_LINES))
        return 0

    self_test = False
    mode: str | None = None
    positionals: list[str] = []
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--self-test":
            self_test = True
            index += 1
            continue
        if arg == "--mode":
            if index + 1 >= len(argv):
                print(MISSING_ARGUMENT_ERROR, file=sys.stderr)
                return 2
            mode = argv[index + 1]
            index += 2
            continue
        positionals.append(arg)
        index += 1

    if mode is not None and mode not in MODE_CHOICES:
        if mode in LEGACY_MODE_ALIASES:
            mode = LEGACY_MODE_ALIASES[mode]
        else:
            print(INVALID_MODE_ERROR_TEMPLATE.format(value=mode), file=sys.stderr)
            return 2

    expected = positionals[0] if len(positionals) >= 1 else None
    actual = positionals[1] if len(positionals) >= 2 else None
    if len(positionals) > 2:
        print(TOO_MANY_ARGUMENTS_ERROR, file=sys.stderr)
        return 2
    return self_test, mode, expected, actual


def main() -> int:
    parsed = parse_args(sys.argv[1:])
    if isinstance(parsed, int):
        return parsed

    self_test, mode, expected_text, actual_text = parsed
    if self_test:
        return run_self_test()

    if mode is None or expected_text is None or actual_text is None:
        print(MISSING_ARGUMENT_ERROR, file=sys.stderr)
        return 2

    expected = Path(expected_text)
    actual = Path(actual_text)
    result = compare(mode, expected, actual)
    return emit_result("pass" if result.ok else "fail", mode, expected, actual, result.extra_lines)


if __name__ == "__main__":
    raise SystemExit(main())