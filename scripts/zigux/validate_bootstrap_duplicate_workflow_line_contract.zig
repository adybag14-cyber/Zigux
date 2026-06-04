const std = @import("std");

const validator_path = "scripts/zigux/validate-bootstrap.py";

fn readValidator(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, validator_path, allocator, .limited(256 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "duplicate workflow line collection remains fail closed" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try requireContains(validator, "def count_exact_lines(text: str, marker: str) -> int:");
    try requireContains(validator, "return sum(1 for line in text.splitlines() if line.strip() == marker)");
    try requireContains(validator, "for marker in REQUIRED_WORKFLOW_LINES:");
    try requireContains(validator, "count = count_exact_lines(workflow, marker)");
    try requireContains(validator, "elif count != 1:");
    try requireContains(validator, "issues.append((\"DUPLICATE_WORKFLOW_LINE\", f\"{marker}:count={count}\"))");

    try requireOrdered(
        validator,
        "count = count_exact_lines(workflow, marker)",
        "issues.append((\"DUPLICATE_WORKFLOW_LINE\", f\"{marker}:count={count}\"))",
    );
}

test "self-test still proves duplicate archive-only and final validator workflow lines" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try requireContains(validator, "duplicate_exact_line(");
    try requireContains(validator, "REQUIRED_WORKFLOW_LINES[2]");
    try requireContains(validator, "f\"{REQUIRED_WORKFLOW_LINES[2]}:count=2\"");
    try requireContains(validator, "REQUIRED_WORKFLOW_LINES[-1]");
    try requireContains(validator, "f\"{REQUIRED_WORKFLOW_LINES[-1]}:count=2\"");
    try requireContains(validator, "DUPLICATE_WORKFLOW_LINE");
    try requireContains(validator, "BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT={checks}");

    try requireOrdered(
        validator,
        "REQUIRED_WORKFLOW_LINES[2]",
        "REQUIRED_WORKFLOW_LINES[-1]",
    );
}

test "required workflow count remains surfaced in normal validator output" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try requireContains(validator, "print(\"BOOTSTRAP_VALIDATION=pass\")");
    try requireContains(validator, "BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}");
    try requireContains(validator, "BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}");
    try requireContains(validator, "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try requireContains(validator, "run: python3 scripts/zigux/validate-bootstrap.py");
}
