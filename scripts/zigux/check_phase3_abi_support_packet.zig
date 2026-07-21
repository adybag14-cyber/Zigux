const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_ABI_SUPPORT_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=pass",
    "PHASE3_ABI_SUPPORT_PACKET_SELF_TEST_CASE_COUNT=",
};

const live_output_markers = [_][]const u8{
    "PHASE3_ABI_SUPPORT_PACKET=pass",
};

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
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
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-low-level-wrappers-test",
    ".github/workflows/zigux-bootstrap.yml",
    "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
};

const markers_1 = [_][]const u8{
    "\"phase\": \"Phase 3\"",
    "\"replay_routes\"",
    "zig run scripts/zigux/check_phase3_abi_support_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_abi_support_packet.zig",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase3-abi-slice.md", .markers = &markers_0 },
    .{ .rel = "zigux/tests/fixtures/phase3_abi_manifest.json", .markers = &markers_1 },
};

fn printOutputMarkers(io: Io, markers: []const []const u8) !void {
    for (markers) |marker| {
        if (std.mem.endsWith(u8, marker, "="))
            try guard.printLine(io, "{s}{d}", .{ marker, contracts.len })
        else
            try guard.printLine(io, "{s}", .{marker});
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const owner_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(owner_path);
        const text = try guard.readUtf8File(io, allocator, owner_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try printOutputMarkers(io, &self_test_output_markers);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try printOutputMarkers(io, &live_output_markers);
}
