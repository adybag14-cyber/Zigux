#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase8-help-kallsyms-packet.py"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE_PATH = "zigux/Makefile"
HELP_SLICE_PATH = "Documentation/zigux/phase8-help-slice.md"
KALLSYMS_SLICE_PATH = "Documentation/zigux/phase8-kallsyms-slice.md"
HELP_SOURCE_PATH = "tools/lib/subcmd/help.zig"
KALLSYMS_SOURCE_PATH = "tools/lib/symbol/kallsyms.zig"
HELP_TEST_PATH = "zigux/tests/phase8_help.zig"
HELP_ONLY_BUILD_PATH = "zigux/tests/phase8_help_only_build.zig"
HELP_KALLSYMS_ONLY_BUILD_PATH = "zigux/tests/phase8_help_kallsyms_only_build.zig"
KALLSYMS_TEST_PATH = "zigux/tests/phase8_kallsyms.zig"
KALLSYMS_ONLY_BUILD_PATH = "zigux/tests/phase8_kallsyms_only_build.zig"
PHASE8_BUILD_PATH = "zigux/tests/phase8_build.zig"

REQUIRED_FILES = (
    SCRIPT_PATH,
    REVIEW_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    HELP_SLICE_PATH,
    KALLSYMS_SLICE_PATH,
    HELP_SOURCE_PATH,
    KALLSYMS_SOURCE_PATH,
    HELP_TEST_PATH,
    HELP_ONLY_BUILD_PATH,
    HELP_KALLSYMS_ONLY_BUILD_PATH,
    KALLSYMS_TEST_PATH,
    KALLSYMS_ONLY_BUILD_PATH,
    PHASE8_BUILD_PATH,
)

REQUIRED_MARKERS = {
    REVIEW_CHECKLIST_PATH: (
        "if the change touches the shared Phase 8 help-and-kallsyms packet",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
    ),
    SCRIPTS_README_PATH: (
        "Phase 8 flow - the current shared Phase 8 review surface on `master` is",
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`zigux/tests/phase8_help.zig`",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_kallsyms.zig`",
        "`make -C zigux phase8-validate`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
    ),
    TESTS_README_PATH: (
        "`scripts/zigux/check-phase8-help-kallsyms-packet.py`",
        "`zigux/tests/phase8_help.zig`",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_kallsyms.zig`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
    ),
    WORKFLOW_PATH: (
        "Validate Phase 8 tooling packet",
        "Run focused Phase 8 help tests",
        "Run focused Phase 8 kallsyms tests",
        "Run focused Phase 8 help and kallsyms tests",
    ),
    MAKEFILE_PATH: (
        "phase8-validate:",
        "scripts/zigux/check-phase8-help-kallsyms-packet.py --self-test",
        "scripts/zigux/check-phase8-help-kallsyms-packet.py",
        "phase8-help-test:",
        "phase8-help-kallsyms-test:",
        "phase8-kallsyms-test:",
    ),
    HELP_SLICE_PATH: (
        "PHASE8_SLICE=help-command-source-and-terminal-starter",
        "make -C zigux phase8-help-test",
        "make -C zigux phase8-help-kallsyms-test",
        "zigux/tests/phase8_help_kallsyms_only_build.zig",
    ),
    KALLSYMS_SLICE_PATH: (
        "PHASE8_SLICE=kallsyms-parse-wrapper-parked",
        "zigux/tests/phase8_kallsyms_only_build.zig",
        "make -C zigux phase8-kallsyms-test",
        "make -C zigux phase8-help-kallsyms-test",
        "one direct `kallsymsParse()` wrapper",
    ),
    HELP_TEST_PATH: (
        'test "phase 8 help module imports cleanly" {',
        'test "phase 8 help slice note keeps helper-first output-stable tooling posture and non-goals explicit" {',
    ),
    KALLSYMS_TEST_PATH: (
        'test "phase 8 kallsyms module imports cleanly" {',
        'test "phase 8 kallsyms slice note keeps the C-aligned truncation contract explicit" {',
        'test "phase 8 kallsyms wrappers preserve the parked callback contract" {',
    ),
    HELP_SOURCE_PATH: (
        "pub fn planPrettyPrint(",
        "pub fn writePrettyPrintStringListForTerminal(",
    ),
    KALLSYMS_ONLY_BUILD_PATH: (
        '"Documentation/zigux/phase8-kallsyms-slice.md"',
        '"../../tools/lib/symbol/kallsyms.zig"',
        '"phase8_kallsyms.zig"',
        '"phase8-kallsyms-tests"',
        '"Run focused Phase 8 kallsyms tests"',
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
    for rel_path in REQUIRED_FILES:
        if rel_path == SCRIPT_PATH:
            continue
        markers = REQUIRED_MARKERS.get(rel_path)
        content = "\n".join(markers) + "\n" if markers else "# fixture\n"
        write_text(root, rel_path, content)


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
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_help_kallsyms_packet_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        mutations = (
            (SCRIPTS_README_PATH, "`scripts/zigux/check-phase8-help-kallsyms-packet.py`"),
            (TESTS_README_PATH, "`make -C zigux phase8-help-kallsyms-test`"),
            (REVIEW_CHECKLIST_PATH, "if the change touches the shared Phase 8 help-and-kallsyms packet"),
            (WORKFLOW_PATH, "Run focused Phase 8 help and kallsyms tests"),
            (MAKEFILE_PATH, "scripts/zigux/check-phase8-help-kallsyms-packet.py --self-test"),
            (HELP_SLICE_PATH, "PHASE8_SLICE=help-command-source-and-terminal-starter"),
            (KALLSYMS_SLICE_PATH, "PHASE8_SLICE=kallsyms-parse-wrapper-parked"),
            (HELP_TEST_PATH, 'test "phase 8 help module imports cleanly" {'),
            (KALLSYMS_TEST_PATH, 'test "phase 8 kallsyms module imports cleanly" {'),
            (KALLSYMS_ONLY_BUILD_PATH, '"phase8-kallsyms-tests"'),
        )
        for rel_path, marker in mutations:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_missing_case(case_root, rel_path, marker)
            cases += 1

        missing_file_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_file_root)
        (missing_file_root / KALLSYMS_ONLY_BUILD_PATH).unlink()
        missing_result = run_validator(missing_file_root)
        missing_output = missing_result.stdout.strip() or missing_result.stderr.strip() or "no_output"
        expected = f"missing-file:{KALLSYMS_ONLY_BUILD_PATH}"
        if missing_result.returncode == 0 or expected not in missing_output:
            raise SystemExit(f"self-test-missing-file-mismatch:{missing_output}")
        cases += 1

    print("PHASE8_HELP_KALLSYMS_PACKET_SELF_TEST=pass")
    print(f"PHASE8_HELP_KALLSYMS_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE8_HELP_KALLSYMS_PACKET=fail")
        print("PHASE8_HELP_KALLSYMS_PACKET_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_HELP_KALLSYMS_PACKET_PROBLEMS_END")
        return 1

    print("PHASE8_HELP_KALLSYMS_PACKET=pass")
    print(f"PHASE8_HELP_KALLSYMS_PACKET_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
