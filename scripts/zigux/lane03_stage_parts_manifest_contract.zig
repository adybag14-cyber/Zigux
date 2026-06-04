const std = @import("std");

const helper_source = @embedFile("stage-pinned-zig-archive.py");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    }
}

fn requireOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse {
        std.debug.print("missing ordered marker: {s}\n", .{before});
        return error.MissingMarker;
    };
    const after_index = std.mem.indexOf(u8, haystack, after) orelse {
        std.debug.print("missing ordered marker: {s}\n", .{after});
        return error.MissingMarker;
    };
    try std.testing.expect(before_index < after_index);
}

fn countContains(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "stage helper keeps parts-dir CLI and input-mode boundary" {
    try requireContains(helper_source, "parser.add_argument(\n        \"--parts-dir\",");
    try requireContains(helper_source, "exactly one of --source or --parts-dir is required unless --self-test is used");
    try requireContains(helper_source, "if (source is None) == (parts_dir is None):");
    try requireContains(helper_source, "return reconstructed_source, \"parts_dir\", temp_dir");
    try requireContains(helper_source, "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=");
    try requireContains(helper_source, "STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=");
    try requireOrder(
        helper_source,
        "parts_dir = args.parts_dir.resolve() if args.parts_dir is not None else None",
        "metadata, status, actual_sha, destination, input_mode = stage_archive(\n            root,\n            source,\n            parts_dir=parts_dir,",
    );
}

test "parts manifest schema remains strict and policy-bound" {
    const markers = [_][]const u8{
        "def load_shard_manifest(parts_dir: Path) -> dict[str, object]:",
        "manifest_path = parts_dir / \"manifest.json\"",
        "missing shard manifest",
        "invalid shard manifest JSON",
        "invalid shard manifest payload",
        "def require_manifest_string(manifest: dict[str, object], key: str, manifest_path: Path) -> str:",
        "def require_manifest_int(manifest: dict[str, object], key: str, manifest_path: Path) -> int:",
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
    };

    for (markers) |marker| {
        try requireContains(helper_source, marker);
    }
}

test "parts reconstruction reads ordered shards and validates final archive" {
    try requireContains(helper_source, "def reconstruct_archive_from_parts(");
    try requireContains(helper_source, "for index in range(part_count):");
    try requireContains(helper_source, "shard_path = parts_dir / f\"part-{index:03d}.b64\"");
    try requireContains(helper_source, "missing expected shard");
    try requireContains(helper_source, "base64.b64decode(encoded, validate=True)");
    try requireContains(helper_source, "invalid base64 shard");
    try requireContains(helper_source, "handle.write(chunk)");
    try requireContains(helper_source, "return validate_source_archive(");
    try requireContains(helper_source, "expected_size=expected_size,");
    try requireContains(helper_source, "expected_sha=expected_sha,");
    try requireOrder(
        helper_source,
        "manifest = load_shard_manifest(parts_dir)",
        "destination.parent.mkdir(parents=True, exist_ok=True)\n    with destination.open(\"wb\") as handle:",
    );
    try requireOrder(helper_source, "for index in range(part_count):", "return validate_source_archive(");
    try std.testing.expectEqual(@as(usize, 1), countContains(helper_source, "for index in range(part_count):"));
}

test "self-test fixtures exercise successful and failing parts packets" {
    const markers = [_][]const u8{
        "def write_parts_fixture(",
        "\"encoding\": \"base64\",",
        "\"parts_glob\": \"part-*.b64\",",
        "(parts_dir / \"manifest.json\").write_text(json.dumps(manifest, indent=2) + \"\\n\", encoding=\"utf-8\")",
        "(parts_dir / f\"part-{index:03d}.b64\").write_text(",
        "use_parts_dir=True",
        "expected_substring=\"missing shard manifest\"",
        "expected_substring=\"expected shard manifest filename\"",
        "expected_substring=\"missing expected shard\"",
        "expected_substring=\"invalid base64 shard\"",
        "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
        "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=",
    };

    for (markers) |marker| {
        try requireContains(helper_source, marker);
    }
    try requireOrder(helper_source, "write_parts_fixture(", "stage_archive(\n            root,\n            None,\n            parts_dir=parts_dir,");
}
