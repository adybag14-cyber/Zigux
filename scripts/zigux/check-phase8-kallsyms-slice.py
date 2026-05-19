#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase8-kallsyms-slice.py"
NOTE_PATH = "Documentation/zigux/phase8-kallsyms-slice.md"

REQUIRED_FILES = (
    SCRIPT_PATH,
    NOTE_PATH,
)

REQUIRED_MARKERS = {
    NOTE_PATH: (
        "This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.",
        "`PHASE8_STATUS=parked`",
        "`PHASE8_SLICE=kallsyms-parse-wrapper-parked`",
        "`scripts/zigux/validate-phase8.py`",
        "`tools/lib/symbol/kallsyms.zig` through the public raw fallback",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "authenticated GitHub contents reads still fail for the dedicated kallsyms helper, checker, focused test, and focused build file paths",
        "This run could not freshly verify helper-local parser test expectations, focused kallsyms test behavior, or the combined help-and-kallsyms checker contents from one consistent source.",
        "restart with one focused replay step around the dedicated packet",
    ),
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    problems: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            problems.append(f"missing-file:{rel_path}")
    if problems:
        return problems

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                problems.append(f"missing-marker:{rel_path}:{marker}")
    return problems


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_PATH)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    script_text = Path(__file__).read_text(encoding="utf-8")
    write_text(root, SCRIPT_PATH, script_text)
    for rel_path, markers in REQUIRED_MARKERS.items():
        write_text(root, rel_path, "\n".join(markers) + "\n")


def assert_missing_case(root: Path, rel_path: str, marker: str) -> None:
    text = read_text(root, rel_path)
    if marker not in text:
        raise SystemExit(f"self-test-fixture-missing:{rel_path}:{marker}")

    (root / rel_path).write_text(text.replace(marker, "", 1), encoding="utf-8")
    result = run_validator(root)
    expected = f"missing-marker:{rel_path}:{marker}"
    output = result.stdout.strip() or result.stderr.strip() or "no_output"
    if result.returncode == 0:
        raise SystemExit(f"self-test-unexpected-pass:{rel_path}:{marker}")
    if expected not in output:
        raise SystemExit(f"self-test-mismatch:{expected}:{output}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_kallsyms_slice_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                case_root = Path(tmp) / f"case_{cases}"
                shutil.copytree(baseline_root, case_root)
                assert_missing_case(case_root, rel_path, marker)
                cases += 1

        missing_note_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_note_root)
        (missing_note_root / NOTE_PATH).unlink()
        missing_note_result = run_validator(missing_note_root)
        expected_missing_note = f"missing-file:{NOTE_PATH}"
        missing_note_output = (
            missing_note_result.stdout.strip()
            or missing_note_result.stderr.strip()
            or "no_output"
        )
        if missing_note_result.returncode == 0:
            raise SystemExit(f"self-test-unexpected-pass:{expected_missing_note}")
        if expected_missing_note not in missing_note_output:
            raise SystemExit(
                f"self-test-mismatch:{expected_missing_note}:{missing_note_output}"
            )
        cases += 1

        missing_script_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_script_root)
        (missing_script_root / SCRIPT_PATH).unlink()
        missing_script_result = run_validator(missing_script_root)
        missing_script_output = (
            missing_script_result.stdout.strip()
            or missing_script_result.stderr.strip()
            or "no_output"
        )
        if missing_script_result.returncode == 0 or "can't open file" not in missing_script_output:
            raise SystemExit(f"self-test-missing-file-mismatch:{missing_script_output}")
        cases += 1

    print("PHASE8_KALLSYMS_SLICE_SELF_TEST=pass")
    print(f"PHASE8_KALLSYMS_SLICE_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE8_KALLSYMS_SLICE=fail")
        print("PHASE8_KALLSYMS_SLICE_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_KALLSYMS_SLICE_PROBLEMS_END")
        return 1

    print("PHASE8_KALLSYMS_SLICE=pass")
    print(f"PHASE8_KALLSYMS_SLICE_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))