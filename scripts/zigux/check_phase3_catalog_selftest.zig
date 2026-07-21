const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_CATALOG_SELFTEST_CHECK=pass";
pub const self_test_pass_marker = "PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=pass",
    "PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST_CASE_COUNT=",
};

const live_output_markers = [_][]const u8{
    "validated scripts/zigux/phase3_catalog.zig",
    "PHASE3_CATALOG_SELFTEST_CHECK=pass",
};

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "Phase 3",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "\"Documentation/zigux/phase3-abi-slice.md\"",
    "\"Documentation/zigux/phase3-export-uapi-boundary-survey.md\"",
    "\"Documentation/zigux/phase3-errptr-xarray-slice.md\"",
    "\"Documentation/zigux/phase3-xarray-slot-slice.md\"",
    "\"Documentation/zigux/phase3-idr-slot-slice.md\"",
    "\"Documentation/zigux/phase3-bitmap-cpumask-slice.md\"",
    "\"Documentation/zigux/phase3-list-hlist-slice.md\"",
    "\"scripts\\zigux/check_phase3_catalog_selftest.zig\"",
    "\"scripts/zigux/check_phase3_wrapper_templates.zig\"",
    "\"scripts\\zigux/check_phase3_wrapper_templates.zig\"",
    "\"scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig\"",
    "\"scripts\\zigux/check_phase3_xarray_slot.zig\"",
    "\"scripts\\zigux/check_phase3_idr_slot_starter_packet.zig\"",
    "\"scripts\\zigux/check_phase3_idr_slot.zig\"",
    "\"scripts\\zigux/check_phase3_bitmap_cpumask.zig\"",
    "\"scripts\\zigux/check_phase3_list_hlist_starter_packet.zig\"",
    "\"scripts\\zigux/check_phase3_list_hlist.zig\"",
    "\"scripts\\zigux/check_phase3_low_level_wrappers.zig\"",
    "\"zigux/helpers/idr_slot_view.zig\"",
    "\"zigux/tests/phase3_idr_slot_starter_packet.zig\"",
    "\"zigux/tests/phase3_idr_slot_starter_packet_build.zig\"",
    "\"zigux/tests/fixtures/phase3_idr_slot_manifest.json\"",
    "\"zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c\"",
    "\"zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json\"",
    "\"zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c\"",
    "\"zigux/tests/fixtures/phase3_list_hlist/expected.json\"",
    "\"zigux/tests/phase3_list_hlist_dump.zig\"",
    "\"zigux/tests/phase3_list_hlist_dump_build.zig\"",
    "\"zigux/tests/phase3_abi_dump_current.zig\"",
    "\"zigux/Makefile\"",
    "\".github/workflows/zigux-bootstrap.yml\"",
    "\"zig run scripts/zigux/check_phase3_wrapper_templates.zig -- --self-test\"",
    "\"zig build phase3-abi-export --build-file zigux/tests/build.zig\"",
    "\"make -C zigux phase3-abi-export\"",
    "\"zig build phase3-idr-slot --build-file zigux/tests/build.zig\"",
    "\"zig build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig\"",
    "\"zig build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig\"",
    "\"zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig\"",
    "PHASE3_CATALOG_SELF_TEST=pass",
};

const markers_1 = [_][]const u8{
    "\"Documentation/zigux/phase3-list-hlist-slice.md\"",
    "\"scripts/zigux/check_phase3_catalog_selftest.zig\"",
    "\"scripts/zigux/check_phase3_list_hlist.zig\"",
    "\"scripts/zigux/check_phase3_low_level_wrappers.zig\"",
    "\"zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c\"",
    "\"zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c\"",
    "\"zigux/tests/phase3_list_hlist_dump.zig\"",
    "\"zigux/tests/phase3_list_hlist_dump_build.zig\"",
    "\"zigux/tests/phase3_abi_dump_current.zig\"",
    "\"zigux/Makefile\"",
    "\".github/workflows/zigux-bootstrap.yml\"",
    "\"zig build phase3-abi-export --build-file zigux/tests/build.zig\"",
    "\"make -C zigux phase3-abi-export\"",
    "\"zig build phase3-idr-slot --build-file zigux/tests/build.zig\"",
    "\"zig build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig\"",
    "\"zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig\"",
};

const markers_2 = [_][]const u8{
    "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts\\zigux/check_phase3_catalog_selftest.zig",
};

const markers_3 = [_][]const u8{
    "PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass",
};

const markers_4 = [_][]const u8{
    "`scripts\\zigux/check_phase3_catalog_selftest.zig`",
};

const markers_5 = [_][]const u8{
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass",
};

const markers_6 = [_][]const u8{
    "PHASE3_ABI_CATALOG_SELFTEST_GUARD=scripts\\zigux/check_phase3_catalog_selftest.zig",
};

const markers_7 = [_][]const u8{
    "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass",
};

const markers_8 = [_][]const u8{
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
};

const markers_9 = [_][]const u8{
    "include/linux/zigux.h",
    "PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass",
};

const contracts = [_]FileContract{
    .{ .rel = "scripts/zigux/phase3_catalog.zig", .markers = &markers_0 },
    .{ .rel = "zigux/tests/fixtures/phase3_abi_manifest.json", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase3-export-uapi-boundary-survey.md", .markers = &markers_2 },
    .{ .rel = "scripts/zigux/validate_phase3_export_uapi_survey.zig", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md", .markers = &markers_4 },
    .{ .rel = "scripts/zigux/validate_phase3_low_level_wrapper_survey.zig", .markers = &markers_5 },
    .{ .rel = "Documentation/zigux/phase3-abi-header-family-survey.md", .markers = &markers_6 },
    .{ .rel = "scripts/zigux/validate_phase3_abi_header_family_survey.zig", .markers = &markers_7 },
    .{ .rel = "Documentation/zigux/phase3-linux-zigux-header-governance.md", .markers = &markers_8 },
    .{ .rel = "scripts/zigux/validate_phase3_linux_zigux_header_governance.zig", .markers = &markers_9 },
};

fn printOutputMarkers(io: Io, markers: []const []const u8) !void {
    for (markers) |marker| {
        if (std.mem.endsWith(u8, marker, "=")) {
            try guard.printLine(io, "{s}{d}", .{ marker, contracts.len });
        } else {
            try guard.printLine(io, "{s}", .{marker});
        }
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
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
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) std.process.exit(try runSelfTest(io, allocator));

    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try printOutputMarkers(io, &live_output_markers);
}
