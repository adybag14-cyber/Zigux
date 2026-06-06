const std = @import("std");
const Io = std.Io;

const artifact_diff_path = "scripts/zigux/artifact_diff.py";

fn artifactDiffSource() ![]u8 {
    return Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        artifact_diff_path,
        std.testing.allocator,
        .limited(256 * 1024),
    );
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn requireLiveUtf8Surface(source: []const u8) !void {
    if (!contains(source, "def format_utf8_error(path: Path, *, side: str, exc: UnicodeDecodeError) -> str:")) {
        return error.SkipZigTest;
    }
}

fn expectContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn expectBefore(source: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, source, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, source, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "artifact diff UTF-8 diagnostics preserve side offset and reason" {
    const source = try artifactDiffSource();
    defer std.testing.allocator.free(source);
    try requireLiveUtf8Surface(source);

    try expectContains(
        source,
        "def format_utf8_error(path: Path, *, side: str, exc: UnicodeDecodeError) -> str:",
    );
    try expectContains(
        source,
        "return f\"{side}_UTF8_ERROR={path}:{exc.start}: {exc.reason}\"",
    );
    try expectContains(source, "except UnicodeDecodeError as exc:");
    try expectContains(source, "return None, format_utf8_error(path, side=side, exc=exc)");
    try expectBefore(
        source,
        "except UnicodeDecodeError as exc:",
        "try:\n        value = json.loads(text)",
    );
}

test "artifact diff JSON comparison checks expected UTF-8 before actual side" {
    const source = try artifactDiffSource();
    defer std.testing.allocator.free(source);
    try requireLiveUtf8Surface(source);

    try expectBefore(
        source,
        "expected_bytes, expected_error = canonical_json_bytes(expected, side=\"EXPECTED\")",
        "actual_bytes, actual_error = canonical_json_bytes(actual, side=\"ACTUAL\")",
    );
    try expectBefore(
        source,
        "if expected_error is not None:\n        return ComparisonResult(ok=False, extra_lines=[expected_error])",
        "if actual_error is not None:\n        return ComparisonResult(ok=False, extra_lines=[actual_error])",
    );
    try expectContains(
        source,
        "compare(\"json\", invalid_expected_utf8_json, invalid_actual_utf8_json).extra_lines",
    );
    try expectContains(
        source,
        "[f\"EXPECTED_UTF8_ERROR={invalid_expected_utf8_json}:0: invalid start byte\"]",
    );
}

test "artifact diff self-test owns expected and actual UTF-8 cases" {
    const source = try artifactDiffSource();
    defer std.testing.allocator.free(source);
    try requireLiveUtf8Surface(source);

    try expectContains(source, "invalid_expected_utf8_json.write_bytes(b\"\\xff{\\n\")");
    try expectContains(source, "invalid_actual_utf8_json.write_bytes(b\"\\xff{\\n\")");
    try expectBefore(source, "\"json_invalid_expected\",", "covered.append(\"json_invalid_expected\")");
    try expectBefore(source, "\"json_invalid_actual\",", "covered.append(\"json_invalid_actual\")");
    try expectContains(
        source,
        "compare(\"json\", expected_json, invalid_actual_utf8_json).extra_lines",
    );
    try expectContains(
        source,
        "[f\"ACTUAL_UTF8_ERROR={invalid_actual_utf8_json}:0: invalid start byte\"]",
    );
    try expectContains(source, "\"json_invalid_both\"");
}
