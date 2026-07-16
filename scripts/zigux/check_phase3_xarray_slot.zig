const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_XARRAY_SLOT=pass";
pub const self_test_pass_marker = "PHASE3_XARRAY_SLOT_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_XARRAY_SLOT_SELF_TEST=pass",
    "PHASE3_XARRAY_SLOT_SELF_TEST_CASES=",
};

const live_output_markers = [_][]const u8{
    "validated zigux/tests/phase3_xarray_slot_dump.zig",
    "validated zigux/tests/fixtures/phase3_xarray_slot_manifest.json",
};

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "PHASE3_XARRAY_SLOT_STARTER_PACKET_SELF_TEST=pass",
};

const markers_1 = [_][]const u8{
    "const xarray_slot_view = @import(\"xarray_slot_view\");",
    ".pointer => \"pointer_like\",",
    "\\\"is_tagged_internal\\\": {s}",
    "try writeCase(writer, \"inline_zero\", inline_zero_raw, true);",
    "try writeCase(writer, \"inline_limit\", inline_limit_raw, true);",
    "try writeCase(writer, \"err_top\", err_ptr.fromErrorCode(-1), true);",
    "try writeCase(writer, \"err_max\", err_ptr.fromErrorCode(-4095), false);",
};

const markers_2 = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/xarray_slot_view.zig\"),",
    ".root_source_file = b.path(\"phase3_xarray_slot_dump.zig\"),",
    "xarray_slot_view.addImport(\"err_ptr\", err_ptr);",
    "xarray_slot_view.addImport(\"xa_value\", xa_value);",
    "\"phase3-xarray-slot-dump\"",
};

const markers_3 = [_][]const u8{
    "phase3-xarray-slot-starter-packet:",
    "phase3-xarray-slot-starter-packet-test:",
    "phase3-xarray-slot-dump:",
    "$(ZIG_REPO_ROOT) build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig",
    "$(ZIG_REPO_ROOT) build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "$(ZIG_REPO_ROOT) build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
};

const markers_4 = [_][]const u8{
    "#define MAX_ERRNO ((uintptr_t)4095)",
    "static const char *kind_name(uintptr_t raw) {",
    "return \"pointer_like\";",
    "write_case(\"inline_zero\", make_value(0), 1);",
    "write_case(\"err_top\", (uintptr_t)(intptr_t)-1, 1);",
    "write_case(\"err_max\", (uintptr_t)(intptr_t)-4095, 0);",
};

const markers_5 = [_][]const u8{
    "\"word_bits\": 64",
    "\"safe_inline_limit_raw_hex\": \"0xffffffffffffefff\"",
    "\"name\": \"inline_zero\"",
    "\"decoded_value\": 0",
    "\"name\": \"err_top\"",
    "\"decoded_error\": -1",
    "\"decoded_error\": -4095",
};

const markers_6 = [_][]const u8{
    "\"slug\": \"phase3-xarray-slot\"",
    "\"status\": \"starter_and_dump_packet_present\"",
    "\"zigux/Makefile\"",
    "\"zigux/tests/phase3_xarray_slot_dump.zig\"",
    "\"zigux/tests/phase3_xarray_slot_dump_build.zig\"",
    "\"zigux/tests/fixtures/phase3_xarray_slot/expected.json\"",
    "\"make -C zigux phase3-xarray-slot-starter-packet\"",
    "\"make -C zigux phase3-xarray-slot-starter-packet-test\"",
    "\"make -C zigux phase3-xarray-slot-dump\"",
};

const contracts = [_]FileContract{
    .{ .rel = "scripts/zigux/check_phase3_xarray_slot_starter_packet.zig", .markers = &markers_0 },
    .{ .rel = "zigux/tests/phase3_xarray_slot_dump.zig", .markers = &markers_1 },
    .{ .rel = "zigux/tests/phase3_xarray_slot_dump_build.zig", .markers = &markers_2 },
    .{ .rel = "zigux/Makefile", .markers = &markers_3 },
    .{ .rel = "zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c", .markers = &markers_4 },
    .{ .rel = "zigux/tests/fixtures/phase3_xarray_slot/expected.json", .markers = &markers_5 },
    .{ .rel = "zigux/tests/fixtures/phase3_xarray_slot_manifest.json", .markers = &markers_6 },
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
