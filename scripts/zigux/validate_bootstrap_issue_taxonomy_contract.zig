const std = @import("std");

const validator_path = "scripts/zigux/validate-bootstrap.py";

const issue_codes = [_][]const u8{
    "MISSING_REQUIRED_PATH",
    "MISSING_README_MARKER",
    "MISSING_ROADMAP_MARKER",
    "MISSING_LEDGER_MARKER",
    "MISSING_DOCS_README_MARKER",
    "MISSING_FREEZE_MAP_MARKER",
    "MISSING_SCRIPTS_README_MARKER",
    "MISSING_WORKFLOW_LINE",
    "DUPLICATE_WORKFLOW_LINE",
};

fn readValidator(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, validator_path, allocator, .limited(256 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

test "bootstrap validator exposes the full issue code taxonomy" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    for (issue_codes) |code| {
        try expectContains(validator, code);
        const append_marker = try std.fmt.allocPrint(std.testing.allocator, "issues.append((\"{s}\"", .{code});
        defer std.testing.allocator.free(append_marker);
        try expectContains(validator, append_marker);
    }

    try expectContains(validator, "elif count != 1:");
    try expectContains(validator, "DUPLICATE_WORKFLOW_LINE");
    try expectOrdered(
        validator,
        "if count == 0:",
        "elif count != 1:",
    );
}

test "failure output keeps grouped start and end envelopes" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "def emit_issues(issues: list[tuple[str, str]]) -> int:");
    try expectContains(validator, "grouped.setdefault(code, []).append(value)");
    try expectContains(validator, "print(\"BOOTSTRAP_VALIDATION=fail\")");
    try expectContains(validator, "print(f\"{code}_START\")");
    try expectContains(validator, "print(f\"{code}_END\")");

    try expectOrdered(validator, "print(\"BOOTSTRAP_VALIDATION=fail\")", "print(f\"{code}_START\")");
    try expectOrdered(validator, "print(f\"{code}_START\")", "print(f\"{code}_END\")");
}

test "self test keeps missing and duplicate workflow diagnostics explicit" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try std.testing.expect(countOccurrences(validator, "\"MISSING_WORKFLOW_LINE\"") >= 2);
    try std.testing.expect(countOccurrences(validator, "\"DUPLICATE_WORKFLOW_LINE\"") >= 2);
    try expectContains(validator, "duplicate_exact_line(");
    try expectContains(validator, "replace_exact_line(");
    try expectContains(validator, "REQUIRED_WORKFLOW_LINES[2]");
    try expectContains(validator, "REQUIRED_WORKFLOW_LINES[-1]");
}

test "pass and self test count outputs stay machine readable" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "BOOTSTRAP_VALIDATION_SELF_TEST=pass");
    try expectContains(validator, "BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT=");
    try expectContains(validator, "BOOTSTRAP_VALIDATION=pass");
    try expectContains(validator, "BOOTSTRAP_REQUIRED_PATH_COUNT=");
    try expectContains(validator, "BOOTSTRAP_WORKFLOW_LINE_COUNT=");
    try expectContains(validator, "return emit_issues(issues)");
}
