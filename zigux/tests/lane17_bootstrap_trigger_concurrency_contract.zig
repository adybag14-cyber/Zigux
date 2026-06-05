const std = @import("std");
const build_options = @import("build_options");
const testing = std.testing;

const max_workflow_bytes = 256 * 1024;

fn readWorkflow() ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        build_options.workflow_path,
        testing.allocator,
        .limited(max_workflow_bytes),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOnce(haystack: []const u8, needle: []const u8) !void {
    try testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try testing.expect(earlier_index < later_index);
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

test "bootstrap trigger policy keeps master pushes exact-head and pull requests path-scoped" {
    const workflow = try readWorkflow();
    defer testing.allocator.free(workflow);

    try requireContains(workflow, "name: zigux-bootstrap\n");
    try requireContains(workflow, "on:\n  push:\n    branches: [ master ]\n  pull_request:\n    paths:\n");
    try requireContains(workflow, "  workflow_dispatch:\n");
    try requireOnce(workflow, "  push:\n    branches: [ master ]\n");
    try requireOnce(workflow, "  pull_request:\n    paths:\n");
    try requireOnce(workflow, "  workflow_dispatch:\n");
    try requireMissing(workflow, "push:\n    branches: [ master ]\n    paths:");
    try requireBefore(workflow, "  push:\n    branches: [ master ]", "  pull_request:\n    paths:");
    try requireBefore(workflow, "  pull_request:\n    paths:", "  workflow_dispatch:");
}

test "pull request path filter covers Zigux sources and workflow-owned surfaces" {
    const workflow = try readWorkflow();
    defer testing.allocator.free(workflow);

    const required_paths = [_][]const u8{
        "      - 'Documentation/zigux/**'",
        "      - 'samples/zigux/**'",
        "      - 'kernel/**/*.zig'",
        "      - 'drivers/**/*.zig'",
        "      - 'scripts/include/xalloc.h'",
        "      - 'scripts/zigux/**'",
        "      - 'third_party/**'",
        "      - 'tools/lib/*.zig'",
        "      - 'tools/lib/**/*.zig'",
        "      - 'zigux/**'",
        "      - 'include/linux/zigux.h'",
        "      - 'include/zigux/**'",
        "      - '.github/workflows/zigux-bootstrap.yml'",
    };
    for (required_paths) |path_marker| {
        try requireContains(workflow, path_marker);
        try requireOnce(workflow, path_marker);
    }

    try requireBefore(workflow, "      - 'scripts/zigux/**'", "      - 'third_party/**'");
    try requireBefore(workflow, "      - 'third_party/**'", "      - 'tools/lib/*.zig'");
}

test "permissions and node runtime policy remain explicit before bootstrap job" {
    const workflow = try readWorkflow();
    defer testing.allocator.free(workflow);

    try requireContains(workflow, "permissions:\n  contents: read\n");
    try requireContains(workflow, "env:\n  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true\n");
    try requireOnce(workflow, "permissions:\n  contents: read\n");
    try requireOnce(workflow, "env:\n  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true\n");
    try requireBefore(workflow, "permissions:\n  contents: read", "jobs:\n  bootstrap:");
    try requireBefore(workflow, "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true", "jobs:\n  bootstrap:");
}

test "concurrency policy preserves master verdicts while cancelling stale branch runs" {
    const workflow = try readWorkflow();
    defer testing.allocator.free(workflow);

    try requireContains(workflow, "concurrency:\n");
    try requireContains(workflow, "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}");
    try requireContains(workflow, "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}");
    try requireOnce(workflow, "concurrency:\n");
    try requireOnce(workflow, "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}");
    try requireOnce(workflow, "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}");
    try requireMissing(workflow, "cancel-in-progress: true");
    try requireBefore(workflow, "concurrency:\n", "jobs:\n  bootstrap:");
}
