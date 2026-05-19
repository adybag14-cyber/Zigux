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

fn compareDirectInt(key: *const u32, item: *const u32) i32 {
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareDirectDescendingInt(key: *const u32, item: *const u32) i32 {
    return switch (std.math.order(item.*, key.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareCDirectInt(key: *const u32, item: *const u32) callconv(.c) c_int {
    return @as(c_int, compareDirectInt(key, item));
}

fn compareCDirectDescendingInt(key: *const u32, item: *const u32) callconv(.c) c_int {
    return @as(c_int, compareDirectDescendingInt(key, item));
}

fn compareDirectOpaqueInt(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareDirectInt(typed_key, typed_item);
}

fn compareDirectOpaqueDescendingInt(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareDirectDescendingInt(typed_key, typed_item);
}

fn compareSymbol(key: *const []const u8, item: *const []const u8) i32 {
    return switch (std.mem.order(u8, key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareOpaqueRecordKey(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const fixtures.RawRecord = @ptrCast(@alignCast(item));
    return switch (std.math.order(typed_key.*, typed_item.key)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
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

fn expectTypedCAbiRange(items: []const u32, target: u32, expected: bsearch.IndexRange, compare: bsearch.CComparator(u32, u32)) !void {
    const found = bsearch.search(u32, u32, &target, items, compare);
    const lower = bsearch.lowerBoundIndex(u32, u32, &target, items, compare);
    const upper = bsearch.upperBoundIndex(u32, u32, &target, items, compare);
    const range = bsearch.equalRangeIndex(u32, u32, &target, items, compare);
    const view = bsearch.equalRange(u32, u32, &target, items, compare);

    try std.testing.expectEqual(expected.lower, lower);
    try std.testing.expectEqual(expected.upper, upper);
    try std.testing.expectEqual(expected, range);
    try std.testing.expectEqual(expected.len(), view.len);

    if (expected.isEmpty()) {
        try std.testing.expectEqual(@as(?*const u32, null), found);
    } else {
        const typed_found = found orelse return error.ExpectedMatch;
        try std.testing.expectEqual(target, typed_found.*);
        try std.testing.expectEqual(target, view[0]);
        try std.testing.expectEqual(target, view[expected.len() - 1]);
    }
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
    const duplicates = fixtures.representative_duplicate_values;
    var duplicate_target = @as(u32, 21);
    const typed_range = bsearch.equalRangeIndex(u32, u32, &duplicate_target, duplicates[0..], compareDirectInt);
    try std.testing.expectEqual(bsearch.IndexRange{ .lower = 4, .upper = 7 }, typed_range);

    const raw_range = bsearch.bsearchEqualRangeIndex(&duplicate_target, @ptrCast(duplicates[0..].ptr), duplicates.len, @sizeOf(u32), compareDirectOpaqueInt);
    try std.testing.expectEqual(bsearch.IndexRange{ .lower = 4, .upper = 7 }, raw_range);
}

test "phase 6 bsearch direct equalRange wrappers keep duplicate-span and write-through coverage aligned" {
    const duplicates = fixtures.representative_duplicate_values;
    const duplicate_target = @as(u32, 21);

    const typed_view = bsearch.equalRange(u32, u32, &duplicate_target, duplicates[0..], compareDirectInt);
    try std.testing.expectEqual(@as(usize, 3), typed_view.len);
    try std.testing.expectEqualSlices(u32, &[_]u32{ 21, 21, 21 }, typed_view);

    const missing_target = @as(u32, 22);
    const missing_view = bsearch.equalRange(u32, u32, &missing_target, duplicates[0..], compareDirectInt);
    try std.testing.expectEqual(@as(usize, 0), missing_view.len);
    try std.testing.expectEqual(@intFromPtr(&duplicates[7]), @intFromPtr(missing_view.ptr));

    var mutable_duplicates = duplicates;
    const mutable_view = bsearch.equalRangeMutable(u32, u32, &duplicate_target, mutable_duplicates[0..], compareDirectInt);
    try std.testing.expectEqual(@as(usize, 3), mutable_view.len);
    mutable_view[1] = 22;
    try std.testing.expectEqual(@as(u32, 22), mutable_duplicates[5]);

    const duplicate_bytes = bsearch.bsearchEqualRange(&duplicate_target, @ptrCast(duplicates[0..].ptr), duplicates.len, @sizeOf(u32), compareDirectOpaqueInt);
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(u32)), duplicate_bytes.len);
    const typed_duplicate_bytes: [*]const u32 = @ptrCast(@alignCast(duplicate_bytes.ptr));
    try std.testing.expectEqual(@as(u32, 21), typed_duplicate_bytes[0]);
    try std.testing.expectEqual(@as(u32, 21), typed_duplicate_bytes[2]);

    const missing_bytes = bsearch.bsearchEqualRange(&missing_target, @ptrCast(duplicates[0..].ptr), duplicates.len, @sizeOf(u32), compareDirectOpaqueInt);
    try std.testing.expectEqual(@as(usize, 0), missing_bytes.len);
    try std.testing.expectEqual(@intFromPtr(@as([*]const u8, @ptrCast(duplicates[0..].ptr)) + (7 * @sizeOf(u32))), @intFromPtr(missing_bytes.ptr));

    var mutable_raw_duplicates = duplicates;
    const mutable_bytes = bsearch.bsearchEqualRangeMutable(&duplicate_target, @ptrCast(mutable_raw_duplicates[0..].ptr), mutable_raw_duplicates.len, @sizeOf(u32), compareDirectOpaqueInt);
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(u32)), mutable_bytes.len);
    const typed_mutable_bytes: [*]u32 = @ptrCast(@alignCast(mutable_bytes.ptr));
    typed_mutable_bytes[1] = 22;
    try std.testing.expectEqual(@as(u32, 22), mutable_raw_duplicates[5]);
}

test "phase 6 bsearch direct descending equalRange wrappers keep duplicate-span and write-through coverage aligned" {
    const descending_duplicates = fixtures.representative_descending_duplicate_values;
    const duplicate_target = @as(u32, 21);

    const typed_view = bsearch.equalRange(u32, u32, &duplicate_target, descending_duplicates[0..], compareDirectDescendingInt);
    try std.testing.expectEqual(@as(usize, 3), typed_view.len);
    try std.testing.expectEqualSlices(u32, &[_]u32{ 21, 21, 21 }, typed_view);

    const missing_target = @as(u32, 20);
    const missing_view = bsearch.equalRange(u32, u32, &missing_target, descending_duplicates[0..], compareDirectDescendingInt);
    try std.testing.expectEqual(@as(usize, 0), missing_view.len);
    try std.testing.expectEqual(@intFromPtr(&descending_duplicates[6]), @intFromPtr(missing_view.ptr));

    var mutable_duplicates = descending_duplicates;
    const mutable_view = bsearch.equalRangeMutable(u32, u32, &duplicate_target, mutable_duplicates[0..], compareDirectDescendingInt);
    try std.testing.expectEqual(@as(usize, 3), mutable_view.len);
    mutable_view[1] = 22;
    try std.testing.expectEqual(@as(u32, 22), mutable_duplicates[4]);

    const duplicate_bytes = bsearch.bsearchEqualRange(&duplicate_target, @ptrCast(descending_duplicates[0..].ptr), descending_duplicates.len, @sizeOf(u32), compareDirectOpaqueDescendingInt);
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(u32)), duplicate_bytes.len);
    const typed_duplicate_bytes: [*]const u32 = @ptrCast(@alignCast(duplicate_bytes.ptr));
    try std.testing.expectEqual(@as(u32, 21), typed_duplicate_bytes[0]);
    try std.testing.expectEqual(@as(u32, 21), typed_duplicate_bytes[2]);

    const missing_bytes = bsearch.bsearchEqualRange(&missing_target, @ptrCast(descending_duplicates[0..].ptr), descending_duplicates.len, @sizeOf(u32), compareDirectOpaqueDescendingInt);
    try std.testing.expectEqual(@as(usize, 0), missing_bytes.len);
    try std.testing.expectEqual(@intFromPtr(@as([*]const u8, @ptrCast(descending_duplicates[0..].ptr)) + (6 * @sizeOf(u32))), @intFromPtr(missing_bytes.ptr));

    var mutable_raw_duplicates = descending_duplicates;
    const mutable_bytes = bsearch.bsearchEqualRangeMutable(&duplicate_target, @ptrCast(mutable_raw_duplicates[0..].ptr), mutable_raw_duplicates.len, @sizeOf(u32), compareDirectOpaqueDescendingInt);
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(u32)), mutable_bytes.len);
    const typed_mutable_bytes: [*]u32 = @ptrCast(@alignCast(mutable_bytes.ptr));
    typed_mutable_bytes[1] = 22;
    try std.testing.expectEqual(@as(u32, 22), mutable_raw_duplicates[4]);
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

test "phase 6 bsearch accepts runtime-selected typed c abi comparator pointers" {
    const ascending_duplicates = fixtures.representative_duplicate_values;
    const descending_duplicates = fixtures.representative_descending_duplicate_values;

    const cases = [_]struct {
        items: []const u32,
        target: u32,
        expected: bsearch.IndexRange,
        compare: bsearch.CComparator(u32, u32),
    }{
        .{ .items = ascending_duplicates[0..], .target = 21, .expected = .{ .lower = 4, .upper = 7 }, .compare = compareCDirectInt },
        .{ .items = ascending_duplicates[0..], .target = 20, .expected = .{ .lower = 4, .upper = 4 }, .compare = compareCDirectInt },
        .{ .items = descending_duplicates[0..], .target = 21, .expected = .{ .lower = 3, .upper = 6 }, .compare = compareCDirectDescendingInt },
        .{ .items = descending_duplicates[0..], .target = 20, .expected = .{ .lower = 6, .upper = 6 }, .compare = compareCDirectDescendingInt },
    };

    for (cases) |case| {
        try expectTypedCAbiRange(case.items, case.target, case.expected, case.compare);
    }
}

test "phase 6 bsearch keeps symbol fixtures searchable through typed bounds" {
    const hit_symbol: []const u8 = "kmalloc";
    const hit_index = bsearch.searchIndex([]const u8, []const u8, &hit_symbol, fixtures.sorted_symbols[0..], compareSymbol) orelse return error.ExpectedMatch;
    try std.testing.expectEqual(@as(usize, 2), hit_index);
    try std.testing.expectEqual(@as(usize, 2), bsearch.lowerBoundIndex([]const u8, []const u8, &hit_symbol, fixtures.sorted_symbols[0..], compareSymbol));
    try std.testing.expectEqual(@as(usize, 3), bsearch.upperBoundIndex([]const u8, []const u8, &hit_symbol, fixtures.sorted_symbols[0..], compareSymbol));

    const miss_symbol: []const u8 = "kzalloc";
    try std.testing.expectEqual(@as(?usize, null), bsearch.searchIndex([]const u8, []const u8, &miss_symbol, fixtures.sorted_symbols[0..], compareSymbol));
    try std.testing.expectEqual(@as(usize, 3), bsearch.lowerBoundIndex([]const u8, []const u8, &miss_symbol, fixtures.sorted_symbols[0..], compareSymbol));
    try std.testing.expectEqual(@as(usize, 3), bsearch.upperBoundIndex([]const u8, []const u8, &miss_symbol, fixtures.sorted_symbols[0..], compareSymbol));
}

test "phase 6 bsearch keeps packed-record fixtures searchable through raw wrappers" {
    const target = @as(u32, 21);
    const found = bsearch.bsearch(&target, @ptrCast(fixtures.packed_record_values[0..].ptr), fixtures.packed_record_values.len, @sizeOf(fixtures.RawRecord), compareOpaqueRecordKey) orelse return error.ExpectedMatch;
    const typed_found: *const fixtures.RawRecord = @ptrCast(@alignCast(found));
    try std.testing.expectEqual(@as(u32, 21), typed_found.key);
    try std.testing.expectEqual(@as(u32, 0x15000), typed_found.value);

    const range = bsearch.bsearchEqualRangeIndex(&target, @ptrCast(fixtures.packed_record_values[0..].ptr), fixtures.packed_record_values.len, @sizeOf(fixtures.RawRecord), compareOpaqueRecordKey);
    try std.testing.expectEqual(bsearch.IndexRange{ .lower = 3, .upper = 4 }, range);

    var mutable_records = fixtures.packed_record_values;
    const mutable_found = bsearch.bsearchMutable(&target, @ptrCast(mutable_records[0..].ptr), mutable_records.len, @sizeOf(fixtures.RawRecord), compareOpaqueRecordKey) orelse return error.ExpectedMatch;
    const typed_mutable_found: *fixtures.RawRecord = @ptrCast(@alignCast(mutable_found));
    typed_mutable_found.value = 0x15001;
    try std.testing.expectEqual(@as(u32, 0x15001), mutable_records[3].value);
}
