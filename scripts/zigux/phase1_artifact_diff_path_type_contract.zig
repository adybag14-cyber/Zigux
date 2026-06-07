const std = @import("std");

const source = @embedFile("artifact_diff.py");

fn requireMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn requireSingleMarker(marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, source, marker));
}

fn requireOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "artifact diff keeps non-file diagnostics separate from missing paths" {
    try requireSingleMarker("def path_problem_lines(expected: Path, actual: Path) -> list[str] | None:");
    try requireMarker("expected_exists = expected.exists()");
    try requireMarker("actual_exists = actual.exists()");
    try requireMarker("if not expected_exists or not actual_exists:");
    try requireMarker("EXPECTED_EXISTS={expected_exists}");
    try requireMarker("ACTUAL_EXISTS={actual_exists}");
    try requireMarker("expected_is_file = expected.is_file()");
    try requireMarker("actual_is_file = actual.is_file()");
    try requireMarker("EXPECTED_IS_FILE={expected_is_file}");
    try requireMarker("ACTUAL_IS_FILE={actual_is_file}");
    try requireOrder("if not expected_exists or not actual_exists:", "expected_is_file = expected.is_file()");
}

test "artifact diff refuses directories before mode-specific comparisons" {
    try requireMarker("if expected_is_file and actual_is_file:");
    try requireMarker("return None");
    try requireMarker("problem = path_problem_lines(expected, actual)");
    try requireMarker("if problem is not None:");
    try requireMarker("return ComparisonResult(ok=False, extra_lines=problem)");
    try requireOrder("problem = path_problem_lines(expected, actual)", "if mode == \"text\":");
    try requireOrder("problem = path_problem_lines(expected, actual)", "if mode == \"json\":");
    try requireOrder("problem = path_problem_lines(expected, actual)", "if mode == \"bytes\":");
}

test "artifact diff self-test roster still covers missing path cases only" {
    try requireMarker("\"text_missing_expected\"");
    try requireMarker("\"text_missing_actual\"");
    try requireMarker("\"text_missing_both\"");
    try requireMarker("\"json_missing_expected\"");
    try requireMarker("\"json_missing_actual\"");
    try requireMarker("\"json_missing_both\"");
    try requireMarker("\"bytes_missing_expected\"");
    try requireMarker("\"bytes_missing_actual\"");
    try requireMarker("\"bytes_missing_both\"");
    try std.testing.expect(std.mem.indexOf(u8, source, "is_file") != null);
    try std.testing.expect(std.mem.indexOf(u8, source, "directory") == null);
}
