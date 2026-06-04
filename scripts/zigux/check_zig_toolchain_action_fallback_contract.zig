const std = @import("std");

const max_file_size = 256 * 1024;

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn indexOf(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    try std.testing.expect((try indexOf(haystack, earlier)) < (try indexOf(haystack, later)));
}

fn sliceBetween(haystack: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = try indexOf(haystack, start_marker);
    const end = try indexOf(haystack[start..], end_marker);
    return haystack[start .. start + end];
}

test "bootstrap setup path avoids legacy Zig action and keeps snapshot checkout before toolchain setup" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    const setup_path = try sliceBetween(
        workflow,
        "      - name: Checkout workspace snapshot\n",
        "      - name: Compile current scripts\n",
    );

    try expectContains(workflow, "  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true\n");
    try expectContains(setup_path, "curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\"");
    try expectContains(setup_path, "shopt -s dotglob\n");
    try expectBefore(setup_path, "Checkout workspace snapshot", "Setup Python");
    try expectBefore(setup_path, "Setup Python", "Setup pinned Zig toolchain");
    try expectAbsent(setup_path, "uses: actions/checkout@");
    try expectAbsent(setup_path, "uses: goto-bus-stop/setup-zig@");
    try expectAbsent(setup_path, "uses: mlugg/setup-zig@");
}

test "pinned setup action path tries trusted local archive then canonical release then mirrors then direct build" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    const setup_path = try sliceBetween(
        workflow,
        "      - name: Setup pinned Zig toolchain\n",
        "      - name: Compile current scripts\n",
    );

    try expectContains(setup_path, "canonical_repo = \"adybag14-cyber/zig\"");
    try expectContains(setup_path, "canonical_tag = \"upstream-748e7c5e39fc\"");
    try expectContains(setup_path, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(setup_path, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(setup_path, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(setup_path, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectBefore(setup_path, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectBefore(setup_path, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt");
    try expectBefore(setup_path, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt", "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try expectContains(setup_path, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");
}

test "make phase2 toolchain route preserves the same checker and helper order" {
    const allocator = std.testing.allocator;
    const makefile = try readFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    const route = try sliceBetween(makefile, "phase2-toolchain:\n", "phase2-tools:\n");

    try expectBefore(route, "check-zig-toolchain.py --self-test", "check-zig-toolchain.py --policy-only");
    try expectBefore(route, "check-zig-toolchain.py --policy-only", "check-zig-toolchain.py --archive-only --allow-missing");
    try expectBefore(route, "check-zig-toolchain.py --archive-only --allow-missing", "check-lane05-local-first-archive-workflow.py --self-test");
    try expectBefore(route, "check-lane05-install-zig-archive-verification.py", "install-zig.py --self-test");
    try expectBefore(route, "install-zig.py --self-test", "stage-pinned-zig-archive.py --self-test");
    try expectBefore(route, "stage-pinned-zig-archive.py --self-test", "check-lane05-stage-helper-contract.py --self-test");
    try expectBefore(route, "check-phase2-toolchain-pinning.py --self-test", "check-phase2-toolchain-pin-scope.py --self-test");
}
