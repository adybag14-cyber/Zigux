const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const self_test_pass_marker = "PHASE15_BLOCKED_ROUTE_RECOVERY_SELF_TEST=pass";
pub const live_pass_marker = "PHASE15_BLOCKED_ROUTE_RECOVERY=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "PHASE15_ROUTE_RECOVERY_STATUS=landed",
    "PHASE15_MAKE_VALIDATE_ROUTE=make -C zigux phase15-validate",
    "PHASE15_MAKE_TEST_ROUTE=make -C zigux phase15-test",
    "PHASE15_MAKE_AGGREGATE_ROUTE=make -C zigux phase15",
    "PHASE15_ROUTE_RECOVERY_NO_APPROVAL_CLAIM=true",
    "PHASE15_FREEZE_MAP_STATUS_CHANGE=false",
};

const markers_1 = [_][]const u8{
    "phase15-validate:",
    "phase15-test:",
    "phase15: phase15-validate phase15-test",
    "zigux/tests/phase15_build.zig",
};

const markers_2 = [_][]const u8{
    "- name: Validate current Phase 15 governance packet",
    "run: make -C zigux phase15-validate",
    "- name: Run current Phase 15 governance tests",
    "run: make -C zigux phase15-test",
    "- name: Run current Phase 15 aggregate route",
    "run: make -C zigux phase15",
};

const markers_3 = [_][]const u8{
    "phase 15 route recovery keeps wrappers and shared CI explicit",
    "phase 15 route recovery leaves governance boundaries unchanged",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase15-route-recovery.md", .markers = &markers_0 },
    .{ .rel = "zigux/Makefile", .markers = &markers_1 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_2 },
    .{ .rel = "zigux/tests/phase15_route_recovery.zig", .markers = &markers_3 },
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
    try guard.printLine(io, "PHASE15_BLOCKED_ROUTE_RECOVERY_REQUIRED_FILE_COUNT={d}", .{contracts.len});
    try guard.printLine(io, "PHASE15_BLOCKED_ROUTE_RECOVERY_REQUIRED_MARKER_COUNT={d}", .{@as(usize, 18)});
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
    if (self_test) try guard.printLine(io, "PHASE15_BLOCKED_ROUTE_RECOVERY_SELF_TEST_CASE_COUNT=1", .{});
    try emitCounts(io);
}
