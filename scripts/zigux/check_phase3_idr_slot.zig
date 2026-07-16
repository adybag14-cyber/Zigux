const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_IDR_SLOT=pass";
pub const self_test_pass_marker = "PHASE3_IDR_SLOT_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_IDR_SLOT_SELF_TEST=pass",
    "PHASE3_IDR_SLOT_SELF_TEST_CASES=",
};

const live_output_markers = [_][]const u8{
    "validated zigux/tests/phase3_idr_slot_dump.zig",
    "validated zigux/tests/fixtures/phase3_idr_slot/expected.json",
    "validated zigux/tests/fixtures/phase3_idr_slot_manifest.json",
};

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "# Phase 3 idr-slot Slice",
    "`zigux/Makefile`",
    "`make -C zigux phase3-idr-slot-starter-packet-test`",
    "`make -C zigux phase3-idr-slot-dump`",
    "two focused Makefile wrappers",
};

const markers_1 = [_][]const u8{
    "pub const SlotKind = enum {",
    "pub fn fromInternalValue(value: usize) xa_value.MakeValueError!SlotView {",
    "pub fn isTaggedInternalEntry(raw: usize) bool {",
};

const markers_2 = [_][]const u8{
    "test \"idr slot view keeps empty slots explicit\" {",
    "test \"idr slot view keeps xa_value entries in the internal lane\" {",
};

const markers_3 = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/idr_slot_view.zig\"),",
    "\"phase3-idr-slot-starter-packet-test\"",
};

const markers_4 = [_][]const u8{
    "PHASE3_IDR_SLOT_STARTER_PACKET_SELF_TEST=pass",
};

const markers_5 = [_][]const u8{
    "const idr_slot_view = @import(\"idr_slot_view\");",
    ".internal_value => \"internal_value\",",
    "try writeCase(writer, \"internal_limit\", inline_limit_raw, true);",
    "try writeCase(writer, \"err_max\", err_ptr.fromErrorCode(-4095), false);",
};

const markers_6 = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/idr_slot_view.zig\"),",
    ".root_source_file = b.path(\"phase3_idr_slot_dump.zig\"),",
    "\"phase3-idr-slot-dump\"",
};

const markers_7 = [_][]const u8{
    "phase3-idr-slot-starter-packet-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig",
    "phase3-idr-slot-dump:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig",
};

const markers_8 = [_][]const u8{
    "#define MAX_ERRNO ((uintptr_t)4095)",
    "return \"internal_value\";",
    "write_case(\"internal_limit\", inline_limit_raw, 1);",
    "write_case(\"err_max\", (uintptr_t)(intptr_t)-4095, 0);",
};

const markers_9 = [_][]const u8{
    "\"safe_inline_limit_raw_hex\": \"0xffffffffffffefff\"",
    "\"name\": \"internal_zero\"",
    "\"decoded_error\": -12",
    "\"decoded_error\": -4095",
};

const markers_10 = [_][]const u8{
    "\"slug\": \"phase3-idr-slot\"",
    "\"status\": \"starter_and_dump_packet_present\"",
    "\"zigux/tests/phase3_idr_slot_dump.zig\"",
    "\"zigux/Makefile\"",
    "\"make -C zigux phase3-idr-slot-starter-packet-test\"",
    "\"make -C zigux phase3-idr-slot-dump\"",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase3-idr-slot-slice.md", .markers = &markers_0 },
    .{ .rel = "zigux/helpers/idr_slot_view.zig", .markers = &markers_1 },
    .{ .rel = "zigux/tests/phase3_idr_slot_starter_packet.zig", .markers = &markers_2 },
    .{ .rel = "zigux/tests/phase3_idr_slot_starter_packet_build.zig", .markers = &markers_3 },
    .{ .rel = "scripts/zigux/check_phase3_idr_slot_starter_packet.zig", .markers = &markers_4 },
    .{ .rel = "zigux/tests/phase3_idr_slot_dump.zig", .markers = &markers_5 },
    .{ .rel = "zigux/tests/phase3_idr_slot_dump_build.zig", .markers = &markers_6 },
    .{ .rel = "zigux/Makefile", .markers = &markers_7 },
    .{ .rel = "zigux/tests/fixtures/phase3_idr_slot/phase3_idr_slot_c_harness.c", .markers = &markers_8 },
    .{ .rel = "zigux/tests/fixtures/phase3_idr_slot/expected.json", .markers = &markers_9 },
    .{ .rel = "zigux/tests/fixtures/phase3_idr_slot_manifest.json", .markers = &markers_10 },
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
