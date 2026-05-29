const std = @import("std");

const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const split_helper_path = "scripts/zigux/split-pinned-zig-archive.py";
const stage_helper_path = "scripts/zigux/stage-pinned-zig-archive.py";
const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const pinned_channel = "0.17.0-dev.87+9b177a7d2";
const pinned_target = "x86_64-linux";
const pinned_digest = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77";
const pinned_size = "58_159_088";

fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(1024 * 1024),
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

test "pinned archive policy still names the single shardable target" {
    const allocator = std.testing.allocator;
    const policy = try readFixture(allocator, policy_path);
    defer allocator.free(policy);

    try expectContains(policy, "\"channel\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy, "\"minimum_version\": \"" ++ pinned_channel ++ "\"");
    try expectContains(policy, "\"" ++ pinned_target ++ "\": \"" ++ pinned_digest ++ "\"");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"" ++ pinned_target ++ "\"");
    try expectContains(policy, "\"phase2-toolchain\"");
    try expectContains(policy, "\"phase2-validate\"");
}

test "split helper writes the manifest and ordered base64 shard packet" {
    const allocator = std.testing.allocator;
    const split_helper = try readFixture(allocator, split_helper_path);
    defer allocator.free(split_helper);

    try expectContains(split_helper, "DEFAULT_CHUNK_BYTES = 786_432");
    try expectContains(split_helper, "EXPECTED_ARCHIVE_SIZES = {");
    try expectContains(split_helper, "\"" ++ pinned_target ++ "\": " ++ pinned_size);
    try expectContains(split_helper, "\"filename\": filename");
    try expectContains(split_helper, "\"encoding\": \"base64\"");
    try expectContains(split_helper, "\"sha256\": sha256");
    try expectContains(split_helper, "\"size\": size");
    try expectContains(split_helper, "\"chunk_bytes\": chunk_bytes");
    try expectContains(split_helper, "\"part_count\": part_count");
    try expectContains(split_helper, "\"parts_glob\": \"part-*.b64\"");
    try expectContains(split_helper, "f\"part-{index:03d}.b64\"");
    try expectBefore(split_helper, "write_manifest(", "return part_count, manifest_path");
}

test "stage helper accepts only matching base64 archive parts" {
    const allocator = std.testing.allocator;
    const stage_helper = try readFixture(allocator, stage_helper_path);
    defer allocator.free(stage_helper);

    try expectContains(stage_helper, "EXPECTED_ARCHIVE_SIZES = {");
    try expectContains(stage_helper, "\"" ++ pinned_target ++ "\": " ++ pinned_size);
    try expectContains(stage_helper, "def reconstruct_archive_from_parts(");
    try expectContains(stage_helper, "expected_filename: str");
    try expectContains(stage_helper, "expected_sha: str");
    try expectContains(stage_helper, "expected_size: int");
    try expectContains(stage_helper, "if filename != expected_filename:");
    try expectContains(stage_helper, "if encoding != \"base64\":");
    try expectContains(stage_helper, "if sha256 != expected_sha:");
    try expectContains(stage_helper, "if size != expected_size:");
    try expectContains(stage_helper, "if parts_glob != \"part-*.b64\":");
    try expectContains(stage_helper, "f\"part-{index:03d}.b64\"");
    try expectContains(stage_helper, "base64.b64decode(encoded, validate=True)");
    try expectContains(stage_helper, "return validate_source_archive(");
}

test "bootstrap workflow tries repo archive parts before network download" {
    const allocator = std.testing.allocator;
    const workflow = try readFixture(allocator, workflow_path);
    defer allocator.free(workflow);

    try expectContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow, "--parts-dir \"$repo_archive_parts_dir\"");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(workflow, "curl -L --fail https://ziglang.org/download/community-mirrors.txt");
    try expectContains(workflow, "try_download \"$ZIGUX_ZIG_URL\"");
    try expectBefore(workflow, "if try_local_archive; then", "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt");
    try expectBefore(workflow, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt", "if [ \"$download_success\" -ne 1 ]; then");
}

test "archive filename remains policy-derived across helper and workflow surfaces" {
    const allocator = std.testing.allocator;
    const split_helper = try readFixture(allocator, split_helper_path);
    defer allocator.free(split_helper);
    const stage_helper = try readFixture(allocator, stage_helper_path);
    defer allocator.free(stage_helper);
    const workflow = try readFixture(allocator, workflow_path);
    defer allocator.free(workflow);

    try expectContains(split_helper, "\"filename\": f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(stage_helper, "\"filename\": f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(workflow, "ZIGUX_ZIG_FILENAME='{filename}'");
}
