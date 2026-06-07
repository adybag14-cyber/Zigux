const std = @import("std");
const testing = std.testing;

const default_workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, default_workflow_path, allocator, .limited(512 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    };
}

fn requireOrdered(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const next = std.mem.indexOf(u8, haystack[cursor..], marker) orelse {
            std.debug.print("missing ordered marker after byte {d}: {s}\n", .{ cursor, marker });
            return error.MissingOrderedMarker;
        };
        cursor += next + marker.len;
    }
}

fn requireAbsentBefore(haystack: []const u8, forbidden: []const u8, boundary: []const u8) !void {
    const boundary_index = try requireContains(haystack, boundary);
    if (std.mem.indexOf(u8, haystack[0..boundary_index], forbidden) != null) {
        std.debug.print("forbidden marker appears before boundary: {s}\n", .{forbidden});
        return error.ForbiddenEarlyMarker;
    }
}

test "lane05 setup fail-closed message stays after every fallback source" {
    const workflow = try readWorkflow(testing.allocator);
    defer testing.allocator.free(workflow);

    try requireOrdered(workflow, &.{
        "if try_local_archive; then",
        "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
        "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
        "if [ \"$download_success\" -ne 1 ]; then",
        "if try_download \"$ZIGUX_ZIG_URL\"; then",
        "if [ \"$download_success\" -ne 1 ]; then",
        "echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2",
        "exit 1",
    });
}

test "lane05 setup exports verified extract root only after final failure gate" {
    const workflow = try readWorkflow(testing.allocator);
    defer testing.allocator.free(workflow);

    try requireAbsentBefore(
        workflow,
        "echo \"$extract_root\" >> \"$GITHUB_PATH\"",
        "if [ \"$download_success\" -ne 1 ]; then\n            echo 'failed to install a verified pinned Zig archive",
    );
    try requireOrdered(workflow, &.{
        "if [ \"$download_success\" -ne 1 ]; then\n            echo 'failed to install a verified pinned Zig archive",
        "exit 1",
        "zig_path=\"$extract_root/zig\"",
        "echo \"$extract_root\" >> \"$GITHUB_PATH\"",
        "\"$zig_path\" version",
    });
}

test "lane05 setup keeps canonical mirror and direct fallback labels in one diagnostic" {
    const workflow = try readWorkflow(testing.allocator);
    defer testing.allocator.free(workflow);

    const diagnostic =
        "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org";
    try testing.expectEqual(@as(usize, 1), std.mem.count(u8, workflow, diagnostic));
    _ = try requireContains(workflow, "ZIGUX_ZIG_CANONICAL_URL");
    _ = try requireContains(workflow, "community-mirrors.txt");
    _ = try requireContains(workflow, "ZIGUX_ZIG_URL");
}

test "lane05 setup requires verified archive before local or downloaded success" {
    const workflow = try readWorkflow(testing.allocator);
    defer testing.allocator.free(workflow);

    try requireOrdered(workflow, &.{
        "if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"; then",
        "tar -xJf \"$repo_archive_path\" -C .zig-toolchain",
        "if python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"; then",
        "return 0",
    });
    try requireOrdered(workflow, &.{
        "if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"; then",
        "tar -xJf \"$archive_path\" -C .zig-toolchain",
        "if python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"; then",
        "return 0",
    });
}
