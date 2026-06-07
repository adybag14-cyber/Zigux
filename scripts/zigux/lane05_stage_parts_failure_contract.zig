const std = @import("std");

const stage_helper_path = "scripts/zigux/stage-pinned-zig-archive.py";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.TestExpectedEqual;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.TestExpectedEqual;
    try std.testing.expect(before_index < after_index);
}

fn expectPartsManifestFailureSurface(stage_helper: []const u8) !void {
    const markers = [_][]const u8{
        "def reconstruct_archive_from_parts(",
        "manifest_path = parts_dir / \"manifest.json\"",
        "filename = require_manifest_string(manifest, \"filename\", manifest_path)",
        "encoding = require_manifest_string(manifest, \"encoding\", manifest_path)",
        "sha256 = require_manifest_string(manifest, \"sha256\", manifest_path)",
        "size = require_manifest_int(manifest, \"size\", manifest_path)",
        "part_count = require_manifest_int(manifest, \"part_count\", manifest_path)",
        "require_manifest_int(manifest, \"chunk_bytes\", manifest_path)",
        "parts_glob = require_manifest_string(manifest, \"parts_glob\", manifest_path)",
        "if filename != expected_filename:",
        "if encoding != \"base64\":",
        "if sha256 != expected_sha:",
        "if size != expected_size:",
        "if parts_glob != \"part-*.b64\":",
        "for index in range(part_count):",
        "shard_path = parts_dir / f\"part-{index:03d}.b64\"",
        "missing expected shard",
        "base64.b64decode(encoded, validate=True)",
        "invalid base64 shard",
    };
    for (markers) |marker| {
        try expectContains(stage_helper, marker);
    }

    try expectOrder(stage_helper, "filename = require_manifest_string", "if filename != expected_filename:");
    try expectOrder(stage_helper, "encoding = require_manifest_string", "if encoding != \"base64\":");
    try expectOrder(stage_helper, "sha256 = require_manifest_string", "if sha256 != expected_sha:");
    try expectOrder(stage_helper, "size = require_manifest_int", "if size != expected_size:");
    try expectOrder(stage_helper, "parts_glob = require_manifest_string", "if parts_glob != \"part-*.b64\":");
    try expectOrder(stage_helper, "shard_path = parts_dir / f\"part-{index:03d}.b64\"", "base64.b64decode(encoded, validate=True)");
    try expectOrder(stage_helper, "base64.b64decode(encoded, validate=True)", "handle.write(chunk)");
    try expectOrder(stage_helper, "handle.write(chunk)", "return validate_source_archive(");
}

fn expectPartsCliAndSelfTestSurface(stage_helper: []const u8) !void {
    const output_markers = [_][]const u8{
        "STAGE_PINNED_ZIG_ARCHIVE=fail",
        "STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}",
        "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}",
        "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256={metadata['sha256']}",
        "STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256={actual_sha}",
        "STAGE_PINNED_ZIG_ARCHIVE_STATUS={status}",
        "input_mode == \"parts_dir\"",
        "exactly one of --source or --parts-dir is required unless --self-test is used",
    };
    for (output_markers) |marker| {
        try expectContains(stage_helper, marker);
    }

    const self_test_failures = [_][]const u8{
        "missing shard manifest",
        "expected shard manifest filename",
        "missing expected shard",
        "invalid base64 shard",
    };
    for (self_test_failures) |failure| {
        try expectContains(stage_helper, failure);
    }

    try expectContainsOnce(stage_helper, "expected_substring=\"missing shard manifest\"");
    try expectContainsOnce(stage_helper, "expected_substring=\"expected shard manifest filename\"");
    try expectContainsOnce(stage_helper, "expected_substring=\"missing expected shard\"");
    try expectContainsOnce(stage_helper, "expected_substring=\"invalid base64 shard\"");
}

test "lane05 stage helper keeps .parts manifest failures fail closed" {
    const stage_helper = try readRepoFile(std.testing.allocator, stage_helper_path);
    defer std.testing.allocator.free(stage_helper);

    try expectPartsManifestFailureSurface(stage_helper);
}

test "lane05 stage helper self-test covers incomplete and corrupt parts packets" {
    const stage_helper = try readRepoFile(std.testing.allocator, stage_helper_path);
    defer std.testing.allocator.free(stage_helper);

    try expectPartsCliAndSelfTestSurface(stage_helper);
}
