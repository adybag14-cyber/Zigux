const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const self_test_pass_marker = "PHASE15_READINESS_GATE_PACKET_SELF_TEST=pass";
pub const live_pass_marker = "PHASE15_READINESS_GATE_PACKET=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "PHASE15_ROUTE_RECOVERY_STATUS=landed",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "No Architecture Council approval is recorded by route recovery",
    "historical survey findings superseded by this current-state block",
};

const markers_1 = [_][]const u8{
    "\"surveyed_commit_mode\": \"current_master_replay\"",
    "\"missing_make_targets\": []",
    "\"missing_workflow_phase15_route\": false",
    "\"phase15_validate_target_present\": true",
    "\"phase15_test_target_present\": true",
    "\"phase15_aggregate_target_present\": true",
    "\"shared_ci_phase15_present\": true",
    "\"phase15_replay_green_on_current_master\": true",
};

const markers_2 = [_][]const u8{
    "\"remaining_readiness_gap_count\": 1",
    "\"blocked_make_route_count\": 0",
    "\"blocked_workflow_route_count\": 0",
    "\"release_evidence_count\": 7",
    "\"gap\": \"no_architecture_council_status_change_approval\"",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase15-readiness-gate-survey.md", .markers = &markers_0 },
    .{ .rel = "zigux/tests/phase15_readiness_gate_manifest.json", .markers = &markers_1 },
    .{ .rel = "zigux/tests/phase15_readiness_gap_matrix.json", .markers = &markers_2 },
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
    try guard.printLine(io, "PHASE15_READINESS_GATE_PACKET_REQUIRED_FILE_COUNT={d}", .{contracts.len});
    try guard.printLine(io, "PHASE15_READINESS_GATE_PACKET_REQUIRED_MARKER_COUNT={d}", .{@as(usize, 19)});
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
    if (self_test) try guard.printLine(io, "PHASE15_READINESS_GATE_PACKET_SELF_TEST_CASE_COUNT=1", .{});
    try emitCounts(io);
}
