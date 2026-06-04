const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const archive_filter_line = "- 'third_party/**'";
const scripts_filter_line = "- 'scripts/zigux/**'";
const tests_filter_line = "- 'zigux/**'";
const workflow_filter_line = "- '.github/workflows/zigux-bootstrap.yml'";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn countExactLines(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    return count;
}

fn firstIndex(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn pullRequestBlock(workflow: []const u8) ![]const u8 {
    const start = try firstIndex(workflow, "pull_request:");
    const end = std.mem.indexOfPos(u8, workflow, start, "  workflow_dispatch:") orelse workflow.len;
    return workflow[start..end];
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = try firstIndex(haystack, before);
    const after_index = try firstIndex(haystack, after);
    try std.testing.expect(before_index < after_index);
}

test "phase2 cross archive payload path remains in pull-request bootstrap filters" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);
    const pr_block = try pullRequestBlock(workflow);

    try std.testing.expectEqual(@as(usize, 1), countExactLines(pr_block, "pull_request:"));
    try std.testing.expectEqual(@as(usize, 1), countExactLines(pr_block, "paths:"));
    try std.testing.expectEqual(@as(usize, 1), countExactLines(pr_block, archive_filter_line));
}

test "phase2 cross archive filter stays with the direct cross packet filters" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);
    const pr_block = try pullRequestBlock(workflow);

    try std.testing.expectEqual(@as(usize, 1), countExactLines(pr_block, scripts_filter_line));
    try std.testing.expectEqual(@as(usize, 1), countExactLines(pr_block, tests_filter_line));
    try std.testing.expectEqual(@as(usize, 1), countExactLines(pr_block, workflow_filter_line));

    try expectOrdered(pr_block, scripts_filter_line, archive_filter_line);
    try expectOrdered(pr_block, archive_filter_line, tests_filter_line);
    try expectOrdered(pr_block, tests_filter_line, workflow_filter_line);
}

test "phase2 cross archive filter does not regress to a legacy explicit tarball-only path" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);
    const pr_block = try pullRequestBlock(workflow);

    try std.testing.expectEqual(@as(usize, 0), countExactLines(
        pr_block,
        "- 'third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz'",
    ));
    try std.testing.expectEqual(@as(usize, 0), countExactLines(
        pr_block,
        "- 'third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz'",
    ));
}
