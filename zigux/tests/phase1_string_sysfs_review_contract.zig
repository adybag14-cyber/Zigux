const std = @import("std");
const string = @import("string");

const SysfsAnchorKind = enum {
    newline_aware_equality,
    linux_style_alias,
    bounded_lookup,
    first_match_lookup,
};

const SysfsAnchor = struct {
    symbol: []const u8,
    kind: SysfsAnchorKind,
    helper_local: bool,
};

const string_sysfs_anchors = [_]SysfsAnchor{
    .{ .symbol = "sysfsStreq", .kind = .newline_aware_equality, .helper_local = true },
    .{ .symbol = "sysfs_streq", .kind = .linux_style_alias, .helper_local = true },
    .{ .symbol = "__sysfs_match_string", .kind = .bounded_lookup, .helper_local = true },
    .{ .symbol = "sysfsMatchString", .kind = .first_match_lookup, .helper_local = true },
    .{ .symbol = "sysfs_match_string", .kind = .linux_style_alias, .helper_local = true },
};

const closure_sysfs_review_marker =
    "PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit";

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn countKind(kind: SysfsAnchorKind) usize {
    var count: usize = 0;
    for (string_sysfs_anchors) |anchor| {
        if (anchor.kind == kind) count += 1;
    }
    return count;
}

test "phase1 string sysfs review roster stays helper-local" {
    try std.testing.expectEqual(@as(usize, 5), string_sysfs_anchors.len);
    try std.testing.expect(contains(closure_sysfs_review_marker, "helper-local string sysfs"));
    try std.testing.expect(contains(closure_sysfs_review_marker, "newline-aware equality"));
    try std.testing.expect(contains(closure_sysfs_review_marker, "lookup-order anchors"));

    for (string_sysfs_anchors) |anchor| {
        try std.testing.expect(anchor.helper_local);
        try std.testing.expect(!contains(anchor.symbol, "validate-phase1-closure"));
        try std.testing.expect(!contains(anchor.symbol, "shared-fixture"));
    }
}

test "phase1 string sysfs review roster keeps equality and lookup surfaces distinct" {
    try std.testing.expectEqual(@as(usize, 1), countKind(.newline_aware_equality));
    try std.testing.expectEqual(@as(usize, 2), countKind(.linux_style_alias));
    try std.testing.expectEqual(@as(usize, 1), countKind(.bounded_lookup));
    try std.testing.expectEqual(@as(usize, 1), countKind(.first_match_lookup));
}

test "sysfsStreq treats one trailing newline as equivalent to C-string end" {
    try std.testing.expect(string.sysfsStreq("enabled\n", "enabled"));
    try std.testing.expect(string.sysfsStreq("enabled", "enabled\n"));
    try std.testing.expect(string.sysfsStreq("enabled\n", "enabled\n"));

    const newline_then_nul = [_]u8{ 'o', 'k', '\n', 0, 'x' };
    const nul_then_tail = [_]u8{ 'o', 'k', 0, 'y' };
    try std.testing.expect(string.sysfsStreq(&newline_then_nul, &nul_then_tail));
    try std.testing.expect(!string.sysfsStreq("en\nabled", "enabled"));
    try std.testing.expect(!string.sysfsStreq("enabled\nextra", "enabled"));
}

test "sysfs_streq alias mirrors newline-aware equality" {
    try std.testing.expectEqual(
        string.sysfsStreq("manual\n", "manual"),
        string.sysfs_streq("manual\n", "manual"),
    );
    try std.testing.expectEqual(
        string.sysfsStreq("manual\nmore", "manual"),
        string.sysfs_streq("manual\nmore", "manual"),
    );
}

test "sysfs match string preserves first newline-aware match" {
    const haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(haystack[0..], "auto\n"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(haystack[0..], "missing"));
}

test "bounded __sysfs_match_string respects count before later matches" {
    const haystack = [_][]const u8{ "off", "auto\n", "manual", "auto" };
    const nul_terminated = [_]u8{ 'm', 'a', 'n', 'u', 'a', 'l', 0, 'x' };

    try std.testing.expectEqual(@as(?usize, null), string.__sysfs_match_string(haystack[0..], 1, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.__sysfs_match_string(haystack[0..], 2, "auto"));
    try std.testing.expectEqual(@as(?usize, 2), string.__sysfs_match_string(haystack[0..], 99, &nul_terminated));
}
