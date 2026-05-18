#!/usr/bin/env python3
"""Guard the bounded Zigux artifact-diff contract."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


ARTIFACT_DIFF = Path("scripts/zigux/artifact_diff.py")
EXPECTED_SELF_TEST_CASE_COUNT = 7
EXPECTED_CONTRACT_SELF_TEST_CASES = 5
EXPECTED_MODES = ("json", "text", "bytes")

SOURCE_MARKERS = (
    'MODE_CHOICES = ("json", "text", "bytes")',
    "EXPECTED_SELF_TEST_CASE_COUNT = 7",
    'print("ARTIFACT_DIFF_SELF_TEST=pass")',
    'print(f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={checks_run}")',
    'print("ARTIFACT_DIFF=pass")',
    'print("ARTIFACT_DIFF=fail")',
    'print("ARTIFACT_DIFF=error")',
    'raise SystemExit("--self-test does not accept artifact paths")',
    'raise SystemExit("expected and actual artifact paths are required unless --self-test is used")',
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in contract self-test")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def require_markers(text: str, label: str) -> None:
    missing = [marker for marker in SOURCE_MARKERS if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def run_python(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def require_result(
    result: subprocess.CompletedProcess[str],
    expected_code: int,
    stdout_markers: tuple[str, ...],
    stderr_markers: tuple[str, ...] = (),
) -> None:
    if result.returncode != expected_code:
        raise RuntimeError(
            "unexpected exit code "
            f"{result.returncode} != {expected_code}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    missing_stdout = [marker for marker in stdout_markers if marker not in result.stdout]
    missing_stderr = [marker for marker in stderr_markers if marker not in result.stderr]
    if missing_stdout or missing_stderr:
        raise RuntimeError(
            "artifact-diff output drifted: "
            f"missing stdout markers={missing_stdout}, missing stderr markers={missing_stderr}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def check(root: Path) -> None:
    script = root / ARTIFACT_DIFF
    if not script.is_file():
        raise RuntimeError(f"missing required file: {ARTIFACT_DIFF.as_posix()}")

    require_markers(read_text(script), ARTIFACT_DIFF.as_posix())

    self_test = run_python(script, "--self-test")
    require_result(
        self_test,
        0,
        (
            "ARTIFACT_DIFF_SELF_TEST=pass",
            f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}",
        ),
    )

    with tempfile.TemporaryDirectory(prefix="artifact-diff-contract-") as tmp_dir:
        tmp = Path(tmp_dir)

        json_expected = tmp / "expected.json"
        json_actual = tmp / "actual.json"
        write_text(json_expected, '{\n  "beta": 2,\n  "alpha": 1\n}\n')
        write_text(json_actual, '{ "alpha": 1, "beta": 2 }\n')
        require_result(
            run_python(script, "--mode", EXPECTED_MODES[0], str(json_expected), str(json_actual)),
            0,
            ("ARTIFACT_DIFF=pass", "ARTIFACT_DIFF_MODE=json"),
        )

        write_text(json_actual, '{ "alpha": 1, "beta": 3 }\n')
        require_result(
            run_python(script, "--mode", EXPECTED_MODES[0], str(json_expected), str(json_actual)),
            1,
            ("ARTIFACT_DIFF=fail", "ARTIFACT_DIFF_MODE=json", "--- ", "+++ "),
        )

        text_expected = tmp / "expected.txt"
        text_actual = tmp / "actual.txt"
        write_text(text_expected, "alpha\nbeta\n")
        write_text(text_actual, "alpha\ngamma\n")
        require_result(
            run_python(script, "--mode", EXPECTED_MODES[1], str(text_expected), str(text_actual)),
            1,
            ("ARTIFACT_DIFF=fail", "ARTIFACT_DIFF_MODE=text", "@@"),
        )

        bytes_expected = tmp / "expected.bin"
        bytes_actual = tmp / "actual.bin"
        write_bytes(bytes_expected, b"\x00\x01\x02")
        write_bytes(bytes_actual, b"\x00\x04\x02")
        require_result(
            run_python(script, "--mode", EXPECTED_MODES[2], str(bytes_expected), str(bytes_actual)),
            1,
            ("ARTIFACT_DIFF=fail", "ARTIFACT_DIFF_MODE=bytes", "offset 1"),
        )

        write_text(json_actual, "{invalid-json}\n")
        require_result(
            run_python(script, "--mode", EXPECTED_MODES[0], str(json_expected), str(json_actual)),
            2,
            ("ARTIFACT_DIFF=error", "ARTIFACT_DIFF_MODE=json", "invalid JSON"),
        )


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        check(root)
    except RuntimeError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected failure containing {expected_fragment!r}, got: {exc}") from exc
    else:
        raise AssertionError("expected contract check to fail")


def run_self_test(root: Path) -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="artifact-diff-contract-selftest-") as tmp_dir:
        tmp = Path(tmp_dir)
        script = tmp / ARTIFACT_DIFF
        write_text(script, read_text(root / ARTIFACT_DIFF))

        check(tmp)
        cases += 1

        write_text(script, read_text(script).replace('MODE_CHOICES = ("json", "text", "bytes")', 'MODE_CHOICES = ("json", "text")', 1))
        expect_failure(tmp, "MODE_CHOICES")
        cases += 1

        write_text(script, read_text(root / ARTIFACT_DIFF))
        write_text(script, read_text(script).replace("EXPECTED_SELF_TEST_CASE_COUNT = 7", "EXPECTED_SELF_TEST_CASE_COUNT = 6", 1))
        expect_failure(tmp, "EXPECTED_SELF_TEST_CASE_COUNT = 7")
        cases += 1

        write_text(script, read_text(root / ARTIFACT_DIFF))
        write_text(script, read_text(script).replace('print("ARTIFACT_DIFF=error")', 'print("ARTIFACT_DIFF_ERROR=error")', 1))
        expect_failure(tmp, "ARTIFACT_DIFF=error")
        cases += 1

        write_text(script, read_text(root / ARTIFACT_DIFF))
        write_text(script, read_text(script).replace('raise SystemExit("--self-test does not accept artifact paths")', 'raise SystemExit("self-test path guard drifted")', 1))
        expect_failure(tmp, "--self-test does not accept artifact paths")
        cases += 1

    if cases != EXPECTED_CONTRACT_SELF_TEST_CASES:
        raise AssertionError(f"unexpected self-test case count: {cases}")
    print("ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass")
    print(f"ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if args.self_test:
        return run_self_test(root)
    try:
        check(root)
    except RuntimeError as exc:
        print(f"ARTIFACT_DIFF_CONTRACT=fail: {exc}", file=sys.stderr)
        return 1
    print("ARTIFACT_DIFF_CONTRACT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
