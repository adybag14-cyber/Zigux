const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn requireOrdered(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const relative = std.mem.indexOf(u8, haystack[cursor..], marker) orelse return error.MissingOrderedMarker;
        cursor += relative + marker.len;
    }
}

test "pinned toolchain setup keeps fallback sources ordered" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    try requireOrdered(workflow, &.{
        "- name: Setup pinned Zig toolchain",
        "try_local_archive()",
        "python3 scripts/zigux/stage-pinned-zig-archive.py",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
        "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
        "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
        "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"",
        "if [ \"$download_success\" -ne 1 ]; then",
        "if try_download \"$ZIGUX_ZIG_URL\"; then",
    });
}

test "download attempts verify archives before extraction" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    try requireOrdered(workflow, &.{
        "try_download() {",
        "if curl -L --fail \"$url\" -o \"$archive_path\"; then",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
        "tar -xJf \"$archive_path\" -C .zig-toolchain",
        "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"",
        "rm -f \"$archive_path\"",
        "rm -rf \"$extract_root\"",
    });
}

test "failed fallback emits explicit verified archive failure" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    _ = try requireContains(workflow, "download_success=0");
    try requireOrdered(workflow, &.{
        "if [ \"$download_success\" -ne 1 ]; then",
        "echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2",
        "exit 1",
    });
    _ = try requireContains(workflow, "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
    _ = try requireContains(workflow, "\"$zig_path\" version");
}
