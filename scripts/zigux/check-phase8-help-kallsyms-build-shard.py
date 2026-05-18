#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase8-help-kallsyms-build-shard.py"
BUILD_PATH = "zigux/tests/phase8_help_kallsyms_only_build.zig"

REQUIRED_FILES = (
    BUILD_PATH,
)

REQUIRED_MARKERS = {
    BUILD_PATH: (
        '"../../tools/lib/subcmd/help.zig"',
        '"../../tools/lib/symbol/kallsyms.zig"',
        '"phase8-help-kallsyms-help-tests"',
        '"phase8-help-kallsyms-kallsyms-tests"',
        '"Run the focused Phase 8 help and kallsyms shared tests."',
        "test_step.dependOn(&run_help_tests.step);",
        "test_step.dependOn(&run_kallsyms_tests.step);",
        "b.default_step.dependOn(test_step);",
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


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    script_text = Path(__file__).read_text(encoding="utf-8")
    write_text(root, SCRIPT_PATH, script_text)
    write_text(root, BUILD_PATH, "\n".join(REQUIRED_MARKERS[BUILD_PATH]) + "\n")


def assert_missing_case(root: Path, rel_path: str, marker: str) -> None:
    text = read_text(root, rel_path)
    if marker not in text:
        raise SystemExit(f"self-test-fixture-missing:{rel_path}:{marker}")
    (root / rel_path).write_text(text.replace(marker, "", 1), encoding="utf-8")
    problems = validate(root)
    expected = f"missing-marker:{rel_path}:{marker}"
    if expected not in problems:
        raise SystemExit(f"self-test-mismatch:{expected}:{problems}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_help_kallsyms_build_shard_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = validate(baseline_root)
        if baseline:
            raise SystemExit(f"self-test-baseline-failed:{baseline}")

        mutations = (
            (BUILD_PATH, '"phase8-help-kallsyms-help-tests"'),
            (BUILD_PATH, '"phase8-help-kallsyms-kallsyms-tests"'),
            (BUILD_PATH, "test_step.dependOn(&run_help_tests.step);"),
            (BUILD_PATH, "test_step.dependOn(&run_kallsyms_tests.step);"),
            (BUILD_PATH, "b.default_step.dependOn(test_step);"),
        )

        for rel_path, marker in mutations:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_missing_case(case_root, rel_path, marker)
            cases += 1

        missing_file_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_file_root)
        (missing_file_root / BUILD_PATH).unlink()
        missing_result = validate(missing_file_root)
        expected = f"missing-file:{BUILD_PATH}"
        if expected not in missing_result:
            raise SystemExit(f"self-test-missing-file-mismatch:{missing_result}")
        cases += 1

    print("PHASE8_HELP_KALLSYMS_BUILD_SHARD_SELF_TEST=pass")
    print(f"PHASE8_HELP_KALLSYMS_BUILD_SHARD_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE8_HELP_KALLSYMS_BUILD_SHARD=fail")
        print("PHASE8_HELP_KALLSYMS_BUILD_SHARD_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_HELP_KALLSYMS_BUILD_SHARD_PROBLEMS_END")
        return 1

    print("PHASE8_HELP_KALLSYMS_BUILD_SHARD=pass")
    print(f"PHASE8_HELP_KALLSYMS_BUILD_SHARD_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
