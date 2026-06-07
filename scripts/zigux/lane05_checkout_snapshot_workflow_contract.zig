const std = @import("std");

fn readWorkflow() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn requireExactlyOnce(haystack: []const u8, needle: []const u8) !usize {
    const first = try requireContains(haystack, needle);
    const after = haystack[first + needle.len ..];
    if (std.mem.indexOf(u8, after, needle) != null) return error.DuplicateMarker;
    return first;
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_pos = try requireContains(haystack, earlier);
    const later_pos = try requireContains(haystack, later);
    if (earlier_pos >= later_pos) return error.MarkerOutOfOrder;
}

test "checkout snapshot hydrates exact repository sha through codeload" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    _ = try requireExactlyOnce(workflow, "- name: Checkout workspace snapshot");
    _ = try requireContains(workflow, "tmpdir=\"$(mktemp -d)\"");
    _ = try requireContains(workflow, "archive=\"$tmpdir/source.tar.gz\"");
    _ = try requireContains(workflow, "curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\" -o \"$archive\"");
    _ = try requireContains(workflow, "tar -xzf \"$archive\" -C \"$tmpdir\"");
    _ = try requireContains(workflow, "src_dir=\"$(find \"$tmpdir\" -mindepth 1 -maxdepth 1 -type d | head -n 1)\"");
}

test "checkout snapshot replaces workspace contents including dotfiles" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    _ = try requireContains(workflow, "find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +");
    _ = try requireContains(workflow, "shopt -s dotglob");
    _ = try requireContains(workflow, "mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/");
    try requireBefore(workflow, "find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +", "shopt -s dotglob");
    try requireBefore(workflow, "shopt -s dotglob", "mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/");
}

test "checkout snapshot stays before bootstrap setup and script preflight" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    try requireBefore(workflow, "- name: Checkout workspace snapshot", "- name: Setup Python");
    try requireBefore(workflow, "- name: Setup Python", "- name: Setup pinned Zig toolchain");
    try requireBefore(workflow, "- name: Setup pinned Zig toolchain", "- name: Compile current scripts");
    try requireBefore(workflow, "- name: Checkout workspace snapshot", "- name: Self-test current Zig toolchain checker");
}

test "checkout snapshot does not regress to actions checkout" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    if (std.mem.indexOf(u8, workflow, "uses: actions/checkout") != null) return error.UnexpectedActionsCheckout;
    _ = try requireExactlyOnce(workflow, "uses: actions/setup-python@v6.2.0");
}
