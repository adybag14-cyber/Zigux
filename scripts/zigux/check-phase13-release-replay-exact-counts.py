#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
BUILD_TEST_NAME_RE = re.compile(r'\.name = "(phase13-[^"]+)"')
BUILD_DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")

RELEASE_SURVEY_PATH = Path("Documentation/zigux/phase13-release-notes-survey.md")
BUILD_PATH = Path("zigux/tests/phase13_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

SHARED_REPLAY_STEPS = [
    "phase13-libfs-tests",
    "phase13-devres-tests",
    "phase13-devres-dma-coherent-tests",
    "phase13-devres-iounmap-reviewability-tests",
    "phase13-devres-iomap-reviewability-tests",
    "phase13-landlock-ruleset-tests",
    "phase13-landlock-ruleset-reviewability-tests",
    "phase13-landlock-syscalls-tests",
    "phase13-landlock-syscalls-reviewability-tests",
    "phase13-landlock-ruleset-fops-sync-tests",
    "phase13-libfs-reviewability-tests",
    "phase13-devres-reviewability-tests",
    "phase13-devres-wrapper-reviewability-tests",
    "phase13-notifier-list-reviewability-tests",
    "phase13-notifier-chain-view-tests",
]

RELEASE_SURVEY_COUNT_MARKERS = [
    "`PHASE13_SHARED_REPLAY_STEP_COUNT=15`",
    "The current shared replay inventory is:",
]

MAKEFILE_ROUTE_MARKERS = [
    "scripts/zigux/check-phase13-release-replay-exact-counts.py --self-test",
    "scripts/zigux/check-phase13-release-replay-exact-counts.py\n",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_exact_count(label: str, text: str, snippet: str, expected_count: int, issues: list[str]) -> None:
    actual = text.count(snippet)
    if actual != expected_count:
        issues.append(f"{label}:exact_count:{actual}!={expected_count}:{snippet}")


def validate(release_survey_text: str, build_text: str, makefile_text: str) -> list[str]:
    issues: list[str] = []
    for marker in RELEASE_SURVEY_COUNT_MARKERS:
        require_exact_count("release_survey", release_survey_text, marker, 1, issues)
    for step in SHARED_REPLAY_STEPS:
        require_exact_count("release_survey", release_survey_text, f"- `{step}`", 1, issues)

    build_names = BUILD_TEST_NAME_RE.findall(build_text)
    if build_names != SHARED_REPLAY_STEPS:
        issues.append("build:test_name_sequence")

    depend_step_count = len(BUILD_DEPEND_STEP_RE.findall(build_text))
    if depend_step_count != len(SHARED_REPLAY_STEPS):
        issues.append(f"build:depend_step_count:{depend_step_count}!={len(SHARED_REPLAY_STEPS)}")

    for marker in MAKEFILE_ROUTE_MARKERS:
        require_exact_count("makefile", makefile_text, marker, 1, issues)

    return issues


def run_self_test() -> int:
    release_survey_text = "\n".join([
        "# Phase 13 Release Notes Survey",
        "",
        "- `PHASE13_SHARED_REPLAY_STEP_COUNT=15`",
        "",
        "The current shared replay inventory is:",
        "",
        *[f"- `{step}`" for step in SHARED_REPLAY_STEPS],
    ])
    build_text = "\n".join([
        *[f'    .name = "{step}"' for step in SHARED_REPLAY_STEPS],
        *[f"test_step.dependOn(&step_{index}.step);" for index, _ in enumerate(SHARED_REPLAY_STEPS, start=1)],
    ])
    makefile_text = "\n".join([
        "phase13-validate:",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-release-replay-exact-counts.py --self-test",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-release-replay-exact-counts.py",
    ]) + "\n"

    cases = [
        ("happy_path", release_survey_text, build_text, makefile_text, False),
        (
            "duplicate_release_step",
            release_survey_text + f"\n- `{SHARED_REPLAY_STEPS[0]}`\n",
            build_text,
            makefile_text,
            True,
        ),
        (
            "missing_replay_count_marker",
            release_survey_text.replace("- `PHASE13_SHARED_REPLAY_STEP_COUNT=15`\n", "", 1),
            build_text,
            makefile_text,
            True,
        ),
        (
            "missing_build_step",
            release_survey_text,
            build_text.replace(f'    .name = "{SHARED_REPLAY_STEPS[-1]}"\n', "", 1),
            makefile_text,
            True,
        ),
        (
            "missing_makefile_route",
            release_survey_text,
            build_text,
            makefile_text.replace("scripts/zigux/check-phase13-release-replay-exact-counts.py --self-test", "", 1),
            True,
        ),
    ]

    for name, survey_value, build_value, makefile_value, should_fail in cases:
        issues = validate(survey_value, build_value, makefile_value)
        failed = bool(issues)
        if failed != should_fail:
            print(f"PHASE13_RELEASE_REPLAY_EXACT_COUNTS_SELF_TEST={name}:fail")
            if issues:
                print("ISSUES_START")
                for issue in issues:
                    print(issue)
                print("ISSUES_END")
            return 1

    print("PHASE13_RELEASE_REPLAY_EXACT_COUNTS_SELF_TEST=pass")
    print(f"PHASE13_RELEASE_REPLAY_EXACT_COUNTS_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        return run_self_test()

    release_survey_path = ROOT / RELEASE_SURVEY_PATH
    build_path = ROOT / BUILD_PATH
    makefile_path = ROOT / MAKEFILE_PATH
    required_paths = [release_survey_path, build_path, makefile_path]
    missing_paths = [str(path) for path in required_paths if not path.exists()]
    if missing_paths:
        print("PHASE13_RELEASE_REPLAY_EXACT_COUNTS=fail")
        print("MISSING_FILES_START")
        for path in missing_paths:
            print(path)
        print("MISSING_FILES_END")
        return 1

    issues = validate(read(release_survey_path), read(build_path), read(makefile_path))
    if issues:
        print("PHASE13_RELEASE_REPLAY_EXACT_COUNTS=fail")
        print("ISSUES_START")
        for issue in issues:
            print(issue)
        print("ISSUES_END")
        return 1

    print("PHASE13_RELEASE_REPLAY_EXACT_COUNTS=pass")
    print(f"PHASE13_RELEASE_REPLAY_STEP_COUNT={len(SHARED_REPLAY_STEPS)}")
    print(f"PHASE13_MAKEFILE_ROUTE_MARKER_COUNT={len(MAKEFILE_ROUTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
