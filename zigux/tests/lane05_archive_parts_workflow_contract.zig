const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap-archive-parts-packet.yml";

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstNeedle;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondNeedle;
    try std.testing.expect(first_index < second_index);
}

test "lane05 archive parts workflow keeps dedicated viability packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const workflow = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), workflow_path, std.testing.allocator, .limited(256 * 1024));
    defer std.testing.allocator.free(workflow);

    try requireContains(workflow, "name: zigux-bootstrap-archive-parts-packet\n");
    try requireContains(workflow, "permissions:\n  contents: read\n");
    try requireContains(workflow, "- 'third_party/**'\n");
    try requireContains(workflow, "- '.github/workflows/zigux-bootstrap-archive-parts-packet.yml'\n");

    try requireContains(workflow, "- name: Checkout workspace snapshot\n");
    try requireContains(workflow, "curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\"");
    try requireContains(workflow, "find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +");
    try requireMissing(workflow, "uses: actions/checkout");

    try requireContains(workflow, "python3 -m py_compile scripts/zigux/check-zig-toolchain.py scripts/zigux/check-lane05-archive-parts-packet.py scripts/zigux/check-lane05-archive-parts-workflow.py");
    try requireContains(workflow, "python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test");
    try requireContains(workflow, "python3 scripts/zigux/check-lane05-archive-parts-workflow.py");
    try requireContains(workflow, "python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test");
    try requireContains(workflow, "python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing");

    try requireOrdered(
        workflow,
        "python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test",
        "python3 scripts/zigux/check-lane05-archive-parts-workflow.py\n",
    );
    try requireOrdered(
        workflow,
        "python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test",
        "python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing",
    );
}
