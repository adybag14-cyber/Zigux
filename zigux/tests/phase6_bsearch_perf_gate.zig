// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");
const bsearch = @import("bsearch");

const CountedIntKey = struct {
    target: i32,
    comparisons: *usize,
};

fn compareCountedInt(key: *const CountedIntKey, item: *const i32) i32 {
    key.comparisons.* += 1;
    return switch (std.math.order(key.target, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareCountedOpaqueInt(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const CountedIntKey = @ptrCast(@alignCast(key));
    const typed_item: *const i32 = @ptrCast(@alignCast(item));
    typed_key.comparisons.* += 1;
    return switch (std.math.order(typed_key.target, typed_item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn maxSearchComparisons(item_count: usize) usize {
    return if (item_count == 0) 0 else std.math.log2_int_ceil(usize, item_count + 1);
}

fn maxEqualRangeComparisons(item_count: usize) usize {
    return maxSearchComparisons(item_count) * 2;
}

fn expectTypedLowerBoundComparisonBudget(items: []const i32, key_value: i32, expected: usize) !void {
    var comparisons: usize = 0;
    const key = CountedIntKey{
        .target = key_value,
        .comparisons = &comparisons,
    };

    try std.testing.expectEqual(expected, bsearch.lowerBoundIndex(CountedIntKey, i32, &key, items, compareCountedInt));
    try std.testing.expect(comparisons <= maxSearchComparisons(items.len));
}

fn expectTypedUpperBoundComparisonBudget(items: []const i32, key_value: i32, expected: usize) !void {
    var comparisons: usize = 0;
    const key = CountedIntKey{
        .target = key_value,
        .comparisons = &comparisons,
    };

    try std.testing.expectEqual(expected, bsearch.upperBoundIndex(CountedIntKey, i32, &key, items, compareCountedInt));
    try std.testing.expect(comparisons <= maxSearchComparisons(items.len));
}

fn expectTypedEqualRangeComparisonBudget(items: []const i32, key_value: i32, expected: bsearch.IndexRange) !void {
    var comparisons: usize = 0;
    const key = CountedIntKey{
        .target = key_value,
        .comparisons = &comparisons,
    };

    try std.testing.expectEqual(expected, bsearch.equalRangeIndex(CountedIntKey, i32, &key, items, compareCountedInt));
    try std.testing.expect(comparisons <= maxEqualRangeComparisons(items.len));
}

fn expectRawLowerBoundComparisonBudget(items: []const i32, key_value: i32, expected: usize) !void {
    var comparisons: usize = 0;
    const key = CountedIntKey{
        .target = key_value,
        .comparisons = &comparisons,
    };

    try std.testing.expectEqual(
        expected,
        bsearch.bsearchLowerBoundIndex(&key, @ptrCast(items.ptr), items.len, @sizeOf(i32), compareCountedOpaqueInt),
    );
    try std.testing.expect(comparisons <= maxSearchComparisons(items.len));
}

fn expectRawUpperBoundComparisonBudget(items: []const i32, key_value: i32, expected: usize) !void {
    var comparisons: usize = 0;
    const key = CountedIntKey{
        .target = key_value,
        .comparisons = &comparisons,
    };

    try std.testing.expectEqual(
        expected,
        bsearch.bsearchUpperBoundIndex(&key, @ptrCast(items.ptr), items.len, @sizeOf(i32), compareCountedOpaqueInt),
    );
    try std.testing.expect(comparisons <= maxSearchComparisons(items.len));
}

fn expectRawEqualRangeComparisonBudget(items: []const i32, key_value: i32, expected: bsearch.IndexRange) !void {
    var comparisons: usize = 0;
    const key = CountedIntKey{
        .target = key_value,
        .comparisons = &comparisons,
    };

    try std.testing.expectEqual(
        expected,
        bsearch.bsearchEqualRangeIndex(&key, @ptrCast(items.ptr), items.len, @sizeOf(i32), compareCountedOpaqueInt),
    );
    try std.testing.expect(comparisons <= maxEqualRangeComparisons(items.len));
}

test "typed and raw bound helpers stay within a logarithmic comparison budget" {
    const ascending = [_]i32{ 1, 4, 4, 4, 9, 16, 16, 16, 20, 24, 29, 31, 31, 33, 35, 40, 44 };

    try expectTypedLowerBoundComparisonBudget(ascending[0..], 4, 1);
    try expectTypedLowerBoundComparisonBudget(ascending[0..], 5, 4);
    try expectTypedLowerBoundComparisonBudget(ascending[0..], 16, 5);
    try expectTypedLowerBoundComparisonBudget(ascending[0..], 32, 13);
    try expectTypedLowerBoundComparisonBudget(&[_]i32{}, 7, 0);

    try expectTypedUpperBoundComparisonBudget(ascending[0..], 4, 4);
    try expectTypedUpperBoundComparisonBudget(ascending[0..], 5, 4);
    try expectTypedUpperBoundComparisonBudget(ascending[0..], 16, 8);
    try expectTypedUpperBoundComparisonBudget(ascending[0..], 32, 13);
    try expectTypedUpperBoundComparisonBudget(&[_]i32{}, 7, 0);

    try expectTypedEqualRangeComparisonBudget(ascending[0..], 4, .{ .lower = 1, .upper = 4 });
    try expectTypedEqualRangeComparisonBudget(ascending[0..], 5, .{ .lower = 4, .upper = 4 });
    try expectTypedEqualRangeComparisonBudget(ascending[0..], 16, .{ .lower = 5, .upper = 8 });
    try expectTypedEqualRangeComparisonBudget(ascending[0..], 32, .{ .lower = 13, .upper = 13 });
    try expectTypedEqualRangeComparisonBudget(&[_]i32{}, 7, .{ .lower = 0, .upper = 0 });

    try expectRawLowerBoundComparisonBudget(ascending[0..], 4, 1);
    try expectRawLowerBoundComparisonBudget(ascending[0..], 5, 4);
    try expectRawLowerBoundComparisonBudget(ascending[0..], 16, 5);
    try expectRawLowerBoundComparisonBudget(ascending[0..], 32, 13);
    try expectRawLowerBoundComparisonBudget(&[_]i32{}, 7, 0);

    try expectRawUpperBoundComparisonBudget(ascending[0..], 4, 4);
    try expectRawUpperBoundComparisonBudget(ascending[0..], 5, 4);
    try expectRawUpperBoundComparisonBudget(ascending[0..], 16, 8);
    try expectRawUpperBoundComparisonBudget(ascending[0..], 32, 13);
    try expectRawUpperBoundComparisonBudget(&[_]i32{}, 7, 0);

    try expectRawEqualRangeComparisonBudget(ascending[0..], 4, .{ .lower = 1, .upper = 4 });
    try expectRawEqualRangeComparisonBudget(ascending[0..], 5, .{ .lower = 4, .upper = 4 });
    try expectRawEqualRangeComparisonBudget(ascending[0..], 16, .{ .lower = 5, .upper = 8 });
    try expectRawEqualRangeComparisonBudget(ascending[0..], 32, .{ .lower = 13, .upper = 13 });
    try expectRawEqualRangeComparisonBudget(&[_]i32{}, 7, .{ .lower = 0, .upper = 0 });
}
