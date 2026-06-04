const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

const json_case_names = [_][]const u8{
    "json_pass",
    "json_mismatch",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
};

const current_json_surface = [_][]const u8{
    "def canonical_json_bytes(path: Path, *, side: str)",
    "json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)",
    "format_utf8_error(path, side=side, exc=exc)",
    "EXPECTED_JSON_ERROR=",
    "ACTUAL_JSON_ERROR=",
    "EXPECTED_UTF8_ERROR=",
    "ACTUAL_UTF8_ERROR=",
};

const legacy_json_surface = [_][]const u8{
    "def canonical_json(path: Path)",
    "return json.loads(read_text(path))",
    "details['expected_json_error']",
    "details['actual_json_error']",
    "EXPECTED_JSON_ERROR=",
    "ACTUAL_JSON_ERROR=",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try expectContains(haystack, needle);
    }
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOf(u8, haystack[index..], needle)) |offset| {
        count += 1;
        index += offset + needle.len;
    }
    return count;
}

fn quotedCount(haystack: []const u8, name: []const u8) usize {
    var single_buffer: [128]u8 = undefined;
    var double_buffer: [128]u8 = undefined;
    const single = std.fmt.bufPrint(&single_buffer, "'{s}'", .{name}) catch unreachable;
    const double = std.fmt.bufPrint(&double_buffer, "\"{s}\"", .{name}) catch unreachable;
    return countOccurrences(haystack, single) + countOccurrences(haystack, double);
}

fn expectQuotedName(haystack: []const u8, name: []const u8) !void {
    try std.testing.expect(quotedCount(haystack, name) > 0);
}

test "artifact diff keeps json self-test catalog explicit" {
    try expectContains(artifact_diff_source, "SELF_TEST_CASES");
    try expectContains(artifact_diff_source, "run_self_test");
    for (json_case_names) |name| {
        try expectQuotedName(artifact_diff_source, name);
    }

    try expectContains(artifact_diff_source, "covered");
    try expectContains(artifact_diff_source, "ARTIFACT_DIFF_SELF_TEST_CASES=");
}

test "artifact diff preserves json canonicalization and error reporting surface" {
    const has_current_surface =
        std.mem.indexOf(u8, artifact_diff_source, current_json_surface[0]) != null;
    const has_legacy_surface =
        std.mem.indexOf(u8, artifact_diff_source, legacy_json_surface[0]) != null;

    try std.testing.expect(has_current_surface or has_legacy_surface);
    try expectContains(artifact_diff_source, "json.JSONDecodeError");
    try std.testing.expect(
        std.mem.indexOf(u8, artifact_diff_source, "mode == \"json\"") != null or
            std.mem.indexOf(u8, artifact_diff_source, "mode == 'json'") != null,
    );

    if (has_current_surface) {
        try expectContainsAll(artifact_diff_source, &current_json_surface);
    } else {
        try expectContainsAll(artifact_diff_source, &legacy_json_surface);
    }
}

test "artifact diff json mode stays separate from text and byte digest modes" {
    try std.testing.expect(
        std.mem.indexOf(u8, artifact_diff_source, "mode == \"text\"") != null or
            std.mem.indexOf(u8, artifact_diff_source, "mode == 'text'") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, artifact_diff_source, "mode == \"json\"") != null or
            std.mem.indexOf(u8, artifact_diff_source, "mode == 'json'") != null,
    );

    const has_current_bytes_mode =
        std.mem.indexOf(u8, artifact_diff_source, "mode == \"bytes\"") != null and
        std.mem.indexOf(u8, artifact_diff_source, "LEGACY_MODE_ALIASES") != null;
    const has_legacy_sha256_mode =
        std.mem.indexOf(u8, artifact_diff_source, "mode == \"sha256\"") != null or
        std.mem.indexOf(u8, artifact_diff_source, "mode == 'sha256'") != null;

    try std.testing.expect(has_current_bytes_mode or has_legacy_sha256_mode);
}
