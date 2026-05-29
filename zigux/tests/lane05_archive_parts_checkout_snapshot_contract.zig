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

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
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

test "archive-parts workflow uses codeload snapshot checkout" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "- name: Checkout workspace snapshot");
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "- name: Checkout workspace snapshot"));
    try expectContains(workflow, "run: |\n          set -euxo pipefail");
    try expectContains(workflow, "tmpdir=\"$(mktemp -d)\"");
    try expectContains(workflow, "archive=\"$tmpdir/source.tar.gz\"");
    try expectContains(workflow, "curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\" -o \"$archive\"");
    try expectContains(workflow, "tar -xzf \"$archive\" -C \"$tmpdir\"");
    try expectContains(workflow, "src_dir=\"$(find \"$tmpdir\" -mindepth 1 -maxdepth 1 -type d | head -n 1)\"");
    try expectContains(workflow, "find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +");
    try expectContains(workflow, "shopt -s dotglob");
    try expectContains(workflow, "mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/");
    try expectMissing(workflow, "uses: actions/checkout");
}

test "checkout snapshot command order preserves clean workspace hydration" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectBefore(workflow, "- name: Checkout workspace snapshot", "- name: Setup Python");
    try expectBefore(workflow, "set -euxo pipefail", "tmpdir=\"$(mktemp -d)\"");
    try expectBefore(workflow, "tmpdir=\"$(mktemp -d)\"", "archive=\"$tmpdir/source.tar.gz\"");
    try expectBefore(workflow, "archive=\"$tmpdir/source.tar.gz\"", "curl -L --fail");
    try expectBefore(workflow, "curl -L --fail", "tar -xzf \"$archive\" -C \"$tmpdir\"");
    try expectBefore(workflow, "tar -xzf \"$archive\" -C \"$tmpdir\"", "src_dir=\"$(find \"$tmpdir\"");
    try expectBefore(workflow, "src_dir=\"$(find \"$tmpdir\"", "find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +");
    try expectBefore(workflow, "find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +", "shopt -s dotglob");
    try expectBefore(workflow, "shopt -s dotglob", "mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/");
}

test "snapshot checkout stays tied to archive-parts guard steps" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectBefore(workflow, "- name: Checkout workspace snapshot", "- name: Compile current Lane 05 archive-parts workflow scripts");
    try expectBefore(workflow, "- name: Checkout workspace snapshot", "python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test");
    try expectBefore(workflow, "- name: Checkout workspace snapshot", "python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test");
    try expectBefore(workflow, "- name: Checkout workspace snapshot", "python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing");
}
