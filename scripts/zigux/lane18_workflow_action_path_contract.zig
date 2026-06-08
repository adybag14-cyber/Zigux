const std = @import("std");

fn requireContains(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingExpectedMarker;
}

fn requirePresent(haystack: []const u8, needle: []const u8) !void {
    _ = try requireContains(haystack, needle);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) != null) return error.ForbiddenMarkerPresent;
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = try requireContains(haystack, earlier);
    const later_index = try requireContains(haystack, later);
    try std.testing.expect(earlier_index < later_index);
}

fn loadWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        ".github/workflows/zigux-bootstrap.yml",
        allocator,
        .limited(256 * 1024),
    );
}

test "bootstrap workflow uses node-free source snapshot checkout" {
    const workflow = try loadWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requirePresent(workflow, "- name: Checkout workspace snapshot");
    try requirePresent(workflow, "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}");
    try requirePresent(workflow, "tar -xzf \"$archive\" -C \"$tmpdir\"");
    try requirePresent(workflow, "find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +");
    try requirePresent(workflow, "shopt -s dotglob");
    try requirePresent(workflow, "mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/");
    try requireAbsent(workflow, "uses: actions/checkout@");
}

test "pinned Zig setup derives one policy target and stages local archives first" {
    const workflow = try loadWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requirePresent(workflow, "- name: Setup pinned Zig toolchain");
    try requirePresent(workflow, "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]");
    try requirePresent(workflow, "expected exactly one pinned archive target");
    try requirePresent(workflow, "canonical_repo = \"adybag14-cyber/zig\"");
    try requirePresent(workflow, "canonical_tag = \"upstream-748e7c5e39fc\"");
    try requirePresent(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try requirePresent(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try requirePresent(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try requirePresent(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try requirePresent(workflow, "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
    try requirePresent(workflow, "\"$zig_path\" version");

    try requireBefore(workflow, "try_local_archive() {", "try_download() {");
    try requireBefore(workflow, "try_local_archive() {", "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try requireBefore(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py", "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
}

test "download fallback order keeps canonical release before mirrors and direct ziglang URL" {
    const workflow = try loadWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireBefore(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireBefore(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "https://ziglang.org/download/community-mirrors.txt");
    try requireBefore(workflow, "https://ziglang.org/download/community-mirrors.txt", "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap");
    try requireBefore(workflow, "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap", "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try requirePresent(workflow, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");
}
