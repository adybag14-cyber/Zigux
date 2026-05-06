#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
TARGET = ROOT / "zigux/tests/phase7_build.zig"

HELPER_SPECS = [
    {
        "key": "string_helpers",
        "helper_path": '"../../lib/string_helpers.zig"',
        "root_path": '"phase7_string_helpers.zig"',
        "import_marker": 'string_helpers_root_module.addImport("string_helpers", string_helpers_module);',
        "test_name_marker": '.name = "phase7-string-helpers-tests",',
        "depend_marker": "test_step.dependOn(&run_string_helpers_tests.step);",
    },
    {
        "key": "cmdline",
        "helper_path": '"../../lib/cmdline.zig"',
        "root_path": '"phase7_cmdline.zig"',
        "import_marker": 'cmdline_root_module.addImport("cmdline", cmdline_module);',
        "test_name_marker": '.name = "phase7-cmdline-tests",',
        "depend_marker": "test_step.dependOn(&run_cmdline_tests.step);",
    },
    {
        "key": "argv_split",
        "helper_path": '"../../lib/argv_split.zig"',
        "root_path": '"phase7_argv_split.zig"',
        "import_marker": 'argv_split_root_module.addImport("argv_split", argv_split_module);',
        "test_name_marker": '.name = "phase7-argv-split-tests",',
        "depend_marker": "test_step.dependOn(&run_argv_split_tests.step);",
    },
    {
        "key": "rbtree",
        "helper_path": '"../../lib/rbtree.zig"',
        "root_path": '"phase7_rbtree.zig"',
        "import_marker": 'rbtree_root_module.addImport("rbtree", rbtree_module);',
        "test_name_marker": '.name = "phase7-rbtree-tests",',
        "depend_marker": "test_step.dependOn(&run_rbtree_tests.step);",
    },
]

REQUIRED_MARKERS = [
    marker
    for spec in HELPER_SPECS
    for marker in (
        spec["helper_path"],
        spec["root_path"],
        spec["import_marker"],
        spec["test_name_marker"],
        spec["depend_marker"],
    )
]

EXACT_COUNT_MARKERS = [(marker, 1) for marker in REQUIRED_MARKERS]


def collect_missing_markers(text: str) -> list[str]:
    missing: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            missing.append(marker)
    for marker, expected_count in EXACT_COUNT_MARKERS:
        actual_count = text.count(marker)
        if actual_count != expected_count:
            missing.append(f"{marker}:expected={expected_count}:actual={actual_count}")
    return missing


def validate(path: Path) -> list[str]:
    return collect_missing_markers(path.read_text(encoding="utf-8"))


def mutate_text(path: Path, old: str, new: str, case: str) -> None:
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def duplicate_first_marker(text: str, marker: str) -> str:
    return text.replace(marker, f"{marker}\n{marker}", 1)


def run_self_test() -> None:
    fixture = "\n".join(REQUIRED_MARKERS) + "\n"
    marker_cases = []
    exact_count_cases = []

    for spec in HELPER_SPECS:
        marker_cases.extend(
            [
                (
                    f"{spec['key']}_helper_path_drift",
                    spec["helper_path"],
                    spec["helper_path"].replace(".zig", "_drift.zig"),
                    spec["helper_path"],
                ),
                (
                    f"{spec['key']}_root_path_drift",
                    spec["root_path"],
                    spec["root_path"].replace(".zig", "_drift.zig"),
                    spec["root_path"],
                ),
                (
                    f"{spec['key']}_import_alias_drift",
                    spec["import_marker"],
                    spec["import_marker"].replace(f'"{spec["key"]}"', f'"{spec["key"]}_drift"'),
                    spec["import_marker"],
                ),
                (
                    f"{spec['key']}_test_name_drift",
                    spec["test_name_marker"],
                    spec["test_name_marker"].replace("-tests", "-tests-drift"),
                    spec["test_name_marker"],
                ),
                (
                    f"{spec['key']}_depend_drift",
                    spec["depend_marker"],
                    spec["depend_marker"].replace(".step);", "_drift.step);"),
                    spec["depend_marker"],
                ),
            ]
        )
        exact_count_cases.extend(
            [
                (
                    f"{spec['key']}_import_exact_count",
                    spec["import_marker"],
                    f"{spec['import_marker']}:expected=1:actual=2",
                ),
                (
                    f"{spec['key']}_depend_exact_count",
                    spec["depend_marker"],
                    f"{spec['depend_marker']}:expected=1:actual=2",
                ),
            ]
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_build_wiring_") as tmp_dir_str:
        tmp_path = Path(tmp_dir_str) / "phase7_build.zig"
        tmp_path.write_text(fixture, encoding="utf-8")
        assert validate(tmp_path) == []

        for case, old, new, expected in marker_cases:
            mutate_text(tmp_path, old, new, case)
            assert expected in validate(tmp_path), case
            tmp_path.write_text(fixture, encoding="utf-8")

        for case, marker, expected in exact_count_cases:
            original = tmp_path.read_text(encoding="utf-8")
            updated = duplicate_first_marker(original, marker)
            assert updated != original, case
            tmp_path.write_text(updated, encoding="utf-8")
            assert expected in validate(tmp_path), case
            tmp_path.write_text(fixture, encoding="utf-8")

    print("PHASE7_BUILD_WIRING_SELF_TEST=pass")
    print(
        "PHASE7_BUILD_WIRING_SELF_TEST_CASE_COUNT=%d"
        % (len(marker_cases) + len(exact_count_cases))
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Phase 7 helper-module wiring in zigux/tests/phase7_build.zig."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-test cases without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing = validate(TARGET)
    if missing:
        print("PHASE7_BUILD_WIRING=fail")
        print("MISSING_PHASE7_BUILD_WIRING_MARKERS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE7_BUILD_WIRING_MARKERS_END")
        return 1

    print("PHASE7_BUILD_WIRING=pass")
    print(f"PHASE7_BUILD_WIRING_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
