#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
BUILD_PATH = ROOT / "zigux" / "tests" / "phase7_build.zig"
FIXTURE_PATH = ROOT / "zigux" / "tests" / "fixtures" / "phase7_build_inventory.json"

IMPORTED_HELPER_RE = re.compile(
    r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)"',
    re.S,
)
STANDALONE_SURVEY_RE = re.compile(
    r'createStandaloneTestRoot\(\s*b,\s*target,\s*optimize,\s*"([^"]+)"',
    re.S,
)
RUN_CALL_RE = re.compile(
    r'const\s+\w+\s*=\s*addTestRun\(\s*'
    r'b,\s*"([^"]+)",\s*\w+,\s*(null|repo_root)\s*,?\s*\)',
    re.S,
)
DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
BUILD_PATH_RE = re.compile(r'b\.path\("([^"]+)"\)')
UNEXPECTED_BUILD_MARKERS = ["../../tools/lib/", "zigux/tests/build.zig"]


def load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def render_inventory() -> dict[str, object]:
    build_text = BUILD_PATH.read_text(encoding="utf-8")
    imported_helpers = [
        {
            "root_path": root_path,
            "import_name": import_name,
            "helper_path": helper_path,
        }
        for root_path, import_name, helper_path in IMPORTED_HELPER_RE.findall(build_text)
    ]
    standalone_surveys = STANDALONE_SURVEY_RE.findall(build_text)
    run_labels: list[str] = []
    run_cwds: dict[str, str | None] = {}
    for run_label, cwd in RUN_CALL_RE.findall(build_text):
        run_labels.append(run_label)
        run_cwds[run_label] = None if cwd == "null" else cwd

    expected_build_paths = set(BUILD_PATH_RE.findall(build_text))
    expected_build_paths.update(entry["root_path"] for entry in imported_helpers)
    expected_build_paths.update(entry["helper_path"] for entry in imported_helpers)
    expected_build_paths.update(standalone_surveys)

    return {
        "repo_root_path": "../..",
        "imported_helpers": imported_helpers,
        "standalone_surveys": standalone_surveys,
        "expected_build_paths": sorted(expected_build_paths),
        "run_labels": run_labels,
        "run_cwds": run_cwds,
        "shared_test_depend_steps": DEPEND_STEP_RE.findall(build_text),
        "unexpected_build_markers": UNEXPECTED_BUILD_MARKERS,
    }


def print_mismatch(expected: dict[str, object], actual: dict[str, object]) -> None:
    print("PHASE7_BUILD_INVENTORY=fail")
    print("PHASE7_BUILD_INVENTORY_MISMATCH_START")
    print("EXPECTED_JSON_START")
    print(json.dumps(expected, indent=2))
    print("EXPECTED_JSON_END")
    print("ACTUAL_JSON_START")
    print(json.dumps(actual, indent=2))
    print("ACTUAL_JSON_END")
    print("PHASE7_BUILD_INVENTORY_MISMATCH_END")


def run_self_test() -> int:
    fixture = load_fixture()
    first = render_inventory()
    second = render_inventory()

    if first != second:
        raise SystemExit("phase7-build-inventory:self-test:repeat_run_stability")
    if first != fixture:
        raise SystemExit("phase7-build-inventory:self-test:fixture_match")
    if len(first["run_labels"]) != len(first["shared_test_depend_steps"]):
        raise SystemExit("phase7-build-inventory:self-test:depend_step_count")

    drifted = dict(first)
    drifted["run_labels"] = ["phase7-mismatch"]
    if drifted == fixture:
        raise SystemExit("phase7-build-inventory:self-test:drift_detection")

    if first["expected_build_paths"] != sorted(first["expected_build_paths"]):
        raise SystemExit("phase7-build-inventory:self-test:path_sorting")

    print("PHASE7_BUILD_INVENTORY_SELF_TEST=pass")
    print("PHASE7_BUILD_INVENTORY_SELF_TEST_CASE_COUNT=5")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild and compare the Phase 7 shared build inventory fixture."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in repeat-run stability and fixture drift checks.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    fixture = load_fixture()
    generated = render_inventory()
    if generated != fixture:
        print_mismatch(fixture, generated)
        return 1

    print("PHASE7_BUILD_INVENTORY=pass")
    print(f"PHASE7_BUILD_INVENTORY_RUN_COUNT={len(generated['run_labels'])}")
    print(f"PHASE7_BUILD_INVENTORY_DEPENDENCY_COUNT={len(generated['shared_test_depend_steps'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
