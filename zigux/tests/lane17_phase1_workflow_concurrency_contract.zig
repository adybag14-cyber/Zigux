const std = @import("std");
const config = @import("config");

const workflow_path = config.workflow_path;

fn readWorkflow(allocator: std.mem.Allocator) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, workflow_path, allocator, .limited(1024 * 1024));
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

fn requireOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn requireBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn lineContaining(haystack: []const u8, needle: []const u8) ![]const u8 {
    const index = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingLine;
    const line_start = if (std.mem.lastIndexOfScalar(u8, haystack[0..index], '\n')) |newline| newline + 1 else 0;
    const line_end = if (std.mem.indexOfScalar(u8, haystack[index..], '\n')) |newline| index + newline else haystack.len;
    return haystack[line_start..line_end];
}

test "bootstrap workflow keeps a single explicit concurrency block before jobs" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireOnce(workflow, "\nconcurrency:\n");
    try requireBefore(workflow, "\nconcurrency:\n", "\njobs:\n");
    try requireOnce(workflow, "cancel-in-progress:");
}

test "master pushes are keyed by exact commit instead of branch-only supersession" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const group_line = try lineContaining(workflow, "group: ${{");
    try std.testing.expect(std.mem.indexOf(u8, group_line, "github.ref == 'refs/heads/master'") != null);
    try std.testing.expect(std.mem.indexOf(u8, group_line, "github.sha") != null);
    try std.testing.expect(std.mem.indexOf(u8, group_line, "github.workflow") != null);
    try std.testing.expect(std.mem.indexOf(u8, group_line, "github.ref") != null);
}

test "master runs are not cancelled while pull request branch runs are superseded" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireOnce(workflow, "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}");
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(workflow, "cancel-in-progress: true"));
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(workflow, "cancel-in-progress: false"));
}

test "stale broad workflow grouping patterns stay absent" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try std.testing.expectEqual(@as(usize, 0), countOccurrences(workflow, "group: ${{ github.workflow }}"));
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(workflow, "group: ${{ github.ref }}"));
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(workflow, "group: ${{ format('{0}-{1}', github.workflow, github.sha) }}"));
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(workflow, "group: ${{ format('{0}-{1}', github.workflow, github.ref) }}"));
}
