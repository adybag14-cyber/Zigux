const std = @import("std");

const validator_path = "scripts/zigux/validate_bootstrap.zig";

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

    try requireContains(validator, "fn countExactLines(text: []const u8, marker: []const u8) usize");
    try requireContains(validator, "inline for (REQUIRED_WORKFLOW_LINES) |marker|");
    try requireContains(validator, "const count = countExactLines(workflow, marker)");
    try requireContains(validator, "} else if (count != 1) {");
    try requireContains(validator, ".code = \"DUPLICATE_WORKFLOW_LINE\"");
    try requireContains(validator, "{s}:count={d}");

    try requireOrdered(
        validator,
        "const count = countExactLines(workflow, marker)",
        ".code = \"DUPLICATE_WORKFLOW_LINE\"",
    );
}

test "self-test still proves stable bootstrap validation markers" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try requireContains(validator, "BOOTSTRAP_VALIDATION_SELF_TEST=pass");
    try requireContains(validator, "BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT=1");
    try requireContains(validator, "DUPLICATE_WORKFLOW_LINE");
}

test "required workflow count remains surfaced in normal validator output" {
    const validator = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(validator);

    try requireContains(validator, "live_pass_marker = \"BOOTSTRAP_VALIDATION=pass\"");
    try requireContains(validator, "BOOTSTRAP_REQUIRED_PATH_COUNT={d}");
    try requireContains(validator, "BOOTSTRAP_WORKFLOW_LINE_COUNT={d}");
    try requireContains(validator, "run: zig run scripts/zigux/check_zig_toolchain.zig -- --archive-only --allow-missing");
    try requireContains(validator, "run: zig run scripts/zigux/validate_bootstrap.zig");
}