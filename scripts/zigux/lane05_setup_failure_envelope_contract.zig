const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn expectOne(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingMarker;
    try std.testing.expect(std.mem.indexOfPos(u8, haystack, first + needle.len, needle) == null);
}

test "Lane 05 setup failure envelope names every trusted fallback source" {
    const workflow = try readRepoFile(workflow_path, 512 * 1024);
    defer std.testing.allocator.free(workflow);

    try expectOne(workflow, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");
    try expectContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow, "canonical_repo = \"adybag14-cyber/zig\"");
    try expectContains(workflow, "canonical_tag = \"upstream-748e7c5e39fc\"");
    try expectContains(workflow, "https://ziglang.org/builds/{filename}");
    try expectContains(workflow, "https://ziglang.org/download/community-mirrors.txt");
}

test "Lane 05 setup ladder fails only after local, canonical, mirror, and direct attempts" {
    const workflow = try readRepoFile(workflow_path, 512 * 1024);
    defer std.testing.allocator.free(workflow);

    try expectBefore(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectBefore(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt");
    try expectBefore(workflow, "while IFS= read -r mirror_url; do", "if [ \"$download_success\" -ne 1 ]; then");
    try expectBefore(workflow, "if [ \"$download_success\" -ne 1 ]; then\n            if try_download \"$ZIGUX_ZIG_URL\"; then", "echo 'failed to install a verified pinned Zig archive");
    try expectBefore(workflow, "echo 'failed to install a verified pinned Zig archive", "exit 1");
}

test "Lane 05 setup verifies archive bytes before exposing zig on PATH" {
    const workflow = try readRepoFile(workflow_path, 512 * 1024);
    defer std.testing.allocator.free(workflow);

    try expectBefore(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"", "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
    try expectBefore(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"", "tar -xJf \"$archive_path\" -C .zig-toolchain");
    try expectBefore(workflow, "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"", "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
    try expectContains(workflow, "rm -rf \"$extract_root\"");
}
