#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json_value(path: Path):
    try:
        return json.loads(_read_text(path))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}:{exc.lineno}:{exc.colno}: {exc.msg}") from exc


def _sha256(path: Path) -> str:
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
        expected_value = _read_text(expected)
        actual_value = _read_text(actual)
    elif mode == "json":
        try:
            expected_value = _json_value(expected)
        except ValueError as exc:
            details["expected_json_error"] = str(exc)
            return False, details
        try:
            actual_value = _json_value(actual)
        except ValueError as exc:
            details["actual_json_error"] = str(exc)
            return False, details
    elif mode == "sha256":
        expected_value = _sha256(expected)
        actual_value = _sha256(actual)
        details["expected_sha256"] = expected_value
        details["actual_sha256"] = actual_value
    else:
        raise ValueError(f"unsupported artifact diff mode: {mode}")

    return expected_value == actual_value, details


def render_result_lines(matched: bool, details: dict[str, object]) -> list[str]:
    lines = ["ARTIFACT_DIFF=pass" if matched else "ARTIFACT_DIFF=fail"]
    lines.append(f"MODE={details['mode']}")
    lines.append(f"EXPECTED={details['expected']}")
    lines.append(f"ACTUAL={details['actual']}")

    if matched:
        if "expected_sha256" in details:
            lines.append(f"SHA256={details['expected_sha256']}")
        return lines

    if "expected_exists" in details:
        lines.append(f"EXPECTED_EXISTS={details['expected_exists']}")
    if "actual_exists" in details:
        lines.append(f"ACTUAL_EXISTS={details['actual_exists']}")
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


def run_self_test() -> int:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_artifact_diff_") as tmp:
        root = Path(tmp)
        text_a = root / "a.txt"
        text_b = root / "b.txt"
        json_a = root / "a.json"
        json_b = root / "b.json"
        bad_json = root / "bad.json"
        bin_a = root / "a.bin"
        bin_b = root / "b.bin"
        missing = root / "missing"

        text_a.write_text("alpha\n", encoding="utf-8", newline="\n")
        text_b.write_text("alpha\n", encoding="utf-8", newline="\n")
        matched, details = compare_artifacts("text", text_a, text_b)
        assert matched
        assert render_result_lines(matched, details)[0] == "ARTIFACT_DIFF=pass"
        covered.append("text_pass")

        text_b.write_text("beta\n", encoding="utf-8", newline="\n")
        matched, details = compare_artifacts("text", text_a, text_b)
        assert not matched
        covered.append("text_mismatch")

        json_a.write_text('{"alpha": 1, "beta": [2, 3]}\n', encoding="utf-8", newline="\n")
        json_b.write_text('{"beta":[2,3],"alpha":1}\n', encoding="utf-8", newline="\n")
        matched, details = compare_artifacts("json", json_a, json_b)
        assert matched
        covered.append("json_pass")

        json_b.write_text('{"alpha": 2}\n', encoding="utf-8", newline="\n")
        matched, details = compare_artifacts("json", json_a, json_b)
        assert not matched
        covered.append("json_mismatch")

        bad_json.write_text('{"alpha":\n', encoding="utf-8", newline="\n")
        matched, details = compare_artifacts("json", bad_json, json_a)
        assert not matched and "expected_json_error" in details
        covered.append("json_invalid_expected")

        matched, details = compare_artifacts("json", json_a, bad_json)
        assert not matched and "actual_json_error" in details
        covered.append("json_invalid_actual")

        matched, details = compare_artifacts("json", missing, json_a)
        assert not matched and details["expected_exists"] is False
        covered.append("json_missing_expected")

        matched, details = compare_artifacts("json", json_a, missing)
        assert not matched and details["actual_exists"] is False
        covered.append("json_missing_actual")

        bin_a.write_bytes(b"zigux-artifact")
        bin_b.write_bytes(b"zigux-artifact")
        matched, details = compare_artifacts("sha256", bin_a, bin_b)
        assert matched and "expected_sha256" in details
        covered.append("sha256_pass")

        bin_b.write_bytes(b"zigux-artifact-drift")
        matched, details = compare_artifacts("sha256", bin_a, bin_b)
        assert not matched and details["expected_sha256"] != details["actual_sha256"]
        covered.append("sha256_drift")

        try:
            compare_artifacts("bogus", text_a, text_b)
        except ValueError as exc:
            assert "unsupported artifact diff mode" in str(exc)
        else:
            raise AssertionError("invalid mode should raise ValueError")
        covered.append("invalid_mode_rejected")

    print("ARTIFACT_DIFF_SELF_TEST=pass")
    print(f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(covered)}")
    print(f"ARTIFACT_DIFF_SELF_TEST_CASES={','.join(covered)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two artifacts as text, JSON, or SHA-256.")
    parser.add_argument("--mode", choices=("text", "json", "sha256"))
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--actual", type=Path)
    parser.add_argument("--self-test", action="store_true", help="Run builtin checks and exit.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.mode is None or args.expected is None or args.actual is None:
        parser.error("--mode, --expected, and --actual are required unless --self-test is used")

    matched, details = compare_artifacts(args.mode, args.expected, args.actual)
    return emit_result(matched, details)


if __name__ == "__main__":
    raise SystemExit(main())
