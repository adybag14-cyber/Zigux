const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const self_test_pass_marker = "PHASE15_DOCS_README_ALIGNMENT_SELF_TEST=pass";
pub const live_pass_marker = "PHASE15_DOCS_README_ALIGNMENT=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "PHASE15_ROUTE_RECOVERY_STATUS=landed",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "No Architecture Council approval is recorded by route recovery",
    "Documentation/zigux/phase15-route-recovery.md",
};

const markers_1 = [_][]const u8{
    "PHASE15_FREEZE_MAP_STATUS_CHANGE=false",
    "PHASE15_STUDY_ONLY_BOUNDARY_UNCHANGED=true",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/README.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase15-route-recovery.md", .markers = &markers_1 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE15_DOCS_README_ALIGNMENT_REQUIRED_FILE_COUNT={d}", .{contracts.len});
    try guard.printLine(io, "PHASE15_DOCS_README_ALIGNMENT_REQUIRED_MARKER_COUNT={d}", .{@as(usize, 8)});
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
        std.process.exit(2);
    }

    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{if (self_test) self_test_pass_marker else live_pass_marker});
    if (self_test) try guard.printLine(io, "PHASE15_DOCS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=1", .{});
    try emitCounts(io);
}
