#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF_PATH = ROOT / "scripts/zigux/artifact_diff.py"


def load_artifact_diff_module():
    spec = importlib.util.spec_from_file_location("zigux_artifact_diff", ARTIFACT_DIFF_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load artifact diff helper from {ARTIFACT_DIFF_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def capture_emit(module, matched: bool, details: dict[str, object]) -> tuple[int, list[str]]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exit_code = module.emit_result(matched, details)
    return exit_code, buffer.getvalue().splitlines()


def expect_lines(lines: list[str], required: list[str]) -> None:
    for item in required:
        if item not in lines:
            raise AssertionError(f"missing line {item!r} in {lines!r}")


def run_contract_checks() -> tuple[list[str], list[str]]:
    module = load_artifact_diff_module()
    base_cases: list[str] = []
    repeat_cases: list[str] = []

    with tempfile.TemporaryDirectory(prefix="zigux_artifact_diff_contract_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        text_a = tmp_dir / "text-a.txt"
        text_b = tmp_dir / "text-b.txt"
        json_a = tmp_dir / "json-a.json"
        json_b = tmp_dir / "json-b.json"
        blob_a = tmp_dir / "blob-a.bin"
        blob_b = tmp_dir / "blob-b.bin"
        missing_a = tmp_dir / "missing-a.bin"
        missing_b = tmp_dir / "missing-b.bin"

        text_a.write_text("alpha\nbeta\n", encoding="utf-8", newline="\n")
        text_b.write_text("alpha\nbeta\n", encoding="utf-8", newline="\n")
        matched, details = module.compare_artifacts("text", text_a, text_b)
        exit_code, lines = capture_emit(module, matched, details)
        if not matched or exit_code != 0:
            raise AssertionError("text match contract regressed")
        expect_lines(
            lines,
            [
                "ARTIFACT_DIFF=pass",
                "MODE=text",
                f"EXPECTED={text_a}",
                f"ACTUAL={text_b}",
            ],
        )
        base_cases.append("text_match")
        text_match_lines = list(lines)

        text_b.write_text("alpha\nBETA\n", encoding="utf-8", newline="\n")
        matched, details = module.compare_artifacts("text", text_a, text_b)
        exit_code, lines = capture_emit(module, matched, details)
        if matched or exit_code != 1:
            raise AssertionError("text mismatch contract regressed")
        expect_lines(
            lines,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=text",
                f"EXPECTED={text_a}",
                f"ACTUAL={text_b}",
            ],
        )
        base_cases.append("text_mismatch")

        json_a.write_text('{"alpha": 1, "beta": [2, 3]}\n', encoding="utf-8", newline="\n")
        json_b.write_text('{\n  "beta": [2, 3],\n  "alpha": 1\n}\n', encoding="utf-8", newline="\n")
        matched, details = module.compare_artifacts("json", json_a, json_b)
        exit_code, lines = capture_emit(module, matched, details)
        if not matched or exit_code != 0:
            raise AssertionError("json canonical match contract regressed")
        expect_lines(
            lines,
            [
                "ARTIFACT_DIFF=pass",
                "MODE=json",
                f"EXPECTED={json_a}",
                f"ACTUAL={json_b}",
            ],
        )
        base_cases.append("json_canonical_match")

        json_b.write_text('{"alpha": 1, "beta": [2, 4]}\n', encoding="utf-8", newline="\n")
        matched, details = module.compare_artifacts("json", json_a, json_b)
        exit_code, lines = capture_emit(module, matched, details)
        if matched or exit_code != 1:
            raise AssertionError("json mismatch contract regressed")
        expect_lines(
            lines,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=json",
                f"EXPECTED={json_a}",
                f"ACTUAL={json_b}",
            ],
        )
        base_cases.append("json_mismatch")

        blob_a.write_bytes(b"zigux-artifact-diff")
        blob_b.write_bytes(b"zigux-artifact-diff")
        matched, details = module.compare_artifacts("sha256", blob_a, blob_b)
        exit_code, lines = capture_emit(module, matched, details)
        if not matched or exit_code != 0:
            raise AssertionError("sha256 match contract regressed")
        expect_lines(
            lines,
            [
                "ARTIFACT_DIFF=pass",
                "MODE=sha256",
                f"EXPECTED={blob_a}",
                f"ACTUAL={blob_b}",
                f"SHA256={module.sha256_digest(blob_a)}",
            ],
        )
        base_cases.append("sha256_match")

        blob_b.write_bytes(b"zigux-artifact-diff-drift")
        matched, details = module.compare_artifacts("sha256", blob_a, blob_b)
        exit_code, lines = capture_emit(module, matched, details)
        if matched or exit_code != 1:
            raise AssertionError("sha256 drift contract regressed")
        expect_lines(
            lines,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=sha256",
                f"EXPECTED={blob_a}",
                f"ACTUAL={blob_b}",
                f"EXPECTED_SHA256={module.sha256_digest(blob_a)}",
                f"ACTUAL_SHA256={module.sha256_digest(blob_b)}",
            ],
        )
        base_cases.append("sha256_drift")

        matched, details = module.compare_artifacts("sha256", missing_a, blob_b)
        exit_code, lines = capture_emit(module, matched, details)
        if matched or exit_code != 1:
            raise AssertionError("sha256 missing expected contract regressed")
        expect_lines(
            lines,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=sha256",
                f"EXPECTED={missing_a}",
                f"ACTUAL={blob_b}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=True",
            ],
        )
        base_cases.append("sha256_missing_expected")

        matched, details = module.compare_artifacts("sha256", missing_a, missing_b)
        exit_code, lines = capture_emit(module, matched, details)
        if matched or exit_code != 1:
            raise AssertionError("sha256 missing both contract regressed")
        expect_lines(
            lines,
            [
                "ARTIFACT_DIFF=fail",
                "MODE=sha256",
                f"EXPECTED={missing_a}",
                f"ACTUAL={missing_b}",
                "EXPECTED_EXISTS=False",
                "ACTUAL_EXISTS=False",
            ],
        )
        base_cases.append("sha256_missing_both")
        sha256_missing_both_lines = list(lines)

        cli = subprocess.run(
            [
                sys.executable,
                str(ARTIFACT_DIFF_PATH),
                "--mode",
                "bogus",
                str(text_a),
                str(text_b),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if cli.returncode == 0 or "invalid choice" not in cli.stderr:
            raise AssertionError("cli invalid-mode contract regressed")
        base_cases.append("cli_invalid_mode_choice")

        text_b.write_text("alpha\nbeta\n", encoding="utf-8", newline="\n")
        matched, details = module.compare_artifacts("text", text_a, text_b)
        exit_code, lines = capture_emit(module, matched, details)
        if exit_code != 0 or lines != text_match_lines:
            raise AssertionError("repeat text match contract regressed")
        repeat_cases.append("text_match_repeat")

        matched, details = module.compare_artifacts("sha256", missing_a, missing_b)
        exit_code, lines = capture_emit(module, matched, details)
        if exit_code != 1 or lines != sha256_missing_both_lines:
            raise AssertionError("repeat sha256 missing both contract regressed")
        repeat_cases.append("sha256_missing_both_repeat")

    return base_cases, repeat_cases


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the bounded Phase 4 artifact-diff contract.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the same deterministic contract replay and report pass or fail.",
    )
    _ = parser.parse_args()

    base_cases, repeat_cases = run_contract_checks()
    print("ARTIFACT_DIFF_CONTRACT=pass")
    print(f"ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={len(base_cases)}")
    print(f"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={len(repeat_cases)}")
    print(f"ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(base_cases) + len(repeat_cases)}")
    print("ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(base_cases + repeat_cases))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
