#!/usr/bin/env python3
"""Compare small deterministic artifacts for Zigux fixture-backed checks."""

from __future__ import annotations

import argparse
import difflib
import json
import tempfile
from pathlib import Path


MODE_CHOICES = ("json", "text", "bytes")
EXPECTED_SELF_TEST_CASE_COUNT = 7


class ArtifactDiffError(Exception):
    """Raised when an artifact cannot be decoded in the requested mode."""


def read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except FileNotFoundError as exc:
        raise SystemExit(f"missing artifact: {path}") from exc


def load_json(path: Path) -> object:
    try:
        return json.loads(read_bytes(path).decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ArtifactDiffError(f"{path}: invalid UTF-8 for json mode") from exc
    except json.JSONDecodeError as exc:
        raise ArtifactDiffError(f"{path}: invalid JSON at line {exc.lineno} column {exc.colno}") from exc


def load_text(path: Path) -> str:
    try:
        return read_bytes(path).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ArtifactDiffError(f"{path}: invalid UTF-8 for text mode") from exc


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def diff_lines(expected_label: str, expected_text: str, actual_label: str, actual_text: str) -> str:
    return "".join(
        difflib.unified_diff(
            expected_text.splitlines(keepends=True),
            actual_text.splitlines(keepends=True),
            fromfile=expected_label,
            tofile=actual_label,
        )
    )


def first_byte_mismatch(expected: bytes, actual: bytes) -> str:
    shared = min(len(expected), len(actual))
    for index in range(shared):
        if expected[index] != actual[index]:
            return (
                f"first differing byte at offset {index}: "
                f"expected=0x{expected[index]:02x} actual=0x{actual[index]:02x}"
            )
    return f"length differs: expected={len(expected)} actual={len(actual)}"


def compare_json(expected_path: Path, actual_path: Path) -> tuple[bool, str]:
    expected = load_json(expected_path)
    actual = load_json(actual_path)
    if expected == actual:
        return True, ""
    return False, diff_lines(
        expected_path.as_posix(),
        canonical_json(expected),
        actual_path.as_posix(),
        canonical_json(actual),
    )


def compare_text(expected_path: Path, actual_path: Path) -> tuple[bool, str]:
    expected = load_text(expected_path)
    actual = load_text(actual_path)
    if expected == actual:
        return True, ""
    return False, diff_lines(expected_path.as_posix(), expected, actual_path.as_posix(), actual)


def compare_bytes(expected_path: Path, actual_path: Path) -> tuple[bool, str]:
    expected = read_bytes(expected_path)
    actual = read_bytes(actual_path)
    if expected == actual:
        return True, ""
    return False, first_byte_mismatch(expected, actual)


def compare_artifacts(mode: str, expected_path: Path, actual_path: Path) -> tuple[bool, str]:
    if mode == "json":
        return compare_json(expected_path, actual_path)
    if mode == "text":
        return compare_text(expected_path, actual_path)
    if mode == "bytes":
        return compare_bytes(expected_path, actual_path)
    raise ValueError(f"unsupported mode: {mode}")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def write_bytes(path: Path, data: bytes) -> None:
    path.write_bytes(data)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_artifact_diff_") as tmp_dir:
        root = Path(tmp_dir)

        expected = root / "expected.json"
        actual = root / "actual.json"
        write_text(expected, '{\n  "beta": 2,\n  "alpha": 1\n}\n')
        write_text(actual, '{ "alpha": 1, "beta": 2 }\n')
        ok, detail = compare_artifacts("json", expected, actual)
        assert ok and detail == ""
        checks_run += 1

        write_text(actual, '{ "alpha": 1, "beta": 3 }\n')
        ok, detail = compare_artifacts("json", expected, actual)
        assert not ok and "--- " in detail and "+++ " in detail
        checks_run += 1

        write_text(expected, "alpha\nbeta\n")
        write_text(actual, "alpha\nbeta\n")
        ok, detail = compare_artifacts("text", expected, actual)
        assert ok and detail == ""
        checks_run += 1

        write_text(actual, "alpha\ngamma\n")
        ok, detail = compare_artifacts("text", expected, actual)
        assert not ok and "@@" in detail
        checks_run += 1

        write_bytes(expected, b"\x00\x01\x02")
        write_bytes(actual, b"\x00\x01\x02")
        ok, detail = compare_artifacts("bytes", expected, actual)
        assert ok and detail == ""
        checks_run += 1

        write_bytes(actual, b"\x00\x04\x02")
        ok, detail = compare_artifacts("bytes", expected, actual)
        assert not ok and "offset 1" in detail
        checks_run += 1

        write_text(actual, "{invalid-json}\n")
        try:
            compare_artifacts("json", expected, actual)
        except ArtifactDiffError as exc:
            assert "invalid JSON" in str(exc)
        else:
            raise AssertionError("invalid json should fail")
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("ARTIFACT_DIFF_SELF_TEST=pass")
    print(f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare deterministic artifact files for Zigux checks.")
    parser.add_argument("--mode", choices=MODE_CHOICES, default="text", help="Comparison mode to use")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("expected", nargs="?", type=Path, help="Expected artifact path")
    parser.add_argument("actual", nargs="?", type=Path, help="Actual artifact path")
    args = parser.parse_args()

    if args.self_test:
        if args.expected is not None or args.actual is not None:
            raise SystemExit("--self-test does not accept artifact paths")
        return run_self_test()

    if args.expected is None or args.actual is None:
        raise SystemExit("expected and actual artifact paths are required unless --self-test is used")

    try:
        ok, detail = compare_artifacts(args.mode, args.expected, args.actual)
    except ArtifactDiffError as exc:
        print("ARTIFACT_DIFF=error")
        print(f"ARTIFACT_DIFF_MODE={args.mode}")
        print(str(exc))
        return 2

    if ok:
        print("ARTIFACT_DIFF=pass")
        print(f"ARTIFACT_DIFF_MODE={args.mode}")
        print(f"ARTIFACT_DIFF_EXPECTED={args.expected}")
        print(f"ARTIFACT_DIFF_ACTUAL={args.actual}")
        return 0

    print("ARTIFACT_DIFF=fail")
    print(f"ARTIFACT_DIFF_MODE={args.mode}")
    print(detail.rstrip("\n"))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
