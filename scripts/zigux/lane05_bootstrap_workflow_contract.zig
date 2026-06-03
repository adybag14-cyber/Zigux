const std = @import("std");
const testing = std.testing;

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn workflowText(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, workflow_path, allocator, .limited(512 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "Lane 05 workflow keeps local archive paths and reconstruction live" {
    const workflow = try workflowText(testing.allocator);
    defer testing.allocator.free(workflow);

    try expectContains(workflow, "- 'third_party/**'");
    try expectContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow, "--parts-dir \"$repo_archive_parts_dir\"");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
}

test "Lane 05 workflow tries repo-local archive before network sources" {
    const workflow = try workflowText(testing.allocator);
    defer testing.allocator.free(workflow);

    try expectOrdered(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectOrdered(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "community-mirrors.txt");
    try expectOrdered(workflow, "community-mirrors.txt", "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try expectContains(workflow, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");
    try expectNotContains(workflow, "uses: actions/checkout@");
}

test "Lane 05 workflow keeps the bootstrap viability checker packet ordered" {
    const workflow = try workflowText(testing.allocator);
    defer testing.allocator.free(workflow);

    try expectOrdered(workflow, "Self-test current Lane 05 local-first archive checker", "Check current Lane 05 local-first archive packet");
    try expectOrdered(workflow, "Check current Lane 05 local-first archive packet", "Self-test current Lane 05 local archive README checker");
    try expectOrdered(workflow, "Check current Lane 05 local archive README packet", "Self-test current Lane 05 install-zig archive verification checker");
    try expectOrdered(workflow, "Check current Lane 05 install-zig archive verification packet", "Self-test current staged pinned Zig archive helper");
    try expectOrdered(workflow, "Self-test current staged pinned Zig archive helper", "Self-test current Zig installer helper");
    try expectOrdered(workflow, "Self-test current Lane 05 stage helper contract checker", "Check current Lane 05 stage helper contract packet");
    try expectOrdered(workflow, "Self-test current Lane 05 stage helper selftest checker", "Check current Lane 05 stage helper selftest packet");
}
