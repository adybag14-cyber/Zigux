const std = @import("std");
const testing = std.testing;

const artifact_diff_source = @embedFile("artifact_diff.py");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

fn requireExactCount(haystack: []const u8, needle: []const u8, expected_count: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |relative_index| {
        count += 1;
        offset += relative_index + needle.len;
    }
    try testing.expectEqual(expected_count, count);
}

fn requireContainsAfter(haystack: []const u8, anchor: []const u8, needle: []const u8) !void {
    const anchor_index = std.mem.indexOf(u8, haystack, anchor) orelse return error.MissingAnchorMarker;
    const needle_index = std.mem.indexOf(u8, haystack[anchor_index..], needle) orelse return error.MissingNeedleMarker;
    try testing.expect(needle_index > 0);
}

test "json diagnostics keep utf8 decode ahead of json parsing" {
    try requireContains(
        artifact_diff_source,
        "def format_utf8_error(path: Path, *, side: str, exc: UnicodeDecodeError) -> str:",
    );
    try requireContains(
        artifact_diff_source,
        "return f\"{side}_UTF8_ERROR={path}:{exc.start}: {exc.reason}\"",
    );
    try requireOrder(
        artifact_diff_source,
        "except UnicodeDecodeError as exc:\n        return None, format_utf8_error(path, side=side, exc=exc)",
        "except json.JSONDecodeError as exc:\n        return None, f\"{side}_JSON_ERROR={path}:{exc.lineno}:{exc.colno}: {exc.msg}\"",
    );
}

test "json self-test pins expected and actual diagnostic labels" {
    try requireContains(
        artifact_diff_source,
        "== [f\"EXPECTED_JSON_ERROR={invalid_expected_json}:2:1: Expecting property name enclosed in double quotes\"]",
    );
    try requireContains(
        artifact_diff_source,
        "== [f\"EXPECTED_UTF8_ERROR={invalid_expected_utf8_json}:0: invalid start byte\"]",
    );
    try requireContains(
        artifact_diff_source,
        "== [f\"ACTUAL_JSON_ERROR={invalid_actual_json}:2:1: Expecting property name enclosed in double quotes\"]",
    );
    try requireContains(
        artifact_diff_source,
        "== [f\"ACTUAL_UTF8_ERROR={invalid_actual_utf8_json}:0: invalid start byte\"]",
    );
}

test "both-bad json cases stop at expected-side diagnostics" {
    try requireContainsAfter(
        artifact_diff_source,
        "compare(\"json\", invalid_expected_json, invalid_actual_json).extra_lines",
        "== [f\"EXPECTED_JSON_ERROR={invalid_expected_json}:2:1: Expecting property name enclosed in double quotes\"]",
    );
    try requireContainsAfter(
        artifact_diff_source,
        "compare(\"json\", invalid_expected_utf8_json, invalid_actual_utf8_json).extra_lines",
        "== [f\"EXPECTED_UTF8_ERROR={invalid_expected_utf8_json}:0: invalid start byte\"]",
    );
    try requireExactCount(artifact_diff_source, "\"json_invalid_both\"", 2);
}
