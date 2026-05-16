#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

BUILD_FILE = "zigux/tests/phase7_build.zig"
MAKEFILE = "zigux/Makefile"

BUILD_INPUTS = [
    "../../lib/string_helpers.zig",
    "phase7_string_helpers.zig",
    "phase7_string_helpers_survey.zig",
    "phase7_string_helpers_sample_boundary.zig",
    "../../lib/cmdline.zig",
    "phase7_cmdline.zig",
    "phase7_cmdline_survey.zig",
    "../../lib/argv_split.zig",
    "phase7_argv_split.zig",
    "phase7_argv_split_survey.zig",
    "../../lib/rbtree.zig",
    "phase7_rbtree.zig",
    "phase7_rbtree_survey.zig",
]

BUILD_MARKERS = [
    "fn createStandaloneRootModule(",
    "fn createImportedRootModule(",
    "const helper_module = createStandaloneRootModule(b, target, optimize, helper_source_file);",
    "const root_module = createStandaloneRootModule(b, target, optimize, root_source_file);",
    "root_module.addImport(import_name, helper_module);",
    'const string_helpers_root_module = createImportedRootModule(',
    'const cmdline_root_module = createImportedRootModule(',
    'const argv_split_root_module = createImportedRootModule(',
    'const rbtree_root_module = createImportedRootModule(',
    '"string_helpers",',
    '"cmdline",',
    '"argv_split",',
    '"rbtree",',
    '.name = "phase7-string-helpers-tests"',
    '.name = "phase7-string-helpers-survey-tests"',
    '.name = "phase7-string-helpers-sample-boundary-tests"',
    '.name = "phase7-cmdline-tests"',
    '.name = "phase7-cmdline-survey-tests"',
    '.name = "phase7-argv-split-tests"',
    '.name = "phase7-argv-split-survey-tests"',
    '.name = "phase7-rbtree-tests"',
    '.name = "phase7-rbtree-survey-tests"',
    '"phase7-string-helpers-test"',
    '"phase7-string-helpers-survey"',
    '"phase7-string-helpers-sample-boundary"',
    '"phase7-cmdline-test"',
    '"phase7-cmdline-survey"',
    '"phase7-argv-split-test"',
    '"phase7-argv-split-survey"',
    '"phase7-rbtree-test"',
    '"phase7-rbtree-survey"',
    'run_string_helpers_survey_tests.setCwd(b.path("../.."));',
    'run_string_helpers_sample_boundary_tests.setCwd(b.path("../.."));',
    'run_cmdline_survey_tests.setCwd(b.path("../.."));',
    'run_argv_split_survey_tests.setCwd(b.path("../.."));',
    'run_rbtree_survey_tests.setCwd(b.path("../.."));',
]

FORBIDDEN_BUILD_MARKERS = [
    "../../tools/lib/",
    "zigux/tests/build.zig",
]

MAKEFILE_EXACT_LINES = [
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-path-drift.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-path-drift.py",
]


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files: list[str] = []
    missing_markers: list[str] = []

    build_path = root / BUILD_FILE
    makefile_path = root / MAKEFILE
    checker_path = root / "scripts/zigux/check-phase7-build-path-drift.py"

    for path in [build_path, makefile_path, checker_path]:
        if not path.exists():
            missing_files.append(path.relative_to(root).as_posix())

    build_root = root / "zigux/tests"
    for rel in BUILD_INPUTS:
        if not (build_root / rel).resolve().exists():
            missing_files.append(f"{BUILD_FILE}: missing build input {rel}")

    if missing_files:
        return missing_files, []

    build_text = build_path.read_text(encoding="utf-8")
    makefile_lines = makefile_path.read_text(encoding="utf-8").splitlines()

    for rel in BUILD_INPUTS:
        quoted = f'"{rel}"'
        if quoted not in build_text:
            missing_markers.append(f"{BUILD_FILE}: {quoted}")

    for marker in BUILD_MARKERS:
        if marker not in build_text:
            missing_markers.append(f"{BUILD_FILE}: {marker}")

    for marker in FORBIDDEN_BUILD_MARKERS:
        if marker in build_text:
            missing_markers.append(f"{BUILD_FILE}: forbidden stale marker {marker}")

    for line in MAKEFILE_EXACT_LINES:
        if line not in makefile_lines:
            missing_markers.append(f"{MAKEFILE}: {line}")

    return [], missing_markers


def write_fixture_tree(tmp_root: Path) -> None:
    for rel in BUILD_INPUTS:
        path = (tmp_root / "zigux/tests" / rel).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n", encoding="utf-8")

    build_file = tmp_root / BUILD_FILE
    build_file.parent.mkdir(parents=True, exist_ok=True)
    build_lines = [f'"{rel}"' for rel in BUILD_INPUTS]
    build_lines.extend(BUILD_MARKERS)
    build_file.write_text("\n".join(dict.fromkeys(build_lines)) + "\n", encoding="utf-8")

    checker_path = tmp_root / "scripts/zigux/check-phase7-build-path-drift.py"
    checker_path.parent.mkdir(parents=True, exist_ok=True)
    checker_path.write_text("# fixture\n", encoding="utf-8")

    makefile_path = tmp_root / MAKEFILE
    makefile_path.parent.mkdir(parents=True, exist_ok=True)
    makefile_path.write_text("\n".join(MAKEFILE_EXACT_LINES) + "\n", encoding="utf-8")


def expect_missing_file(tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == []
    assert missing_files == [rel]


def expect_missing_marker(tmp_root: Path, expected: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == []
    assert missing_markers == [expected]


def remove_once(path: Path, marker: str) -> None:
    original = path.read_text(encoding="utf-8")
    updated = original.replace(marker, "", 1)
    assert updated != original
    path.write_text(updated, encoding="utf-8")


def remove_line(path: Path, line: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert line in lines
    lines.remove(line)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_build_path_drift_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)
        assert validate(tmp_root) == ([], [])

        (tmp_root / "scripts/zigux/check-phase7-build-path-drift.py").unlink()
        expect_missing_file(tmp_root, "scripts/zigux/check-phase7-build-path-drift.py")
        write_fixture_tree(tmp_root)

        missing_input = (tmp_root / "zigux/tests/../../lib/cmdline.zig").resolve()
        missing_input.unlink()
        expect_missing_file(tmp_root, f"{BUILD_FILE}: missing build input ../../lib/cmdline.zig")
        write_fixture_tree(tmp_root)

        build_file = tmp_root / BUILD_FILE
        remove_once(build_file, '"../../lib/rbtree.zig"')
        expect_missing_marker(tmp_root, f'{BUILD_FILE}: "../../lib/rbtree.zig"')
        write_fixture_tree(tmp_root)

        remove_once(build_file, '.name = "phase7-cmdline-tests"')
        expect_missing_marker(tmp_root, f'{BUILD_FILE}: .name = "phase7-cmdline-tests"')
        write_fixture_tree(tmp_root)

        remove_once(build_file, 'run_rbtree_survey_tests.setCwd(b.path("../.."));')
        expect_missing_marker(tmp_root, f'{BUILD_FILE}: run_rbtree_survey_tests.setCwd(b.path("../.."));')
        write_fixture_tree(tmp_root)

        build_file.write_text(
            build_file.read_text(encoding="utf-8") + "../../tools/lib/rbtree.c\n",
            encoding="utf-8",
        )
        expect_missing_marker(tmp_root, f"{BUILD_FILE}: forbidden stale marker ../../tools/lib/")
        write_fixture_tree(tmp_root)

        build_file.write_text(
            build_file.read_text(encoding="utf-8") + "zig build test --build-file zigux/tests/build.zig\n",
            encoding="utf-8",
        )
        expect_missing_marker(tmp_root, f"{BUILD_FILE}: forbidden stale marker zigux/tests/build.zig")
        write_fixture_tree(tmp_root)

        makefile_path = tmp_root / MAKEFILE
        remove_line(makefile_path, MAKEFILE_EXACT_LINES[0])
        expect_missing_marker(tmp_root, f"{MAKEFILE}: {MAKEFILE_EXACT_LINES[0]}")
        write_fixture_tree(tmp_root)

        remove_line(makefile_path, MAKEFILE_EXACT_LINES[1])
        expect_missing_marker(tmp_root, f"{MAKEFILE}: {MAKEFILE_EXACT_LINES[1]}")

    print("PHASE7_BUILD_PATH_DRIFT=pass")
    print("PHASE7_BUILD_PATH_DRIFT_CASE_COUNT=8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 7 build graph stays free of stale path and route drift."
    )
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE7_BUILD_PATH_DRIFT=fail")
        print("MISSING_PHASE7_BUILD_PATH_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_BUILD_PATH_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_BUILD_PATH_DRIFT=fail")
        print("MISSING_PHASE7_BUILD_PATH_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_BUILD_PATH_MARKERS_END")
        return 1

    print("PHASE7_BUILD_PATH_DRIFT=pass")
    print(f"PHASE7_BUILD_PATH_INPUT_COUNT={len(BUILD_INPUTS)}")
    print(f"PHASE7_BUILD_PATH_MARKER_COUNT={len(BUILD_MARKERS) + len(MAKEFILE_EXACT_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
