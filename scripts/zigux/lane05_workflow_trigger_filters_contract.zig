const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const critical_pr_paths = [_][]const u8{
    "      - 'scripts/zigux/**'",
    "      - 'third_party/**'",
    "      - 'zigux/**'",
    "      - 'include/linux/zigux.h'",
    "      - 'include/zigux/**'",
    "      - '.github/workflows/zigux-bootstrap.yml'",
};

fn readWorkflow() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn countExactLines(haystack: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), marker)) {
            count += 1;
        }
    }
    return count;
}

fn expectExactLineOnce(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countExactLines(haystack, marker));
}

test "lane05 workflow trigger filters keep bootstrap-critical paths visible to pull request CI" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    try expectExactLineOnce(workflow, "pull_request:");
    try expectContains(workflow, "    paths:");
    inline for (critical_pr_paths) |path_marker| {
        try expectContains(workflow, path_marker);
    }

    try expectOrder(workflow, "pull_request:", "      - 'scripts/zigux/**'");
    try expectOrder(workflow, "pull_request:", "      - 'third_party/**'");
    try expectOrder(workflow, "pull_request:", "      - '.github/workflows/zigux-bootstrap.yml'");
}

test "lane05 workflow still pins exact-head master bootstrap status and manual recovery" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "name: zigux-bootstrap");
    try expectExactLineOnce(workflow, "push:");
    try expectContains(workflow, "    branches: [ master ]");
    try expectExactLineOnce(workflow, "workflow_dispatch:");

    try expectContains(workflow, "github.workflow, github.sha");
    try expectContains(workflow, "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}");
    try expectOrder(workflow, "push:", "pull_request:");
    try expectOrder(workflow, "pull_request:", "workflow_dispatch:");
}

test "lane05 trigger surface protects bootstrap setup prerequisites" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "permissions:");
    try expectContains(workflow, "  contents: read");
    try expectContains(workflow, "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true");
    try expectContains(workflow, "actions/setup-python@v6.2.0");

    try expectOrder(workflow, "      - name: Checkout workspace snapshot", "      - name: Setup Python");
    try expectOrder(workflow, "      - name: Setup Python", "      - name: Setup pinned Zig toolchain");
    try expectOrder(workflow, "      - name: Setup pinned Zig toolchain", "      - name: Compile current scripts");
}
