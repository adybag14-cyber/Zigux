const std = @import("std");
const bsearch = @import("bsearch");
const fixtures = @import("fixtures/phase6_bsearch_vectors.zig");

fn compareCOpaqueInt(key: *const anyopaque, item: *const anyopaque) callconv(.c) c_int {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return switch (std.math.order(typed_key.*, typed_item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareCOpaqueDescendingInt(key: *const anyopaque, item: *const anyopaque) callconv(.c) c_int {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return switch (std.math.order(typed_item.*, typed_key.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn expectRange(
    items: []const u32,
    target: u32,
    expected: bsearch.IndexRange,
    compare: bsearch.CRawComparator,
) !void {
    const base: [*]const u8 = @ptrCast(items.ptr);
    const lower = bsearch.bsearchLowerBoundIndex(&target, base, items.len, @sizeOf(u32), compare);
    const upper = bsearch.bsearchUpperBoundIndex(&target, base, items.len, @sizeOf(u32), compare);
    const range = bsearch.bsearchEqualRangeIndex(&target, base, items.len, @sizeOf(u32), compare);
    const bytes = bsearch.bsearchEqualRange(&target, base, items.len, @sizeOf(u32), compare);

    try std.testing.expectEqual(expected.lower, lower);
    try std.testing.expectEqual(expected.upper, upper);
    try std.testing.expectEqual(expected, range);
    try std.testing.expectEqual(expected.len() * @sizeOf(u32), bytes.len);

    if (!expected.isEmpty()) {
        const typed_bytes: [*]const u32 = @ptrCast(@alignCast(bytes.ptr));
        try std.testing.expectEqual(target, typed_bytes[0]);
        try std.testing.expectEqual(target, typed_bytes[expected.len() - 1]);
    }
}

test "phase 6 bsearch raw c abi bounds keep duplicate spans and insertion points aligned" {
    const duplicates = fixtures.representative_duplicate_values;
    const compare = compareCOpaqueInt;

    try expectRange(duplicates[0..], 21, .{ .lower = 4, .upper = 7 }, compare);
    try expectRange(duplicates[0..], 20, .{ .lower = 4, .upper = 4 }, compare);
    try expectRange(duplicates[0..], 22, .{ .lower = 7, .upper = 7 }, compare);
    try expectRange(duplicates[0..], 3, .{ .lower = 0, .upper = 1 }, compare);
    try expectRange(duplicates[0..], 45, .{ .lower = 14, .upper = 15 }, compare);
    try expectRange(duplicates[0..], 1, .{ .lower = 0, .upper = 0 }, compare);
    try expectRange(duplicates[0..], 46, .{ .lower = duplicates.len, .upper = duplicates.len }, compare);
}

test "phase 6 bsearch descending raw c abi bounds stay comparator-driven" {
    const descending_duplicates = fixtures.representative_descending_duplicate_values;
    const compare = compareCOpaqueDescendingInt;

    try expectRange(descending_duplicates[0..], 45, .{ .lower = 0, .upper = 1 }, compare);
    try expectRange(descending_duplicates[0..], 21, .{ .lower = 3, .upper = 6 }, compare);
    try expectRange(descending_duplicates[0..], 22, .{ .lower = 3, .upper = 3 }, compare);
    try expectRange(descending_duplicates[0..], 20, .{ .lower = 6, .upper = 6 }, compare);
    try expectRange(descending_duplicates[0..], 1, .{ .lower = descending_duplicates.len, .upper = descending_duplicates.len }, compare);
    try expectRange(descending_duplicates[0..], 50, .{ .lower = 0, .upper = 0 }, compare);
}

test "phase 6 bsearch descending raw c abi mutable wrappers keep duplicate-span write-through aligned" {
    const compare = compareCOpaqueDescendingInt;
    const target = @as(u32, 21);

    var mutable_duplicates = fixtures.representative_descending_duplicate_values;
    const mutable_lower = bsearch.bsearchLowerBoundMutable(
        &target,
        @ptrCast(mutable_duplicates[0..].ptr),
        mutable_duplicates.len,
        @sizeOf(u32),
        compare,
    ) orelse return error.ExpectedMatch;
    const typed_mutable_lower: *u32 = @ptrCast(@alignCast(mutable_lower));
    try std.testing.expectEqual(@as(u32, 21), typed_mutable_lower.*);
    try std.testing.expectEqual(@intFromPtr(&mutable_duplicates[3]), @intFromPtr(typed_mutable_lower));

    const mutable_bytes = bsearch.bsearchEqualRangeMutable(
        &target,
        @ptrCast(mutable_duplicates[0..].ptr),
        mutable_duplicates.len,
        @sizeOf(u32),
        compare,
    );
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(u32)), mutable_bytes.len);
    const typed_mutable_bytes: [*]u32 = @ptrCast(@alignCast(mutable_bytes.ptr));
    typed_mutable_bytes[1] = 22;
    try std.testing.expectEqual(@as(u32, 22), mutable_duplicates[4]);

    var insertion_duplicates = fixtures.representative_descending_duplicate_values;
    const missing_target = @as(u32, 20);
    const missing_lower = bsearch.bsearchLowerBoundMutable(
        &missing_target,
        @ptrCast(insertion_duplicates[0..].ptr),
        insertion_duplicates.len,
        @sizeOf(u32),
        compare,
    ) orelse return error.ExpectedMatch;
    const typed_missing_lower: *u32 = @ptrCast(@alignCast(missing_lower));
    try std.testing.expectEqual(@as(u32, 12), typed_missing_lower.*);
    try std.testing.expectEqual(@intFromPtr(&insertion_duplicates[6]), @intFromPtr(typed_missing_lower));

    const missing_bytes = bsearch.bsearchEqualRangeMutable(
        &missing_target,
        @ptrCast(insertion_duplicates[0..].ptr),
        insertion_duplicates.len,
        @sizeOf(u32),
        compare,
    );
    try std.testing.expectEqual(@as(usize, 0), missing_bytes.len);
    try std.testing.expectEqual(
        @intFromPtr(@as([*]u8, @ptrCast(insertion_duplicates[0..].ptr)) + (6 * @sizeOf(u32))),
        @intFromPtr(missing_bytes.ptr),
    );
}
