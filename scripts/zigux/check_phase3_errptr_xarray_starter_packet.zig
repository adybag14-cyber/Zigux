const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_ERRPTR_XARRAY_STARTER_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=pass",
    "PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST_CASES=",
};

const live_output_markers = [_][]const u8{
    "PHASE3_ERRPTR_XARRAY_STARTER_PACKET=pass",
};

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json",
    "scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "the highest tagged inline boundary still stays below the `err_ptr` floor",
    "It is one helper-local interop proof layered beside the existing `dev_t` starter packet.",
};

const markers_1 = [_][]const u8{
    "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json",
    "scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "the manifest-backed starter packet",
};

const markers_2 = [_][]const u8{
    "pub const max_errno: usize = 4095;",
    "pub const err_floor: usize = @bitCast(-@as(isize, @intCast(max_errno)));",
    "pub fn fromErrorCode(code: isize) usize {",
    "pub fn isErrValue(raw: usize) bool {",
    "pub fn toErrorCode(raw: usize) isize {",
    "test \"err_ptr encodes the Linux error band as a tagged pointer-sized value\" {",
    "test \"err_ptr keeps the floor boundary explicit\" {",
    "test \"non-error values stay outside the err_ptr band\" {",
};

const markers_3 = [_][]const u8{
    "const err_ptr = @import(\"err_ptr\");",
    "pub const value_tag_mask: usize = 0x1;",
    "pub const safe_inline_limit: usize = (err_ptr.err_floor >> 1) - 1;",
    "ValueWouldOverlapErrPtr",
    "return (value << 1) | value_tag_mask;",
    "return (raw & value_tag_mask) == value_tag_mask and !err_ptr.isErrValue(raw);",
};

const markers_4 = [_][]const u8{
    "test \"err_ptr encodes the Linux error band as a tagged pointer-sized value\" {",
    "test \"xa_value round-trips a bounded inline value without entering the err_ptr band\" {",
    "test \"xa_value rejects inline values that would overlap err_ptr encodings\" {",
    "test \"safe inline limit stays the highest tagged value below the err_ptr floor\" {",
    "try testing.expectEqual(err_ptr.err_floor, raw + 2);",
};

const markers_5 = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/err_ptr.zig\"),",
    ".root_source_file = b.path(\"../helpers/xa_value.zig\"),",
    ".root_source_file = b.path(\"phase3_errptr_xarray_starter_packet.zig\"),",
    "xa_value.addImport(\"err_ptr\", err_ptr);",
    "\"phase3-errptr-xarray-starter-packet-test\"",
};

const markers_6 = [_][]const u8{
    "\"slug\": \"phase3-errptr-xarray-starter-packet\"",
    "\"status\": \"starter_packet_present\"",
    "\"Documentation/zigux/phase3-errptr-xarray-slice.md\"",
    "\"Documentation/zigux/phase3-validator-support-surface.md\"",
    "\"zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json\"",
    "\"repo_reality_gaps\": []",
    "\"next_safe_step\": \"keep the helper-local err_ptr/xarray packet honest with manifest-backed replay before widening into broader Phase 3 validator or export-boundary claims\"",
    "zig build phase3-errptr-xarray-starter-packet-test --build-file zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase3-errptr-xarray-slice.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase3-validator-support-surface.md", .markers = &markers_1 },
    .{ .rel = "zigux/helpers/err_ptr.zig", .markers = &markers_2 },
    .{ .rel = "zigux/helpers/xa_value.zig", .markers = &markers_3 },
    .{ .rel = "zigux/tests/phase3_errptr_xarray_starter_packet.zig", .markers = &markers_4 },
    .{ .rel = "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig", .markers = &markers_5 },
    .{ .rel = "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json", .markers = &markers_6 },
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
