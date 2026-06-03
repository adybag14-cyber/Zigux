const std = @import("std");

const route = "make -C zigux phase2-cross";

const FixtureField = struct {
    name: []const u8,
    expected: []const u8,
};

const fixture_fields = [_]FixtureField{
    .{ .name = "phase", .expected = "Phase 2" },
    .{ .name = "status", .expected = "active" },
    .{ .name = "route", .expected = route },
};

const direct_checker_issue_codes = [_][]const u8{
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

const matrix_issue_codes = [_][]const u8{
    "ARCHIVE_SCOPE_MISMATCH",
    "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH",
    "DUPLICATE_CROSS_TARGET",
    "INVALID_CROSS_TARGET_MODE",
    "INVALID_CROSS_TARGET_ROUTE",
};

const structural_issue_codes = [_][]const u8{
    "INVALID_FIXTURE_SHAPE",
    "INVALID_FIXTURE_FIELD",
    "INVALID_CROSS_TARGET_ENTRY",
    "MISSING_MAKEFILE_LINE",
    "DUPLICATE_MAKEFILE_LINE",
};

fn expectString(expected: []const u8, actual: []const u8) !void {
    try std.testing.expectEqualStrings(expected, actual);
}

fn countCode(haystack: []const []const u8, needle: []const u8) usize {
    var count: usize = 0;
    for (haystack) |candidate| {
        if (std.mem.eql(u8, candidate, needle)) {
            count += 1;
        }
    }
    return count;
}

fn containsCode(haystack: []const []const u8, needle: []const u8) bool {
    return countCode(haystack, needle) != 0;
}

test "direct cross checker issue vocabulary stays unique and bounded" {
    try std.testing.expectEqual(@as(usize, 10), direct_checker_issue_codes.len);

    for (direct_checker_issue_codes, 0..) |code, index| {
        try std.testing.expect(code.len > 0);
        try std.testing.expectEqual(@as(usize, 1), countCode(&direct_checker_issue_codes, code));
        if (index != 0) {
            try std.testing.expect(!std.mem.eql(u8, direct_checker_issue_codes[index - 1], code));
        }
    }
}

test "matrix issue codes remain a focused subset of the direct checker" {
    try std.testing.expectEqual(@as(usize, 5), matrix_issue_codes.len);

    for (matrix_issue_codes) |code| {
        try std.testing.expect(containsCode(&direct_checker_issue_codes, code));
    }

    try std.testing.expect(containsCode(&matrix_issue_codes, "ARCHIVE_SCOPE_MISMATCH"));
    try std.testing.expect(containsCode(&matrix_issue_codes, "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH"));
    try std.testing.expect(containsCode(&matrix_issue_codes, "INVALID_CROSS_TARGET_MODE"));
}

test "structural issue codes cover fixture and makefile failure lanes" {
    try std.testing.expectEqual(@as(usize, 5), structural_issue_codes.len);

    for (structural_issue_codes) |code| {
        try std.testing.expect(containsCode(&direct_checker_issue_codes, code));
    }

    try std.testing.expect(containsCode(&structural_issue_codes, "INVALID_FIXTURE_SHAPE"));
    try std.testing.expect(containsCode(&structural_issue_codes, "INVALID_FIXTURE_FIELD"));
    try std.testing.expect(containsCode(&structural_issue_codes, "MISSING_MAKEFILE_LINE"));
    try std.testing.expect(containsCode(&structural_issue_codes, "DUPLICATE_MAKEFILE_LINE"));
}

test "fixture identity fields stay tied to the phase2-cross route" {
    try std.testing.expectEqual(@as(usize, 3), fixture_fields.len);

    try expectString("phase", fixture_fields[0].name);
    try expectString("Phase 2", fixture_fields[0].expected);
    try expectString("status", fixture_fields[1].name);
    try expectString("active", fixture_fields[1].expected);
    try expectString("route", fixture_fields[2].name);
    try expectString(route, fixture_fields[2].expected);
}
