const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn has(needle: []const u8) bool {
    return std.mem.indexOf(u8, artifact_diff_source, needle) != null;
}

fn requireMarker(needle: []const u8) !void {
    try std.testing.expect(has(needle));
}

fn requireOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, artifact_diff_source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, artifact_diff_source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn requireCount(needle: []const u8, expected: usize) !void {
    var index: usize = 0;
    var count: usize = 0;
    while (std.mem.indexOfPos(u8, artifact_diff_source, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

test "path preflight separates missing paths from file-type problems" {
    try requireMarker("def path_problem_lines(expected: Path, actual: Path) -> list[str] | None:");
    try requireMarker("expected_exists = expected.exists()");
    try requireMarker("actual_exists = actual.exists()");
    try requireMarker("if not expected_exists or not actual_exists:");
    try requireMarker("f\"EXPECTED_EXISTS={expected_exists}\"");
    try requireMarker("f\"ACTUAL_EXISTS={actual_exists}\"");
    try requireMarker("expected_is_file = expected.is_file()");
    try requireMarker("actual_is_file = actual.is_file()");
    try requireMarker("if expected_is_file and actual_is_file:");
    try requireMarker("return None");
    try requireMarker("f\"EXPECTED_IS_FILE={expected_is_file}\"");
    try requireMarker("f\"ACTUAL_IS_FILE={actual_is_file}\"");

    try requireOrder("if not expected_exists or not actual_exists:", "expected_is_file = expected.is_file()");
    try requireOrder("actual_is_file = actual.is_file()", "if expected_is_file and actual_is_file:");
    try requireOrder("if expected_is_file and actual_is_file:", "f\"EXPECTED_IS_FILE={expected_is_file}\"");
}

test "compare dispatch runs file preflight before mode-specific comparison" {
    try requireMarker("def compare(mode: str, expected: Path, actual: Path) -> ComparisonResult:");
    try requireMarker("mode = normalize_mode(mode)");
    try requireMarker("problem = path_problem_lines(expected, actual)");
    try requireMarker("if problem is not None:");
    try requireMarker("return ComparisonResult(ok=False, extra_lines=problem)");
    try requireMarker("if mode == \"text\":");
    try requireMarker("return compare_text(expected, actual)");
    try requireMarker("if mode == \"json\":");
    try requireMarker("return compare_json(expected, actual)");
    try requireMarker("if mode == \"bytes\":");
    try requireMarker("return compare_bytes(expected, actual)");

    try requireOrder("problem = path_problem_lines(expected, actual)", "if mode == \"text\":");
    try requireOrder("return ComparisonResult(ok=False, extra_lines=problem)", "return compare_text(expected, actual)");
    try requireOrder("return ComparisonResult(ok=False, extra_lines=problem)", "return compare_json(expected, actual)");
    try requireOrder("return ComparisonResult(ok=False, extra_lines=problem)", "return compare_bytes(expected, actual)");
}

test "self-test keeps missing-path coverage across all modes while file-type branch stays distinct" {
    try requireCount("EXPECTED_EXISTS=False", 6);
    try requireCount("ACTUAL_EXISTS=False", 6);
    try requireMarker("\"json_missing_expected\"");
    try requireMarker("\"json_missing_actual\"");
    try requireMarker("\"json_missing_both\"");
    try requireMarker("\"text_missing_expected\"");
    try requireMarker("\"text_missing_actual\"");
    try requireMarker("\"text_missing_both\"");
    try requireMarker("\"bytes_missing_expected\"");
    try requireMarker("\"bytes_missing_actual\"");
    try requireMarker("\"bytes_missing_both\"");

    try requireMarker("EXPECTED_IS_FILE");
    try requireMarker("ACTUAL_IS_FILE");
}
