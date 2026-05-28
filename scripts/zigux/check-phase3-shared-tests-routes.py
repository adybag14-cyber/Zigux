#!/usr/bin/env python3
"""Fail-close the current shared Phase 3 tests-root route inventory."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


BUILD_PATH = Path("zigux/tests/build.zig")
EXPORT_SHIM_BUILD_PATH = Path("zigux/tests/phase3_export_shim_build.zig")
SELFTEST_DRIVER_PATH = Path("scripts/zigux/validate_phase3_selftest.py")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

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
    "fn addPhase3BitmapCpumaskStarterPacket(",
    '.root_source_file = b.path("../helpers/bitmap_view.zig"),',
    '.root_source_file = b.path("../helpers/cpumask_view.zig"),',
    '.root_source_file = b.path("phase3_bitmap_cpumask_starter_packet.zig"),',
    'cpumask_view.addImport("bitmap_view", bitmap_view);',
    'root_module.addImport("bitmap_view", bitmap_view);',
    'root_module.addImport("cpumask_view", cpumask_view);',
    "fn addPhase3ListHListStarterPacket(",
    '.root_source_file = b.path("../helpers/list_view.zig"),',
    '.root_source_file = b.path("../helpers/hlist_view.zig"),',
    '.root_source_file = b.path("phase3_list_hlist_starter_packet.zig"),',
    'root_module.addImport("list_view", list_view);',
    'root_module.addImport("hlist_view", hlist_view);',
    "fn addPhase3ErrPtrXarrayDump(",
    "fn addPhase3PolicyStarterPacket(",
    "fn addPhase3AbiCorePacket(",
    '.root_source_file = b.path("../helpers/layout_assert.zig"),',
    '.root_source_file = b.path("phase3_abi.zig"),',
    'root_module.addImport("layout_assert", layout_assert);',
    "fn addPhase3ExportUapiLayout(",
    '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
    '.root_source_file = b.path("../bindings/header_family.zig"),',
    'header_family_binding.addImport("abi_bindings", abi_bindings);',
    'header_family_binding.addImport("dev_t_binding", dev_t_binding);',
    'header_family_binding.addImport("version_binding", version_binding);',
    'header_family_binding.addImport("uapi_version", uapi_version);',
    'root_module.addImport("uapi_version", uapi_version);',
    'root_module.addImport("header_family_binding", header_family_binding);',
    "fn addPhase3LowLevelWrappers(",
    "fn addPhase3AbiDump(",
    '.root_source_file = b.path("phase3_abi_dump_current.zig"),',
    '"phase3-dev-t-starter-packet"',
    '"phase3-errptr-xarray-starter-packet"',
    '"phase3-xarray-slot-starter-packet"',
    '"phase3-bitmap-cpumask-starter-packet"',
    '"phase3-list-hlist-starter-packet"',
    '"phase3-errptr-xarray-dump"',
    '"phase3-policy-starter-packet"',
    '"phase3-abi-core-packet"',
    '"phase3-export-uapi-layout"',
    '"phase3-low-level-wrappers"',
    '"phase3-test"',
    '"phase3-dump"',
    "const phase3_xarray_slot_starter_packet = addPhase3XarraySlotStarterPacket(",
    "const phase3_bitmap_cpumask_starter_packet = addPhase3BitmapCpumaskStarterPacket(",
    "const phase3_list_hlist_starter_packet = addPhase3ListHListStarterPacket(",
    "const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);",
    "const phase3_export_uapi_layout = addPhase3ExportUapiLayout(",
    "const phase3_xarray_slot_step = b.step(",
    "const phase3_bitmap_cpumask_step = b.step(",
    "const phase3_list_hlist_step = b.step(",
    "const phase3_abi_core_step = b.step(",
    "const phase3_export_uapi_layout_step = b.step(",
    "phase3_xarray_slot_step.dependOn(&phase3_xarray_slot_starter_packet.step);",
    "phase3_bitmap_cpumask_step.dependOn(&phase3_bitmap_cpumask_starter_packet.step);",
    "phase3_list_hlist_step.dependOn(&phase3_list_hlist_starter_packet.step);",
    "phase3_abi_core_step.dependOn(&phase3_abi_core_packet.step);",
    "phase3_export_uapi_layout_step.dependOn(&phase3_export_uapi_layout.step);",
    "phase3_test_step.dependOn(&phase3_dev_t_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_errptr_xarray_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_xarray_slot_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_bitmap_cpumask_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_list_hlist_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_policy_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_abi_core_packet.step);",
    "phase3_test_step.dependOn(&phase3_export_uapi_layout.step);",
    "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);",
    "phase3_dump_step.dependOn(&phase3_abi_dump.step);",
    "smoke_step.dependOn(phase3_test_step);",
    "test_step.dependOn(phase3_test_step);",
)

REQUIRED_EXPORT_SHIM_BUILD_MARKERS = (
    '.root_source_file = b.path("../bindings/abi.zig"),',
    '.root_source_file = b.path("../uapi/dev_t.zig"),',
    '.root_source_file = b.path("../uapi/version.zig"),',
    '.root_source_file = b.path("../bindings/dev_t.zig"),',
    '.root_source_file = b.path("../bindings/version.zig"),',
    '.root_source_file = b.path("../kernel/export_shim.zig"),',
    'uapi_version_module.addImport("abi_bindings", abi_bindings_module);',
    'dev_t_binding_module.addImport("uapi_dev_t", uapi_dev_t_module);',
    'version_binding_module.addImport("uapi_version", uapi_version_module);',
    'export_shim_module.addImport("abi_bindings", abi_bindings_module);',
    'export_shim_module.addImport("dev_t_binding", dev_t_binding_module);',
    'export_shim_module.addImport("version_binding", version_binding_module);',
    '.name = "phase3-export-shim-test",',
    'b.step(',
    '"phase3-export-shim-test"',
    '"Run the focused Phase 3 export shim replay"',
)

REQUIRED_DRIVER_MARKERS = (
    'Path("scripts/zigux/check-phase3-dev-t-starter-packet.py")',
    'Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py")',
    'Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py")',
    'Path("scripts/zigux/check-phase3-xarray-slot.py")',
    'Path("scripts/zigux/check-phase3-idr-slot-starter-packet.py")',
    'Path("scripts/zigux/check-phase3-idr-slot.py")',
    'Path("scripts/zigux/check-phase3-policy-starter-packet.py")',
    'Path("scripts/zigux/check-phase3-policy-dump.py")',
    'Path("scripts/zigux/validate-phase3.py")',
    'Path("scripts/zigux/check-phase3-abi.py")',
    'Path("scripts/zigux/check-phase3-abi-support-packet.py")',
    'Path("scripts/zigux/check-phase3-abi-manifest-replay-routes.py")',
    'Path("scripts/zigux/check-phase3-shared-tests-routes.py")',
    'Path("scripts/zigux/check-phase3-readme-tooling-inventory.py")',
    'Path("scripts/zigux/check-phase3-wrapper-templates.py")',
    'Path("scripts/zigux/check-phase3-catalog-selftest.py")',
    'Path("scripts/zigux/run-phase3-checks.py")',
    'Path("scripts/zigux/validate-phase3-validator-support-surface.py")',
    'Path("scripts/zigux/validate-phase3-export-uapi-survey.py")',
    'Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")',
    'Path("scripts/zigux/validate-phase3-abi-header-family-survey.py")',
    'Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py")',
    'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
    'Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py")',
    'Path("scripts/zigux/generate-phase3-check-wrappers.py")',
    'Path("scripts/zigux/check-phase3-selftest-surface.py")',
    'Path("scripts/zigux/check-phase3-bitmap-cpumask.py")',
    'Path("scripts/zigux/check-phase3-list-hlist-starter-packet.py")',
)

REQUIRED_MAKEFILE_MARKERS = (
    "phase3-export-uapi-layout:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "phase3-export-uapi-layout-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "phase3-export-shim-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "phase3-low-level-wrappers:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "phase3-low-level-wrappers-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "phase3-policy-starter-packet-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "phase3-policy-dump:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "phase3-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-test --build-file zigux/tests/build.zig",
    "phase3-dump:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump",
)

REQUIRED_WORKFLOW_MARKERS = (
    "- name: Self-test current Phase 3 interop packet",
    "run: python3 scripts/zigux/validate_phase3_selftest.py",
    "- name: Check current Phase 3 interop packet",
    "run: python3 scripts/zigux/run-phase3-checks.py",
    "- name: Run current Phase 3 export/UAPI layout replay",
    "run: zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "- name: Run current Phase 3 export shim replay",
    "run: zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "- name: Run current Phase 3 policy starter-packet replay",
    "run: make -C zigux phase3-policy-starter-packet-test",
    "- name: Run current Phase 3 policy dump replay",
    "run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "- name: Run current Phase 3 policy dump make wrapper",
    "run: make -C zigux phase3-policy-dump",
    "- name: Self-test current Phase 3 low-level wrapper survey validator",
    "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "- name: Check current Phase 3 low-level wrapper survey packet",
    "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "- name: Run current Phase 3 low-level wrapper replay",
    "run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "- name: Run current Phase 3 low-level wrapper make route",
    "run: make -C zigux phase3-low-level-wrappers",
    "- name: Run current Phase 3 focused low-level wrapper make route",
    "run: make -C zigux phase3-low-level-wrappers-test",
    "- name: Run current Phase 3 shared tests-root packet",
    "run: zig build phase3-test --build-file zigux/tests/build.zig",
    "- name: Run current Phase 3 ABI dump replay",
)

SAMPLE_BUILD_TEXT = "\n".join(REQUIRED_BUILD_MARKERS) + "\n"
SAMPLE_EXPORT_SHIM_BUILD_TEXT = "\n".join(REQUIRED_EXPORT_SHIM_BUILD_MARKERS) + "\n"
SAMPLE_DRIVER_TEXT = "\n".join(REQUIRED_DRIVER_MARKERS) + "\n"
SAMPLE_MAKEFILE_TEXT = "\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n"
SAMPLE_WORKFLOW_TEXT = "\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n"

SELF_TEST_CASES = (
    (BUILD_PATH, 'root_module.addImport("export_shim", export_shim);'),
    (BUILD_PATH, '.root_source_file = b.path("../helpers/layout_assert.zig"),'),
    (BUILD_PATH, '.root_source_file = b.path("phase3_abi.zig"),'),
    (BUILD_PATH, 'root_module.addImport("layout_assert", layout_assert);'),
    (BUILD_PATH, '.root_source_file = b.path("../helpers/xarray_slot_view.zig"),'),
    (BUILD_PATH, '.root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),'),
    (BUILD_PATH, 'root_module.addImport("xarray_slot_view", xarray_slot_view);'),
    (BUILD_PATH, 'fn addPhase3BitmapCpumaskStarterPacket('),
    (BUILD_PATH, '.root_source_file = b.path("../helpers/bitmap_view.zig"),'),
    (BUILD_PATH, '.root_source_file = b.path("../helpers/cpumask_view.zig"),'),
    (BUILD_PATH, '.root_source_file = b.path("phase3_bitmap_cpumask_starter_packet.zig"),'),
    (BUILD_PATH, 'cpumask_view.addImport("bitmap_view", bitmap_view);'),
    (BUILD_PATH, 'root_module.addImport("cpumask_view", cpumask_view);'),
    (BUILD_PATH, '"phase3-bitmap-cpumask-starter-packet"'),
    (BUILD_PATH, "const phase3_bitmap_cpumask_starter_packet = addPhase3BitmapCpumaskStarterPacket("),
    (BUILD_PATH, "const phase3_bitmap_cpumask_step = b.step("),
    (BUILD_PATH, "phase3_bitmap_cpumask_step.dependOn(&phase3_bitmap_cpumask_starter_packet.step);"),
    (BUILD_PATH, "phase3_test_step.dependOn(&phase3_bitmap_cpumask_starter_packet.step);"),
    (BUILD_PATH, 'fn addPhase3ListHListStarterPacket('),
    (BUILD_PATH, '.root_source_file = b.path("../helpers/list_view.zig"),'),
    (BUILD_PATH, '.root_source_file = b.path("../helpers/hlist_view.zig"),'),
    (BUILD_PATH, '.root_source_file = b.path("phase3_list_hlist_starter_packet.zig"),'),
    (BUILD_PATH, 'root_module.addImport("list_view", list_view);'),
    (BUILD_PATH, 'root_module.addImport("hlist_view", hlist_view);'),
    (BUILD_PATH, '"phase3-list-hlist-starter-packet"'),
    (BUILD_PATH, "const phase3_list_hlist_starter_packet = addPhase3ListHListStarterPacket("),
    (BUILD_PATH, "const phase3_list_hlist_step = b.step("),
    (BUILD_PATH, "phase3_list_hlist_step.dependOn(&phase3_list_hlist_starter_packet.step);"),
    (BUILD_PATH, "phase3_test_step.dependOn(&phase3_list_hlist_starter_packet.step);"),
    (BUILD_PATH, "fn addPhase3ExportUapiLayout("),
    (BUILD_PATH, '.root_source_file = b.path("phase3_export_uapi_layout.zig"),'),
    (BUILD_PATH, '.root_source_file = b.path("../bindings/header_family.zig"),'),
    (BUILD_PATH, 'header_family_binding.addImport("uapi_version", uapi_version);'),
    (BUILD_PATH, 'root_module.addImport("uapi_version", uapi_version);'),
    (BUILD_PATH, 'root_module.addImport("header_family_binding", header_family_binding);'),
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
        EXPORT_SHIM_BUILD_PATH,
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
    ),
    (
        EXPORT_SHIM_BUILD_PATH,
        'export_shim_module.addImport("version_binding", version_binding_module);',
    ),
    (
        EXPORT_SHIM_BUILD_PATH,
        '.name = "phase3-export-shim-test",',
    ),
    (
        EXPORT_SHIM_BUILD_PATH,
        '"Run the focused Phase 3 export shim replay"',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-dev-t-starter-packet.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-xarray-slot.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-idr-slot-starter-packet.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-idr-slot.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-policy-starter-packet.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-policy-dump.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/validate-phase3.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-abi.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-abi-support-packet.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-abi-manifest-replay-routes.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-shared-tests-routes.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-readme-tooling-inventory.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-wrapper-templates.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-catalog-selftest.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/run-phase3-checks.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/validate-phase3-validator-support-surface.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/validate-phase3-export-uapi-survey.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/validate-phase3-abi-header-family-survey.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/generate-phase3-check-wrappers.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-selftest-surface.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-bitmap-cpumask.py")',
    ),
    (
        SELFTEST_DRIVER_PATH,
        'Path("scripts/zigux/check-phase3-list-hlist-starter-packet.py")',
    ),
    (
        MAKEFILE_PATH,
        "phase3-export-uapi-layout:",
    ),
    (
        MAKEFILE_PATH,
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    ),
    (
        MAKEFILE_PATH,
        "phase3-export-uapi-layout-test:",
    ),
    (
        MAKEFILE_PATH,
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    ),
    (
        MAKEFILE_PATH,
        "phase3-export-shim-test:",
    ),
    (
        MAKEFILE_PATH,
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    ),
    (
        MAKEFILE_PATH,
        "phase3-low-level-wrappers:",
    ),
    (
        MAKEFILE_PATH,
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    ),
    (
        MAKEFILE_PATH,
        "phase3-low-level-wrappers-test:",
    ),
    (
        MAKEFILE_PATH,
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    (
        MAKEFILE_PATH,
        "phase3-policy-starter-packet-test:",
    ),
    (
        MAKEFILE_PATH,
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    ),
    (
        MAKEFILE_PATH,
        "phase3-policy-dump:",
    ),
    (
        MAKEFILE_PATH,
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    ),
    (
        MAKEFILE_PATH,
        "phase3-test:",
    ),
    (
        MAKEFILE_PATH,
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-test --build-file zigux/tests/build.zig",
    ),
    (
        MAKEFILE_PATH,
        "phase3-dump:",
    ),
    (
        MAKEFILE_PATH,
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-dump --build-file zigux/tests/build.zig",
    ),
    (
        MAKEFILE_PATH,
        "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump",
    ),
    (
        WORKFLOW_PATH,
        "- name: Self-test current Phase 3 interop packet",
    ),
    (
        WORKFLOW_PATH,
        "run: python3 scripts/zigux/validate_phase3_selftest.py",
    ),
    (
        WORKFLOW_PATH,
        "- name: Check current Phase 3 interop packet",
    ),
    (
        WORKFLOW_PATH,
        "run: python3 scripts/zigux/run-phase3-checks.py",
    ),
    (
        WORKFLOW_PATH,
        "- name: Run current Phase 3 export/UAPI layout replay",
    ),
    (
        WORKFLOW_PATH,
        "run: zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    ),
    (
        WORKFLOW_PATH,
        "- name: Run current Phase 3 export shim replay",
    ),
    (
        WORKFLOW_PATH,
        "run: zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    ),
    (
        WORKFLOW_PATH,
        "- name: Run current Phase 3 policy starter-packet replay",
    ),
    (
        WORKFLOW_PATH,
        "run: make -C zigux phase3-policy-starter-packet-test",
    ),
    (
        WORKFLOW_PATH,
        "- name: Run current Phase 3 policy dump replay",
    ),
    (
        WORKFLOW_PATH,
        "run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    ),
    (
        WORKFLOW_PATH,
        "- name: Run current Phase 3 policy dump make wrapper",
    ),
    (
        WORKFLOW_PATH,
        "run: make -C zigux phase3-policy-dump",
    ),
    (
        WORKFLOW_PATH,
        "- name: Self-test current Phase 3 low-level wrapper survey validator",
    ),
    (
        WORKFLOW_PATH,
        "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    ),
    (
        WORKFLOW_PATH,
        "- name: Check current Phase 3 low-level wrapper survey packet",
    ),
    (
        WORKFLOW_PATH,
        "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    ),
    (
        WORKFLOW_PATH,
        "- name: Run current Phase 3 low-level wrapper replay",
    ),
    (
        WORKFLOW_PATH,
        "run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    (
        WORKFLOW_PATH,
        "- name: Run current Phase 3 low-level wrapper make route",
    ),
    (
        WORKFLOW_PATH,
        "run: make -C zigux phase3-low-level-wrappers",
    ),
    (
        WORKFLOW_PATH,
        "- name: Run current Phase 3 focused low-level wrapper make route",
    ),
    (
        WORKFLOW_PATH,
        "run: make -C zigux phase3-low-level-wrappers-test",
    ),
    (
        WORKFLOW_PATH,
        "- name: Run current Phase 3 shared tests-root packet",
    ),
    (
        WORKFLOW_PATH,
        "run: zig build phase3-test --build-file zigux/tests/build.zig",
    ),
    (
        WORKFLOW_PATH,
        "- name: Run current Phase 3 ABI dump replay",
    ),
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _remove_exact_line(path: Path, marker: str) -> None:
    lines = _read_text(path).splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            del lines[index]
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _validate_markers(repo_root: Path, relative_path: Path, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    path = repo_root / relative_path
    try:
        text = _read_text(path)
    except FileNotFoundError:
        issues.append(f"missing repo file: {relative_path.as_posix()}")
        return issues

    for marker in markers:
        if marker not in text:
            issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    return issues


def _validate_exact_lines(repo_root: Path, relative_path: Path, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    path = repo_root / relative_path
    try:
        lines = _read_text(path).splitlines()
    except FileNotFoundError:
        issues.append(f"missing repo file: {relative_path.as_posix()}")
        return issues

    for marker in markers:
        if marker not in lines:
            issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    return issues


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    issues.extend(_validate_markers(repo_root, BUILD_PATH, REQUIRED_BUILD_MARKERS))
    issues.extend(
        _validate_markers(
            repo_root,
            EXPORT_SHIM_BUILD_PATH,
            REQUIRED_EXPORT_SHIM_BUILD_MARKERS,
        )
    )
    issues.extend(_validate_markers(repo_root, SELFTEST_DRIVER_PATH, REQUIRED_DRIVER_MARKERS))
    issues.extend(_validate_exact_lines(repo_root, MAKEFILE_PATH, REQUIRED_MAKEFILE_MARKERS))
    issues.extend(_validate_exact_lines(repo_root, WORKFLOW_PATH, REQUIRED_WORKFLOW_MARKERS))
    return issues


def _populate_repo(root: Path) -> None:
    _write_text(root / BUILD_PATH, SAMPLE_BUILD_TEXT)
    _write_text(root / EXPORT_SHIM_BUILD_PATH, SAMPLE_EXPORT_SHIM_BUILD_TEXT)
    _write_text(root / SELFTEST_DRIVER_PATH, SAMPLE_DRIVER_TEXT)
    _write_text(root / MAKEFILE_PATH, SAMPLE_MAKEFILE_TEXT)
    _write_text(root / WORKFLOW_PATH, SAMPLE_WORKFLOW_TEXT)


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
            _remove_exact_line(path, marker)
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
    print(f"validated {args.repo_root / EXPORT_SHIM_BUILD_PATH}")
    print(f"validated {args.repo_root / SELFTEST_DRIVER_PATH}")
    print(f"validated {args.repo_root / MAKEFILE_PATH}")
    print(f"validated {args.repo_root / WORKFLOW_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
