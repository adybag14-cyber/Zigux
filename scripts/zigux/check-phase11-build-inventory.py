#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
BUILD_PATH = ROOT / "zigux/tests/phase11_build.zig"
FIXTURE_PATH = ROOT / "zigux/tests/fixtures/phase11_build_inventory.json"
ARTIFACT_DIFF_PATH = ROOT / "scripts/zigux/artifact_diff.py"

BUILD_TEST_NAME_RE = re.compile(r'\.name = "(phase11-[^"]+)"')
BUILD_DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
BUILD_MODULE_RE = re.compile(
    r'const ([A-Za-z0-9_]+) = b\.createModule\(\.\{\s*'
    r'\.root_source_file = b\.path\("([^"]+)"\),',
    re.S,
)
BUILD_IMPORT_RE = re.compile(r'([A-Za-z0-9_]+)\.addImport\("([^"]+)", ([A-Za-z0-9_]+)\);')
BUILD_TEST_ROOT_MODULE_RE = re.compile(
    r'\.name = "(phase11-[^"]+)",\s*'
    r'\.root_module = ([A-Za-z0-9_]+),',
    re.S,
)
FORBIDDEN_BUILD_MARKERS = [
    "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
]
DEDICATED_SURVEY_REPLAYS = [
    "zigux/tests/phase11_hvc_console_survey.zig",
]


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_inventory() -> dict[str, object]:
    build_text = BUILD_PATH.read_text(encoding="utf-8")
    return {
        "build_test_names": BUILD_TEST_NAME_RE.findall(build_text),
        "shared_test_depend_steps": BUILD_DEPEND_STEP_RE.findall(build_text),
        "module_root_source_files": [
            {"module": module_name, "path": root_path}
            for module_name, root_path in BUILD_MODULE_RE.findall(build_text)
        ],
        "module_imports": [
            {
                "module": module_name,
                "import_name": import_name,
                "imported_module": imported_module,
            }
            for module_name, import_name, imported_module in BUILD_IMPORT_RE.findall(build_text)
        ],
        "test_root_modules": [
            {"test": test_name, "root_module": root_module}
            for test_name, root_module in BUILD_TEST_ROOT_MODULE_RE.findall(build_text)
        ],
        "forbidden_markers": FORBIDDEN_BUILD_MARKERS,
        "dedicated_survey_replays": DEDICATED_SURVEY_REPLAYS,
    }


def validate_module_root_paths_exist(inventory: dict[str, object]) -> list[str]:
    missing: list[str] = []
    module_roots = inventory.get("module_root_source_files")
    if not isinstance(module_roots, list):
        return ["phase11_build_inventory:module_root_source_files"]

    build_dir = BUILD_PATH.parent
    for item in module_roots:
        if not isinstance(item, dict):
            missing.append("phase11_build_inventory:module_root_source_files:item")
            continue
        module_name = item.get("module")
        root_path = item.get("path")
        if not isinstance(module_name, str) or not isinstance(root_path, str):
            missing.append("phase11_build_inventory:module_root_source_files:shape")
            continue
        if not (build_dir / root_path).exists():
            missing.append(f"{module_name}:{root_path}")
    return missing


def main() -> int:
    _ = load_json(FIXTURE_PATH)
    generated = render_inventory()
    missing_module_roots = validate_module_root_paths_exist(generated)

    if missing_module_roots:
        print("PHASE11_BUILD_INVENTORY=fail")
        print("PHASE11_BUILD_INVENTORY_MISSING_MODULE_ROOTS_START")
        for item in missing_module_roots:
            print(item)
        print("PHASE11_BUILD_INVENTORY_MISSING_MODULE_ROOTS_END")
        return 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase11_inventory_") as tmp_dir_str:
        actual_path = Path(tmp_dir_str) / "phase11_build_inventory.json"
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
        print("PHASE11_BUILD_INVENTORY=fail")
        return result.returncode

    print("PHASE11_BUILD_INVENTORY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
