#!/usr/bin/env python3
"""Fail-close the current shared Phase 3 tests-root route inventory."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


BUILD_PATH = Path("zigux/tests/build.zig")
SELFTEST_DRIVER_PATH = Path("scripts/zigux/validate_phase3_selftest.py")

REQUIRED_BUILD_MARKERS = (
    "fn addPhase3DevTStarterPacket(",
    '.root_source_file = b.path("../uapi/dev_t.zig"),',
    '.root_source_file = b.path("../uapi/version.zig"),',
    '.root_source_file = b.path("../bindings/dev_t.zig"),',
    '.root_source_file = b.path("../bindings/version.zig"),',
    '.root_source_file = b.path("../bindings/abi.zig"),',
    '.root_source_file = b.path("../kernel/export_shim.zig"),',
    'version_binding.addImport("uapi_version", uapi_version);',
    'export_shim.addImport("abi_bindings", abi_bindings);',
    'export_shim.addImport("dev_t_binding", dev_t_binding);',
    'export_shim.addImport("version_binding", version_binding);',
    'root_module.addImport("uapi_dev_t", uapi_dev_t);',
    'root_module.addImport("dev_t_binding", dev_t_binding);',
    'root_module.addImport("version_binding", version_binding);',
    'root_module.addImport("export_shim", export_shim);',
    "fn addPhase3ErrPtrXarrayStarterPacket(",
    "fn addPhase3XarraySlotStarterPacket(",
    '.root_source_file = b.path("../helpers/xarray_slot_view.zig"),',
    '.root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),',
    'xarray_slot_view.addImport("err_ptr", err_ptr);',
    'xarray_slot_view.addImport("xa_value", xa_value);',
    'root_module.addImport("xarray_slot_view", xarray_slot_view);',
    "fn addPhase3ErrPtrXarrayDump(",
    "fn addPhase3PolicyStarterPacket(",
    "fn addPhase3AbiCorePacket(",
    '.root_source_file = b.path("../helpers/layout_assert.zig"),',
    '.root_source_file = b.path("phase3_abi.zig"),',
    'root_module.addImport("layout_assert", layout_assert);',
    "fn addPhase3ExportUapiLayout(",
    '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
    'root_module.addImport("uapi_version", uapi_version);',
    "fn addPhase3LowLevelWrappers(",
    "fn addPhase3AbiDump(",
    '.root_source_file = b.path("phase3_abi_dump_current.zig"),',
    '"phase3-dev-t-starter-packet"',
    '"phase3-errptr-xarray-starter-packet"',
    '"phase3-xarray-slot-starter-packet"',
    '"phase3-errptr-xarray-dump"',
    '"phase3-policy-starter-packet"',
    '"phase3-abi-core-packet"',
    '"phase3-export-uapi-layout"',
    '"phase3-low-level-wrappers"',
    '"phase3-test"',
    '"phase3-dump"',
    "const phase3_xarray_slot_starter_packet = addPhase3XarraySlotStarterPacket(",
    "const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);",
    "const phase3_export_uapi_layout = addPhase3ExportUapiLayout(",
    "const phase3_xarray_slot_step = b.step(",
    "const phase3_abi_core_step = b.step(",
    "const phase3_export_uapi_layout_step = b.step(",
    "phase3_xarray_slot_step.dependOn(&phase3_xarray_slot_starter_packet.step);",
    "phase3_abi_core_step.dependOn(&phase3_abi_core_packet.step);",
    "phase3_export_uapi_layout_step.dependOn(&phase3_export_uapi_layout.step);",
    "phase3_test_step.dependOn(&phase3_dev_t_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_errptr_xarray_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_xarray_slot_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_policy_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_abi_core_packet.step);",
    "phase3_test_step.dependOn(&phase3_export_uapi_layout.step);",
    "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);",
    "phase3_dump_step.dependOn(&phase3_abi_dump.step);",
    "smoke_step.dependOn(phase3_test_step);",
    "test_step.dependOn(phase3_test_step);",
)

REQUIRED_DRIVER_MARKERS = (
    'Path("scripts/zigux/check-phase3-dev-t-starter-packet.py")',
    'Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py")',
    'Path("scripts/zigux/check-phase3-policy-starter-packet.py")',
    'Path("scripts/zigux/check-phase3-shared-tests-routes.py")',
    'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
    'Path("scripts/zigux/check-phase3-selftest-surface.py")',
)

SAMPLE_BUILD_TEXT = "\n".join(REQUIRED_BUILD_MARKERS) + "\n"
SAMPLE_DRIVER_TEXT = "\n".join(REQUIRED_DRIVER_MARKERS) + "\n"

SELF_TEST_CASES = (
    (BUILD_PATH, 'root_module.addImport("export_shim", export_shim);'),
    (BUILD_PATH, '.root_source_file = b.path("../helpers/layout_assert.zig"),'),
    (BUILD_PATH, '.root_source_file = b.path("phase3_abi.zig"),'),
    (BUILD_PATH, 'root_module.addImport("layout_assert", layout_assert);'),
    (BUILD_PATH, '.root_source_file = b.path("../helpers/xarray_slot_view.zig"),'),
    (BUILD_PATH, '.root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),'),
    (BUILD_PATH, 'root_module.addImport("xarray_slot_view", xarray_slot_view);'),
    (BUILD_PATH, "fn addPhase3ExportUapiLayout("),
    (BUILD_PATH, '.root_source_file = b.path("phase3_export_uapi_layout.zig"),'),
    (BUILD_PATH, 'root_module.addImport("uapi_version", uapi_version);'),
    (BUILD_PATH, '"phase3-export-uapi-layout"'),
    (BUILD_PATH, "const phase3_export_uapi_layout = addPhase3ExportUapiLayout("),
    (BUILD_PATH, "const phase3_export_uapi_layout_step = b.step("),
    (BUILD_PATH, "phase3_export_uapi_layout_step.dependOn(&phase3_export_uapi_layout.step);"),
    (BUILD_PATH, "phase3_test_step.dependOn(&phase3_export_uapi_layout.step);"),
    (BUILD_PATH, '"phase3-abi-core-packet"'),
    (BUILD_PATH, '"phase3-xarray-slot-starter-packet"'),
    (BUILD_PATH, "const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);"),
    (BUILD_PATH, "const phase3_abi_core_step = b.step("),
    (BUILD_PATH, "phase3_abi_core_step.dependOn(&phase3_abi_core_packet.step);"),
    (BUILD_PATH, "phase3_xarray_slot_step.dependOn(&phase3_xarray_slot_starter_packet.step);"),
    (BUILD_PATH, '.root_source_file = b.path("phase3_abi_dump_current.zig"),'),
    (BUILD_PATH, '"phase3-low-level-wrappers"'),
    (BUILD_PATH, "phase3_test_step.dependOn(&phase3_abi_core_packet.step);"),
    (BUILD_PATH, "phase3_test_step.dependOn(&phase3_xarray_slot_starter_packet.step);"),
    (BUILD_PATH, "phase3_dump_step.dependOn(&phase3_abi_dump.step);"),
    (BUILD_PATH, "smoke_step.dependOn(phase3_test_step);"),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-shared-tests-routes.py")',
    ),
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    build_path = repo_root / BUILD_PATH
    try:
        build_text = _read_text(build_path)
    except FileNotFoundError:
        issues.append(f"missing repo file: {BUILD_PATH.as_posix()}")
    else:
        for marker in REQUIRED_BUILD_MARKERS:
            if marker not in build_text:
                issues.append(f"missing {BUILD_PATH.as_posix()} marker: {marker}")

    driver_path = repo_root / SELFTEST_DRIVER_PATH
    try:
        driver_text = _read_text(driver_path)
    except FileNotFoundError:
        issues.append(f"missing repo file: {SELFTEST_DRIVER_PATH.as_posix()}")
    else:
        for marker in REQUIRED_DRIVER_MARKERS:
            if marker not in driver_text:
                issues.append(
                    f"missing {SELFTEST_DRIVER_PATH.as_posix()} marker: {marker}"
                )

    return issues


def _populate_repo(root: Path) -> None:
    _write_text(root / BUILD_PATH, SAMPLE_BUILD_TEXT)
    _write_text(root / SELFTEST_DRIVER_PATH, SAMPLE_DRIVER_TEXT)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(
        prefix="zigux_phase3_shared_tests_routes_"
    ) as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_SHARED_TESTS_ROUTES_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read_text(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_SHARED_TESTS_ROUTES_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_SHARED_TESTS_ROUTES_SELF_TEST=pass")
    print(f"PHASE3_SHARED_TESTS_ROUTES_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current shared Phase 3 tests-root route inventory."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the shared Phase 3 tests-root surfaces",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_SHARED_TESTS_ROUTES=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / BUILD_PATH}")
    print(f"validated {args.repo_root / SELFTEST_DRIVER_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
