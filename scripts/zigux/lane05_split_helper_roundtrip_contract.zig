const std = @import("std");

const split_helper_path = "scripts/zigux/split-pinned-zig-archive.py";

fn readFileAlloc(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "lane05 split helper keeps policy-derived archive metadata and defaults" {
    const helper = try readFileAlloc(split_helper_path, 96 * 1024);
    defer std.testing.allocator.free(helper);

    try expectContains(helper, "TOOLCHAIN_POLICY = Path(\"scripts/zigux/zig-toolchain-policy.json\")");
    try expectContains(helper, "DEFAULT_CHUNK_BYTES = 786_432");
    try expectContains(helper, "\"x86_64-linux\": 59_410_844");
    try expectContains(helper, "archive_target_scope");
    try expectContains(helper, "archive_sha256");
    try expectContains(helper, "f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(helper, "missing expected archive size for {target}");
}

test "lane05 split helper writes a staged manifest matching the existing parts contract" {
    const helper = try readFileAlloc(split_helper_path, 96 * 1024);
    defer std.testing.allocator.free(helper);

    try expectContains(helper, "def write_manifest(");
    try expectContains(helper, "\"filename\": filename");
    try expectContains(helper, "\"encoding\": \"base64\"");
    try expectContains(helper, "\"sha256\": sha256");
    try expectContains(helper, "\"size\": size");
    try expectContains(helper, "\"chunk_bytes\": chunk_bytes");
    try expectContains(helper, "\"part_count\": part_count");
    try expectContains(helper, "\"parts_glob\": \"part-*.b64\"");
    try expectContains(helper, "manifest.json");
    try expectBefore(helper, "write_manifest(", "return manifest_path");
}

test "lane05 split helper keeps split and reconstruct routes fail-closed" {
    const helper = try readFileAlloc(split_helper_path, 96 * 1024);
    defer std.testing.allocator.free(helper);

    try expectContains(helper, "def ensure_clean_output_dir(");
    try expectContains(helper, "output directory must be empty");
    try expectContains(helper, "def split_archive(");
    try expectContains(helper, "validate_archive(source");
    try expectContains(helper, "base64.b64encode(chunk)");
    try expectContains(helper, "def reconstruct_archive(");
    try expectContains(helper, "missing expected shard");
    try expectContains(helper, "base64.b64decode(encoded, validate=True)");
    try expectContains(helper, "expected reconstructed archive to have sha256");
    try expectBefore(helper, "def split_archive(", "base64.b64encode(chunk)");
    try expectBefore(helper, "load_manifest(parts_dir)", "for index in range(int(metadata[\"part_count\"]))");
}

test "lane05 split helper exposes self-test and CLI status markers" {
    const helper = try readFileAlloc(split_helper_path, 96 * 1024);
    defer std.testing.allocator.free(helper);

    try expectContains(helper, "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass");
    try expectContains(helper, "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=");
    try expectContains(helper, "SPLIT_PINNED_ZIG_ARCHIVE=pass");
    try expectContains(helper, "SPLIT_PINNED_ZIG_ARCHIVE=fail");
    try expectContains(helper, "RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass");
    try expectContains(helper, "RECONSTRUCT_PINNED_ZIG_ARCHIVE=fail");
    try expectContains(helper, "--source");
    try expectContains(helper, "--output-dir");
    try expectContains(helper, "--parts-dir");
    try expectContains(helper, "--destination");
}
