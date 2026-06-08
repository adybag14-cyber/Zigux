const std = @import("std");
const build_options = @import("build_options");

const WORKFLOW_NAME = "name: zigux-bootstrap";
const READ_ONLY_PERMISSION = "contents: read";
const NODE24_RUNTIME = "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true";
const CONCURRENCY_GROUP = "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}";
const PR_CANCEL_ONLY = "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}";
const BOOTSTRAP_JOB = "jobs:";

const FORBIDDEN_POLICY_MARKERS = [_][]const u8{
    "contents: write",
    "actions: write",
    "pull-requests: write",
    "FORCE_JAVASCRIPT_ACTIONS_TO_NODE20",
    "cancel-in-progress: true",
    "cancel-in-progress: false",
    "group: ${{ github.workflow }}",
    "group: ${{ github.workflow }}-${{ github.ref }}",
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    if (needle.len == 0) return 0;
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOf(u8, haystack[start..], needle)) |relative| {
        count += 1;
        start += relative + needle.len;
    }
    return count;
}

fn countTrimmedLines(text: []const u8, expected: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), expected)) {
            count += 1;
        }
    }
    return count;
}

fn requireLineOnce(text: []const u8, line: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countTrimmedLines(text, line));
}

fn requireAbsent(text: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(text, needle));
}

fn requireOrdered(text: []const u8, chain: []const []const u8) !void {
    var previous_end: usize = 0;
    for (chain) |needle| {
        const index = std.mem.indexOf(u8, text[previous_end..], needle) orelse return error.MissingOrderedMarker;
        previous_end += index + needle.len;
    }
}

fn validateWorkflow(text: []const u8) !void {
    try requireLineOnce(text, WORKFLOW_NAME);
    try requireLineOnce(text, "permissions:");
    try requireLineOnce(text, READ_ONLY_PERMISSION);
    try requireLineOnce(text, "env:");
    try requireLineOnce(text, NODE24_RUNTIME);
    try requireLineOnce(text, "concurrency:");
    try requireLineOnce(text, CONCURRENCY_GROUP);
    try requireLineOnce(text, PR_CANCEL_ONLY);

    for (FORBIDDEN_POLICY_MARKERS) |marker| {
        try requireAbsent(text, marker);
    }

    try requireOrdered(text, &[_][]const u8{
        "workflow_dispatch:",
        "permissions:",
        READ_ONLY_PERMISSION,
        "env:",
        NODE24_RUNTIME,
        "concurrency:",
        CONCURRENCY_GROUP,
        PR_CANCEL_ONLY,
        BOOTSTRAP_JOB,
        "bootstrap:",
        "runs-on: ubuntu-latest",
    });
}

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        build_options.workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

test "live workflow keeps the bootstrap policy header fail-closed" {
    const text = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(text);
    try validateWorkflow(text);
}

test "contract accepts the current workflow policy header" {
    try validateWorkflow(
        "name: zigux-bootstrap\n" ++
            "on:\n" ++
            "  workflow_dispatch:\n" ++
            "\n" ++
            "permissions:\n" ++
            "  contents: read\n" ++
            "\n" ++
            "env:\n" ++
            "  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true\n" ++
            "\n" ++
            "concurrency:\n" ++
            "  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}\n" ++
            "  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}\n" ++
            "\n" ++
            "jobs:\n" ++
            "  bootstrap:\n" ++
            "    runs-on: ubuntu-latest\n",
    );
}

test "contract rejects write-scoped workflow permissions" {
    const writable =
        "name: zigux-bootstrap\n" ++
        "on:\n" ++
        "  workflow_dispatch:\n" ++
        "permissions:\n" ++
        "  contents: write\n" ++
        "env:\n" ++
        "  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true\n" ++
        "concurrency:\n" ++
        "  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}\n" ++
        "  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}\n" ++
        "jobs:\n" ++
        "  bootstrap:\n" ++
        "    runs-on: ubuntu-latest\n";
    try std.testing.expectError(error.TestExpectedEqual, validateWorkflow(writable));
}

test "contract rejects master-cancelling concurrency drift" {
    const stale_cancel =
        "name: zigux-bootstrap\n" ++
        "on:\n" ++
        "  workflow_dispatch:\n" ++
        "permissions:\n" ++
        "  contents: read\n" ++
        "env:\n" ++
        "  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true\n" ++
        "concurrency:\n" ++
        "  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}\n" ++
        "  cancel-in-progress: true\n" ++
        "jobs:\n" ++
        "  bootstrap:\n" ++
        "    runs-on: ubuntu-latest\n";
    try std.testing.expectError(error.TestExpectedEqual, validateWorkflow(stale_cancel));
}

test "contract rejects broad ref-only concurrency groups" {
    const stale_group =
        "name: zigux-bootstrap\n" ++
        "on:\n" ++
        "  workflow_dispatch:\n" ++
        "permissions:\n" ++
        "  contents: read\n" ++
        "env:\n" ++
        "  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true\n" ++
        "concurrency:\n" ++
        "  group: ${{ github.workflow }}-${{ github.ref }}\n" ++
        "  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}\n" ++
        "jobs:\n" ++
        "  bootstrap:\n" ++
        "    runs-on: ubuntu-latest\n";
    try std.testing.expectError(error.TestExpectedEqual, validateWorkflow(stale_group));
}
