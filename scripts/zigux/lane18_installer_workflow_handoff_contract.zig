const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const installer_path = "scripts/zigux/install-zig.py";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "workflow keeps installer helper self-test before Phase 2 gates" {
    const workflow_source = try readRepoFile(std.testing.allocator, workflow_path);
    defer std.testing.allocator.free(workflow_source);

    try requireContains(workflow_source, "Self-test current Zig installer helper");
    try requireContains(workflow_source, "python3 scripts/zigux/install-zig.py --self-test");
    try requireContains(workflow_source, "Self-test current Phase 2 toolchain pinning checker");
    try requireContains(workflow_source, "Check current Phase 2 bootstrap workflow routes packet");
    try requireBefore(
        workflow_source,
        "python3 scripts/zigux/install-zig.py --self-test",
        "python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    );
    try requireBefore(
        workflow_source,
        "python3 scripts/zigux/install-zig.py --self-test",
        "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    );
}

test "workflow setup ladder still prefers verified repo-local archive before network fallbacks" {
    const workflow_source = try readRepoFile(std.testing.allocator, workflow_path);
    defer std.testing.allocator.free(workflow_source);

    try requireContains(workflow_source, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try requireContains(workflow_source, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try requireContains(workflow_source, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try requireContains(workflow_source, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try requireContains(workflow_source, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireContains(workflow_source, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then");
    try requireContains(workflow_source, "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try requireBefore(workflow_source, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireBefore(workflow_source, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then");
    try requireBefore(workflow_source, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then", "if try_download \"$ZIGUX_ZIG_URL\"; then");
}

test "installer helper owns resumable curl and Range fallback semantics" {
    const installer_source = try readRepoFile(std.testing.allocator, installer_path);
    defer std.testing.allocator.free(installer_source);

    try requireContains(installer_source, "def copy_url_to_file_with_curl(");
    try requireContains(installer_source, "'--retry-all-errors',");
    try requireContains(installer_source, "'--continue-at',");
    try requireContains(installer_source, "'-',");
    try requireContains(installer_source, "def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:");
    try requireContains(installer_source, "return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})");
    try requireContains(installer_source, "append = resume_offset > 0 and status == 206");
    try requireBefore(installer_source, "if shutil.which('curl') is not None:", "for attempt in range(1, retries + 1):");
}

test "installer helper pins canonical release and checksum-visible install status" {
    const installer_source = try readRepoFile(std.testing.allocator, installer_path);
    defer std.testing.allocator.free(installer_source);

    try requireContains(installer_source, "CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.758+748e7c5e3'");
    try requireContains(installer_source, "CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', 'adybag14-cyber/zig')");
    try requireContains(installer_source, "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', 'upstream-748e7c5e39fc')");
    try requireContains(installer_source, "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')");
    try requireContains(installer_source, "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')");
    try requireContains(installer_source, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')");
    try requireContains(installer_source, "print(f'ZIG_INSTALL_SOURCE={archive_source}')");
    try requireContains(installer_source, "print('ZIG_INSTALL_STATUS=pass')");
    try requireNotContains(installer_source, "setup-zig");
}
