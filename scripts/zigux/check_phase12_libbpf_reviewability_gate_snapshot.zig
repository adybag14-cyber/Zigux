const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_LIBBPF_REVIEWABILITY_GATE_SNAPSHOT_SELF_TEST=pass";

const EXPECTED_EVIDENCE = [_][]const u8{
    "primary snapshot replay parses surveyed_commit and asserts it is a lowercase 40-character hex SHA",
};

const REVIEWABILITY_MARKERS = [_][]const u8{
    "test_name",
    "test \"phase12 libbpf reviewability gate keeps the current snapshot anchor exact\"",
    "surveyed_commit_field",
    "surveyed_commit: []const u8,",
    "surveyed_commit_assertion",
    "try std.testing.expect(isHexSha(fixture.surveyed_commit));",
    "snapshot_fixture_path",
    "snapshot_checker_blob_assertion",
    "277554397ab1a236c71f1dac9061ffe4cfbeaf67",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_EVIDENCE) |marker| try guard.requireMarker(text, marker);
    for (REVIEWABILITY_MARKERS) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
