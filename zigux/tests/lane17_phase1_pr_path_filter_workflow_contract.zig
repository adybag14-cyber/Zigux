const std = @import("std");
const testing = std.testing;

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const RequiredPath = struct {
    label: []const u8,
    entry: []const u8,
};

const required_pull_request_paths = [_]RequiredPath{
    .{ .label = "phase1 docs", .entry = "'Documentation/zigux/**'" },
    .{ .label = "phase1 scripts", .entry = "'scripts/zigux/**'" },
    .{ .label = "trusted zig payload", .entry = "'third_party/**'" },
    .{ .label = "phase1 helper files", .entry = "'tools/lib/*.zig'" },
    .{ .label = "nested helper files", .entry = "'tools/lib/**/*.zig'" },
    .{ .label = "zigux tests and make routes", .entry = "'zigux/**'" },
    .{ .label = "zigux headers", .entry = "'include/zigux/**'" },
    .{ .label = "linux zigux header", .entry = "'include/linux/zigux.h'" },
    .{ .label = "workflow self-trigger", .entry = "'.github/workflows/zigux-bootstrap.yml'" },
};

fn lineEquals(line: []const u8, needle: []const u8) bool {
    return std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle);
}

fn countExactLines(text: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (lineEquals(line, needle)) count += 1;
    }
    return count;
}

fn indexOfExactLine(text: []const u8, needle: []const u8) ?usize {
    var offset: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (lineEquals(line, needle)) return offset;
        offset += line.len + 1;
    }
    return null;
}

fn slicePullRequestPaths(text: []const u8) ![]const u8 {
    const pull_request_at = indexOfExactLine(text, "pull_request:") orelse return error.MissingPullRequestBlock;
    const after_pull_request = text[pull_request_at..];
    const paths_relative = indexOfExactLine(after_pull_request, "paths:") orelse return error.MissingPullRequestPaths;
    const paths_start = pull_request_at + paths_relative;

    const dispatch_at = indexOfExactLine(text[paths_start..], "workflow_dispatch:") orelse return error.MissingWorkflowDispatchBoundary;
    return text[paths_start .. paths_start + dispatch_at];
}

fn expectPathOnce(paths_block: []const u8, entry: RequiredPath) !void {
    const expected_line = try std.fmt.allocPrint(testing.allocator, "- {s}", .{entry.entry});
    defer testing.allocator.free(expected_line);

    const count = countExactLines(paths_block, expected_line);
    if (count != 1) {
        std.debug.print("path filter entry `{s}` for {s} appeared {d} times\n", .{
            entry.entry,
            entry.label,
            count,
        });
    }
    try testing.expectEqual(@as(usize, 1), count);
}

test "pull request path filter keeps Phase 1 workflow surfaces eligible" {
    const workflow_text = try std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        workflow_path,
        testing.allocator,
        .limited(256 * 1024),
    );
    defer testing.allocator.free(workflow_text);

    const paths_block = try slicePullRequestPaths(workflow_text);
    inline for (required_pull_request_paths) |entry| {
        try expectPathOnce(paths_block, entry);
    }
}

test "path filter block stays under pull_request and before manual dispatch" {
    const workflow_text = try std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        workflow_path,
        testing.allocator,
        .limited(256 * 1024),
    );
    defer testing.allocator.free(workflow_text);

    const pull_request_at = indexOfExactLine(workflow_text, "pull_request:") orelse return error.MissingPullRequestBlock;
    const workflow_dispatch_at = indexOfExactLine(workflow_text, "workflow_dispatch:") orelse return error.MissingWorkflowDispatchBoundary;
    const paths_block = try slicePullRequestPaths(workflow_text);
    const paths_at = indexOfExactLine(workflow_text, "paths:") orelse return error.MissingPullRequestPaths;

    try testing.expect(pull_request_at < paths_at);
    try testing.expect(paths_at < workflow_dispatch_at);
    try testing.expect(std.mem.indexOf(u8, paths_block, "push:") == null);
    try testing.expect(std.mem.indexOf(u8, paths_block, "workflow_dispatch:") == null);
}

test "master pushes remain exact-head workflow evidence even when filters miss" {
    const workflow_text = try std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        workflow_path,
        testing.allocator,
        .limited(256 * 1024),
    );
    defer testing.allocator.free(workflow_text);

    try testing.expectEqual(@as(usize, 1), countExactLines(workflow_text, "push:"));
    try testing.expectEqual(@as(usize, 1), countExactLines(workflow_text, "branches: [ master ]"));
    try testing.expect(std.mem.indexOf(u8, workflow_text, "Run every master push so exact-head bootstrap status stays attached") != null);
}
