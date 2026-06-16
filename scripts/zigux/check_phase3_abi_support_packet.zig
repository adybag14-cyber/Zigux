const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_ABI_SUPPORT_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=pass";

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-kernel-export-shim-governance.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "Documentation/zigux/phase3-shared-reminder-gap.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "include/linux/zigux.h",
    "zigux/uapi/version.zig",
    "zigux/kernel/export_shim.zig",
    "scripts/zigux/phase3_catalog.zig",
    "scripts\\zigux/check_phase3_catalog_selftest.zig",
    "scripts\\zigux/check_phase3_policy_starter_packet.zig",
    "scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig",
    "scripts\\zigux/check_phase3_abi_support_packet.zig",
    "scripts\\zigux/check_phase3_abi_manifest_replay_routes.zig",
    "scripts\\zigux/check_phase3_shared_tests_routes.zig",
    "scripts\\zigux/check_phase3_selftest_surface.zig",
    "scripts\\zigux/validate_phase3_validator_support_surface.zig",
    "scripts\\zigux/validate_phase3_export_uapi_survey.zig",
    "scripts\\zigux/validate_phase3_abi_header_family_survey.zig",
    "scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "scripts\\zigux/validate_phase3_linux_zigux_header_governance.zig",
    "scripts/zigux/run_phase3_checks.zig",
    "scripts/zigux/validate_phase3_selftest.zig",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "zigux/tests/phase3_export_uapi_c_header_smoke.c",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_export_shim_build.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zig run scripts\\zigux/check_phase3_abi_support_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_abi_support_packet.zig",
    "zig run scripts\\zigux/check_phase3_abi_manifest_replay_routes.zig --self-test",
    "zig run scripts\\zigux/check_phase3_abi_manifest_replay_routes.zig",
    "zig run scripts\\zigux/check_phase3_shared_tests_routes.zig --self-test",
    "zig run scripts\\zigux/check_phase3_shared_tests_routes.zig",
    "zig run scripts\\zigux/check_phase3_selftest_surface.zig --self-test",
    "zig run scripts\\zigux/check_phase3_selftest_surface.zig",
    "zig run scripts\\zigux/validate_phase3_validator_support_surface.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_validator_support_surface.zig",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-low-level-wrappers-test",
    ".github/workflows/zigux-bootstrap.yml",
};

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_abi_support_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_abi_support_packet.zig",
    "zig run scripts\\zigux/check_phase3_policy_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_policy_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_xarray_slot.zig --self-test",
    "zig run scripts\\zigux/check_phase3_xarray_slot.zig",
    "zig run scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig",
    "zig run scripts\\zigux/check_phase3_shared_tests_routes.zig --self-test",
    "zig run scripts\\zigux/check_phase3_shared_tests_routes.zig",
    "zig run scripts\\zigux/check_phase3_abi_manifest_replay_routes.zig --self-test",
    "zig run scripts\\zigux/check_phase3_abi_manifest_replay_routes.zig",
    "zig run scripts\\zigux/check_phase3_selftest_surface.zig --self-test",
    "zig run scripts\\zigux/check_phase3_selftest_surface.zig",
    "zig run scripts\\zigux/validate_phase3_validator_support_surface.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_validator_support_surface.zig",
    "zig run scripts\\zigux/validate_phase3_export_uapi_survey.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_export_uapi_survey.zig",
    "zig run scripts\\zigux/validate_phase3_abi_header_family_survey.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_abi_header_family_survey.zig",
    "zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "zig run scripts\\zigux/validate_phase3_linux_zigux_header_governance.zig --self-test",
    "zig run scripts\\zigux/validate_phase3_linux_zigux_header_governance.zig",
    "zig run scripts/zigux/validate_phase3_selftest.zig",
    "zig run scripts/zigux/run_phase3_checks.zig",
    "zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "make -C zigux phase3-export-uapi-layout",
    "make -C zigux phase3-export-uapi-layout-test",
    "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-low-level-wrappers-test",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-slice.md");
    defer allocator.free(text_required_note_markers_path);
    const text_required_note_markers = try guard.readUtf8File(io, allocator, text_required_note_markers_path);
    defer allocator.free(text_required_note_markers);
    for (REQUIRED_NOTE_MARKERS) |marker| try guard.requireMarker(text_required_note_markers, marker);
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-slice.md");
    defer allocator.free(text_required_replay_routes_path);
    const text_required_replay_routes = try guard.readUtf8File(io, allocator, text_required_replay_routes_path);
    defer allocator.free(text_required_replay_routes);
    for (REQUIRED_REPLAY_ROUTES) |marker| try guard.requireMarker(text_required_replay_routes, marker);
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
