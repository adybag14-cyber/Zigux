const std = @import("std");

const validator_path = "scripts/zigux/validate-bootstrap.py";

fn readValidator() ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        validator_path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectInOrder(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

test "validate-bootstrap success output reports dynamic roster counts" {
    const validator = try readValidator();
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "print(\"BOOTSTRAP_VALIDATION=pass\")");
    try expectContains(validator, "print(f\"BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}\")");
    try expectContains(validator, "print(f\"BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}\")");
    try expectInOrder(
        validator,
        "print(\"BOOTSTRAP_VALIDATION=pass\")",
        "print(f\"BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}\")",
    );
}

test "validate-bootstrap failure output keeps grouped issue boundaries" {
    const validator = try readValidator();
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "print(\"BOOTSTRAP_VALIDATION=fail\")");
    try expectContains(validator, "print(f\"{code}_START\")");
    try expectContains(validator, "print(f\"{code}_END\")");
    try expectContains(validator, "\"MISSING_REQUIRED_PATH\"");
    try expectContains(validator, "\"MISSING_WORKFLOW_LINE\"");
    try expectContains(validator, "\"DUPLICATE_WORKFLOW_LINE\"");
}

test "validate-bootstrap self-test count stays tied to exercised checks" {
    const validator = try readValidator();
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "checks = 0");
    try expectContains(validator, "checks += 1");
    try expectContains(validator, "print(\"BOOTSTRAP_VALIDATION_SELF_TEST=pass\")");
    try expectContains(validator, "print(f\"BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT={checks}\")");
    try expectInOrder(
        validator,
        "checks += 1",
        "print(f\"BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT={checks}\")",
    );
}

test "validate-bootstrap workflow roster keeps toolchain front and validator tail" {
    const validator = try readValidator();
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "run: python3 scripts/zigux/check-zig-toolchain.py --self-test");
    try expectContains(validator, "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only");
    try expectContains(validator, "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try expectContains(validator, "run: python3 scripts/zigux/validate-bootstrap.py --self-test");
    try expectContains(validator, "run: python3 scripts/zigux/validate-bootstrap.py");
    try expectInOrder(
        validator,
        "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
        "run: python3 scripts/zigux/validate-bootstrap.py --self-test",
    );
}
