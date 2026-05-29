const std = @import("std");

const checker_path = "scripts/zigux/check-lane05-archive-parts-packet.py";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "archive-parts checker requires complete manifest schema" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "filename = require_string(manifest.get(\"filename\"), \"manifest filename\")");
    try expectContains(checker, "encoding = require_string(manifest.get(\"encoding\"), \"manifest encoding\")");
    try expectContains(checker, "sha256 = require_string(manifest.get(\"sha256\"), \"manifest sha256\")");
    try expectContains(checker, "size = require_positive_int(manifest.get(\"size\"), \"manifest size\")");
    try expectContains(checker, "chunk_bytes = require_positive_int(manifest.get(\"chunk_bytes\"), \"manifest chunk_bytes\")");
    try expectContains(checker, "part_count = require_positive_int(manifest.get(\"part_count\"), \"manifest part_count\")");
    try expectContains(checker, "parts_glob = require_string(manifest.get(\"parts_glob\"), \"manifest parts_glob\")");
}

test "archive-parts checker pins encoding and shard glob contract" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "if encoding != \"base64\":");
    try expectContains(checker, "packet encoding mismatch: expected base64, got {encoding}");
    try expectContains(checker, "if parts_glob != \"part-*.b64\":");
    try expectContains(checker, "packet parts_glob mismatch: expected part-*.b64, got {parts_glob}");
}

test "archive-parts checker derives part count from manifest size and chunk bytes" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "expected_part_count = (size + chunk_bytes - 1) // chunk_bytes");
    try expectContains(checker, "packet part_count mismatch: expected {expected_part_count}, got {part_count}");
    try expectContains(checker, "expected_names = {f\"part-{index:03d}.b64\" for index in range(part_count)}");
    try expectContains(checker, "actual_names = {path.name for path in parts_dir.glob(\"part-*.b64\")}");
}

test "verified packet status preserves manifest-driven details for CI logs" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "\"chunk_bytes\": chunk_bytes,");
    try expectContains(checker, "\"part_count\": part_count,");
    try expectContains(checker, "LANE05_ARCHIVE_PARTS_PACKET_CHUNK_BYTES={validated['chunk_bytes']}");
    try expectContains(checker, "LANE05_ARCHIVE_PARTS_PACKET_PART_COUNT={validated['part_count']}");
}
