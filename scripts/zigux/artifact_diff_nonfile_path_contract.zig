const std = @import("std");

const artifact_diff_text = @embedFile("artifact_diff.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstNeedle;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondNeedle;
    try std.testing.expect(first_index < second_index);
}

test "artifact diff checks path existence before non-file classification" {
    try expectBefore(
        artifact_diff_text,
        \\    expected_exists = expected.exists()
    ,
        \\    expected_is_file = expected.is_file()
        ,
    );
    try expectBefore(
        artifact_diff_text,
        \\    actual_exists = actual.exists()
    ,
        \\    actual_is_file = actual.is_file()
        ,
    );
    try expectBefore(
        artifact_diff_text,
        \\        f"EXPECTED_EXISTS={expected_exists}",
    ,
        \\        f"EXPECTED_IS_FILE={expected_is_file}",
        ,
    );
    try expectBefore(
        artifact_diff_text,
        \\        f"ACTUAL_EXISTS={actual_exists}",
    ,
        \\        f"ACTUAL_IS_FILE={actual_is_file}",
        ,
    );
}

test "artifact diff preserves non-file diagnostic labels" {
    try expectContains(artifact_diff_text, "f\"EXPECTED_IS_FILE={expected_is_file}\"");
    try expectContains(artifact_diff_text, "f\"ACTUAL_IS_FILE={actual_is_file}\"");
    try expectContains(artifact_diff_text, "if expected_is_file and actual_is_file:");
    try expectContains(artifact_diff_text, "return None");
}

test "artifact diff applies path gate before mode-specific comparison" {
    try expectBefore(
        artifact_diff_text,
        \\    problem = path_problem_lines(expected, actual)
    ,
        \\    if mode == "text":
        ,
    );
    try expectBefore(
        artifact_diff_text,
        \\    problem = path_problem_lines(expected, actual)
    ,
        \\    if mode == "json":
        ,
    );
    try expectBefore(
        artifact_diff_text,
        \\    problem = path_problem_lines(expected, actual)
    ,
        \\    if mode == "bytes":
        ,
    );
}
