const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

const missing_case_names = [_][]const u8{
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectEitherContains(haystack: []const u8, first: []const u8, second: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, first) != null) return;
    try expectContains(haystack, second);
}

fn indexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    };
}

fn indexOfEitherRequired(haystack: []const u8, first: []const u8, second: []const u8) !usize {
    if (std.mem.indexOf(u8, haystack, first)) |index| return index;
    return indexOfRequired(haystack, second);
}

test "missing path output keeps stable expected and actual existence markers" {
    try expectContains(artifact_diff_source, "EXPECTED_EXISTS=");
    try expectContains(artifact_diff_source, "ACTUAL_EXISTS=");
    try expectContains(artifact_diff_source, "EXPECTED_EXISTS=False");
    try expectContains(artifact_diff_source, "ACTUAL_EXISTS=True");
    try expectContains(artifact_diff_source, "EXPECTED_EXISTS=True");
    try expectContains(artifact_diff_source, "ACTUAL_EXISTS=False");
    try expectContains(artifact_diff_source, "EXPECTED_EXISTS=False");
    try expectContains(artifact_diff_source, "ACTUAL_EXISTS=False");
}

test "missing path self-test cases cover text json and digest modes" {
    for (missing_case_names) |case_name| {
        try expectContains(artifact_diff_source, case_name);
    }

    try expectEitherContains(
        artifact_diff_source,
        "bytes_missing_expected",
        "sha256_missing_expected",
    );
    try expectEitherContains(
        artifact_diff_source,
        "bytes_missing_actual",
        "sha256_missing_actual",
    );
    try expectEitherContains(
        artifact_diff_source,
        "bytes_missing_both",
        "sha256_missing_both",
    );
}

test "missing path guard runs before mode-specific artifact reads" {
    const missing_gate = if (std.mem.indexOf(u8, artifact_diff_source, "path_problem_lines(expected, actual)")) |index|
        index
    else
        try indexOfRequired(artifact_diff_source, "if not expected.exists() or not actual.exists():");

    const text_read = try indexOfEitherRequired(
        artifact_diff_source,
        "if mode == \"text\":",
        "if mode == 'text':",
    );
    const json_read = try indexOfEitherRequired(
        artifact_diff_source,
        "if mode == \"json\":",
        "if mode == 'json':",
    );
    const digest_read = if (std.mem.indexOf(u8, artifact_diff_source, "if mode == \"bytes\":")) |index|
        index
    else
        try indexOfRequired(artifact_diff_source, "elif mode == 'sha256':");

    try std.testing.expect(missing_gate < text_read);
    try std.testing.expect(missing_gate < json_read);
    try std.testing.expect(missing_gate < digest_read);
}
