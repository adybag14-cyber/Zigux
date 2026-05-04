#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
BUILD_PATH = ROOT / "zigux/tests/phase12_build.zig"
FIXTURE_PATH = ROOT / "zigux/tests/fixtures/phase12_build_inventory.json"
ARTIFACT_DIFF_PATH = ROOT / "scripts/zigux/artifact_diff.py"

BUILD_TEST_NAME_RE = re.compile(r'\.name = "(phase12-[^"]+)"')
BUILD_DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
BUILD_MODULE_RE = re.compile(
    r'const ([A-Za-z0-9_]+) = b\.createModule\(\.\{\s*'
    r'\.root_source_file = b\.path\("([^"]+)"\),',
    re.S,
)
BUILD_IMPORT_RE = re.compile(r'([A-Za-z0-9_]+)\.addImport\("([^"]+)", ([A-Za-z0-9_]+)\);')
BUILD_TEST_ROOT_MODULE_RE = re.compile(
    r'\.name = "(phase12-[^"]+)",\s*'
    r'\.root_module = ([A-Za-z0-9_]+),',
    re.S,
)
BUILD_RUN_ARTIFACT_RE = re.compile(r"const ([A-Za-z0-9_]+) = b\.addRunArtifact\(")
BUILD_STEP_RE = re.compile(r'b\.step\("([^"]+)",')
TEST_DECL_RE = re.compile(r'^\s*test\s*(?:"[^"]*"|\{)', re.M)
LOCAL_ZIG_IMPORT_RE = re.compile(r'@import\("([^"]+\.zig)"\)')

FORBIDDEN_BUILD_MARKERS: list[str] = []
DEDICATED_SURVEY_REPLAYS = []


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def count_transitive_tests(path: Path, seen: set[Path]) -> int:
    resolved_path = path.resolve()
    if resolved_path in seen:
        return 0
    seen.add(resolved_path)

    source = resolved_path.read_text(encoding="utf-8")
    total = len(TEST_DECL_RE.findall(source))
    for import_path in LOCAL_ZIG_IMPORT_RE.findall(source):
        child_path = (resolved_path.parent / import_path).resolve()
        if ROOT not in child_path.parents:
            continue
        if not child_path.is_file():
            continue
        total += count_transitive_tests(child_path, seen)
    return total


def derive_expected_step_count(build_text: str) -> int:
    return (
        len(BUILD_TEST_NAME_RE.findall(build_text))
        + len(BUILD_RUN_ARTIFACT_RE.findall(build_text))
        + len(BUILD_STEP_RE.findall(build_text))
    )


def derive_expected_test_count(
    test_root_modules: list[dict[str, str]],
    module_root_source_files: list[dict[str, str]],
) -> int:
    module_paths = {
        entry["module"]: (BUILD_PATH.parent / entry["path"]).resolve()
        for entry in module_root_source_files
    }
    seen: set[Path] = set()
    total = 0
    for entry in test_root_modules:
        root_module_name = entry["root_module"]
        root_module_path = module_paths[root_module_name]
        total += count_transitive_tests(root_module_path, seen)
    return total


def render_inventory() -> dict[str, object]:
    build_text = BUILD_PATH.read_text(encoding="utf-8")
    module_root_source_files = [
        {"module": module_name, "path": root_path}
        for module_name, root_path in BUILD_MODULE_RE.findall(build_text)
    ]
    test_root_modules = [
        {"test": test_name, "root_module": root_module}
        for test_name, root_module in BUILD_TEST_ROOT_MODULE_RE.findall(build_text)
    ]
    expected_step_count = derive_expected_step_count(build_text)
    expected_test_count = derive_expected_test_count(test_root_modules, module_root_source_files)
    return {
        "build_test_names": BUILD_TEST_NAME_RE.findall(build_text),
        "shared_test_depend_steps": BUILD_DEPEND_STEP_RE.findall(build_text),
        "module_root_source_files": module_root_source_files,
        "module_imports": [
            {
                "module": module_name,
                "import_name": import_name,
                "imported_module": imported_module,
            }
            for module_name, import_name, imported_module in BUILD_IMPORT_RE.findall(build_text)
        ],
        "test_root_modules": test_root_modules,
        "expected_step_count": expected_step_count,
        "expected_test_count": expected_test_count,
        "expected_summary_line": (
            f"Build Summary: {expected_step_count}/{expected_step_count} steps succeeded; "
            f"{expected_test_count}/{expected_test_count} tests passed"
        ),
        "forbidden_markers": FORBIDDEN_BUILD_MARKERS,
        "dedicated_survey_replays": DEDICATED_SURVEY_REPLAYS,
    }


def compare_inventory(inventory: dict[str, object]) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_inventory_") as tmp_dir_str:
        actual_path = Path(tmp_dir_str) / "phase12_build_inventory.json"
        actual_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(ARTIFACT_DIFF_PATH),
                "--mode",
                "json",
                str(FIXTURE_PATH),
                str(actual_path),
            ],
            check=False,
            text=True,
            capture_output=True,
        )
    return result


def find_duplicate_strings(values: list[str]) -> bool:
    return len(values) != len(set(values))


def find_duplicate_record_fields(entries: list[dict[str, str]], fields: tuple[str, ...]) -> bool:
    seen: set[tuple[str, ...]] = set()
    for entry in entries:
        signature_parts: list[str] = []
        for field in fields:
            value = entry.get(field)
            if not isinstance(value, str):
                return False
            signature_parts.append(value)
        signature = tuple(signature_parts)
        if signature in seen:
            return True
        seen.add(signature)
    return False


def validate_module_root_paths_exist(
    inventory: dict[str, object],
    build_dir: Path = BUILD_PATH.parent,
) -> list[str]:
    problems: list[str] = []
    module_roots = inventory.get("module_root_source_files")
    if not isinstance(module_roots, list):
        return ["module_root_source_files_missing"]

    for entry in module_roots:
        if not isinstance(entry, dict):
            problems.append("module_root_source_files_invalid_entry")
            continue
        module_name = entry.get("module")
        root_path = entry.get("path")
        if not isinstance(module_name, str) or not isinstance(root_path, str):
            problems.append("module_root_source_files_invalid_shape")
            continue
        if not (build_dir / root_path).is_file():
            problems.append(f"module_root_source_files_missing_path:{module_name}:{root_path}")
    return problems


def validate_inventory_shape(inventory: dict[str, object]) -> list[str]:
    problems: list[str] = []
    module_names: set[str] = set()

    build_test_names = inventory.get("build_test_names")
    if isinstance(build_test_names, list) and all(isinstance(item, str) for item in build_test_names):
        if find_duplicate_strings(build_test_names):
            problems.append("build_test_names_duplicates")

    depend_steps = inventory.get("shared_test_depend_steps")
    if isinstance(depend_steps, list) and all(isinstance(item, str) for item in depend_steps):
        if find_duplicate_strings(depend_steps):
            problems.append("shared_test_depend_steps_duplicates")

    module_root_source_files = inventory.get("module_root_source_files")
    if isinstance(module_root_source_files, list) and all(
        isinstance(item, dict) for item in module_root_source_files
    ):
        for item in module_root_source_files:
            module_name = item.get("module")
            if isinstance(module_name, str):
                module_names.add(module_name)
        if find_duplicate_record_fields(module_root_source_files, ("module",)):
            problems.append("module_root_source_files_module_duplicates")
        if find_duplicate_record_fields(module_root_source_files, ("path",)):
            problems.append("module_root_source_files_path_duplicates")

    module_imports = inventory.get("module_imports")
    if isinstance(module_imports, list) and all(isinstance(item, dict) for item in module_imports):
        if find_duplicate_record_fields(module_imports, ("module", "import_name")):
            problems.append("module_imports_module_import_name_duplicates")
        for item in module_imports:
            module_name = item.get("module")
            imported_module = item.get("imported_module")
            if isinstance(module_name, str) and module_name not in module_names:
                problems.append("module_imports_unknown_module")
            if isinstance(imported_module, str) and imported_module not in module_names:
                problems.append("module_imports_unknown_imported_module")

    test_root_modules = inventory.get("test_root_modules")
    if isinstance(test_root_modules, list) and all(
        isinstance(item, dict) for item in test_root_modules
    ):
        if find_duplicate_record_fields(test_root_modules, ("test",)):
            problems.append("test_root_modules_test_duplicates")
        for item in test_root_modules:
            root_module = item.get("root_module")
            if isinstance(root_module, str) and root_module not in module_names:
                problems.append("test_root_modules_unknown_root_module")

    return problems


def expect_inventory_mismatch(label: str, inventory: dict[str, object]) -> None:
    mismatched_result = compare_inventory(inventory)
    if mismatched_result.returncode == 0:
        raise SystemExit(f"phase12-build-inventory:self-test:{label}:fixture_drift_exit")
    if "ARTIFACT_DIFF=fail" not in mismatched_result.stdout:
        raise SystemExit(f"phase12-build-inventory:self-test:{label}:fixture_drift_stdout")


def expect_shape_problem(label: str, inventory: dict[str, object], expected_problem: str) -> None:
    problems = validate_inventory_shape(inventory)
    if expected_problem not in problems:
        raise SystemExit(f"phase12-build-inventory:self-test:{label}:shape_guard")


def expect_missing_module_root_path(
    label: str,
    inventory: dict[str, object],
    build_dir: Path,
    expected_problem: str,
) -> None:
    problems = validate_module_root_paths_exist(inventory, build_dir)
    if expected_problem not in problems:
        raise SystemExit(f"phase12-build-inventory:self-test:{label}:module_root_guard")


def run_self_test() -> int:
    load_json(FIXTURE_PATH)

    first = render_inventory()
    second = render_inventory()
    if first != second:
        raise SystemExit("phase12-build-inventory:self-test:repeat_run_stability")
    if not first["build_test_names"]:
        raise SystemExit("phase12-build-inventory:self-test:build_test_names_empty")
    if len(first["build_test_names"]) != len(first["test_root_modules"]):
        raise SystemExit("phase12-build-inventory:self-test:test_root_module_count")
    if len(first["shared_test_depend_steps"]) != len(first["build_test_names"]):
        raise SystemExit("phase12-build-inventory:self-test:depend_step_count")
    baseline_shape_problems = validate_inventory_shape(first)
    if baseline_shape_problems:
        raise SystemExit(
            f"phase12-build-inventory:self-test:baseline_shape:{baseline_shape_problems[0]}"
        )
    baseline_module_root_path_problems = validate_module_root_paths_exist(first)
    if baseline_module_root_path_problems:
        raise SystemExit(
            "phase12-build-inventory:self-test:baseline_module_root_paths:"
            f"{baseline_module_root_path_problems[0]}"
        )

    matched_result = compare_inventory(first)
    if matched_result.returncode != 0:
        raise SystemExit("phase12-build-inventory:self-test:fixture_match")
    if "ARTIFACT_DIFF=pass" not in matched_result.stdout:
        raise SystemExit("phase12-build-inventory:self-test:fixture_match_stdout")

    drifted_summary = dict(first)
    drifted_summary["expected_summary_line"] = "Build Summary: 0/0 steps succeeded; 0/0 tests passed"
    expect_inventory_mismatch("fixture_summary_line_drift", drifted_summary)

    drifted_test_names = json.loads(json.dumps(first))
    drifted_test_names["build_test_names"][0] = "phase12-build-inventory-drift"
    expect_inventory_mismatch("fixture_build_test_name_drift", drifted_test_names)

    duplicate_test_names = json.loads(json.dumps(first))
    duplicate_test_names["build_test_names"][0] = duplicate_test_names["build_test_names"][1]
    expect_shape_problem(
        "duplicate_build_test_names",
        duplicate_test_names,
        "build_test_names_duplicates",
    )

    drifted_depend_steps = json.loads(json.dumps(first))
    drifted_depend_steps["shared_test_depend_steps"][0] = "run_phase12_inventory_drift"
    expect_inventory_mismatch("fixture_depend_step_drift", drifted_depend_steps)

    duplicate_depend_steps = json.loads(json.dumps(first))
    duplicate_depend_steps["shared_test_depend_steps"][0] = duplicate_depend_steps[
        "shared_test_depend_steps"
    ][1]
    expect_shape_problem(
        "duplicate_depend_steps",
        duplicate_depend_steps,
        "shared_test_depend_steps_duplicates",
    )

    drifted_module_roots = json.loads(json.dumps(first))
    drifted_module_roots["module_root_source_files"][0]["path"] = "../../drivers/virtio/virtio_drift.zig"
    expect_inventory_mismatch("fixture_module_root_source_file_drift", drifted_module_roots)

    duplicate_module_root_paths = json.loads(json.dumps(first))
    duplicate_module_root_paths["module_root_source_files"][0]["path"] = duplicate_module_root_paths[
        "module_root_source_files"
    ][1]["path"]
    expect_shape_problem(
        "duplicate_module_root_paths",
        duplicate_module_root_paths,
        "module_root_source_files_path_duplicates",
    )

    module_root_fixture = {
        "module_root_source_files": [
            {"module": "phase12_self_test_present", "path": "phase12_self_test_present.zig"},
        ]
    }
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_inventory_self_test_paths_") as tmp_dir_str:
        tmp_build_dir = Path(tmp_dir_str)
        (tmp_build_dir / "phase12_self_test_present.zig").write_text(
            "// self-test placeholder\n",
            encoding="utf-8",
        )
        baseline_module_root_fixture_problems = validate_module_root_paths_exist(
            module_root_fixture,
            tmp_build_dir,
        )
        if baseline_module_root_fixture_problems:
            raise SystemExit(
                "phase12-build-inventory:self-test:baseline_module_root_fixture:"
                f"{baseline_module_root_fixture_problems[0]}"
            )
        missing_module_root_fixture = json.loads(json.dumps(module_root_fixture))
        missing_module_root_fixture["module_root_source_files"][0]["path"] = (
            "phase12_self_test_missing.zig"
        )
        expect_missing_module_root_path(
            "missing_module_root_path",
            missing_module_root_fixture,
            tmp_build_dir,
            "module_root_source_files_missing_path:phase12_self_test_present:"
            "phase12_self_test_missing.zig",
        )

    drifted_module_imports = json.loads(json.dumps(first))
    drifted_module_imports["module_imports"][0]["import_name"] = "virtio_drift"
    expect_inventory_mismatch("fixture_module_import_drift", drifted_module_imports)

    duplicate_module_imports = json.loads(json.dumps(first))
    duplicate_module_imports["module_imports"][1]["module"] = duplicate_module_imports[
        "module_imports"
    ][0]["module"]
    duplicate_module_imports["module_imports"][1]["import_name"] = duplicate_module_imports[
        "module_imports"
    ][0]["import_name"]
    expect_shape_problem(
        "duplicate_module_imports",
        duplicate_module_imports,
        "module_imports_module_import_name_duplicates",
    )

    unknown_module_import_owner = json.loads(json.dumps(first))
    unknown_module_import_owner["module_imports"][0]["module"] = "phase12_unknown_owner_module"
    expect_shape_problem(
        "unknown_module_import_owner",
        unknown_module_import_owner,
        "module_imports_unknown_module",
    )

    unknown_imported_module = json.loads(json.dumps(first))
    unknown_imported_module["module_imports"][0]["imported_module"] = "phase12_unknown_imported_module"
    expect_shape_problem(
        "unknown_imported_module",
        unknown_imported_module,
        "module_imports_unknown_imported_module",
    )

    drifted_test_root_modules = json.loads(json.dumps(first))
    drifted_test_root_modules["test_root_modules"][0]["root_module"] = "phase12_inventory_drift_module"
    expect_inventory_mismatch("fixture_test_root_module_drift", drifted_test_root_modules)

    duplicate_test_root_modules = json.loads(json.dumps(first))
    duplicate_test_root_modules["test_root_modules"][0]["test"] = duplicate_test_root_modules[
        "test_root_modules"
    ][1]["test"]
    expect_shape_problem(
        "duplicate_test_root_modules",
        duplicate_test_root_modules,
        "test_root_modules_test_duplicates",
    )

    unknown_test_root_module = json.loads(json.dumps(first))
    unknown_test_root_module["test_root_modules"][0]["root_module"] = "phase12_unknown_test_root_module"
    expect_shape_problem(
        "unknown_test_root_module",
        unknown_test_root_module,
        "test_root_modules_unknown_root_module",
    )

    drifted_step_count = dict(first)
    drifted_step_count["expected_step_count"] = 0
    expect_inventory_mismatch("fixture_expected_step_count_drift", drifted_step_count)

    drifted_test_count = dict(first)
    drifted_test_count["expected_test_count"] = 0
    expect_inventory_mismatch("fixture_expected_test_count_drift", drifted_test_count)

    drifted_forbidden_markers = dict(first)
    drifted_forbidden_markers["forbidden_markers"] = ["phase12-build-inventory-drift"]
    expect_inventory_mismatch("fixture_forbidden_markers_drift", drifted_forbidden_markers)

    drifted_dedicated_replays = dict(first)
    drifted_dedicated_replays["dedicated_survey_replays"] = ["phase12-build-inventory-drift"]
    expect_inventory_mismatch("fixture_dedicated_survey_replays_drift", drifted_dedicated_replays)

    print("PHASE12_BUILD_INVENTORY_SELF_TEST=pass")
    print("PHASE12_BUILD_INVENTORY_SELF_TEST_CASE_COUNT=26")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild and compare the bounded Phase 12 build inventory fixture."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in repeat-run and artifact-diff drift checks",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    load_json(FIXTURE_PATH)
    generated = render_inventory()
    shape_problems = validate_inventory_shape(generated)
    if shape_problems:
        print("PHASE12_BUILD_INVENTORY=fail")
        print("PHASE12_BUILD_INVENTORY_SHAPE_MISMATCH_START")
        for problem in shape_problems:
            print(problem)
        print("PHASE12_BUILD_INVENTORY_SHAPE_MISMATCH_END")
        return 1

    missing_module_root_paths = validate_module_root_paths_exist(generated)
    if missing_module_root_paths:
        print("PHASE12_BUILD_INVENTORY=fail")
        print("PHASE12_BUILD_INVENTORY_MISSING_MODULE_ROOTS_START")
        for problem in missing_module_root_paths:
            print(problem)
        print("PHASE12_BUILD_INVENTORY_MISSING_MODULE_ROOTS_END")
        return 1

    result = compare_inventory(generated)

    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)

    if result.returncode != 0:
        print("PHASE12_BUILD_INVENTORY=fail")
        return result.returncode

    print("PHASE12_BUILD_INVENTORY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
