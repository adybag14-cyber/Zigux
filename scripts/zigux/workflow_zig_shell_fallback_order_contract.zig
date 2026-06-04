const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const required_markers = [_][]const u8{
    "- name: Setup pinned Zig toolchain",
    "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))",
    "canonical_repo = \"adybag14-cyber/zig\"",
    "canonical_tag = \"upstream-748e7c5e39fc\"",
    "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
    "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
    "python3 scripts/zigux/stage-pinned-zig-archive.py",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
    "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
    "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
    "if try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"; then",
    "if try_download \"$ZIGUX_ZIG_URL\"; then",
    "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org",
    "echo \"$extract_root\" >> \"$GITHUB_PATH\"",
    "\"$zig_path\" version",
};

const forbidden_markers = [_][]const u8{
    "uses: goto-bus-stop/setup-zig",
    "uses: mlugg/setup-zig",
    "uses: korandoru/setup-zig",
    "uses: goto-bus-stop/setup-zig@",
    "uses: mlugg/setup-zig@",
    "uses: korandoru/setup-zig@",
    "with:\n          version: 0.17.0-dev",
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn expectContainsExactlyOnce(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, marker));
}

fn expectContainsAtLeastOnce(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expect(countOccurrences(haystack, marker) > 0);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, workflow_path, allocator, .limited(512 * 1024));
}

test "bootstrap workflow keeps pinned Zig shell fallback order explicit" {
    const workflow_text = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow_text);

    inline for (required_markers) |marker| {
        try expectContainsExactlyOnce(workflow_text, marker);
    }

    try expectBefore(workflow_text, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectBefore(workflow_text, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then");
    try expectBefore(workflow_text, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then", "if try_download \"$ZIGUX_ZIG_URL\"; then");
}

test "bootstrap workflow does not rely on a node-bound setup-zig action" {
    const workflow_text = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow_text);

    inline for (forbidden_markers) |marker| {
        try std.testing.expectEqual(@as(usize, 0), countOccurrences(workflow_text, marker));
    }

    try expectContainsExactlyOnce(workflow_text, "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true");
    try expectContainsAtLeastOnce(workflow_text, "- name: Setup Python\n        uses: actions/setup-python@v6.2.0");
    try expectContainsExactlyOnce(workflow_text, "- name: Setup pinned Zig toolchain\n        run: |");
}
