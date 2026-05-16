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

const Entry = struct {
    name: []const u8,
    value: u32,
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

fn compareName(key: *const []const u8, item: *const Entry) i32 {
    return switch (std.mem.order(u8, key.*, item.name)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareOpaqueName(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const []const u8 = @ptrCast(@alignCast(key));
    const typed_item: *const Entry = @ptrCast(@alignCast(item));
    return compareName(typed_key, typed_item);
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
    const values = fixtures.representative_ascending_values;

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
    const values = fixtures.representative_descending_values;

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
    const miss_queries = fixtures.representative_miss_queries;

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
        const counted_raw_compare_calls = try rawProbe(descending_values[0..], miss_queries[4], false, compareCountedOpaqueDescendingInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
    {
        const counted_raw_compare_calls = try rawProbe(descending_values[0..], miss_queries[3], false, compareCountedOpaqueDescendingInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
    {
        const counted_raw_compare_calls = try rawProbe(descending_values[0..], miss_queries[2], false, compareCountedOpaqueDescendingInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
    {
        const counted_raw_compare_calls = try rawProbe(descending_values[0..], miss_queries[1], false, compareCountedOpaqueDescendingInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
    {
        const counted_raw_compare_calls = try rawProbe(descending_values[0..], miss_queries[0], false, compareCountedOpaqueDescendingInt);
        try std.testing.expect(counted_raw_compare_calls <= 4);
    }
}

test "phase 6 bsearch bounded typed and raw equality probes stay inside a binary-search budget" {
    const duplicates = fixtures.representative_duplicate_values;
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

test "phase 6 bsearch bound and range helpers support heterogeneous duplicate keys" {
    var entries = [_]Entry{
        .{ .name = "alpha", .value = 1 },
        .{ .name = "beta", .value = 2 },
        .{ .name = "beta", .value = 3 },
        .{ .name = "beta", .value = 5 },
        .{ .name = "delta", .value = 8 },
        .{ .name = "omega", .value = 13 },
    };

    const key = @as([]const u8, "beta");
    const gap_key = @as([]const u8, "charlie");

    try std.testing.expectEqual(@as(usize, 1), bsearch.lowerBoundIndex([]const u8, Entry, &key, entries[0..], compareName));
    try std.testing.expectEqual(@as(usize, 4), bsearch.upperBoundIndex([]const u8, Entry, &key, entries[0..], compareName));
    try std.testing.expectEqual(
        bsearch.IndexRange{ .lower = 1, .upper = 4 },
        bsearch.equalRangeIndex([]const u8, Entry, &key, entries[0..], compareName),
    );
    try std.testing.expectEqual(@as(usize, 4), bsearch.lowerBoundIndex([]const u8, Entry, &gap_key, entries[0..], compareName));
    try std.testing.expectEqual(@as(usize, 4), bsearch.upperBoundIndex([]const u8, Entry, &gap_key, entries[0..], compareName));

    const typed_lower = bsearch.lowerBound([]const u8, Entry, &key, entries[0..], compareName) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@intFromPtr(&entries[1]), @intFromPtr(typed_lower));
    const typed_upper = bsearch.upperBound([]const u8, Entry, &key, entries[0..], compareName) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@intFromPtr(&entries[4]), @intFromPtr(typed_upper));

    const typed_range = bsearch.equalRange([]const u8, Entry, &key, entries[0..], compareName);
    try std.testing.expectEqual(@as(usize, 3), typed_range.len);
    try std.testing.expectEqual(@as(u32, 2), typed_range[0].value);
    try std.testing.expectEqual(@as(u32, 5), typed_range[2].value);

    const gap_lower = bsearch.lowerBound([]const u8, Entry, &gap_key, entries[0..], compareName) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@intFromPtr(&entries[4]), @intFromPtr(gap_lower));
    const gap_upper = bsearch.upperBound([]const u8, Entry, &gap_key, entries[0..], compareName) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@intFromPtr(&entries[4]), @intFromPtr(gap_upper));

    const raw_base: [*]const u8 = @ptrCast(entries[0..].ptr);
    try std.testing.expectEqual(@as(usize, 1), bsearch.bsearchLowerBoundIndex(@ptrCast(&key), raw_base, entries.len, @sizeOf(Entry), compareOpaqueName));
    try std.testing.expectEqual(@as(usize, 4), bsearch.bsearchUpperBoundIndex(@ptrCast(&key), raw_base, entries.len, @sizeOf(Entry), compareOpaqueName));
    try std.testing.expectEqual(
        bsearch.IndexRange{ .lower = 1, .upper = 4 },
        bsearch.bsearchEqualRangeIndex(@ptrCast(&key), raw_base, entries.len, @sizeOf(Entry), compareOpaqueName),
    );
    try std.testing.expectEqual(@as(usize, 4), bsearch.bsearchLowerBoundIndex(@ptrCast(&gap_key), raw_base, entries.len, @sizeOf(Entry), compareOpaqueName));
    try std.testing.expectEqual(@as(usize, 4), bsearch.bsearchUpperBoundIndex(@ptrCast(&gap_key), raw_base, entries.len, @sizeOf(Entry), compareOpaqueName));

    const raw_lower = bsearch.bsearchLowerBound(@ptrCast(&key), raw_base, entries.len, @sizeOf(Entry), compareOpaqueName) orelse return error.TestUnexpectedResult;
    const typed_raw_lower: *const Entry = @ptrCast(@alignCast(raw_lower));
    try std.testing.expectEqual(@intFromPtr(&entries[1]), @intFromPtr(typed_raw_lower));
    const raw_upper = bsearch.bsearchUpperBound(@ptrCast(&key), raw_base, entries.len, @sizeOf(Entry), compareOpaqueName) orelse return error.TestUnexpectedResult;
    const typed_raw_upper: *const Entry = @ptrCast(@alignCast(raw_upper));
    try std.testing.expectEqual(@intFromPtr(&entries[4]), @intFromPtr(typed_raw_upper));

    const raw_bytes = bsearch.bsearchEqualRange(@ptrCast(&key), raw_base, entries.len, @sizeOf(Entry), compareOpaqueName);
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(Entry)), raw_bytes.len);
    const typed_raw_range: [*]const Entry = @ptrCast(@alignCast(raw_bytes.ptr));
    try std.testing.expectEqual(@as(u32, 2), typed_raw_range[0].value);
    try std.testing.expectEqual(@as(u32, 5), typed_raw_range[2].value);

    var typed_mutable_entries = entries;
    const typed_mutable_range = bsearch.equalRangeMutable([]const u8, Entry, &key, typed_mutable_entries[0..], compareName);
    typed_mutable_range[1].value = 34;
    try std.testing.expectEqual(@as(u32, 34), typed_mutable_entries[2].value);

    var raw_mutable_entries = entries;
    const raw_mutable_bytes = bsearch.bsearchEqualRangeMutable(
        @ptrCast(&key),
        @ptrCast(raw_mutable_entries[0..].ptr),
        raw_mutable_entries.len,
        @sizeOf(Entry),
        compareOpaqueName,
    );
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(Entry)), raw_mutable_bytes.len);
    const raw_mutable_range: [*]Entry = @ptrCast(@alignCast(raw_mutable_bytes.ptr));
    raw_mutable_range[2].value = 55;
    try std.testing.expectEqual(@as(u32, 55), raw_mutable_entries[3].value);
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
