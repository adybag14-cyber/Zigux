const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE3_VALIDATION_SELF_TEST=pass";

const CURRENT_NEXT_SAFE_STEP = [_][]const u8{
    "keep the shared Phase 3 policy, export/UAPI, low-level wrapper packet, and retired generated-packet guard aligned with the dedicated replay routes and only reopen this manifest if the checker, focused builds, or reminder surfaces drift again",
};

const REQUIRED_MANIFEST_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_abi.zig --self-test",
    "zig run scripts\\zigux/check_phase3_abi.zig",
    "zig run scripts\\zigux/check_phase3_abi_manifest_replay_routes.zig --self-test",
    "zig run scripts\\zigux/check_phase3_abi_manifest_replay_routes.zig",
    "zig run scripts\\zigux/check_phase3_abi_support_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_abi_support_packet.zig",
    "zig run scripts\\zigux/check_phase3_dev_t_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_dev_t_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_xarray_slot.zig --self-test",
    "zig run scripts\\zigux/check_phase3_xarray_slot.zig",
    "zig run scripts\\zigux/check_phase3_policy_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_policy_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_policy_dump.zig --self-test",
    "zig run scripts\\zigux/check_phase3_policy_dump.zig",
    "zig run scripts\\zigux/check_phase3_shared_tests_routes.zig --self-test",
    "zig run scripts\\zigux/check_phase3_shared_tests_routes.zig",
    "zig run scripts\\zigux/check_phase3_readme_tooling_inventory.zig --self-test",
    "zig run scripts\\zigux/check_phase3_readme_tooling_inventory.zig",
    "zig run scripts\\zigux/check_phase3_wrapper_templates.zig --self-test",
    "zig run scripts\\zigux/check_phase3_wrapper_templates.zig",
    "zig run scripts\\zigux/check_phase3_catalog_selftest.zig --self-test",
    "zig run scripts\\zigux/check_phase3_catalog_selftest.zig",
    "zig run scripts\\zigux/validate_phase3.zig --self-test",
    "zig run scripts\\zigux/validate_phase3.zig",
    "zig run scripts\\zigux/validate_phase3_validator_support_surface.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_validator_support_surface.zig",
    "zig run scripts\\zigux/validate_phase3_export_uapi_survey.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_export_uapi_survey.zig",
    "zig run scripts\\zigux/validate_phase3_abi_header_family_survey.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_abi_header_family_survey.zig",
    "zig run scripts\\zigux/validate_phase3_policy_unsafe_survey.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_policy_unsafe_survey.zig",
    "zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "zig run scripts\\zigux/check_phase3_low_level_wrappers.zig --self-test",
    "zig run scripts\\zigux/check_phase3_low_level_wrappers.zig",
    "zig run scripts\\zigux/validate_phase3_linux_zigux_header_governance.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_linux_zigux_header_governance.zig",
    "zig run scripts\\zigux/check_phase3_selftest_surface.zig --self-test",
    "zig run scripts\\zigux/check_phase3_selftest_surface.zig",
    "zig run scripts/zigux/check_phase3_wrapper_templates.zig --self-test",
    "zig run scripts/zigux/validate_phase3_selftest.zig",
    "zig run scripts/zigux/run_phase3_checks.zig",
    "make -C zigux phase3-validate",
    "zig run scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig --self-test",
    "zig run scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig",
    "zig run scripts\\zigux/check_phase3_bitmap_cpumask.zig --self-test",
    "zig run scripts\\zigux/check_phase3_bitmap_cpumask.zig",
    "zig run scripts\\zigux/check_phase3_list_hlist_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_list_hlist_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_list_hlist.zig --self-test",
    "zig run scripts\\zigux/check_phase3_list_hlist.zig --repo-root . --zig zig --cc gcc",
    "zig run scripts\\zigux/check_phase3_idr_slot_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_idr_slot_starter_packet.zig --repo-root .",
    "zig run scripts\\zigux/check_phase3_idr_slot.zig --self-test",
    "zig run scripts\\zigux/check_phase3_idr_slot.zig --repo-root . --zig zig --cc gcc",
    "zig build phase3-idr-slot --build-file zigux/tests/build.zig",
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
    "zig build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig",
    "zig build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_current_next_safe_step_path = try guard.joinPath(allocator, root, "include/zigux/abi.h");
    defer allocator.free(text_current_next_safe_step_path);
    const text_current_next_safe_step = try guard.readUtf8File(io, allocator, text_current_next_safe_step_path);
    defer allocator.free(text_current_next_safe_step);
    for (CURRENT_NEXT_SAFE_STEP) |marker| try guard.requireMarker(text_current_next_safe_step, marker);
    const text_required_manifest_replay_routes_path = try guard.joinPath(allocator, root, "include/zigux/abi.h");
    defer allocator.free(text_required_manifest_replay_routes_path);
    const text_required_manifest_replay_routes = try guard.readUtf8File(io, allocator, text_required_manifest_replay_routes_path);
    defer allocator.free(text_required_manifest_replay_routes);
    for (REQUIRED_MANIFEST_REPLAY_ROUTES) |marker| try guard.requireMarker(text_required_manifest_replay_routes, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
