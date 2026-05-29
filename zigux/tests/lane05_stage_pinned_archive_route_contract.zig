const std = @import("std");

const max_file_bytes = 512 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(max_file_bytes),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "stage helper keeps source and parts-dir CLI contract visible" {
    const allocator = std.testing.allocator;
    const stage_script = try readRepoFile(allocator, "scripts/zigux/stage-pinned-zig-archive.py");
    defer allocator.free(stage_script);

    try expectContains(stage_script, "parser.add_argument(\"--source\"");
    try expectContains(stage_script, "parser.add_argument(\n        \"--parts-dir\"");
    try expectContains(stage_script, "exactly one of --source or --parts-dir is required unless --self-test is used");
    try expectContains(stage_script, "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}");
    try expectContains(stage_script, "STAGE_PINNED_ZIG_ARCHIVE_STATUS={status}");
    try expectContains(stage_script, "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass");
    try expectContains(stage_script, "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}");
}

test "stage helper preserves pinned policy and duplicate guardrails" {
    const allocator = std.testing.allocator;
    const stage_script = try readRepoFile(allocator, "scripts/zigux/stage-pinned-zig-archive.py");
    defer allocator.free(stage_script);

    try expectContains(stage_script, "TOOLCHAIN_POLICY = Path(\"scripts/zigux/zig-toolchain-policy.json\")");
    try expectContains(stage_script, "THIRD_PARTY_DIR = Path(\"third_party\")");
    try expectContains(stage_script, "\"x86_64-linux\": 58_159_088");
    try expectContains(stage_script, "object_pairs_hook=DuplicateTrackingDict");
    try expectContains(stage_script, "duplicate toolchain policy keys");
    try expectContains(stage_script, "duplicate archive_sha256 targets");
    try expectContains(stage_script, "archive_target_scope");
    try expectContains(stage_script, "channel_minimum_lockstep");
    try expectContains(stage_script, "third_party contains duplicate-suffix archive copies");
}

test "stage helper fail-closes shard reconstruction contract" {
    const allocator = std.testing.allocator;
    const stage_script = try readRepoFile(allocator, "scripts/zigux/stage-pinned-zig-archive.py");
    defer allocator.free(stage_script);

    try expectContains(stage_script, "def reconstruct_archive_from_parts(");
    try expectContains(stage_script, "manifest_path = parts_dir / \"manifest.json\"");
    try expectContains(stage_script, "require_manifest_string(manifest, \"filename\", manifest_path)");
    try expectContains(stage_script, "require_manifest_string(manifest, \"encoding\", manifest_path)");
    try expectContains(stage_script, "require_manifest_string(manifest, \"sha256\", manifest_path)");
    try expectContains(stage_script, "require_manifest_int(manifest, \"size\", manifest_path)");
    try expectContains(stage_script, "require_manifest_int(manifest, \"part_count\", manifest_path)");
    try expectContains(stage_script, "require_manifest_int(manifest, \"chunk_bytes\", manifest_path)");
    try expectContains(stage_script, "parts_glob != \"part-*.b64\"");
    try expectContains(stage_script, "part-{index:03d}.b64");
    try expectContains(stage_script, "base64.b64decode(encoded, validate=True)");
    try expectContains(stage_script, "missing expected shard");
    try expectContains(stage_script, "invalid base64 shard");
    try expectContains(stage_script, "expected shard manifest filename");
    try expectContains(stage_script, "return validate_source_archive(");
}

test "bootstrap workflow keeps local parts staging before downloads" {
    const allocator = std.testing.allocator;
    const bootstrap_workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(bootstrap_workflow);

    try expectContains(bootstrap_workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(bootstrap_workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(bootstrap_workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(bootstrap_workflow, "--parts-dir \"$repo_archive_parts_dir\"");
    try expectContains(bootstrap_workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\"");
    try expectContains(bootstrap_workflow, "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org");
    try expectNotContains(bootstrap_workflow, "actions/checkout@");

    try expectBefore(bootstrap_workflow, "try_local_archive()", "try_download() {");
    try expectBefore(bootstrap_workflow, "if try_local_archive; then", "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt");
    try expectBefore(bootstrap_workflow, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt", "if try_download \"$ZIGUX_ZIG_URL\"; then");
}
