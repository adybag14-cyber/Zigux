const std = @import("std");

fn requireContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireOrder(source: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.Options.debug_io,
        path,
        allocator,
        std.Io.Limit.limited(1024 * 1024),
    );
}

test "workflow setup ladder keeps repo-local archive before external action paths" {
    const workflow_source = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow_source);

    try requireOrder(workflow_source, "try_local_archive() {", "try_download() {");
    try requireOrder(workflow_source, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireOrder(
        workflow_source,
        "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
        "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
    );
    try requireOrder(
        workflow_source,
        "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
        "if try_download \"$ZIGUX_ZIG_URL\"; then",
    );
    try requireContains(
        workflow_source,
        "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org",
    );
}

test "workflow download action path verifies archive before publishing zig" {
    const workflow_source = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow_source);

    try requireContains(workflow_source, "try_download() {");
    try requireOrder(
        workflow_source,
        "if curl -L --fail \"$url\" -o \"$archive_path\"; then",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
    );
    try requireOrder(
        workflow_source,
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
        "tar -xJf \"$archive_path\" -C .zig-toolchain",
    );
    try requireOrder(
        workflow_source,
        "tar -xJf \"$archive_path\" -C .zig-toolchain",
        "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"",
    );
    try requireContains(workflow_source, "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
}

test "installer helper keeps hardened curl resume before urllib fallback" {
    const installer_source = try readRepoFile(std.testing.allocator, "scripts/zigux/install-zig.py");
    defer std.testing.allocator.free(installer_source);

    try requireOrder(installer_source, "def copy_url_to_file_with_curl(", "def copy_url_to_file(");
    try requireContains(installer_source, "'--retry'");
    try requireContains(installer_source, "'--retry-all-errors'");
    try requireContains(installer_source, "'--continue-at'");
    try requireContains(installer_source, "subprocess.run(cmd, check=True)");
    try requireOrder(
        installer_source,
        "if shutil.which('curl') is not None:",
        "request = build_download_request(url, resume_offset)",
    );
    try requireContains(installer_source, "resume_offset = destination.stat().st_size if destination.exists() else 0");
    try requireContains(installer_source, "urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})");
    try requireContains(installer_source, "append = resume_offset > 0 and status == 206");
}
