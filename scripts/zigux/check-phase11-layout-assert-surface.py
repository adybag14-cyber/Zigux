#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys
import tempfile


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT
if (ROOT / "scripts").exists():
    REPO_ROOT = ROOT

HELPER_PATH = "zigux/helpers/layout_assert.zig"
BUILD_PATH = "zigux/tests/phase11_build.zig"
INVENTORY_PATH = "zigux/tests/fixtures/phase11_build_inventory.json"
SURVEY_PATH = "zigux/tests/phase11_uapi_header_parity_survey.zig"

HELPER_MARKERS = [
    'const abi = @import("abi_bindings");',
    "pub fn assertSize(comptime T: type, comptime expected: usize) void {",
    "pub fn assertAlign(comptime T: type, comptime expected: usize) void {",
    "pub fn assertOffset(comptime T: type, comptime field_name: []const u8, comptime expected: usize) void {",
    "pub fn assertBoundaryHeaderLayout() void {",
    "pub fn assertExportStatusLayout() void {",
    "pub fn assertInteropPolicyLayout() void {",
    "pub fn assertMmioRangeLayout() void {",
    "pub fn assertBitmapViewLayout() void {",
    "pub fn assertCpuMaskViewLayout() void {",
    'test "phase3 layout assertions cover canonical bindings" {',
]

BUILD_MARKERS = [
    "const layout_assert_module = b.createModule(.{",
    '.root_source_file = b.path("../helpers/layout_assert.zig"),',
    'layout_assert_module.addImport("abi_bindings", abi_bindings_module);',
    'phase11_uapi_header_parity_survey_module.addImport("layout_assert", layout_assert_module);',
]

SURVEY_MARKERS = [
    'const layout_assert = @import("layout_assert");',
    "layout_assert.assertSize(WatchdogInfoLayout, 40);",
    "layout_assert.assertAlign(WatchdogInfoLayout, 4);",
    'layout_assert.assertOffset(WatchdogInfoLayout, "options", 0);',
    'layout_assert.assertOffset(WatchdogInfoLayout, "firmware_version", 4);',
    'layout_assert.assertOffset(WatchdogInfoLayout, "identity", 8);',
    "layout_assert.assertSize(WinsizeLayout, 8);",
    "layout_assert.assertAlign(WinsizeLayout, 2);",
    'layout_assert.assertOffset(WinsizeLayout, "ws_row", 0);',
    'layout_assert.assertOffset(WinsizeLayout, "ws_col", 2);',
    'layout_assert.assertOffset(WinsizeLayout, "ws_xpixel", 4);',
    'layout_assert.assertOffset(WinsizeLayout, "ws_ypixel", 6);',
]

EXPECTED_LAYOUT_MODULE = {
    "module": "layout_assert_module",
    "path": "../helpers/layout_assert.zig",
}

EXPECTED_SURVEY_IMPORT = {
    "module": "phase11_uapi_header_parity_survey_module",
    "import_name": "layout_assert",
    "imported_module": "layout_assert_module",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def expect_markers(missing: list[str], label: str, source: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            missing.append(f"{label}:{marker}")


def check_root(root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path in [HELPER_PATH, BUILD_PATH, INVENTORY_PATH, SURVEY_PATH]:
        if not (root / rel_path).exists():
            missing.append(f"missing_file:{rel_path}")
    if missing:
        return missing

    helper_text = read_text(root, HELPER_PATH)
    build_text = read_text(root, BUILD_PATH)
    survey_text = read_text(root, SURVEY_PATH)
    expect_markers(missing, "helper", helper_text, HELPER_MARKERS)
    expect_markers(missing, "build", build_text, BUILD_MARKERS)
    expect_markers(missing, "survey", survey_text, SURVEY_MARKERS)

    inventory = json.loads(read_text(root, INVENTORY_PATH))
    module_roots = inventory.get("module_root_source_files")
    if not isinstance(module_roots, list) or EXPECTED_LAYOUT_MODULE not in module_roots:
        missing.append("inventory:layout_assert_module_root")

    module_imports = inventory.get("module_imports")
    if not isinstance(module_imports, list) or EXPECTED_SURVEY_IMPORT not in module_imports:
        missing.append("inventory:phase11_uapi_header_parity_survey_layout_assert_import")

    return missing


def write_fixture(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    helper_text = """const abi = @import(\"abi_bindings\");

pub fn assertSize(comptime T: type, comptime expected: usize) void {}
pub fn assertAlign(comptime T: type, comptime expected: usize) void {}
pub fn assertOffset(comptime T: type, comptime field_name: []const u8, comptime expected: usize) void {}
pub fn assertBoundaryHeaderLayout() void {}
pub fn assertExportStatusLayout() void {}
pub fn assertInteropPolicyLayout() void {}
pub fn assertMmioRangeLayout() void {}
pub fn assertBitmapViewLayout() void {}
pub fn assertCpuMaskViewLayout() void {}

test \"phase3 layout assertions cover canonical bindings\" {}
"""
    build_text = """const abi_bindings_module = b.createModule(.{
    .root_source_file = b.path(\"../bindings/abi.zig\"),
});
const layout_assert_module = b.createModule(.{
    .root_source_file = b.path(\"../helpers/layout_assert.zig\"),
});
layout_assert_module.addImport(\"abi_bindings\", abi_bindings_module);
const phase11_uapi_header_parity_survey_module = b.createModule(.{
    .root_source_file = b.path(\"phase11_uapi_header_parity_survey.zig\"),
});
phase11_uapi_header_parity_survey_module.addImport(\"layout_assert\", layout_assert_module);
"""
    survey_text = """const layout_assert = @import(\"layout_assert\");

test \"phase11 shared header parity survey keeps a bounded watchdog_info layout proof\" {
    comptime {
        layout_assert.assertSize(WatchdogInfoLayout, 40);
        layout_assert.assertAlign(WatchdogInfoLayout, 4);
        layout_assert.assertOffset(WatchdogInfoLayout, \"options\", 0);
        layout_assert.assertOffset(WatchdogInfoLayout, \"firmware_version\", 4);
        layout_assert.assertOffset(WatchdogInfoLayout, \"identity\", 8);
    }
}

test \"phase11 shared header parity survey keeps a bounded winsize layout proof\" {
    comptime {
        layout_assert.assertSize(WinsizeLayout, 8);
        layout_assert.assertAlign(WinsizeLayout, 2);
        layout_assert.assertOffset(WinsizeLayout, \"ws_row\", 0);
        layout_assert.assertOffset(WinsizeLayout, \"ws_col\", 2);
        layout_assert.assertOffset(WinsizeLayout, \"ws_xpixel\", 4);
        layout_assert.assertOffset(WinsizeLayout, \"ws_ypixel\", 6);
    }
}
"""
    inventory_text = json.dumps(
        {
            "module_root_source_files": [EXPECTED_LAYOUT_MODULE],
            "module_imports": [EXPECTED_SURVEY_IMPORT],
        },
        indent=2,
    )

    with tempfile.TemporaryDirectory(prefix="phase11_layout_assert_surface_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture(tmp_root, HELPER_PATH, helper_text)
        write_fixture(tmp_root, BUILD_PATH, build_text)
        write_fixture(tmp_root, INVENTORY_PATH, inventory_text)
        write_fixture(tmp_root, SURVEY_PATH, survey_text)

        baseline_missing = check_root(tmp_root)
        if baseline_missing:
            raise SystemExit(f"phase11-layout-assert-self-test:baseline:{baseline_missing[0]}")

        write_fixture(
            tmp_root,
            HELPER_PATH,
            helper_text.replace(
                "pub fn assertOffset(comptime T: type, comptime field_name: []const u8, comptime expected: usize) void {}\n",
                "",
                1,
            ),
        )
        helper_missing = check_root(tmp_root)
        if not any(item.startswith("helper:pub fn assertOffset") for item in helper_missing):
            raise SystemExit("phase11-layout-assert-self-test:helper_missing_assertOffset")
        write_fixture(tmp_root, HELPER_PATH, helper_text)

        write_fixture(
            tmp_root,
            BUILD_PATH,
            build_text.replace('.root_source_file = b.path("../helpers/layout_assert.zig"),\n', "", 1),
        )
        build_missing = check_root(tmp_root)
        if not any(item.startswith('build:.root_source_file = b.path("../helpers/layout_assert.zig"),') for item in build_missing):
            raise SystemExit("phase11-layout-assert-self-test:build_missing_layout_helper_path")
        write_fixture(tmp_root, BUILD_PATH, build_text)

        write_fixture(
            tmp_root,
            INVENTORY_PATH,
            json.dumps({"module_root_source_files": [], "module_imports": [EXPECTED_SURVEY_IMPORT]}, indent=2),
        )
        inventory_missing = check_root(tmp_root)
        if "inventory:layout_assert_module_root" not in inventory_missing:
            raise SystemExit("phase11-layout-assert-self-test:inventory_missing_layout_module_root")
        write_fixture(tmp_root, INVENTORY_PATH, inventory_text)

        write_fixture(
            tmp_root,
            SURVEY_PATH,
            survey_text.replace('const layout_assert = @import("layout_assert");\n', "", 1),
        )
        survey_missing = check_root(tmp_root)
        if not any(item.startswith('survey:const layout_assert = @import("layout_assert");') for item in survey_missing):
            raise SystemExit("phase11-layout-assert-self-test:survey_missing_layout_import")

    print("PHASE11_LAYOUT_ASSERT_SURFACE_SELF_TEST=pass")
    print("PHASE11_LAYOUT_ASSERT_SURFACE_SELF_TEST_CASE_COUNT=4")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


missing = check_root(REPO_ROOT)
if missing:
    print("PHASE11_LAYOUT_ASSERT_SURFACE=fail")
    print("PHASE11_LAYOUT_ASSERT_SURFACE_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE11_LAYOUT_ASSERT_SURFACE_MISSING_END")
    raise SystemExit(1)

print("PHASE11_LAYOUT_ASSERT_SURFACE=pass")
print("PHASE11_LAYOUT_ASSERT_REQUIRED_FILE_COUNT=4")
