#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
TARGET = ROOT / "zigux/tests/phase7_build.zig"

REQUIRED_MARKERS = [
    '"../../lib/string_helpers.zig"',
    'string_helpers_root_module.addImport("string_helpers", string_helpers_module);',
    '"../../lib/cmdline.zig"',
    'cmdline_root_module.addImport("cmdline", cmdline_module);',
    '"../../lib/argv_split.zig"',
    'argv_split_root_module.addImport("argv_split", argv_split_module);',
    '"../../lib/rbtree.zig"',
    'rbtree_root_module.addImport("rbtree", rbtree_module);',
]

EXACT_COUNT_MARKERS = [
    ('"../../lib/string_helpers.zig"', 1),
    ('string_helpers_root_module.addImport("string_helpers", string_helpers_module);', 1),
    ('"../../lib/cmdline.zig"', 1),
    ('cmdline_root_module.addImport("cmdline", cmdline_module);', 1),
    ('"../../lib/argv_split.zig"', 1),
    ('argv_split_root_module.addImport("argv_split", argv_split_module);', 1),
    ('"../../lib/rbtree.zig"', 1),
    ('rbtree_root_module.addImport("rbtree", rbtree_module);', 1),
]


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
    marker_cases = [
        (
            "string_helpers_import_alias_drift",
            'string_helpers_root_module.addImport("string_helpers", string_helpers_module);',
            'string_helpers_root_module.addImport("string_helpers_drift", string_helpers_module);',
            'string_helpers_root_module.addImport("string_helpers", string_helpers_module);',
        ),
        (
            "string_helpers_root_path_drift",
            '"../../lib/string_helpers.zig"',
            '"../../lib/string_helpers_drift.zig"',
            '"../../lib/string_helpers.zig"',
        ),
    ]
    exact_count_cases = [
        (
            "string_helpers_import_exact_count",
            'string_helpers_root_module.addImport("string_helpers", string_helpers_module);',
            'string_helpers_root_module.addImport("string_helpers", string_helpers_module);:expected=1:actual=2',
        ),
        (
            "string_helpers_root_path_exact_count",
            '"../../lib/string_helpers.zig"',
            '"../../lib/string_helpers.zig":expected=1:actual=2',
        ),
    ]

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
