const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(256 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

test "Lane 05 bootstrap setup tries repo-local archive before all download fallbacks" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try requireContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try requireContains(workflow, "try_local_archive() {");
    try requireContains(workflow, "try_download() {");
    try requireContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try requireContains(workflow, "--parts-dir \"$repo_archive_parts_dir\"");

    try requireOrder(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireOrder(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt");
    try requireOrder(workflow, "while IFS= read -r mirror_url; do", "if [ \"$download_success\" -ne 1 ]; then\n            if try_download \"$ZIGUX_ZIG_URL\"; then");
}

test "Lane 05 staged parts path feeds the same policy archive validator before extraction" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireOrder(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"", "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try requireOrder(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py", "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try requireOrder(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"", "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
    try requireOrder(workflow, "tar -xJf \"$repo_archive_path\" -C .zig-toolchain", "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"");
}

test "Lane 05 fallback cleanup clears partial archive and extraction state" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireContains(workflow, "rm -f \"$archive_path\" \"$mirror_file\"");
    try requireContains(workflow, "rm -f \"$archive_path\"\n              rm -rf \"$extract_root\"");
    try std.testing.expect(countOccurrences(workflow, "rm -rf \"$extract_root\"") >= 3);

    try requireOrder(workflow, "rm -f \"$archive_path\" \"$mirror_file\"", "if try_local_archive; then");
    try requireOrder(workflow, "rm -rf \"$extract_root\"", "if try_local_archive; then");
}

test "Lane 05 workflow still runs the shipped local archive guards" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireOrder(workflow, "Check current Zig toolchain policy packet", "Check current pinned Zig archive packet");
    try requireOrder(workflow, "Check current pinned Zig archive packet", "Self-test current Lane 05 local-first archive checker");
    try requireOrder(workflow, "Self-test current Lane 05 local-first archive checker", "Check current Lane 05 local-first archive packet");
    try requireOrder(workflow, "Check current Lane 05 local archive README packet", "Self-test current Lane 05 install-zig archive verification checker");
    try requireOrder(workflow, "Check current Lane 05 install-zig archive verification packet", "Self-test current staged pinned Zig archive helper");
    try requireOrder(workflow, "Self-test current Lane 05 stage helper contract checker", "Check current Lane 05 stage helper contract packet");
    try requireOrder(workflow, "Self-test current Lane 05 stage helper selftest checker", "Check current Lane 05 stage helper selftest packet");
}
