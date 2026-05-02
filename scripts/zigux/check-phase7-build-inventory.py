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
VALIDATOR_PATH = ROOT / "scripts" / "zigux" / "validate-phase7.py"

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
VALIDATOR_REQUIRED_FILE_MARKER = (
    'ROOT / "scripts" / "zigux" / "check-phase7-build-inventory.py",'
)
VALIDATOR_EXPECTED_MARKERS = {
    "expected_make_expansions": [
        '"python3 scripts/zigux/check-phase7-build-inventory.py --self-test",',
        '"python3 scripts/zigux/check-phase7-build-inventory.py",',
    ],
    "unexpected_make_expansions": [
        '"python3 scripts/zigux/check-phase7-build-inventory.py --self-test",',
        '"python3 scripts/zigux/check-phase7-build-inventory.py",',
    ],
}


def load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def render_inventory_from_text(build_text: str) -> dict[str, object]:
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


def render_inventory(build_path: Path = BUILD_PATH) -> dict[str, object]:
    return render_inventory_from_text(build_path.read_text(encoding="utf-8"))


def collect_validator_alignment_failures(validator_text: str) -> list[str]:
    failures: list[str] = []
    if VALIDATOR_REQUIRED_FILE_MARKER not in validator_text:
        failures.append(
            "validate-phase7.py: missing required_files entry for scripts/zigux/check-phase7-build-inventory.py"
        )

    for block_name, markers in VALIDATOR_EXPECTED_MARKERS.items():
        block_match = re.search(rf"{block_name} = \{{(.*?)\n \}}", validator_text, re.S)
        if block_match is None:
            failures.append(f"validate-phase7.py: missing {block_name} block")
            continue

        block_text = block_match.group(1)
        for marker in markers:
            if marker not in block_text:
                failures.append(
                    f"validate-phase7.py: {block_name} missing marker {marker}"
                )

    return failures


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


def print_validator_alignment_failures(failures: list[str]) -> None:
    print("PHASE7_BUILD_INVENTORY_VALIDATOR_ALIGNMENT_START")
    for failure in failures:
        print(failure)
    print("PHASE7_BUILD_INVENTORY_VALIDATOR_ALIGNMENT_END")


def expect_validator_failure(label: str, validator_text: str, expected_message: str) -> None:
    failures = collect_validator_alignment_failures(validator_text)
    if not failures:
        raise SystemExit(f"phase7-build-inventory:self-test:{label}:unexpected_pass")
    joined = "\n".join(failures)
    if expected_message not in joined:
        raise SystemExit(
            f"phase7-build-inventory:self-test:{label}:expected:{expected_message}:actual:{joined}"
        )


def run_self_test() -> int:
    fixture = load_fixture()
    first = render_inventory()
    second = render_inventory()
    validator_text = VALIDATOR_PATH.read_text(encoding="utf-8")

    if first != second:
        raise SystemExit("phase7-build-inventory:self-test:repeat_run_stability")
    if first != fixture:
        raise SystemExit("phase7-build-inventory:self-test:fixture_match")
    if len(first["run_labels"]) != len(first["shared_test_depend_steps"]):
        raise SystemExit("phase7-build-inventory:self-test:depend_step_count")
    if collect_validator_alignment_failures(validator_text):
        raise SystemExit("phase7-build-inventory:self-test:validator_alignment_baseline")

    drifted = dict(first)
    drifted["run_labels"] = ["phase7-mismatch"]
    if drifted == fixture:
        raise SystemExit("phase7-build-inventory:self-test:drift_detection")

    if first["expected_build_paths"] != sorted(first["expected_build_paths"]):
        raise SystemExit("phase7-build-inventory:self-test:path_sorting")

    build_text = BUILD_PATH.read_text(encoding="utf-8")
    cwd_drift_text, replacements = re.subn(
        r'("phase7-argv-split-survey-tests",\s*argv_split_survey_root_module,\s*)repo_root(\s*,\s*\))',
        r"\1null\2",
        build_text,
        count=1,
        flags=re.S,
    )
    if replacements != 1:
        raise SystemExit("phase7-build-inventory:self-test:cwd_drift_rewrite")

    cwd_drift = render_inventory_from_text(cwd_drift_text)
    if cwd_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:cwd_drift_detection")
    if first["run_cwds"].get("phase7-argv-split-survey-tests") != "repo_root":
        raise SystemExit("phase7-build-inventory:self-test:argv_split_repo_root_baseline")
    if cwd_drift["run_cwds"].get("phase7-argv-split-survey-tests") is not None:
        raise SystemExit("phase7-build-inventory:self-test:argv_split_repo_root_drift")

    helper_path_drift_text, replacements = re.subn(
        r'("phase7_argv_split\.zig",\s*"argv_split",\s*")\.\./\.\./lib/argv_split\.zig("\s*,)',
        r'\1../../lib/cmdline.zig\2',
        build_text,
        count=1,
        flags=re.S,
    )
    if replacements != 1:
        raise SystemExit("phase7-build-inventory:self-test:helper_path_drift_rewrite")

    helper_path_drift = render_inventory_from_text(helper_path_drift_text)
    if helper_path_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:helper_path_drift_detection")
    if helper_path_drift["imported_helpers"][2]["helper_path"] != "../../lib/cmdline.zig":
        raise SystemExit("phase7-build-inventory:self-test:helper_path_drift_shape")

    dependency_drift_text = build_text.replace(
        "    test_step.dependOn(&run_rbtree_tests.step);\n",
        "",
        1,
    )
    if dependency_drift_text == build_text:
        raise SystemExit("phase7-build-inventory:self-test:dependency_drift_rewrite")

    dependency_drift = render_inventory_from_text(dependency_drift_text)
    if dependency_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:dependency_drift_detection")
    dependency_steps = dependency_drift["shared_test_depend_steps"]
    if "run_rbtree_tests" in dependency_steps:
        raise SystemExit("phase7-build-inventory:self-test:dependency_drift_shape")
    if len(dependency_steps) != len(first["shared_test_depend_steps"]) - 1:
        raise SystemExit("phase7-build-inventory:self-test:dependency_drift_count")

    expect_validator_failure(
        "missing_validator_required_file_marker",
        validator_text.replace(VALIDATOR_REQUIRED_FILE_MARKER, "", 1),
        "validate-phase7.py: missing required_files entry for scripts/zigux/check-phase7-build-inventory.py",
    )
    expect_validator_failure(
        "missing_validator_expected_marker",
        validator_text.replace(
            '"python3 scripts/zigux/check-phase7-build-inventory.py --self-test",',
            "",
            1,
        ),
        'validate-phase7.py: expected_make_expansions missing marker "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",',
    )
    expect_validator_failure(
        "missing_validator_unexpected_marker",
        validator_text.replace(
            '"python3 scripts/zigux/check-phase7-build-inventory.py",',
            "",
            1,
        ),
        'validate-phase7.py: unexpected_make_expansions missing marker "python3 scripts/zigux/check-phase7-build-inventory.py",',
    )

    print("PHASE7_BUILD_INVENTORY_SELF_TEST=pass")
    print("PHASE7_BUILD_INVENTORY_SELF_TEST_CASE_COUNT=11")
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
    validator_failures = collect_validator_alignment_failures(
        VALIDATOR_PATH.read_text(encoding="utf-8")
    )
    if generated != fixture or validator_failures:
        print("PHASE7_BUILD_INVENTORY=fail")
        if generated != fixture:
            print("PHASE7_BUILD_INVENTORY_MISMATCH_START")
            print("EXPECTED_JSON_START")
            print(json.dumps(fixture, indent=2))
            print("EXPECTED_JSON_END")
            print("ACTUAL_JSON_START")
            print(json.dumps(generated, indent=2))
            print("ACTUAL_JSON_END")
            print("PHASE7_BUILD_INVENTORY_MISMATCH_END")
        if validator_failures:
            print_validator_alignment_failures(validator_failures)
        return 1

    print("PHASE7_BUILD_INVENTORY=pass")
    print(f"PHASE7_BUILD_INVENTORY_RUN_COUNT={len(generated['run_labels'])}")
    print(f"PHASE7_BUILD_INVENTORY_DEPENDENCY_COUNT={len(generated['shared_test_depend_steps'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
