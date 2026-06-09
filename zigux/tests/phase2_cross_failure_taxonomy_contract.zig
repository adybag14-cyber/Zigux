const std = @import("std");

const checker_path = "scripts/zigux/check-phase2-cross.py";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "direct cross checker keeps stable failure taxonomy names" {
    const checker = try readFile(std.testing.allocator, checker_path);
    defer std.testing.allocator.free(checker);

    const failure_codes = [_][]const u8{
        "MISSING_MAKEFILE_LINE",
        "DUPLICATE_MAKEFILE_LINE",
        "INVALID_FIXTURE_SHAPE",
        "INVALID_FIXTURE_FIELD",
        "ARCHIVE_SCOPE_MISMATCH",
        "INVALID_CROSS_TARGET_ENTRY",
        "DUPLICATE_CROSS_TARGET",
        "INVALID_CROSS_TARGET_ROUTE",
        "INVALID_CROSS_TARGET_MODE",
        "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH",
    };

    for (failure_codes) |code| {
        try expectContains(checker, code);
    }
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE=fail");
    try expectContains(checker, "print(f\"{code}_START\")");
    try expectContains(checker, "print(f\"{code}_END\")");
}

test "direct cross checker groups failures after fail marker and preserves route-first issue order" {
    const checker = try readFile(std.testing.allocator, checker_path);
    defer std.testing.allocator.free(checker);

    try expectOrder(checker, "print(\"PHASE2_DIRECT_CROSS_ROUTE=fail\")", "print(f\"{code}_START\")");
    try expectOrder(checker, "MISSING_MAKEFILE_LINE", "DUPLICATE_MAKEFILE_LINE");
    try expectOrder(checker, "DUPLICATE_MAKEFILE_LINE", "INVALID_FIXTURE_SHAPE");
    try expectOrder(checker, "INVALID_FIXTURE_FIELD", "ARCHIVE_SCOPE_MISMATCH");
    try expectOrder(checker, "ARCHIVE_SCOPE_MISMATCH", "INVALID_CROSS_TARGET_ENTRY");
    try expectOrder(checker, "DUPLICATE_CROSS_TARGET", "INVALID_CROSS_TARGET_ROUTE");
    try expectOrder(checker, "INVALID_CROSS_TARGET_ROUTE", "INVALID_CROSS_TARGET_MODE");
    try expectOrder(checker, "INVALID_CROSS_TARGET_MODE", "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH");
}

test "direct cross checker keeps pass markers and self-test accounting visible" {
    const checker = try readFile(std.testing.allocator, checker_path);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(checker, "assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT={checks_run}");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT={len(cross_targets)}");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT={len(load_archive_target_scope(args.root.resolve()))}");
}

test "direct cross fixture remains two-target x86 archive plus aarch64 route contract" {
    const fixture = try readFile(std.testing.allocator, fixture_path);
    defer std.testing.allocator.free(fixture);

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"review_status\": \"route contract only\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, "riscv64-linux");
}
