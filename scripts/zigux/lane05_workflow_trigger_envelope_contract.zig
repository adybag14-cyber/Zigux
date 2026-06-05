const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[cursor..], needle);
        try std.testing.expect(found != null);
        cursor += found.? + needle.len;
    }
}

fn requireExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle);
    try std.testing.expect(first != null);
    const after_first = first.? + needle.len;
    try std.testing.expect(std.mem.indexOf(u8, haystack[after_first..], needle) == null);
}

test "bootstrap workflow keeps master exact-head push and manual triggers enabled" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try requireContains(workflow, "name: zigux-bootstrap");
    try requireContains(workflow, "# Run every master push so exact-head bootstrap status stays attached");
    try requireContains(workflow, "  push:\n    branches: [ master ]");
    try requireContains(workflow, "  workflow_dispatch:");

    try requireOrdered(workflow, &.{
        "on:",
        "  push:",
        "    branches: [ master ]",
        "  pull_request:",
        "    paths:",
        "  workflow_dispatch:",
    });
    try requireExactlyOnce(workflow, "  push:\n    branches: [ master ]");
    try requireExactlyOnce(workflow, "  workflow_dispatch:");
}

test "pull request path filter keeps Zigux implementation and CI surfaces in scope" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try requireOrdered(workflow, &.{
        "  pull_request:",
        "    paths:",
        "      - 'lib/**'",
        "      - 'zigux-alpha/**'",
        "      - 'Documentation/zigux/**'",
        "      - 'scripts/zigux/**'",
        "      - 'third_party/**'",
        "      - 'tools/lib/*.zig'",
        "      - 'zigux/**'",
        "      - '.github/workflows/zigux-bootstrap.yml'",
    });

    try requireContains(workflow, "      - 'kernel/**/*.zig'");
    try requireContains(workflow, "      - 'net/**/*.zig'");
    try requireContains(workflow, "      - 'drivers/**/*.zig'");
    try requireContains(workflow, "      - 'include/linux/zigux.h'");
    try requireContains(workflow, "      - 'include/zigux/**'");
}

test "workflow permissions and Node24 envelope remain minimal and explicit" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try requireOrdered(workflow, &.{
        "permissions:",
        "  contents: read",
        "env:",
        "  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
        "concurrency:",
    });

    try requireContains(workflow, "      - name: Setup Python");
    try requireContains(workflow, "        uses: actions/setup-python@v6.2.0");
    try requireContains(workflow, "          python-version: '3.x'");
    try requireAbsent(workflow, "contents: write");
    try requireAbsent(workflow, "FORCE_JAVASCRIPT_ACTIONS_TO_NODE20");
}

test "concurrency preserves exact-head master runs while cancelling stale branch runs" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try requireContains(workflow, "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}");
    try requireContains(workflow, "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}");
    try requireOrdered(workflow, &.{
        "concurrency:",
        "github.ref == 'refs/heads/master'",
        "github.sha",
        "github.ref",
        "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}",
        "jobs:",
        "  bootstrap:",
    });
}
