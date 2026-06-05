const std = @import("std");

const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");

const ListSortFixture = struct {
    tri_sorted_keys: []const i32,
    tri_sorted_ordinals: []const u8,
    bool_sorted_keys: []const i32,
    bool_sorted_ordinals: []const u8,
};

const Fixture = struct {
    list_sort: ListSortFixture,
};

fn loadFixture() !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_bytes, .{
        .ignore_unknown_fields = true,
    });
}

fn expectNeedleAfter(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierNeedle;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterNeedle;
    try std.testing.expect(earlier_index < later_index);
}

test "phase 1 list_sort fixture pins tri-state comparator ordering" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const list_sort = parsed.value.list_sort;

    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 3, 3 }, list_sort.tri_sorted_keys);
    try std.testing.expectEqualSlices(u8, &.{ 1, 3, 0, 2, 4 }, list_sort.tri_sorted_ordinals);
}

test "phase 1 list_sort fixture pins boolean comparator ordering" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const list_sort = parsed.value.list_sort;

    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 3, 3 }, list_sort.bool_sorted_keys);
    try std.testing.expectEqualSlices(u8, &.{ 1, 3, 0, 2, 4 }, list_sort.bool_sorted_ordinals);
}

test "phase 1 list_sort fixture stays between hweight and zalloc" {
    try expectNeedleAfter(fixture_bytes, "\"hweight\"", "\"list_sort\"");
    try expectNeedleAfter(fixture_bytes, "\"list_sort\"", "\"zalloc\"");
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, fixture_bytes, "\"list_sort\""));
}
