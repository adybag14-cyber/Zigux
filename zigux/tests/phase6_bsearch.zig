const std = @import("std");
const bsearch = @import("bsearch");
const fixtures = @import("fixtures/phase6_bsearch_vectors.zig");

const CountedKey = struct {
    target: u32,
    comparisons: *usize,
};

const CountedOpaqueKey = struct {
    target: u32,
    comparisons: *usize,
};

fn compareCountedInt(key: *const CountedKey, item: *const u32) i32 {
    key.comparisons.* += 1;
    return switch (std.math.order(key.target, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareCountedDescendingInt(key: *const CountedKey, item: *const u32) i32 {
    key.comparisons.* += 1;
    return switch (std.math.order(item.*, key.target)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareCountedOpaqueInt(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const CountedOpaqueKey = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    typed_key.comparisons.* += 1;
    return switch (std.math.order(typed_key.target, typed_item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareCountedOpaqueDescendingInt(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const CountedOpaqueKey = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    typed_key.comparisons.* += 1;
    return switch (std.math.order(typed_item.*, typed_key.target)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareCOpaqueDescendingInt(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    return compareCountedOpaqueDescendingInt(key, item);
}

fn typedProbe(items: []const u32, target: u32, expect_hit: bool, compare: anytype) !usize {
    var comparisons: usize = 0;
    const key = CountedKey{ .target = target, .comparisons = &comparisons };
    const result = bsearch.search(CountedKey, u32, &key, items, compare);
    if (expect_hit) {
        const found = result orelse return error.ExpectedMatch;
        try std.testing.expectEqual(target, found.*);
    } else {
        try std.testing.expectEqual(@as(?*const u32, null), result);
    }
    return comparisons;
}

fn rawProbe(items: []const u32, target: u32, expect_hit: bool, compare: anytype) !usize {
    var comparisons: usize = 0;
    const key = CountedOpaqueKey{ .target = target, .comparisons = &comparisons };
    const result = bsearch.bsearch(&key, @ptrCast(items.ptr), items.len, @sizeOf(u32), compare);
    if (expect_hit) {
        const found = result orelse return error.ExpectedMatch;
        const typed_found: *const u32 = @ptrCast(@alignCast(found));
        try std.testing.expectEqual(target, typed_found.*);
    } else {
        try std.testing.expectEqual(@as(?*const anyopaque, null), result);
    }
    return comparisons;
}

test "phase 6 bsearch keeps representative lookup work inside a binary-search budget" {
    const values = [_]u32{ 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45 };

    {
        const counted_compare_calls = try typedProbe(values[0..], 3, true, compareCountedInt);
        try std.testing.expect(counted_compare_calls <= 4);
    }
    {
        const counted_compare_calls = try typedProbe(values[0..], 21, true, compareCountedInt);
        try std.testing.expect(counted_compare_calls <= 4);
    }
    {
        const counted_compare_calls = try typedProbe(values[0..], 24, true, compareCountedInt);
        try std.testing.expect(counted_compare_calls <= 4);
    }
    {
        const counted_compare_calls = try typedProbe(values[0..], 39, true, compareCountedInt);
        try std.testing.expect(counted_compare_calls <= 4);
    }
    {
        const counted_compare_calls = try typedProbe(values[0..], 45, true, compareCountedInt);
        try std.testing.expect(counted_compare_calls <= 4);
    }
    {
        const counted_compare_calls = try typedProbe(values[0..], 1, false, compareCountedInt);
        try std.testing.expect(counted_compare_calls <= 4);
    }
    {
        const counted_compare_calls = try typedProbe(values[0..], 10, false, compareCountedInt);
        try std.testing.expect(counted_compare_calls <= 4);
    }
    {
        const counted_compare_calls = try typedProbe(values[0..], 26, false, compareCountedInt);
        try std.testing.expect(counted_compare_calls <= 4);
    }
    {
        const counted_compare_calls = try typedProbe(values[0..], 44, false, compareCountedInt);
        try std.testing.expect(counted_compare_calls <= 4);
    }
    {
        const counted_compare_calls = try typedProbe(values[0..], 50, false, compareCountedInt);
        try std.testing.expect(counted_compare_calls <= 4);
    }
}

test "phase 6 bsearch keeps descending lookup work inside a binary-search budget" {
    const values = [_]u32{ 45, 42, 39, 36, 33, 30, 27, 24, 21, 18, 15, 12, 9, 6, 3 };

    {
        const descending_compare_calls = try typedProbe(values[0..], 45, true, compareCountedDescendingInt);
        try std.testing.expect(descending_compare_calls <= 4);
    }
    {
        const descending_compare_calls = try typedProbe(values[0..], 39, true, compareCountedDescendingInt);
        try std.testing.expect(descending_compare_calls <= 4);
    }
    {
        const descending_compare_calls = try typedProbe(values[0..], 24, true, compareCountedDescendingInt);
        try std.testing.expect(descending_compare_calls <= 4);
    }
    {
        const descending_compare_calls = try typedProbe(values[0..], 21, true, compareCountedDescendingInt);
        try std.testing.expect(descending_compare_calls <= 4);
    }
    {
        const descending_compare_calls = try typedProbe(values[0..], 3, true, compareCountedDescendingInt);
        try std.testing.expect(descending_compare_calls <= 4);
    }
    {
        const descending_compare_calls = try typedProbe(values[0..], 50, false, compareCountedDescendingInt);
        try std.testing.expect(descending_compare_calls <= 4);
    }
    {
        const descending_compare_calls = try typedProbe(values[0..], 44, false, compareCountedDescendingInt);
        try std.testing.expect(descending_compare_calls <= 4);
    }
    {
        const descending_compare_calls = try typedProbe(values[0..], 26, false, compareCountedDescendingInt);
        try std.testing.expect(descending_compare_calls <= 4);
    }
    {
        const descending_compare_calls = try typedProbe(values[0..], 10, false, compareCountedDescendingInt);
        try std.testing.expect(descending_compare_calls <= 4);
    }
    {
        const descending_compare_calls = try typedProbe(values[0..], 1, false, compareCountedDescendingInt);
        try std.testing.expect(descending_compare_calls <= 4);
    }
}

test "phase 6 bsearch raw lookup keeps representative work inside a binary-search budget" {
    const values = fixtures.representative_ascending_values;
    const descending_values = fixtures.representative_descending_values;

    {
        const counted_raw_compare_calls = try rawProbe(values[0..], 3, true, compareCountedOpaqueInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
    {
        const counted_raw_compare_calls = try rawProbe(values[0..], 21, true, compareCountedOpaqueInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
    {
        const counted_raw_compare_calls = try rawProbe(values[0..], 24, true, compareCountedOpaqueInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
    {
        const counted_raw_compare_calls = try rawProbe(values[0..], 39, true, compareCountedOpaqueInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
    {
        const counted_raw_compare_calls = try rawProbe(values[0..], 45, true, compareCountedOpaqueInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
    {
        const counted_raw_compare_calls = try rawProbe(descending_values[0..], 45, true, compareCountedOpaqueDescendingInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
    {
        const counted_raw_compare_calls = try rawProbe(descending_values[0..], 39, true, compareCountedOpaqueDescendingInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
    {
        const counted_raw_compare_calls = try rawProbe(descending_values[0..], 24, true, compareCountedOpaqueDescendingInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
    {
        const counted_raw_compare_calls = try rawProbe(descending_values[0..], 21, true, compareCountedOpaqueDescendingInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
    {
        const counted_raw_compare_calls = try rawProbe(descending_values[0..], 3, true, compareCountedOpaqueDescendingInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
}

test "phase 6 bsearch bounded typed and raw equality probes stay inside a binary-search budget" {
    const duplicates = [_]u32{ 3, 6, 9, 12, 21, 21, 21, 24, 27, 30, 33, 36, 39, 42, 45 };
    var duplicate_target = @as(u32, 21);
    const typed_range = bsearch.equalRangeIndex(u32, u32, &duplicate_target, duplicates[0..], struct {
        fn compare(key: *const u32, item: *const u32) i32 {
            return switch (std.math.order(key.*, item.*)) {
                .lt => -1,
                .eq => 0,
                .gt => 1,
            };
        }
    }.compare);
    try std.testing.expectEqual(bsearch.IndexRange{ .lower = 4, .upper = 7 }, typed_range);

    const raw_range = bsearch.bsearchEqualRangeIndex(&duplicate_target, @ptrCast(duplicates[0..].ptr), duplicates.len, @sizeOf(u32), struct {
        fn compare(key: *const anyopaque, item: *const anyopaque) i32 {
            const typed_key: *const u32 = @ptrCast(@alignCast(key));
            const typed_item: *const u32 = @ptrCast(@alignCast(item));
            return switch (std.math.order(typed_key.*, typed_item.*)) {
                .lt => -1,
                .eq => 0,
                .gt => 1,
            };
        }
    }.compare);
    try std.testing.expectEqual(bsearch.IndexRange{ .lower = 4, .upper = 7 }, raw_range);
}

test "phase 6 bsearch accepts runtime-selected descending raw c abi comparator pointers" {
    const values = fixtures.representative_descending_values;
    const comparators = [_]bsearch.CRawComparator{
        compareCOpaqueDescendingInt,
    };
    for (comparators) |compare| {
        var comparisons: usize = 0;
        const raw_key = CountedOpaqueKey{ .target = 24, .comparisons = &comparisons };
        const found = bsearch.bsearch(&raw_key, @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compare) orelse return error.ExpectedMatch;
        const typed_found: *const u32 = @ptrCast(@alignCast(found));
        try std.testing.expectEqual(@as(u32, 24), typed_found.*);
    }
}
