const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectContainsBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierAnchor;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterAnchor;
    try std.testing.expect(earlier_index < later_index);
}

test "lane05 broad bootstrap keeps exact-head tarball snapshot checkout" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 128 * 1024);
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "name: zigux-bootstrap");
    try expectContains(workflow, "Run every master push so exact-head bootstrap status stays attached");
    try expectContains(workflow, "push:\n    branches: [ master ]\n  pull_request:");
    try expectContains(workflow, "- name: Checkout workspace snapshot");
    try expectContains(workflow, "curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\" -o \"$archive\"");
    try expectContains(workflow, "tar -xzf \"$archive\" -C \"$tmpdir\"");
    try expectContains(workflow, "src_dir=\"$(find \"$tmpdir\" -mindepth 1 -maxdepth 1 -type d | head -n 1)\"");
    try expectContains(workflow, "find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +");
    try expectContains(workflow, "shopt -s dotglob");
    try expectContains(workflow, "mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/");

    try expectContainsBefore(workflow, "Checkout workspace snapshot", "Setup pinned Zig toolchain");
    try expectAbsent(workflow, "uses: actions/checkout");
    try expectAbsent(workflow, "fetch-depth:");
}

test "lane05 snapshot checkout keeps local parts route reachable" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 128 * 1024);
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow, "--root \"$GITHUB_WORKSPACE\"");
    try expectContains(workflow, "--parts-dir \"$repo_archive_parts_dir\"");
    try expectContainsBefore(workflow, "try_local_archive", "try_download");
    try expectContainsBefore(workflow, "if try_local_archive; then", "https://ziglang.org/download/community-mirrors.txt");
    try expectContainsBefore(workflow, "https://ziglang.org/download/community-mirrors.txt", "if [ \"$download_success\" -ne 1 ]; then");
}
