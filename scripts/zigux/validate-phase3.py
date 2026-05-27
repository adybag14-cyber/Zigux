#!/usr/bin/env python3
"""Validate the current bounded Phase 3 shared ABI packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

ABI_HEADER_PATH = Path("include/zigux/abi.h")
ABI_BINDINGS_PATH = Path("zigux/bindings/abi.zig")
NOTIFIER_BINDINGS_PATH = Path("zigux/bindings/notifier_abi.zig")
RUNNER_PATH = Path("scripts/zigux/run-phase3-checks.py")
VALIDATE_PHASE3_SELFTEST_PATH = Path("scripts/zigux/validate_phase3_selftest.py")
README_TOOLING_INVENTORY_PATH = Path(
    "scripts/zigux/check-phase3-readme-tooling-inventory.py"
)
TESTS_BUILD_PATH = Path("zigux/tests/build.zig")
ABI_TEST_PATH = Path("zigux/tests/phase3_abi.zig")
ABI_DUMP_PATH = Path("zigux/tests/phase3_abi_dump_current.zig")
EXPORT_UAPI_LAYOUT_PATH = Path("zigux/tests/phase3_export_uapi_layout.zig")
EXPORT_UAPI_LAYOUT_BUILD_PATH = Path("zigux/tests/phase3_export_uapi_layout_build.zig")
EXPORT_SHIM_BUILD_PATH = Path("zigux/tests/phase3_export_shim_build.zig")
EXPORT_SHIM_PATH = Path("zigux/kernel/export_shim.zig")
UAPI_VERSION_PATH = Path("zigux/uapi/version.zig")
ABI_MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

CURRENT_NEXT_SAFE_STEP = (
    "keep the shared Phase 3 policy, export/UAPI, and low-level wrapper packet "
    "aligned with the dedicated replay routes and only reopen this manifest if the "
    "checker, focused builds, or reminder surfaces drift again"
)

REQUIRED_SOURCE_MARKERS = {
    ABI_HEADER_PATH: (
        "#define ZIGUX_ABI_VERSION 1U",
        "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U",
        "struct zigux_boundary_header {",
        "struct zigux_interop_policy {",
        "struct zigux_export_status {",
        "struct zigux_notifier_block {",
        "static inline int zigux_notifier_chain_has_nonincreasing_priority(",
        "static inline int zigux_list_first_broken_backlink(",
        "static inline int zigux_hlist_first_broken_prev_link(",
        "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
        "static inline struct zigux_interop_policy zigux_default_interop_policy(void)",
        "static inline struct zigux_export_status zigux_make_status(",
    ),
    ABI_BINDINGS_PATH: (
        'const notifier_abi = @import("notifier_abi.zig");',
        "pub const ABI_VERSION: u16 = 1;",
        "pub const UNSAFE_RAW_POINTER_BRIDGE: u8 = 2;",
        "pub const BoundaryHeader = extern struct {",
        "pub const InteropPolicy = extern struct {",
        "pub const ExportStatus = extern struct {",
        "pub const NotifierResult = notifier_abi.NotifierResult;",
        "pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {",
        "pub fn firstBrokenPrevLink(head: ?*const HListHead) ?HListPrevLinkBreak {",
        "pub fn defaultHeader(flags: u16) BoundaryHeader {",
        "pub fn defaultInteropPolicy() InteropPolicy {",
        "pub fn makeStatus(code: i32, facility: Facility) ExportStatus {",
    ),
    NOTIFIER_BINDINGS_PATH: (
        "pub const NotifierResult = enum(u32) {",
        "pub const NotifierBlock = extern struct {",
        "pub const NotifierChainPriorityIncrease = extern struct {",
        "pub const ListHead = extern struct {",
        "pub const HListHead = extern struct {",
        "pub const HListNode = extern struct {",
        "pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?NotifierChainPriorityIncrease {",
        "pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {",
        "pub fn firstBrokenPrevLink(head: ?*const HListHead) ?HListPrevLinkBreak {",
    ),
    RUNNER_PATH: (
        'Path("scripts/zigux/check-phase3-policy-dump.py")',
        'Path("scripts/zigux/validate-phase3.py")',
        'Path("scripts/zigux/check-phase3-abi.py")',
        'Path("scripts/zigux/check-phase3-abi-support-packet.py")',
        'Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py")',
        'Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py")',
        'Path("scripts/zigux/check-phase3-xarray-slot.py")',
        'Path("scripts/zigux/check-phase3-shared-tests-routes.py")',
        'Path("scripts/zigux/check-phase3-readme-tooling-inventory.py")',
        'Path("scripts/zigux/check-phase3-selftest-surface.py")',
        'Path("scripts/zigux/check-phase3-abi-manifest-replay-routes.py")',
        'Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")',
        'Path("scripts/zigux/check-phase3-wrapper-templates.py")',
        'Path("scripts/zigux/validate-phase3-export-uapi-survey.py")',
        'Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py")',
        'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
        'Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py")',
        'Path("scripts/zigux/check-phase3-bitmap-cpumask.py")',
        'Path("scripts/zigux/check-phase3-list-hlist-starter-packet.py")',
        'Path("scripts/zigux/check-phase3-idr-slot-starter-packet.py")',
        'Path("scripts/zigux/check-phase3-idr-slot.py")',
        '"PHASE3_ERRPTR_XARRAY_STARTER_PACKET=pass"',
        '"PHASE3_XARRAY_SLOT_STARTER_PACKET=pass"',
        '"validated zigux/tests/phase3_xarray_slot_dump.zig"',
        '"validated zigux/tests/fixtures/phase3_xarray_slot_manifest.json"',
        '"PHASE3_ABI_MANIFEST_REPLAY_ROUTES=pass"',
        '"validated scripts/zigux/generate-phase3-check-wrappers.py"',
        '"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass"',
        '"PHASE3_WRAPPER_TEMPLATES_CHECK=pass"',
        '"PHASE3_BITMAP_CPUMASK_PACKET=pass"',
        '"validated zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json"',
        '"validated zigux/helpers/list_view.zig"',
        '"validated zigux/tests/fixtures/phase3_list_hlist_manifest.json"',
        '"validated zigux/tests/phase3_idr_slot_starter_packet.zig"',
        '"validated zigux/tests/fixtures/phase3_idr_slot_manifest.json"',
    ),
    VALIDATE_PHASE3_SELFTEST_PATH: (
        'Path("scripts/zigux/validate-phase3.py")',
        'Path("scripts/zigux/check-phase3-abi.py")',
        'Path("scripts/zigux/check-phase3-abi-support-packet.py")',
        'Path("scripts/zigux/check-phase3-abi-manifest-replay-routes.py")',
        'Path("scripts/zigux/check-phase3-policy-dump.py")',
        'Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py")',
        'Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py")',
        'Path("scripts/zigux/check-phase3-xarray-slot.py")',
        'Path("scripts/zigux/check-phase3-readme-tooling-inventory.py")',
        'Path("scripts/zigux/check-phase3-wrapper-templates.py")',
        'Path("scripts/zigux/generate-phase3-check-wrappers.py")',
        'Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py")',
        'Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")',
        'Path("scripts/zigux/check-phase3-selftest-surface.py")',
        'Path("scripts/zigux/run-phase3-checks.py")',
        'Path("scripts/zigux/check-phase3-bitmap-cpumask.py")',
        'Path("scripts/zigux/check-phase3-list-hlist-starter-packet.py")',
        '"PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=pass"',
        '"PHASE3_POLICY_DUMP_SELF_TEST=pass"',
        '"PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=pass"',
        '"PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST_CASES="',
        '"PHASE3_XARRAY_SLOT_STARTER_PACKET_SELF_TEST=pass"',
        '"PHASE3_XARRAY_SLOT_STARTER_PACKET_SELF_TEST_CASES="',
        '"PHASE3_XARRAY_SLOT_SELF_TEST=pass"',
        '"PHASE3_XARRAY_SLOT_SELF_TEST_CASES="',
        '"PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass"',
        '"PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT="',
        '"PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass"',
        '"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass"',
        '"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT="',
        '"PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=pass"',
        '"PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST_CASE_COUNT="',
        '"PHASE3_WRAPPER_SELF_TEST=pass"',
        '"PHASE3_WRAPPER_SELF_TEST_CASE_COUNT="',
        '"PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=pass"',
        '"PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST_CASE_COUNT="',
        '"PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=pass"',
        '"PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST_CASE_COUNT="',
        '"PHASE3_VALIDATE_SELFTEST=pass"',
    ),
    TESTS_BUILD_PATH: (
        "const phase3_policy_starter_packet = addPhase3PolicyStarterPacket(b, target, optimize);",
        "const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);",
        "const phase3_export_uapi_layout = addPhase3ExportUapiLayout(b, target, optimize);",
        "const phase3_low_level_wrappers = addPhase3LowLevelWrappers(b, target, optimize);",
        "const phase3_abi_dump = addPhase3AbiDump(b, target, optimize);",
        'root_source_file = b.path("phase3_abi.zig"),',
        'root_source_file = b.path("phase3_export_uapi_layout.zig"),',
        'root_source_file = b.path("phase3_abi_dump_current.zig"),',
        'root_module.addImport("header_family_binding", header_family_binding);',
        '"phase3-export-uapi-layout"',
        '"phase3-low-level-wrappers"',
        '"phase3-test"',
        '"phase3-dump"',
        "phase3_test_step.dependOn(&phase3_export_uapi_layout.step);",
        "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);",
        "phase3_dump_step.dependOn(&phase3_abi_dump.step);",
    ),
    ABI_TEST_PATH: (
        'test "phase3 abi keeps shared layout assertions wired into the replay" {',
        "try layout_assert.assertPublishedAbiLayouts();",
        'test "phase3 abi keeps export shim compatibility and status helpers reviewable" {',
        'test "phase3 abi keeps version and dev_t relays explicit" {',
        'test "phase3 abi keeps policy helper decoding aligned with interop policy bytes" {',
        'test "phase3 abi keeps malformed notifier list relays visible through the shared ABI surface" {',
    ),
    ABI_DUMP_PATH: (
        'const abi = @import("abi_bindings");',
        "const default_header = abi.defaultHeader(0);",
        "const policy = abi.defaultInteropPolicy();",
        "abi.STATUS_FLAG_ERROR,",
        "abi.NOTIFIER_DONE,",
        '@offsetOf(abi.NotifierBlock, "priority"),',
        '"  \\\"notifier\\\": {\\n"',
    ),
    EXPORT_UAPI_LAYOUT_PATH: (
        'const header_family = @import("header_family_binding");',
        'test "export and uapi dev_t layouts stay aligned" {',
        'test "export and uapi version layouts stay aligned" {',
        'test "header-family binding keeps the bounded relay surface explicit" {',
        'test "export shim relays version compatibility without widening the boundary" {',
        'test "export shim keeps facility tagged statuses explicit" {',
    ),
    EXPORT_UAPI_LAYOUT_BUILD_PATH: (
        '.root_source_file = b.path("../uapi/dev_t.zig"),',
        '.root_source_file = b.path("../uapi/version.zig"),',
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
        '.root_source_file = b.path("../bindings/header_family.zig"),',
        '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
        'root_module.addImport("header_family_binding", header_family_binding);',
        '"phase3-export-uapi-layout-test"',
    ),
    EXPORT_SHIM_BUILD_PATH: (
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
        'export_shim_module.addImport("abi_bindings", abi_bindings_module);',
        'export_shim_module.addImport("dev_t_binding", dev_t_binding_module);',
        'export_shim_module.addImport("version_binding", version_binding_module);',
        '.name = "phase3-export-shim-test",',
        '"Run the focused Phase 3 export shim replay",',
    ),
    EXPORT_SHIM_PATH: (
        "pub const Header = version.Header;",
        "pub fn canonicalHeader(flags: u16) BoundaryHeader {",
        "pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {",
        "pub fn validateVersion(candidate: Version) ExportStatus {",
        "pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {",
        'test "export shim relays boundary header compatibility through status helpers" {',
    ),
    UAPI_VERSION_PATH: (
        "pub const abi_major: u32 = 0;",
        "pub const abi_minor: u32 = 1;",
        "pub const header_family_revision: u32 = 1;",
        "pub fn compatibleHeader(size: u32, flags: u16) Header {",
        "pub fn validateBoundaryHeader(header: Header) abi.ExportStatus {",
        'test "version helpers keep boundary header compatibility explicit" {',
    ),
}

REQUIRED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
    "status": "shared_abi_and_header_family_binding_surface_present",
    "scope": (
        "shared ABI bindings, directly coupled helper decoding, header-family "
        "follow-through, notifier layouts, export-status layout, and "
        "header-compatibility replay"
    ),
    "next_safe_step": CURRENT_NEXT_SAFE_STEP,
}

REQUIRED_MANIFEST_PACKET_FILES = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-kernel-export-shim-governance.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "Documentation/zigux/phase3-shared-reminder-gap.md",
    "include/zigux/abi.h",
    "include/zigux/dev_t.h",
    "include/linux/zigux.h",
    "zigux/uapi/dev_t.zig",
    "zigux/uapi/version.zig",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/version.zig",
    "zigux/bindings/header_family.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/unsafe/narrow.zig",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/check-phase3-abi-manifest-replay-routes.py",
    "scripts/zigux/check-phase3-abi-support-packet.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
    "scripts/zigux/check-phase3-xarray-slot.py",
    "scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "scripts/zigux/check-phase3-policy-dump.py",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/check-phase3-shared-tests-routes.py",
    "scripts/zigux/check-phase3-wrapper-templates.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "scripts/zigux/run-phase3-checks.py",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump_current.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json",
    "zigux/tests/phase3_errptr_xarray_dump.zig",
    "zigux/tests/phase3_errptr_xarray_dump_build.zig",
    "Documentation/zigux/phase3-xarray-slot-slice.md",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c",
    "zigux/tests/fixtures/phase3_xarray_slot/expected.json",
    "zigux/tests/fixtures/phase3_xarray_slot_manifest.json",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "zigux/tests/phase3_policy_dump.zig",
    "zigux/tests/phase3_policy_dump_build.zig",
    "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
    "zigux/tests/phase3_export_uapi_c_header_smoke.c",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_export_shim_build.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
    "zigux/helpers/bitmap_view.zig",
    "zigux/helpers/cpumask_view.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json",
    "scripts/zigux/check-phase3-bitmap-cpumask.py",
    "Documentation/zigux/phase3-list-hlist-slice.md",
    "zigux/helpers/list_view.zig",
    "zigux/helpers/hlist_view.zig",
    "zigux/tests/phase3_list_hlist_starter_packet.zig",
    "zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_list_hlist_manifest.json",
    "scripts/zigux/check-phase3-list-hlist-starter-packet.py",
    "Documentation/zigux/phase3-idr-slot-slice.md",
    "zigux/helpers/idr_slot_view.zig",
    "zigux/tests/phase3_idr_slot_starter_packet.zig",
    "zigux/tests/phase3_idr_slot_starter_packet_build.zig",
    "zigux/tests/phase3_idr_slot_dump.zig",
    "zigux/tests/phase3_idr_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_idr_slot/phase3_idr_slot_c_harness.c",
    "zigux/tests/fixtures/phase3_idr_slot/expected.json",
    "zigux/tests/fixtures/phase3_idr_slot_manifest.json",
    "scripts/zigux/check-phase3-idr-slot-starter-packet.py",
    "scripts/zigux/check-phase3-idr-slot.py",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml"
)

REQUIRED_MANIFEST_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-abi.py --self-test",
    "python3 scripts/zigux/check-phase3-abi.py",
    "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test",
    "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py",
    "python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-abi-support-packet.py",
    "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
    "python3 scripts/zigux/check-phase3-xarray-slot.py --self-test",
    "python3 scripts/zigux/check-phase3-xarray-slot.py",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py",
    "python3 scripts/zigux/check-phase3-policy-dump.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-dump.py",
    "python3 scripts/zigux/check-phase3-shared-tests-routes.py --self-test",
    "python3 scripts/zigux/check-phase3-shared-tests-routes.py",
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test",
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "python3 scripts/zigux/check-phase3-wrapper-templates.py --self-test",
    "python3 scripts/zigux/check-phase3-wrapper-templates.py",
    "python3 scripts/zigux/check-phase3-catalog-selftest.py --self-test",
    "python3 scripts/zigux/check-phase3-catalog-selftest.py",
    "python3 scripts/zigux/validate-phase3.py --self-test",
    "python3 scripts/zigux/validate-phase3.py",
    "python3 scripts/zigux/validate-phase3-validator-support-surface.py --self-test",
    "python3 scripts/zigux/validate-phase3-validator-support-surface.py",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
    "python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test",
    "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "python3 scripts/zigux/check-phase3-selftest-surface.py --self-test",
    "python3 scripts/zigux/check-phase3-selftest-surface.py",
    "python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test",
    "python3 scripts/zigux/validate_phase3_selftest.py",
    "python3 scripts/zigux/run-phase3-checks.py",
    "make -C zigux phase3-validate",
    "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py --self-test",
    "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test",
    "python3 scripts/zigux/check-phase3-bitmap-cpumask.py",
    "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py",
    "python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --repo-root .",
    "python3 scripts/zigux/check-phase3-idr-slot.py --self-test",
    "python3 scripts/zigux/check-phase3-idr-slot.py --repo-root . --zig zig --cc gcc",
    "zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all",
    "zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig",
    "zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "make -C zigux phase3-policy-starter-packet-test",
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "make -C zigux phase3-policy-dump",
    "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "make -C zigux phase3-export-shim-test",
    "make -C zigux phase3-export-uapi-layout",
    "make -C zigux phase3-export-uapi-layout-test",
    "zig build phase3-abi-core-packet --build-file zigux/tests/build.zig",
    "zig build phase3-dump --build-file zigux/tests/build.zig",
    "make -C zigux phase3-dump",
    "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "make -C zigux phase3-low-level-wrappers",
    "zig build phase3-test --build-file zigux/tests/build.zig",
    "make -C zigux phase3-test",
    "make -C zigux phase3",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-low-level-wrappers-test",
    "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "zig build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig",
    "zig build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig",
)

HEADER_TYPEDEF_ALIAS_RE = re.compile(r"^\s*}\s*([A-Za-z_][A-Za-z0-9_]*)\s*;")
ZIG_PUB_FN_RE = re.compile(r"^\s*pub fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _append_duplicate_name_issues(
    rel_path: Path,
    text: str,
    pattern: re.Pattern[str],
    label: str,
    issues: list[str],
) -> None:
    first_lines: dict[str, int] = {}
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = pattern.match(line)
        if match is None:
            continue
        name = match.group(1)
        first_line = first_lines.get(name)
        if first_line is None:
            first_lines[name] = line_no
            continue
        issues.append(
            f"duplicate {label}: {name} (first line {first_line}, duplicate line {line_no})"
        )


def _append_duplicate_list_entry_issues(
    label: str,
    values: list[object],
    issues: list[str],
) -> None:
    seen: dict[str, int] = {}
    for index, value in enumerate(values):
        key = repr(value)
        first_index = seen.get(key)
        if first_index is None:
            seen[key] = index
            continue
        issues.append(
            f"{label} duplicate entry: {value!r} (first index {first_index}, duplicate index {index})"
        )


def _append_missing_packet_file_issues(
    repo_root: Path,
    packet_files: list[object],
    issues: list[str],
) -> None:
    for entry in packet_files:
        if not isinstance(entry, str):
            issues.append(
                f"phase3_abi_manifest.json packet_files has non-string entry: {entry!r}"
            )
            continue
        if not (repo_root / entry).is_file():
            issues.append(
                "phase3_abi_manifest.json packet_files entry missing on disk: "
                f"{entry}"
            )


def _abi_header_constant_names(text: str) -> set[str]:
    return set(re.findall(r"^\s*#define\s+ZIGUX_([A-Z0-9_]+)\b", text, flags=re.MULTILINE))


def _abi_binding_constant_names(text: str) -> set[str]:
    return set(re.findall(r"^\s*pub const\s+([A-Z0-9_]+)\s*:", text, flags=re.MULTILINE))


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    texts: dict[Path, str] = {}

    for rel_path, markers in REQUIRED_SOURCE_MARKERS.items():
        path = repo_root / rel_path
        if not path.is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
            continue
        text = _read(path)
        texts[rel_path] = text
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {rel_path.as_posix()} marker: {marker}")

    manifest_path = repo_root / ABI_MANIFEST_PATH
    if not manifest_path.is_file():
        issues.append(f"missing repo file: {ABI_MANIFEST_PATH.as_posix()}")
    else:
        manifest_text = _read(manifest_path)
        try:
            manifest = json.loads(manifest_text)
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON in {ABI_MANIFEST_PATH.as_posix()}: {exc}")
        else:
            for field, expected in REQUIRED_MANIFEST_FIELDS.items():
                actual = manifest.get(field)
                if actual != expected:
                    issues.append(
                        f"phase3_abi_manifest.json wrong {field}: {actual!r} != {expected!r}"
                    )

            packet_files = manifest.get("packet_files")
            replay_routes = manifest.get("replay_routes")
            repo_reality_gaps = manifest.get("repo_reality_gaps")

            if not isinstance(packet_files, list):
                issues.append("phase3_abi_manifest.json packet_files is not a list")
            else:
                _append_duplicate_list_entry_issues(
                    "phase3_abi_manifest.json packet_files",
                    packet_files,
                    issues,
                )
                for entry in REQUIRED_MANIFEST_PACKET_FILES:
                    if entry not in packet_files:
                        issues.append(
                            f"phase3_abi_manifest.json missing packet_files entry: {entry}"
                        )
                _append_missing_packet_file_issues(repo_root, packet_files, issues)

            if not isinstance(replay_routes, list):
                issues.append("phase3_abi_manifest.json replay_routes is not a list")
            else:
                _append_duplicate_list_entry_issues(
                    "phase3_abi_manifest.json replay_routes",
                    replay_routes,
                    issues,
                )
                for entry in REQUIRED_MANIFEST_REPLAY_ROUTES:
                    if entry not in replay_routes:
                        issues.append(
                            f"phase3_abi_manifest.json missing replay route: {entry}"
                        )

            if not isinstance(repo_reality_gaps, list):
                issues.append("phase3_abi_manifest.json repo_reality_gaps is not a list")
            else:
                _append_duplicate_list_entry_issues(
                    "phase3_abi_manifest.json repo_reality_gaps",
                    repo_reality_gaps,
                    issues,
                )
                if repo_reality_gaps:
                    issues.append(
                        "phase3_abi_manifest.json repo_reality_gaps drifted from the current shared packet expectation"
                    )

    header_text = texts.get(ABI_HEADER_PATH)
    if header_text is not None:
        _append_duplicate_name_issues(
            ABI_HEADER_PATH,
            header_text,
            HEADER_TYPEDEF_ALIAS_RE,
            "ABI header typedef alias",
            issues,
        )

    bindings_text = texts.get(ABI_BINDINGS_PATH)
    if bindings_text is not None:
        _append_duplicate_name_issues(
            ABI_BINDINGS_PATH,
            bindings_text,
            ZIG_PUB_FN_RE,
            "ABI binding pub fn",
            issues,
        )

    export_shim_text = texts.get(EXPORT_SHIM_PATH)
    if export_shim_text is not None:
        _append_duplicate_name_issues(
            EXPORT_SHIM_PATH,
            export_shim_text,
            ZIG_PUB_FN_RE,
            "export shim pub fn",
            issues,
        )

    uapi_version_text = texts.get(UAPI_VERSION_PATH)
    if uapi_version_text is not None:
        _append_duplicate_name_issues(
            UAPI_VERSION_PATH,
            uapi_version_text,
            ZIG_PUB_FN_RE,
            "uapi version pub fn",
            issues,
        )

    if header_text is not None and bindings_text is not None:
        missing_binding_constants = sorted(
            _abi_header_constant_names(header_text).difference(
                _abi_binding_constant_names(bindings_text)
            )
        )
        for name in missing_binding_constants:
            issues.append(
                "missing ABI binding constant for header define: "
                f"ZIGUX_{name} -> {name}"
            )

    return issues


def _populate_repo(root: Path) -> None:
    for rel_path, markers in REQUIRED_SOURCE_MARKERS.items():
        suffix = "\n} zigux_boundary_header;\n" if rel_path == ABI_HEADER_PATH else "\n"
        _write(root / rel_path, "\n".join(markers) + suffix)

    manifest = {
        "phase": "Phase 3",
        "lane": "abi-runtime",
        "slug": "phase3-abi-packet",
        "status": "shared_abi_and_header_family_binding_surface_present",
        "scope": REQUIRED_MANIFEST_FIELDS["scope"],
        "packet_files": list(REQUIRED_MANIFEST_PACKET_FILES),
        "replay_routes": list(REQUIRED_MANIFEST_REPLAY_ROUTES),
        "repo_reality_gaps": [],
        "next_safe_step": CURRENT_NEXT_SAFE_STEP,
    }
    _write(root / ABI_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")

    for rel_path in REQUIRED_MANIFEST_PACKET_FILES:
        path = root / rel_path
        if path.exists():
            continue
        suffix = "\n" if path.suffix else ""
        _write(path, "// packet file self-test placeholder" + suffix)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validator_") as temp_dir:
        repo_root = Path(temp_dir)
        _populate_repo(repo_root)

        issues = validate_repo(repo_root)
        if issues:
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        cases = (
            (
                TESTS_BUILD_PATH,
                'const phase3_low_level_wrappers = addPhase3LowLevelWrappers(b, target, optimize);\n',
                "missing zigux/tests/build.zig marker: const phase3_low_level_wrappers = addPhase3LowLevelWrappers(b, target, optimize);",
            ),
            (
                TESTS_BUILD_PATH,
                '"phase3-test"\n',
                'missing zigux/tests/build.zig marker: "phase3-test"',
            ),
            (
                ABI_HEADER_PATH,
                'static inline int zigux_list_first_broken_backlink(\n',
                "missing include/zigux/abi.h marker: static inline int zigux_list_first_broken_backlink(",
            ),
            (
                ABI_BINDINGS_PATH,
                'pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {\n',
                "missing zigux/bindings/abi.zig marker: pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {",
            ),
            (
                NOTIFIER_BINDINGS_PATH,
                'pub fn firstBrokenPrevLink(head: ?*const HListHead) ?HListPrevLinkBreak {\n',
                "missing zigux/bindings/notifier_abi.zig marker: pub fn firstBrokenPrevLink(head: ?*const HListHead) ?HListPrevLinkBreak {",
            ),
            (
                RUNNER_PATH,
                'Path("scripts/zigux/check-phase3-abi-manifest-replay-routes.py")\n',
                'missing scripts/zigux/run-phase3-checks.py marker: Path("scripts/zigux/check-phase3-abi-manifest-replay-routes.py")',
            ),
            (
                RUNNER_PATH,
                'Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py")\n',
                'missing scripts/zigux/run-phase3-checks.py marker: Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py")',
            ),
            (
                RUNNER_PATH,
                'Path("scripts/zigux/check-phase3-xarray-slot.py")\n',
                'missing scripts/zigux/run-phase3-checks.py marker: Path("scripts/zigux/check-phase3-xarray-slot.py")',
            ),
            (
                RUNNER_PATH,
                'Path("scripts/zigux/check-phase3-readme-tooling-inventory.py")\n',
                'missing scripts/zigux/run-phase3-checks.py marker: Path("scripts/zigux/check-phase3-readme-tooling-inventory.py")',
            ),
            (
                RUNNER_PATH,
                'Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")\n',
                'missing scripts/zigux/run-phase3-checks.py marker: Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")',
            ),
            (
                RUNNER_PATH,
                'Path("scripts/zigux/check-phase3-wrapper-templates.py")\n',
                'missing scripts/zigux/run-phase3-checks.py marker: Path("scripts/zigux/check-phase3-wrapper-templates.py")',
            ),
            (
                RUNNER_PATH,
                'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")\n',
                'missing scripts/zigux/run-phase3-checks.py marker: Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
            ),
            (
                RUNNER_PATH,
                '"validated zigux/tests/phase3_xarray_slot_dump.zig"\n',
                'missing scripts/zigux/run-phase3-checks.py marker: "validated zigux/tests/phase3_xarray_slot_dump.zig"',
            ),
            (
                RUNNER_PATH,
                '"validated scripts/zigux/generate-phase3-check-wrappers.py"\n',
                'missing scripts/zigux/run-phase3-checks.py marker: "validated scripts/zigux/generate-phase3-check-wrappers.py"',
            ),
            (
                RUNNER_PATH,
                '"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass"\n',
                'missing scripts/zigux/run-phase3-checks.py marker: "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass"',
            ),
            (
                RUNNER_PATH,
                '"PHASE3_WRAPPER_TEMPLATES_CHECK=pass"\n',
                'missing scripts/zigux/run-phase3-checks.py marker: "PHASE3_WRAPPER_TEMPLATES_CHECK=pass"',
            ),
            (
                RUNNER_PATH,
                'Path("scripts/zigux/check-phase3-bitmap-cpumask.py")\n',
                'missing scripts/zigux/run-phase3-checks.py marker: Path("scripts/zigux/check-phase3-bitmap-cpumask.py")',
            ),
            (
                RUNNER_PATH,
                'Path("scripts/zigux/check-phase3-list-hlist-starter-packet.py")\n',
                'missing scripts/zigux/run-phase3-checks.py marker: Path("scripts/zigux/check-phase3-list-hlist-starter-packet.py")',
            ),
            (
                RUNNER_PATH,
                '"PHASE3_BITMAP_CPUMASK_PACKET=pass"\n',
                'missing scripts/zigux/run-phase3-checks.py marker: "PHASE3_BITMAP_CPUMASK_PACKET=pass"',
            ),
            (
                RUNNER_PATH,
                '"validated zigux/tests/fixtures/phase3_list_hlist_manifest.json"\n',
                'missing scripts/zigux/run-phase3-checks.py marker: "validated zigux/tests/fixtures/phase3_list_hlist_manifest.json"',
            ),
            (
                RUNNER_PATH,
                'Path("scripts/zigux/check-phase3-idr-slot-starter-packet.py")\n',
                'missing scripts/zigux/run-phase3-checks.py marker: Path("scripts/zigux/check-phase3-idr-slot-starter-packet.py")',
            ),
            (
                RUNNER_PATH,
                'Path("scripts/zigux/check-phase3-idr-slot.py")\n',
                'missing scripts/zigux/run-phase3-checks.py marker: Path("scripts/zigux/check-phase3-idr-slot.py")',
            ),
            (
                RUNNER_PATH,
                '"validated zigux/tests/phase3_idr_slot_starter_packet.zig"\n',
                'missing scripts/zigux/run-phase3-checks.py marker: "validated zigux/tests/phase3_idr_slot_starter_packet.zig"',
            ),
            (
                RUNNER_PATH,
                '"validated zigux/tests/fixtures/phase3_idr_slot_manifest.json"\n',
                'missing scripts/zigux/run-phase3-checks.py marker: "validated zigux/tests/fixtures/phase3_idr_slot_manifest.json"',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                'Path("scripts/zigux/check-phase3-policy-dump.py")\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: Path("scripts/zigux/check-phase3-policy-dump.py")',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                'Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py")\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py")',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                'Path("scripts/zigux/check-phase3-xarray-slot.py")\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: Path("scripts/zigux/check-phase3-xarray-slot.py")',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                'Path("scripts/zigux/check-phase3-readme-tooling-inventory.py")\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: Path("scripts/zigux/check-phase3-readme-tooling-inventory.py")',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                'Path("scripts/zigux/check-phase3-wrapper-templates.py")\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: Path("scripts/zigux/check-phase3-wrapper-templates.py")',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                'Path("scripts/zigux/generate-phase3-check-wrappers.py")\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: Path("scripts/zigux/generate-phase3-check-wrappers.py")',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                'Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: Path("scripts/zigux/check-phase3-export-uapi-c-header-smoke.py")',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                '"PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=pass"\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: "PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=pass"',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                '"PHASE3_XARRAY_SLOT_SELF_TEST=pass"\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: "PHASE3_XARRAY_SLOT_SELF_TEST=pass"',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                '"PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass"\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: "PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass"',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                '"PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT="\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: "PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT="',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                '"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass"\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass"',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                '"PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT="\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT="',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                '"PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=pass"\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: "PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=pass"',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                '"PHASE3_WRAPPER_SELF_TEST=pass"\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: "PHASE3_WRAPPER_SELF_TEST=pass"',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                'Path("scripts/zigux/check-phase3-bitmap-cpumask.py")\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: Path("scripts/zigux/check-phase3-bitmap-cpumask.py")',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                'Path("scripts/zigux/check-phase3-list-hlist-starter-packet.py")\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: Path("scripts/zigux/check-phase3-list-hlist-starter-packet.py")',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                '"PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=pass"\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: "PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=pass"',
            ),
            (
                VALIDATE_PHASE3_SELFTEST_PATH,
                '"PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST_CASE_COUNT="\n',
                'missing scripts/zigux/validate_phase3_selftest.py marker: "PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST_CASE_COUNT="',
            ),
            (
                ABI_DUMP_PATH,
                'abi.NOTIFIER_DONE,\n',
                "missing zigux/tests/phase3_abi_dump_current.zig marker: abi.NOTIFIER_DONE,",
            ),
            (
                EXPORT_UAPI_LAYOUT_BUILD_PATH,
                '.root_source_file = b.path("../kernel/export_shim.zig"),\n',
                'missing zigux/tests/phase3_export_uapi_layout_build.zig marker: .root_source_file = b.path("../kernel/export_shim.zig"),',
            ),
            (
                EXPORT_SHIM_BUILD_PATH,
                '.name = "phase3-export-shim-test",\n',
                'missing zigux/tests/phase3_export_shim_build.zig marker: .name = "phase3-export-shim-test",',
            ),
            (
                EXPORT_SHIM_PATH,
                "pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {\n",
                "missing zigux/kernel/export_shim.zig marker: pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {",
            ),
            (
                UAPI_VERSION_PATH,
                "pub fn validateBoundaryHeader(header: Header) abi.ExportStatus {\n",
                "missing zigux/uapi/version.zig marker: pub fn validateBoundaryHeader(header: Header) abi.ExportStatus {",
            ),
        )

        for rel_path, needle, expected in cases:
            current = _read(repo_root / rel_path)
            _write(repo_root / rel_path, current.replace(needle, "", 1))
            issues = validate_repo(repo_root)
            if expected not in issues:
                print("PHASE3_VALIDATION_SELF_TEST=fail")
                print(f"expected issue was not reported: {expected}")
                return 1
            _write(repo_root / rel_path, current)

        _populate_repo(repo_root)
        current_bindings = _read(repo_root / ABI_BINDINGS_PATH)
        _write(
            repo_root / ABI_BINDINGS_PATH,
            current_bindings.replace("pub const ABI_VERSION: u16 = 1;\n", "", 1),
        )
        issues = validate_repo(repo_root)
        expected_missing_binding_constant = (
            "missing ABI binding constant for header define: "
            "ZIGUX_ABI_VERSION -> ABI_VERSION"
        )
        if expected_missing_binding_constant not in issues:
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("expected missing ABI binding constant was not reported")
            return 1

        packet_file_checks = (
            ("Documentation/zigux/phase3-abi-h-boundary-next-step.md", "expected abi-h boundary note packet-file drift was not reported"),
            ("scripts/zigux/check-phase3-abi-manifest-replay-routes.py", "expected manifest replay-checker packet-file drift was not reported"),
            ("scripts/zigux/check-phase3-readme-tooling-inventory.py", "expected readme-tooling checker packet-file drift was not reported"),
            ("scripts/zigux/check-phase3-dev-t-starter-packet.py", "expected dev-t starter checker packet-file drift was not reported"),
            ("Documentation/zigux/phase3-errptr-xarray-slice.md", "expected err-ptr xarray slice packet-file drift was not reported"),
            ("zigux/helpers/err_ptr.zig", "expected err-ptr helper packet-file drift was not reported"),
            ("zigux/helpers/xarray_slot_view.zig", "expected xarray-slot helper packet-file drift was not reported"),
            ("scripts/zigux/check-phase3-xarray-slot.py", "expected xarray-slot checker packet-file drift was not reported"),
            ("zigux/tests/phase3_xarray_slot_dump_build.zig", "expected xarray-slot dump build packet-file drift was not reported"),
            ("scripts/zigux/check-phase3-wrapper-templates.py", "expected wrapper-template checker packet-file drift was not reported"),
            ("scripts/zigux/generate-phase3-check-wrappers.py", "expected wrapper generator packet-file drift was not reported"),
            ("zigux/tests/phase3_dev_t_starter_packet.zig", "expected dev-t starter packet zig drift was not reported"),
            ("zigux/tests/phase3_dev_t_starter_packet_build.zig", "expected dev-t starter packet build drift was not reported"),
            ("zigux/tests/phase3_dev_t_starter_packet_manifest.json", "expected dev-t starter packet manifest drift was not reported"),
            ("scripts/zigux/check-phase3-policy-dump.py", "expected policy-dump packet-file drift was not reported"),
            ("zigux/tests/phase3_policy_dump.zig", "expected policy-dump zig packet-file drift was not reported"),
            ("scripts/zigux/validate-phase3-policy-unsafe-survey.py", "expected policy-unsafe validator packet-file drift was not reported"),
            ("zigux/tests/phase3_export_shim_build.zig", "expected export-shim build packet-file drift was not reported"),
            ("scripts/zigux/README.md", "expected scripts README packet-file drift was not reported"),
            ("zigux/tests/phase3_errptr_xarray_dump.zig", "expected err-ptr xarray dump zig packet-file drift was not reported"),
            ("zigux/tests/phase3_errptr_xarray_dump_build.zig", "expected err-ptr xarray dump build drift was not reported"),
            ("Documentation/zigux/phase3-bitmap-cpumask-slice.md", "expected bitmap cpumask slice packet-file drift was not reported"),
            ("zigux/helpers/bitmap_view.zig", "expected bitmap helper packet-file drift was not reported"),
            ("zigux/helpers/cpumask_view.zig", "expected cpumask helper packet-file drift was not reported"),
            ("zigux/tests/phase3_bitmap_cpumask_starter_packet.zig", "expected bitmap cpumask starter packet zig drift was not reported"),
            ("zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig", "expected bitmap cpumask starter packet build drift was not reported"),
            ("zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json", "expected bitmap cpumask manifest drift was not reported"),
            ("scripts/zigux/check-phase3-bitmap-cpumask.py", "expected bitmap cpumask checker drift was not reported"),
            ("Documentation/zigux/phase3-list-hlist-slice.md", "expected list hlist slice packet-file drift was not reported"),
            ("zigux/helpers/list_view.zig", "expected list helper packet-file drift was not reported"),
            ("zigux/helpers/hlist_view.zig", "expected hlist helper packet-file drift was not reported"),
            ("zigux/tests/phase3_list_hlist_starter_packet.zig", "expected list hlist starter packet zig drift was not reported"),
            ("zigux/tests/phase3_list_hlist_starter_packet_build.zig", "expected list hlist starter packet build drift was not reported"),
            ("zigux/tests/fixtures/phase3_list_hlist_manifest.json", "expected list hlist manifest drift was not reported"),
            ("scripts/zigux/check-phase3-list-hlist-starter-packet.py", "expected list hlist starter checker drift was not reported"),
            ("Documentation/zigux/phase3-idr-slot-slice.md", "expected idr-slot slice packet-file drift was not reported"),
            ("zigux/helpers/idr_slot_view.zig", "expected idr-slot helper packet-file drift was not reported"),
            ("zigux/tests/phase3_idr_slot_starter_packet.zig", "expected idr-slot starter packet zig drift was not reported"),
            ("zigux/tests/phase3_idr_slot_starter_packet_build.zig", "expected idr-slot starter packet build drift was not reported"),
            ("zigux/tests/phase3_idr_slot_dump.zig", "expected idr-slot dump zig drift was not reported"),
            ("zigux/tests/phase3_idr_slot_dump_build.zig", "expected idr-slot dump build drift was not reported"),
            ("zigux/tests/fixtures/phase3_idr_slot/phase3_idr_slot_c_harness.c", "expected idr-slot c-harness drift was not reported"),
            ("zigux/tests/fixtures/phase3_idr_slot/expected.json", "expected idr-slot expected-json drift was not reported"),
            ("zigux/tests/fixtures/phase3_idr_slot_manifest.json", "expected idr-slot manifest drift was not reported"),
            ("scripts/zigux/check-phase3-idr-slot-starter-packet.py", "expected idr-slot starter checker drift was not reported"),
            ("scripts/zigux/check-phase3-idr-slot.py", "expected idr-slot dump checker drift was not reported"),
        )
        for entry, failure_message in packet_file_checks:
            _populate_repo(repo_root)
            manifest = json.loads(_read(repo_root / ABI_MANIFEST_PATH))
            manifest["packet_files"].remove(entry)
            _write(repo_root / ABI_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
            issues = validate_repo(repo_root)
            expected = f"phase3_abi_manifest.json missing packet_files entry: {entry}"
            if expected not in issues:
                print("PHASE3_VALIDATION_SELF_TEST=fail")
                print(failure_message)
                return 1

        replay_route_checks = (
            ("python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test", "expected dev-t starter self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-dev-t-starter-packet.py", "expected dev-t starter direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test", "expected manifest replay-checker self-test drift was not reported"),
            ("python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py", "expected manifest replay-checker direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test", "expected readme-tooling self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-readme-tooling-inventory.py", "expected readme-tooling direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test", "expected err-ptr xarray starter self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py", "expected err-ptr xarray starter direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test", "expected xarray-slot starter self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py", "expected xarray-slot starter direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-xarray-slot.py --self-test", "expected xarray-slot self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-xarray-slot.py", "expected xarray-slot direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-wrapper-templates.py --self-test", "expected wrapper-template self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-wrapper-templates.py", "expected wrapper-template direct route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3.py --self-test", "expected shared ABI validator self-test route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3.py", "expected shared ABI validator direct route drift was not reported"),
            ("python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test", "expected policy-unsafe self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-policy-dump.py", "expected policy-dump direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py --self-test", "expected export-uapi c-header smoke self-test route drift was not reported"),
            ("python3 scripts/zigux/generate-phase3-check-wrappers.py --self-test", "expected wrapper generator self-test route drift was not reported"),
            ("zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all", "expected dev-t starter build route drift was not reported"),
            ("zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig", "expected err-ptr xarray dump build route drift was not reported"),
            ("zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig", "expected xarray-slot starter build route drift was not reported"),
            ("zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig", "expected xarray-slot dump build route drift was not reported"),
            ("zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig", "expected policy-starter build route drift was not reported"),
            ("make -C zigux phase3-policy-starter-packet-test", "expected policy-starter make route drift was not reported"),
            ("zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig", "expected policy-dump build route drift was not reported"),
            ("make -C zigux phase3-policy-dump", "expected policy-dump make route drift was not reported"),
            ("zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig", "expected export-shim build replay-route drift was not reported"),
            ("make -C zigux phase3-export-shim-test", "expected export-shim make route drift was not reported"),
            ("python3 scripts/zigux/validate_phase3_selftest.py", "expected selftest driver replay drift was not reported"),
            ("python3 scripts/zigux/run-phase3-checks.py", "expected runner replay drift was not reported"),
            ("make -C zigux phase3-validate", "expected shared phase3 validate make route drift was not reported"),
            ("make -C zigux phase3-dump", "expected shared ABI dump make route drift was not reported"),
            ("make -C zigux phase3-export-uapi-layout", "expected export-uapi shared make route drift was not reported"),
            ("make -C zigux phase3-export-uapi-layout-test", "expected export-uapi dedicated make route drift was not reported"),
            ("zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig", "expected low-level-wrapper shared build route drift was not reported"),
            ("make -C zigux phase3-low-level-wrappers", "expected low-level-wrapper shared make route drift was not reported"),
            ("zig build phase3-test --build-file zigux/tests/build.zig", "expected shared ABI aggregate build route drift was not reported"),
            ("make -C zigux phase3-test", "expected shared ABI aggregate make route drift was not reported"),
            ("make -C zigux phase3", "expected shared ABI top-level make route drift was not reported"),
            ("zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig", "expected low-level-wrapper focused build route drift was not reported"),
            ("make -C zigux phase3-low-level-wrappers-test", "expected low-level-wrapper focused make route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test", "expected bitmap cpumask self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-bitmap-cpumask.py", "expected bitmap cpumask direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test", "expected list hlist self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py", "expected list hlist direct route drift was not reported"),
            ("zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig", "expected bitmap cpumask build route drift was not reported"),
            ("zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig", "expected list hlist build route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --self-test", "expected idr-slot starter self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --repo-root .", "expected idr-slot starter direct route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-idr-slot.py --self-test", "expected idr-slot dump self-test route drift was not reported"),
            ("python3 scripts/zigux/check-phase3-idr-slot.py --repo-root . --zig zig --cc gcc", "expected idr-slot dump direct route drift was not reported"),
            ("zig build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig", "expected idr-slot starter build route drift was not reported"),
            ("zig build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig", "expected idr-slot dump build route drift was not reported"),
        )
        for route, failure_message in replay_route_checks:
            _populate_repo(repo_root)
            manifest = json.loads(_read(repo_root / ABI_MANIFEST_PATH))
            manifest["replay_routes"].remove(route)
            _write(repo_root / ABI_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
            issues = validate_repo(repo_root)
            expected = f"phase3_abi_manifest.json missing replay route: {route}"
            if expected not in issues:
                print("PHASE3_VALIDATION_SELF_TEST=fail")
                print(failure_message)
                return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(repo_root / ABI_MANIFEST_PATH))
        manifest["replay_routes"].append(REQUIRED_MANIFEST_REPLAY_ROUTES[0])
        _write(repo_root / ABI_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = "phase3_abi_manifest.json replay_routes duplicate entry:"
        if not any(issue.startswith(expected) for issue in issues):
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("expected duplicate replay-route issue was not reported")
            return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(repo_root / ABI_MANIFEST_PATH))
        manifest["repo_reality_gaps"] = ["stale gap text"]
        _write(repo_root / ABI_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = (
            "phase3_abi_manifest.json repo_reality_gaps drifted from the current shared packet expectation"
        )
        if expected not in issues:
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("expected repo-reality-gap drift was not reported")
            return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(repo_root / ABI_MANIFEST_PATH))
        manifest["next_safe_step"] = "old next step"
        _write(repo_root / ABI_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = "phase3_abi_manifest.json wrong next_safe_step:"
        if not any(issue.startswith(expected) for issue in issues):
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("expected next-safe-step drift was not reported")
            return 1

        _populate_repo(repo_root)
        current_header = _read(repo_root / ABI_HEADER_PATH)
        _write(
            repo_root / ABI_HEADER_PATH,
            current_header
            + "\ntypedef struct zigux_duplicate_layout_alias {\n"
            + "    int value;\n"
            + "} zigux_boundary_header;\n",
        )
        issues = validate_repo(repo_root)
        if not any(
            issue.startswith("duplicate ABI header typedef alias: zigux_boundary_header ")
            for issue in issues
        ):
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("expected duplicate typedef alias issue was not reported")
            return 1

        _populate_repo(repo_root)
        current_bindings = _read(repo_root / ABI_BINDINGS_PATH)
        _write(
            repo_root / ABI_BINDINGS_PATH,
            current_bindings
            + "\npub fn defaultHeader(flags: u16) BoundaryHeader {\n"
            + "    _ = flags;\n"
            + "    return undefined;\n"
            + "}\n",
        )
        issues = validate_repo(repo_root)
        if not any(
            issue.startswith("duplicate ABI binding pub fn: defaultHeader ")
            for issue in issues
        ):
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("expected duplicate pub fn issue was not reported")
            return 1

        _populate_repo(repo_root)
        current_export_shim = _read(repo_root / EXPORT_SHIM_PATH)
        _write(
            repo_root / EXPORT_SHIM_PATH,
            current_export_shim
            + "\npub fn validateVersion(candidate: Version) ExportStatus {\n"
            + "    _ = candidate;\n"
            + "    return undefined;\n"
            + "}\n",
        )
        issues = validate_repo(repo_root)
        if not any(
            issue.startswith("duplicate export shim pub fn: validateVersion ")
            for issue in issues
        ):
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("expected export shim duplicate pub fn issue was not reported")
            return 1

        _populate_repo(repo_root)
        current_uapi_version = _read(repo_root / UAPI_VERSION_PATH)
        _write(
            repo_root / UAPI_VERSION_PATH,
            current_uapi_version
            + "\npub fn validateBoundaryHeader(header: Header) abi.ExportStatus {\n"
            + "    _ = header;\n"
            + "    return undefined;\n"
            + "}\n",
        )
        issues = validate_repo(repo_root)
        if not any(
            issue.startswith("duplicate uapi version pub fn: validateBoundaryHeader ")
            for issue in issues
        ):
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("expected uapi version duplicate pub fn issue was not reported")
            return 1

        _populate_repo(repo_root)
        (repo_root / "zigux/kernel/export_shim.zig").unlink()
        issues = validate_repo(repo_root)
        expected = (
            "phase3_abi_manifest.json packet_files entry missing on disk: "
            "zigux/kernel/export_shim.zig"
        )
        if expected not in issues:
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("expected missing on-disk packet-file issue was not reported")
            return 1

    print("PHASE3_VALIDATION_SELF_TEST=pass")
    print(f"PHASE3_VALIDATION_SELF_TEST_CASE_COUNT={len(cases) + len(packet_file_checks) + len(replay_route_checks) + 9}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bounded Phase 3 shared ABI packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help=(
            "repository root that contains include/zigux/, zigux/bindings/, "
            "scripts/zigux/, and zigux/tests/"
        ),
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_VALIDATION=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_VALIDATION=pass")
    print(
        "PHASE3_SCOPE=shared-abi-binding-layout-catalog-dump-export-uapi-and-low-level-wrapper-route-surface"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())