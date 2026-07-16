const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_IDR_SLOT_STARTER_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_IDR_SLOT_STARTER_PACKET_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_IDR_SLOT_STARTER_PACKET_SELF_TEST=pass",
    "PHASE3_IDR_SLOT_STARTER_PACKET_SELF_TEST_CASES=",
};

const live_output_markers = [_][]const u8{
    "validated zigux/tests/phase3_idr_slot_starter_packet.zig",
    "validated zigux/tests/phase3_idr_slot_starter_packet_build.zig",
};

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "pub const value_tag_mask: usize = 0x1;",
    "pub const safe_inline_limit: usize = (err_ptr.err_floor >> 1) - 1;",
    "pub fn makeValue(value: usize) MakeValueError!usize {",
};

const markers_1 = [_][]const u8{
    "pub const SlotKind = enum {",
    "pub fn fromErrorCode(code: isize) SlotView {",
    "pub fn isTaggedInternalEntry(raw: usize) bool {",
};

const markers_2 = [_][]const u8{
    "pub const SlotKind = enum {",
    "pub fn fromInternalValue(value: usize) xa_value.MakeValueError!SlotView {",
    "pub fn isTaggedInternalEntry(raw: usize) bool {",
    "test \"empty slots stay distinct from pointer and internal lanes\" {",
    "test \"xa_value-tagged entries stay internal instead of looking like mapped pointers\" {",
    "test \"err_ptr encodings stay separated from pointer-backed idr entries\" {",
};

const markers_3 = [_][]const u8{
    "test \"idr slot view keeps empty slots explicit\" {",
    "test \"idr slot view keeps pointer lanes publishable without tagging drift\" {",
    "test \"idr slot view keeps xa_value entries in the internal lane\" {",
    "test \"idr slot view preserves err_ptr encodings as tagged error entries\" {",
    "test \"top err_ptr encoding never falls back into the pointer lane\" {",
    "try testing.expect(idr_slot_view.isTaggedInternalEntry(raw));",
};

const markers_4 = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/idr_slot_view.zig\"),",
    ".root_source_file = b.path(\"phase3_idr_slot_starter_packet.zig\"),",
    "idr_slot_view.addImport(\"xarray_slot_view\", xarray_slot_view);",
    "idr_slot_view.addImport(\"xa_value\", xa_value);",
    "\"phase3-idr-slot-starter-packet-test\"",
};

const contracts = [_]FileContract{
    .{ .rel = "zigux/helpers/xa_value.zig", .markers = &markers_0 },
    .{ .rel = "zigux/helpers/xarray_slot_view.zig", .markers = &markers_1 },
    .{ .rel = "zigux/helpers/idr_slot_view.zig", .markers = &markers_2 },
    .{ .rel = "zigux/tests/phase3_idr_slot_starter_packet.zig", .markers = &markers_3 },
    .{ .rel = "zigux/tests/phase3_idr_slot_starter_packet_build.zig", .markers = &markers_4 },
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
