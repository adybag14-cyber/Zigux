const std = @import("std");

const validator_path = "scripts/zigux/validate-phase2-closure.py";

fn readValidator(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, validator_path, allocator, .limited(256 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "phase2 closure validator keeps pass status vocabulary stable" {
    const source = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "print(\"PHASE2_CLOSURE_VALIDATION=pass\")");
    try expectContains(source, "print(\"PHASE2_CLOSURE_STATUS=parked\")");
    try expectContains(source, "print(\"PHASE2_CLOSURE_PACKET=toolchain_cross_kconfig_genksyms_fixdep_closure\")");
    try expectContains(source, "print(\"PHASE2_CLOSURE_REMAINING_GAPS=\")");
}

test "phase2 closure validator fail output remains grouped by issue code" {
    const source = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "def emit_issues(issues: list[tuple[str, str]]) -> int:");
    try expectContains(source, "print(\"PHASE2_CLOSURE_VALIDATION=fail\")");
    try expectContains(source, "print(f\"{code}_START\")");
    try expectContains(source, "print(f\"{code}_END\")");
    try expectContains(source, "\"MISSING_CLOSURE_LINE\"");
    try expectContains(source, "\"MISSING_CLOSURE_MARKER\"");
    try expectContains(source, "\"MISSING_MANIFEST_SURFACE\"");
}

test "phase2 closure validator self-test advertises status and case count" {
    const source = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "parser.add_argument(\"--self-test\", action=\"store_true\"");
    try expectContains(source, "parser.add_argument(\"--root\", type=Path");
    try expectContains(source, "print(\"PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass\")");
    try expectContains(source, "print(f\"PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}\")");
    try std.testing.expect(countOccurrences(source, "checks_run += 1") >= 8);
}
