const std = @import("std");

const SourceFile = struct {
    path: []const u8,
    text: []const u8,
};

const RequiredCode = struct {
    code: []const u8,
    fixture: []const u8,
};

const expected_issue_codes = [_]RequiredCode{
    .{ .code = "MISSING_MAKEFILE_LINE", .fixture = "# removed" },
    .{ .code = "DUPLICATE_MAKEFILE_LINE", .fixture = ":count=2" },
    .{ .code = "ARCHIVE_SCOPE_MISMATCH", .fixture = "archive_target_scope" },
    .{ .code = "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH", .fixture = "route_contract_only" },
    .{ .code = "DUPLICATE_CROSS_TARGET", .fixture = "cross_targets" },
    .{ .code = "INVALID_CROSS_TARGET_ROUTE", .fixture = "make -C zigux phase2" },
    .{ .code = "INVALID_CROSS_TARGET_ENTRY", .fixture = "review_status" },
    .{ .code = "INVALID_CROSS_TARGET_MODE", .fixture = "unexpected_mode" },
};

fn readFirstExisting(allocator: std.mem.Allocator, comptime label: []const u8, candidates: []const []const u8) !SourceFile {
    var last_error: anyerror = error.FileNotFound;
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    for (candidates) |path| {
        const text = std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(1024 * 1024)) catch |err| {
            last_error = err;
            continue;
        };
        return .{ .path = path, .text = text };
    }
    std.debug.print("unable to locate {s}; last error: {s}\n", .{ label, @errorName(last_error) });
    return error.RequiredSourceMissing;
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

test "phase2 cross checker keeps fail-closed issue envelope explicit" {
    const allocator = std.testing.allocator;
    const checker = try readFirstExisting(allocator, "direct cross checker", &.{
        "scripts/zigux/check-phase2-cross.py",
        "../../scripts/zigux/check-phase2-cross.py",
    });
    defer allocator.free(checker.text);

    try expectContains(checker.text, "PHASE2_DIRECT_CROSS_ROUTE=fail");
    try expectContains(checker.text, "{code}_START");
    try expectContains(checker.text, "{code}_END");
    try expectContains(checker.text, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try expectContains(checker.text, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(checker.text, "assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT");

    for (expected_issue_codes) |entry| {
        try expectContains(checker.text, entry.code);
        try expectContains(checker.text, entry.fixture);
    }
}

test "phase2 cross checker proves each issue code in self-test before the count lock" {
    const allocator = std.testing.allocator;
    const checker = try readFirstExisting(allocator, "direct cross checker", &.{
        "scripts/zigux/check-phase2-cross.py",
        "../../scripts/zigux/check-phase2-cross.py",
    });
    defer allocator.free(checker.text);

    try expectOrdered(checker.text, "assert collect_issues(root) == []", "assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT");
    for (expected_issue_codes) |entry| {
        try expectOrdered(checker.text, entry.code, "assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT");
    }
}

test "live cross fixture stays aligned with issue-code expectations" {
    const allocator = std.testing.allocator;
    const fixture = try readFirstExisting(allocator, "cross target fixture", &.{
        "zigux/tests/fixtures/phase2_cross_targets.json",
        "fixtures/phase2_cross_targets.json",
    });
    defer allocator.free(fixture.text);

    try expectContains(fixture.text, "\"phase\": \"Phase 2\"");
    try expectContains(fixture.text, "\"status\": \"active\"");
    try expectContains(fixture.text, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture.text, "\"archive_target_scope\"");
    try expectContains(fixture.text, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture.text, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture.text, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture.text, "\"validation_mode\": \"route_contract_only\"");
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(fixture.text, "\"archive_required\""));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(fixture.text, "\"route_contract_only\""));
}
