const std = @import("std");

const artifact_diff_path = "scripts/zigux/artifact_diff.py";

fn readArtifactDiff(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, artifact_diff_path, allocator, .limited(1024 * 1024));
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(contains(haystack, needle));
}

fn expectOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn hasLiveCanonicalJsonSurface(source: []const u8) bool {
    return contains(source, "def canonical_json_bytes(path: Path, *, side: str) -> tuple[bytes | None, str | None]:") and
        contains(source, "json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)") and
        contains(source, "def compare_json(expected: Path, actual: Path) -> ComparisonResult:");
}

test "artifact diff canonical json serialization stays stable" {
    const source = try readArtifactDiff(std.testing.allocator);
    defer std.testing.allocator.free(source);

    if (!hasLiveCanonicalJsonSurface(source)) return error.SkipZigTest;

    try expectContains(source, "json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + \"\\n\"");
    try expectContains(source, ".encode(\"utf-8\"), None");
    try expectOrder(
        source,
        "value = json.loads(text)",
        "json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + \"\\n\"",
    );
}

test "artifact diff json comparison canonicalizes expected before actual" {
    const source = try readArtifactDiff(std.testing.allocator);
    defer std.testing.allocator.free(source);

    if (!hasLiveCanonicalJsonSurface(source)) return error.SkipZigTest;

    try expectOrder(source, "expected_bytes, expected_error = canonical_json_bytes(expected, side=\"EXPECTED\")", "actual_bytes, actual_error = canonical_json_bytes(actual, side=\"ACTUAL\")");
    try expectOrder(source, "if expected_error is not None:", "actual_bytes, actual_error = canonical_json_bytes(actual, side=\"ACTUAL\")");
    try expectOrder(source, "if actual_error is not None:", "if expected_bytes == actual_bytes:");
    try expectContains(source, "return ComparisonResult(ok=True, extra_lines=[])");
    try expectContains(source, "return ComparisonResult(ok=False, extra_lines=[])");
}

test "artifact diff self test proves reordered json pass and mismatch" {
    const source = try readArtifactDiff(std.testing.allocator);
    defer std.testing.allocator.free(source);

    if (!hasLiveCanonicalJsonSurface(source)) return error.SkipZigTest;

    try expectContains(source, "\"json_pass\"");
    try expectContains(source, "\"json_mismatch\"");
    try expectOrder(
        source,
        "actual_json.write_text('{\\n \"beta\": [2, 3],\\n \"alpha\": 1\\n}\\n'",
        "assert_case(compare(\"json\", expected_json, actual_json).ok, \"json_pass\")",
    );
    try expectOrder(
        source,
        "actual_json_mismatch.write_text('{\"alpha\": 1, \"beta\": [2, 4]}\\n'",
        "assert_case(not compare(\"json\", expected_json, actual_json_mismatch).ok, \"json_mismatch\")",
    );
    try expectContains(source, "assert_case(covered == SELF_TEST_CASES, \"self_test_case_order\")");
}
