const std = @import("std");

const phase6_validate_line = "run: make -C zigux phase6-validate";
const phase6_build_line = "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all";
const validator_self_test_line = "run: python3 scripts/zigux/validate-bootstrap.py --self-test";
const validator_run_line = "run: python3 scripts/zigux/validate-bootstrap.py";

fn readValidatorSource(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        "scripts/zigux/validate-bootstrap.py",
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before);
    const after_index = std.mem.indexOf(u8, haystack, after);

    try std.testing.expect(before_index != null);
    try std.testing.expect(after_index != null);
    try std.testing.expect(before_index.? < after_index.?);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

test "validate-bootstrap keeps phase6 tail lines in required workflow roster" {
    const allocator = std.testing.allocator;
    const source = try readValidatorSource(allocator);
    defer allocator.free(source);

    try requireContains(source, "REQUIRED_WORKFLOW_LINES = (");
    try requireContains(source, phase6_validate_line);
    try requireContains(source, phase6_build_line);
    try requireOrder(source, phase6_validate_line, phase6_build_line);
    try requireOrder(source, phase6_build_line, validator_self_test_line);
    try requireContains(source, validator_run_line);
}

test "phase6 workflow tail remains outside required path inventory" {
    const allocator = std.testing.allocator;
    const source = try readValidatorSource(allocator);
    defer allocator.free(source);

    try requireContains(source, "REQUIRED_PATHS = (");
    try requireContains(source, "\"zigux/tests/README.md\",");
    try requireContains(source, "WORKFLOW,");
    try requireNotContains(source, "\"zigux/tests/phase6_build.zig\",");
    try requireNotContains(source, "\"scripts/zigux/validate-phase6.py\",");
}

test "self-test fixture seeds workflow from the validator roster" {
    const allocator = std.testing.allocator;
    const source = try readValidatorSource(allocator);
    defer allocator.free(source);

    try requireContains(
        source,
        "write_text(root, WORKFLOW, \"\\n\".join((\"name: zigux-bootstrap\", *REQUIRED_WORKFLOW_LINES)) + \"\\n\")",
    );
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(source, phase6_validate_line));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(source, phase6_build_line));
}

test "pass output reports required path and workflow roster counts dynamically" {
    const allocator = std.testing.allocator;
    const source = try readValidatorSource(allocator);
    defer allocator.free(source);

    try requireContains(source, "BOOTSTRAP_VALIDATION=pass");
    try requireContains(source, "BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}");
    try requireContains(source, "BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}");
}
