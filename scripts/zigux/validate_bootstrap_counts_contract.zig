const std = @import("std");

const validate_bootstrap_source = @embedFile("validate-bootstrap.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "successful bootstrap validation emits stable pass and count keys" {
    try expectContains(validate_bootstrap_source, "print(\"BOOTSTRAP_VALIDATION=pass\")");
    try expectContains(validate_bootstrap_source, "print(f\"BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}\")");
    try expectContains(validate_bootstrap_source, "print(f\"BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}\")");
    try expectOrdered(
        validate_bootstrap_source,
        "print(\"BOOTSTRAP_VALIDATION=pass\")",
        "print(f\"BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}\")",
    );
    try expectOrdered(
        validate_bootstrap_source,
        "print(f\"BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}\")",
        "print(f\"BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}\")",
    );
}

test "failure output stays grouped by issue code" {
    try expectContains(validate_bootstrap_source, "print(\"BOOTSTRAP_VALIDATION=fail\")");
    try expectContains(validate_bootstrap_source, "print(f\"{code}_START\")");
    try expectContains(validate_bootstrap_source, "print(f\"{code}_END\")");
    try expectContains(validate_bootstrap_source, "grouped.setdefault(code, []).append(value)");
    try expectContains(validate_bootstrap_source, "return emit_issues(issues)");
}

test "self-test protects pass output and duplicate workflow count behavior" {
    try expectContains(validate_bootstrap_source, "print(\"BOOTSTRAP_VALIDATION_SELF_TEST=pass\")");
    try expectContains(validate_bootstrap_source, "print(f\"BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT={checks}\")");
    try expectContains(validate_bootstrap_source, "(\"DUPLICATE_WORKFLOW_LINE\",");
    try expectContains(validate_bootstrap_source, "f\"{REQUIRED_WORKFLOW_LINES[2]}:count=2\"");
    try expectContains(validate_bootstrap_source, "f\"{REQUIRED_WORKFLOW_LINES[-1]}:count=2\"");
}
