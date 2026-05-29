const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap-archive-parts-packet.yml";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        workflow_path,
        allocator,
        .limited(24 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

test "archive-parts workflow keeps exact-head master concurrency" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const group_line = "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}";
    const cancel_line = "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}";

    try expectContains(workflow, "concurrency:");
    try expectContains(workflow, group_line);
    try expectContains(workflow, cancel_line);
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, group_line));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, cancel_line));
}

test "archive-parts concurrency is declared before jobs" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const group_line = "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}";
    const cancel_line = "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}";

    try expectBefore(workflow, "permissions:", "concurrency:");
    try expectBefore(workflow, "contents: read", "concurrency:");
    try expectBefore(workflow, "concurrency:", group_line);
    try expectBefore(workflow, group_line, cancel_line);
    try expectBefore(workflow, cancel_line, "jobs:");
    try expectBefore(workflow, cancel_line, "- name: Checkout workspace snapshot");
}

test "archive-parts concurrency preserves pull request cancellation" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "push:\n    branches: [ master ]");
    try expectContains(workflow, "pull_request:");
    try expectContains(workflow, "workflow_dispatch:");
    try expectContains(workflow, "github.ref == 'refs/heads/master'");
    try expectContains(workflow, "github.sha");
    try expectContains(workflow, "github.ref != 'refs/heads/master'");
}