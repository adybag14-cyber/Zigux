const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE3_CATALOG_SELF_TEST=pass";

const PHASE3_CATALOG_MANIFEST_SCOPE = [_][]const u8{
    "shared ABI bindings, directly coupled helper decoding, header-family follow-through, notifier layouts, export-status layout, and header-compatibility replay",
};

const PHASE3_CATALOG_NEXT_SAFE_STEP = [_][]const u8{
    "keep the shared Phase 3 policy, export/UAPI, low-level wrapper packet, and retired generated-packet guard aligned with the dedicated replay routes and only reopen this manifest if the checker, focused builds, or reminder surfaces drift again",
};

const EXPECTED_PACKET_FILES = [_][]const u8{
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
    "scripts\zigux/validate_phase3.zig",
    "scripts\zigux/check_phase3_abi.zig",
    "scripts\zigux/check_phase3_abi_manifest_replay_routes.zig",
    "scripts\zigux/check_phase3_abi_support_packet.zig",
    "scripts\zigux/check_phase3_catalog_selftest.zig",
    "scripts\zigux/check_phase3_readme_tooling_inventory.zig",
    "scripts\zigux/check_phase3_dev_t_starter_packet.zig",
    "scripts\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "scripts\zigux/check_phase3_xarray_slot_starter_packet.zig",
    "scripts\zigux/check_phase3_xarray_slot.zig",
    "scripts\zigux/check_phase3_export_uapi_c_header_smoke.zig",
    "scripts\zigux/check_phase3_policy_dump.zig",
    "scripts\zigux/check_phase3_policy_starter_packet.zig",
    "scripts\zigux/check_phase3_selftest_surface.zig",
    "scripts\zigux/check_phase3_shared_tests_routes.zig",
    "scripts\zigux/check_phase3_wrapper_templates.zig",
    "scripts/zigux/check_phase3_wrapper_templates.zig",
    "scripts/zigux/phase3_catalog.zig",
    "scripts\zigux/validate_phase3_policy_unsafe_survey.zig",
    "scripts\zigux/validate_phase3_validator_support_surface.zig",
    "scripts\zigux/validate_phase3_export_uapi_survey.zig",
    "scripts\zigux/validate_phase3_abi_header_family_survey.zig",
    "scripts\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "scripts\zigux/check_phase3_low_level_wrappers.zig",
    "scripts\zigux/validate_phase3_linux_zigux_header_governance.zig",
    "scripts/zigux/run_phase3_checks.zig",
    "scripts/zigux/validate_phase3_selftest.zig",
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
    "Documentation/zigux/phase3-idr-slot-slice.md",
    "zigux/helpers/idr_slot_view.zig",
    "zigux/tests/phase3_idr_slot_starter_packet.zig",
    "zigux/tests/phase3_idr_slot_starter_packet_build.zig",
    "zigux/tests/phase3_idr_slot_dump.zig",
    "zigux/tests/phase3_idr_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_idr_slot/phase3_idr_slot_c_harness.c",
    "zigux/tests/fixtures/phase3_idr_slot/expected.json",
    "zigux/tests/fixtures/phase3_idr_slot_manifest.json",
    "scripts\zigux/check_phase3_idr_slot_starter_packet.zig",
    "scripts\zigux/check_phase3_idr_slot.zig",
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
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
    "zigux/helpers/bitmap_view.zig",
    "zigux/helpers/cpumask_view.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c",
    "zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json",
    "zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json",
    "scripts\zigux/check_phase3_bitmap_cpumask.zig",
    "Documentation/zigux/phase3-list-hlist-slice.md",
    "zigux/helpers/list_view.zig",
    "zigux/helpers/hlist_view.zig",
    "zigux/tests/phase3_list_hlist_starter_packet.zig",
    "zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "zigux/tests/phase3_list_hlist_dump.zig",
    "zigux/tests/phase3_list_hlist_dump_build.zig",
    "zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c",
    "zigux/tests/fixtures/phase3_list_hlist/expected.json",
    "zigux/tests/fixtures/phase3_list_hlist_manifest.json",
    "scripts\zigux/check_phase3_list_hlist_starter_packet.zig",
    "scripts\zigux/check_phase3_list_hlist.zig",
};

const EXPECTED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts/zigux/check_phase3_abi.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_abi.zig",
    "zig run scripts/zigux/check_phase3_abi_manifest_replay_routes.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_abi_manifest_replay_routes.zig",
    "zig run scripts/zigux/check_phase3_abi_support_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_abi_support_packet.zig",
    "zig run scripts/zigux/check_phase3_policy_starter_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_policy_starter_packet.zig",
    "zig run scripts/zigux/check_phase3_policy_dump.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_policy_dump.zig",
    "zig run scripts/zigux/check_phase3_shared_tests_routes.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_shared_tests_routes.zig",
    "zig run scripts/zigux/check_phase3_readme_tooling_inventory.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_readme_tooling_inventory.zig",
    "zig run scripts/zigux/check_phase3_wrapper_templates.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_wrapper_templates.zig",
    "zig run scripts/zigux/check_phase3_catalog_selftest.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_catalog_selftest.zig",
    "zig run scripts/zigux/validate_phase3.zig -- --self-test",
    "zig run scripts/zigux/validate_phase3.zig",
    "zig run scripts/zigux/validate_phase3_validator_support_surface.zig -- --self-test",
    "zig run scripts/zigux/validate_phase3_validator_support_surface.zig",
    "zig run scripts/zigux/validate_phase3_export_uapi_survey.zig -- --self-test",
    "zig run scripts/zigux/validate_phase3_export_uapi_survey.zig",
    "zig run scripts/zigux/validate_phase3_abi_header_family_survey.zig -- --self-test",
    "zig run scripts/zigux/validate_phase3_abi_header_family_survey.zig",
    "zig run scripts/zigux/validate_phase3_policy_unsafe_survey.zig -- --self-test",
    "zig run scripts/zigux/validate_phase3_policy_unsafe_survey.zig",
    "zig run scripts/zigux/validate_phase3_low_level_wrapper_survey.zig -- --self-test",
    "zig run scripts/zigux/validate_phase3_low_level_wrapper_survey.zig",
    "zig run scripts/zigux/check_phase3_low_level_wrappers.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_low_level_wrappers.zig",
    "zig run scripts/zigux/validate_phase3_linux_zigux_header_governance.zig -- --self-test",
    "zig run scripts/zigux/validate_phase3_linux_zigux_header_governance.zig",
    "zig run scripts/zigux/check_phase3_selftest_surface.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_selftest_surface.zig",
    "zig run scripts/zigux/check_phase3_wrapper_templates.zig -- --self-test",
    "zig run scripts/zigux/validate_phase3_selftest.zig",
    "zig run scripts/zigux/run_phase3_checks.zig",
    "make -C zigux phase3-validate",
    "zig run scripts/zigux/check_phase3_dev_t_starter_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_dev_t_starter_packet.zig",
    "zig run scripts/zigux/check_phase3_errptr_xarray_starter_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "zig run scripts/zigux/check_phase3_xarray_slot_starter_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_xarray_slot_starter_packet.zig",
    "zig run scripts/zigux/check_phase3_xarray_slot.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_xarray_slot.zig",
    "zig run scripts/zigux/check_phase3_export_uapi_c_header_smoke.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_export_uapi_c_header_smoke.zig",
    "zig run scripts/zigux/check_phase3_bitmap_cpumask.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_bitmap_cpumask.zig",
    "zig run scripts/zigux/check_phase3_list_hlist_starter_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_list_hlist_starter_packet.zig",
    "zig run scripts/zigux/check_phase3_list_hlist.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_list_hlist.zig -- --repo-root . --zig zig --cc gcc",
    "zig run scripts/zigux/check_phase3_idr_slot_starter_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_idr_slot_starter_packet.zig -- --repo-root .",
    "zig run scripts/zigux/check_phase3_idr_slot.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_idr_slot.zig -- --repo-root . --zig zig --cc gcc",
    "zig build phase3-dev-t-starter-packet-test --build-file zigux/tests/phase3_dev_t_starter_packet_build.zig --summary all",
    "zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig",
    "zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zig build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig",
    "zig build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig",
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
    "zig build phase3-abi-export --build-file zigux/tests/build.zig",
    "make -C zigux phase3-abi-export",
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
    "zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig",
    "zig build phase3-idr-slot --build-file zigux/tests/build.zig",
};

const FORBIDDEN_PACKET_FILES = [_][]const u8{
    "zigux/tests/phase3_abi_dump.zig",
};

const FORBIDDEN_REPLAY_ROUTE_MARKERS = [_][]const u8{
    "phase3_abi_dump.zig",
    "phase3_abi_dump_build.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (PHASE3_CATALOG_MANIFEST_SCOPE) |marker| try guard.requireMarker(text, marker);
    for (PHASE3_CATALOG_NEXT_SAFE_STEP) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_PACKET_FILES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_REPLAY_ROUTES) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_PACKET_FILES) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_REPLAY_ROUTE_MARKERS) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
