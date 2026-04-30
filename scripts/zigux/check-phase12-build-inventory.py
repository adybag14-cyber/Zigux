#!/usr/bin/env python3
from __future__ import annotations

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
DEDICATED_SURVEY_REPLAYS: list[str] = []


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


def derive_expected_test_count(test_root_modules: list[dict[str, str]], module_root_source_files: list[dict[str, str]]) -> int:
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


def main() -> int:
    expected = load_json(FIXTURE_PATH)
    _ = expected
    generated = render_inventory()

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_inventory_") as tmp_dir_str:
        actual_path = Path(tmp_dir_str) / "phase12_build_inventory.json"
        actual_path.write_text(json.dumps(generated, indent=2) + "\n", encoding="utf-8")
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
