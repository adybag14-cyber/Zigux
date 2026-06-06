const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const stage_helper_path = "scripts/zigux/stage-pinned-zig-archive.py";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.Options.debug_io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "bootstrap workflow stages local archive parts before archive verification" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, workflow_path);
    defer allocator.free(workflow);

    try requireContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try requireContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try requireContains(workflow, "if [ ! -f \"$repo_archive_path\" ]; then");
    try requireContains(workflow, "if [ ! -d \"$repo_archive_parts_dir\" ]; then");
    try requireContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try requireContains(workflow, "--parts-dir \"$repo_archive_parts_dir\" || return 1");
    try requireContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try requireContains(workflow, "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
    try requireBefore(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"", "try_local_archive() {");
    try requireBefore(workflow, "--parts-dir \"$repo_archive_parts_dir\" || return 1", "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try requireBefore(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"", "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
}

test "local parts path remains before canonical mirror and direct download fallback" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, workflow_path);
    defer allocator.free(workflow);

    try requireContains(workflow, "if try_local_archive; then");
    try requireContains(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireContains(workflow, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then");
    try requireContains(workflow, "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try requireContains(workflow, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");
    try requireBefore(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireBefore(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then");
    try requireBefore(workflow, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then", "if try_download \"$ZIGUX_ZIG_URL\"; then");
}

test "stage helper exposes shard manifest and reconstructed archive status markers" {
    const allocator = std.testing.allocator;
    const stage_helper = try readRepoFile(allocator, stage_helper_path);
    defer allocator.free(stage_helper);

    try requireContains(stage_helper, "def load_shard_manifest(parts_dir: Path) -> dict[str, object]:");
    try requireContains(stage_helper, "manifest_path = parts_dir / \"manifest.json\"");
    try requireContains(stage_helper, "def reconstruct_archive_from_parts(");
    try requireContains(stage_helper, "expected_filename: str,");
    try requireContains(stage_helper, "expected_sha: str,");
    try requireContains(stage_helper, "STAGE_PINNED_ZIG_ARCHIVE_STATUS=");
    try requireContains(stage_helper, "STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=");
    try requireBefore(stage_helper, "def load_shard_manifest(parts_dir: Path) -> dict[str, object]:", "def reconstruct_archive_from_parts(");
}

test "workflow keeps stage helper self-test before install helper self-test" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, workflow_path);
    defer allocator.free(workflow);

    try requireContains(workflow, "Self-test current staged pinned Zig archive helper");
    try requireContains(workflow, "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test");
    try requireContains(workflow, "Self-test current Zig installer helper");
    try requireContains(workflow, "run: python3 scripts/zigux/install-zig.py --self-test");
    try requireBefore(workflow, "Self-test current staged pinned Zig archive helper", "Self-test current Zig installer helper");
}
