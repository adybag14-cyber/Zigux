const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const self_test_pass_marker = "PHASE15_VALIDATION_SELF_TEST=pass";
pub const live_pass_marker = "PHASE15_VALIDATION=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "PHASE15_STATUS=route_recovery_landed",
    "PHASE15_ROUTE_RECOVERY_STATUS=landed",
    "PHASE15_ROUTE_RECOVERY_NO_APPROVAL_CLAIM=true",
    "PHASE15_FREEZE_MAP_STATUS_CHANGE=false",
    "PHASE15_STUDY_ONLY_BOUNDARY_UNCHANGED=true",
};

const markers_1 = [_][]const u8{
    "phase15-validate:",
    "phase15-test:",
    "phase15: phase15-validate phase15-test",
};

const markers_2 = [_][]const u8{
    "Validate current Phase 15 governance packet",
    "Run current Phase 15 governance tests",
    "Run current Phase 15 aggregate route",
};

const markers_3 = [_][]const u8{
    "phase15-route-recovery",
    "phase15_route_recovery.zig",
};

const markers_4 = [_][]const u8{
    "\"missing_make_targets\": []",
    "\"missing_workflow_phase15_route\": false",
    "\"phase15_replay_green_on_current_master\": true",
};

const markers_5 = [_][]const u8{
    "\"remaining_readiness_gap_count\": 1",
    "\"gap\": \"no_architecture_council_status_change_approval\"",
};

const markers_6 = [_][]const u8{
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

const markers_7 = [_][]const u8{
    "phase 15 route recovery keeps wrappers and shared CI explicit",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase15-route-recovery.md", .markers = &markers_0 },
    .{ .rel = "zigux/Makefile", .markers = &markers_1 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_2 },
    .{ .rel = "zigux/tests/phase15_build.zig", .markers = &markers_3 },
    .{ .rel = "zigux/tests/phase15_readiness_gate_manifest.json", .markers = &markers_4 },
    .{ .rel = "zigux/tests/phase15_readiness_gap_matrix.json", .markers = &markers_5 },
    .{ .rel = "Documentation/zigux/freeze-map.md", .markers = &markers_6 },
    .{ .rel = "zigux/tests/phase15_route_recovery.zig", .markers = &markers_7 },
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
    try guard.printLine(io, "PHASE15_VALIDATION_REQUIRED_FILE_COUNT={d}", .{contracts.len});
    try guard.printLine(io, "PHASE15_VALIDATION_REQUIRED_MARKER_COUNT={d}", .{@as(usize, 25)});
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
    if (self_test) try guard.printLine(io, "PHASE15_VALIDATION_SELF_TEST_CASE_COUNT=1", .{});
    try emitCounts(io);
}
