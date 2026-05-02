const std = @import("std");
const bsearch = @import("bsearch");

const Symbol = struct {
    name: []const u8,
    address: usize,
};

var counted_compare_calls: usize = 0;

fn compareU32(key: *const u32, item: *const u32) i32 {
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareDescendingU32(key: *const u32, item: *const u32) i32 {
    return compareU32(item, key);
}

fn compareCU32(key: *const u32, item: *const u32) callconv(.c) i32 {
    return compareU32(key, item);
}

fn compareCDescendingU32(key: *const u32, item: *const u32) callconv(.c) i32 {
    return compareU32(item, key);
}

fn compareOpaqueU32(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareU32(typed_key, typed_item);
}

fn compareOpaqueDescendingU32(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareDescendingU32(typed_key, typed_item);
}

fn compareCOpaqueU32(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    return compareOpaqueU32(key, item);
}

fn compareCOpaqueDescendingU32(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    return compareOpaqueDescendingU32(key, item);
}

test "phase 6 bsearch module imports cleanly" {
    _ = bsearch;
}

test "phase 6 bsearch finds integer keys across the slice" {
    const values = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };

    try std.testing.expectEqual(@as(?usize, 0), bsearch.searchIndex(u32, u32, &@as(u32, 3), values[0..], compareU32));
    try std.testing.expectEqual(@as(?usize, 3), bsearch.searchIndex(u32, u32, &@as(u32, 21), values[0..], compareU32));
    try std.testing.expectEqual(@as(?usize, 6), bsearch.searchIndex(u32, u32, &@as(u32, 89), values[0..], compareU32));
}

test "phase 6 bsearch rejects missing integer keys without widening the contract" {
    const values = [_]u32{ 1, 4, 9, 16, 25, 36 };

    try std.testing.expectEqual(@as(?usize, null), bsearch.searchIndex(u32, u32, &@as(u32, 0), values[0..], compareU32));
    try std.testing.expectEqual(@as(?usize, null), bsearch.searchIndex(u32, u32, &@as(u32, 15), values[0..], compareU32));
    try std.testing.expectEqual(@as(?usize, null), bsearch.searchIndex(u32, u32, &@as(u32, 40), values[0..], compareU32));
}

test "phase 6 bsearch keeps singleton and empty slices on the same found-or-null boundary" {
    const empty = [_]u32{};
    var singleton = [_]u32{21};

    try std.testing.expectEqual(@as(?usize, 0), bsearch.searchIndex(u32, u32, &@as(u32, 21), singleton[0..], compareU32));
    try std.testing.expectEqual(@as(?usize, null), bsearch.searchIndex(u32, u32, &@as(u32, 20), singleton[0..], compareU32));
    try std.testing.expect(bsearch.search(u32, u32, &@as(u32, 21), empty[0..], compareU32) == null);

    const found = bsearch.searchMutable(u32, u32, &@as(u32, 21), singleton[0..], compareU32) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@intFromPtr(&singleton[0]), @intFromPtr(found));
    found.* = 22;
    try std.testing.expectEqual(@as(u32, 22), singleton[0]);
}

test "phase 6 bsearch supports string keys against sorted records" {
    const symbols = [_]Symbol{
        .{ .name = "do_exit", .address = 0x1000 },
        .{ .name = "kfree", .address = 0x1200 },
        .{ .name = "kmalloc", .address = 0x1400 },
        .{ .name = "schedule", .address = 0x1800 },
    };

    const found = bsearch.search([]const u8, Symbol, &@as([]const u8, "kmalloc"), symbols[0..], compareSymbolName) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0x1400), found.address);
    try std.testing.expectEqual(@intFromPtr(&symbols[2]), @intFromPtr(found));
    try std.testing.expect(bsearch.search([]const u8, Symbol, &@as([]const u8, "vfree"), symbols[0..], compareSymbolName) == null);
}

test "phase 6 bsearch exposes a mutable pointer when searching mutable storage" {
    var values = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };
    const found = bsearch.searchMutable(u32, u32, &@as(u32, 21), values[0..], compareU32) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@intFromPtr(&values[3]), @intFromPtr(found));
    found.* = 22;
    try std.testing.expectEqual(@as(u32, 22), values[3]);
}

test "phase 6 bsearch exposes the raw Linux-style helper contract" {
    const values = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };
    const descending = [_]u32{ 89, 55, 34, 21, 13, 8, 3 };
    var mutable_values = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };

    try std.testing.expectEqual(
        @as(?usize, 4),
        bsearch.bsearchIndex(&@as(u32, 34), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compareOpaqueU32),
    );
    try std.testing.expectEqual(
        @as(?usize, null),
        bsearch.bsearchIndex(&@as(u32, 20), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compareOpaqueU32),
    );
    try std.testing.expectEqual(
        @as(?usize, 2),
        bsearch.bsearchIndex(&@as(u32, 34), @ptrCast(descending[0..].ptr), descending.len, @sizeOf(u32), compareOpaqueDescendingU32),
    );

    const found = bsearch.bsearch(&@as(u32, 21), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compareOpaqueU32) orelse return error.TestUnexpectedResult;
    const typed_found: *const u32 = @ptrCast(@alignCast(found));
    try std.testing.expectEqual(@as(u32, 21), typed_found.*);
    try std.testing.expectEqual(@intFromPtr(&values[3]), @intFromPtr(typed_found));

    const found_mutable = bsearch.bsearchMutable(&@as(u32, 21), @ptrCast(mutable_values[0..].ptr), mutable_values.len, @sizeOf(u32), compareOpaqueU32) orelse return error.TestUnexpectedResult;
    const typed_found_mutable: *u32 = @ptrCast(@alignCast(found_mutable));
    typed_found_mutable.* = 22;
    try std.testing.expectEqual(@as(u32, 22), mutable_values[3]);
}

test "phase 6 bsearch treats duplicate keys as found-or-null without claiming stable selection" {
    const cases = [_]struct {
        values: [6]u32,
        needle: u32,
        lower: usize,
        upper: usize,
    }{
        .{ .values = .{ 7, 7, 7, 12, 18, 24 }, .needle = 7, .lower = 0, .upper = 2 },
        .{ .values = .{ 2, 7, 7, 7, 12, 18 }, .needle = 7, .lower = 1, .upper = 3 },
        .{ .values = .{ 2, 7, 12, 18, 18, 18 }, .needle = 18, .lower = 3, .upper = 5 },
    };

    for (cases) |case| {
        const values = case.values;
        const index = bsearch.searchIndex(u32, u32, &case.needle, values[0..], compareU32) orelse return error.TestUnexpectedResult;
        const found = bsearch.search(u32, u32, &case.needle, values[0..], compareU32) orelse return error.TestUnexpectedResult;
        const found_index = (@intFromPtr(found) - @intFromPtr(&values[0])) / @sizeOf(u32);

        try std.testing.expect(index >= case.lower and index <= case.upper);
        try std.testing.expectEqual(case.needle, values[index]);
        try std.testing.expect(found_index >= case.lower and found_index <= case.upper);
        try std.testing.expectEqual(case.needle, found.*);
    }
}

test "phase 6 bsearch keeps representative lookup work inside a binary-search budget" {
    const values = [_]u32{ 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45 };

    counted_compare_calls = 0;
    try std.testing.expectEqual(@as(?usize, 0), bsearch.searchIndex(u32, u32, &@as(u32, 3), values[0..], compareU32Counted));
    try std.testing.expect(counted_compare_calls <= 4);

    counted_compare_calls = 0;
    try std.testing.expectEqual(@as(?usize, 7), bsearch.searchIndex(u32, u32, &@as(u32, 24), values[0..], compareU32Counted));
    try std.testing.expect(counted_compare_calls <= 4);

    counted_compare_calls = 0;
    try std.testing.expectEqual(@as(?usize, 14), bsearch.searchIndex(u32, u32, &@as(u32, 45), values[0..], compareU32Counted));
    try std.testing.expect(counted_compare_calls <= 4);

    counted_compare_calls = 0;
    try std.testing.expectEqual(@as(?usize, null), bsearch.searchIndex(u32, u32, &@as(u32, 26), values[0..], compareU32Counted));
    try std.testing.expect(counted_compare_calls <= 4);

    counted_compare_calls = 0;
    try std.testing.expectEqual(@as(?usize, null), bsearch.searchIndex(u32, u32, &@as(u32, 50), values[0..], compareU32Counted));
    try std.testing.expect(counted_compare_calls <= 4);
}

test "phase 6 bsearch keeps runtime-selected typed and raw comparator paths inside the same comparison budget" {
    const ascending = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };
    const descending = [_]u32{ 89, 55, 34, 21, 13, 8, 3 };
    const budget = std.math.log2_int_ceil(usize, ascending.len) + 1;

    const typed_cases = [_]struct {
        key: u32,
        values: []const u32,
        compare: bsearch.Comparator(u32, u32),
        expected: ?usize,
    }{
        .{ .key = 34, .values = ascending[0..], .compare = compareU32Counted, .expected = 4 },
        .{ .key = 34, .values = descending[0..], .compare = compareDescendingU32Counted, .expected = 2 },
        .{ .key = 20, .values = ascending[0..], .compare = compareU32Counted, .expected = null },
        .{ .key = 20, .values = descending[0..], .compare = compareDescendingU32Counted, .expected = null },
    };

    for (typed_cases) |case| {
        counted_compare_calls = 0;
        try std.testing.expectEqual(case.expected, bsearch.searchIndex(u32, u32, &case.key, case.values, case.compare));
        try std.testing.expect(counted_compare_calls <= budget);
    }

    const c_typed_cases = [_]struct {
        key: u32,
        values: []const u32,
        compare: bsearch.CComparator(u32, u32),
        expected: ?usize,
    }{
        .{ .key = 34, .values = ascending[0..], .compare = compareCU32Counted, .expected = 4 },
        .{ .key = 34, .values = descending[0..], .compare = compareCDescendingU32Counted, .expected = 2 },
        .{ .key = 20, .values = ascending[0..], .compare = compareCU32Counted, .expected = null },
        .{ .key = 20, .values = descending[0..], .compare = compareCDescendingU32Counted, .expected = null },
    };

    for (c_typed_cases) |case| {
        counted_compare_calls = 0;
        try std.testing.expectEqual(case.expected, bsearch.searchIndex(u32, u32, &case.key, case.values, case.compare));
        try std.testing.expect(counted_compare_calls <= budget);
    }

    const raw_cases = [_]struct {
        key: u32,
        values: []const u32,
        compare: bsearch.RawComparator,
        expected: ?usize,
    }{
        .{ .key = 34, .values = ascending[0..], .compare = compareOpaqueU32Counted, .expected = 4 },
        .{ .key = 34, .values = descending[0..], .compare = compareOpaqueDescendingU32Counted, .expected = 2 },
        .{ .key = 20, .values = ascending[0..], .compare = compareOpaqueU32Counted, .expected = null },
        .{ .key = 20, .values = descending[0..], .compare = compareOpaqueDescendingU32Counted, .expected = null },
    };

    for (raw_cases) |case| {
        counted_compare_calls = 0;
        try std.testing.expectEqual(
            case.expected,
            bsearch.bsearchIndex(&case.key, @ptrCast(case.values.ptr), case.values.len, @sizeOf(u32), case.compare),
        );
        try std.testing.expect(counted_compare_calls <= budget);
    }

    const c_raw_cases = [_]struct {
        key: u32,
        values: []const u32,
        compare: bsearch.CRawComparator,
        expected: ?usize,
    }{
        .{ .key = 34, .values = ascending[0..], .compare = compareCOpaqueU32Counted, .expected = 4 },
        .{ .key = 34, .values = descending[0..], .compare = compareCOpaqueDescendingU32Counted, .expected = 2 },
        .{ .key = 20, .values = ascending[0..], .compare = compareCOpaqueU32Counted, .expected = null },
        .{ .key = 20, .values = descending[0..], .compare = compareCOpaqueDescendingU32Counted, .expected = null },
    };

    for (c_raw_cases) |case| {
        counted_compare_calls = 0;
        try std.testing.expectEqual(
            case.expected,
            bsearch.bsearchIndex(&case.key, @ptrCast(case.values.ptr), case.values.len, @sizeOf(u32), case.compare),
        );
        try std.testing.expect(counted_compare_calls <= budget);
    }
}

test "phase 6 bsearch accepts runtime-selected comparator function pointers" {
    const ascending = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };
    const descending = [_]u32{ 89, 55, 34, 21, 13, 8, 3 };
    const comparators = [_]bsearch.Comparator(u32, u32){ compareU32, compareDescendingU32 };
    const slices = [_][]const u32{ ascending[0..], descending[0..] };
    const targets = [_]u32{ 34, 13 };

    for (comparators, slices, targets) |compare, items, target| {
        const found = bsearch.search(u32, u32, &target, items, compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(target, found.*);
    }
}

test "phase 6 bsearch accepts runtime-selected C ABI comparator pointers" {
    const ascending = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };
    const descending = [_]u32{ 89, 55, 34, 21, 13, 8, 3 };
    const comparators = [_]bsearch.CComparator(u32, u32){ compareCU32, compareCDescendingU32 };
    const slices = [_][]const u32{ ascending[0..], descending[0..] };
    const targets = [_]u32{ 55, 34 };

    for (comparators, slices, targets) |compare, items, target| {
        const found = bsearch.search(u32, u32, &target, items, compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(target, found.*);
    }
}

test "phase 6 bsearch accepts runtime-selected raw comparator pointers" {
    const ascending = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };
    const descending = [_]u32{ 89, 55, 34, 21, 13, 8, 3 };
    const comparators = [_]bsearch.RawComparator{ compareOpaqueU32, compareOpaqueDescendingU32 };
    const slices = [_][]const u32{ ascending[0..], descending[0..] };
    const targets = [_]u32{ 55, 34 };

    for (comparators, slices, targets) |compare, items, target| {
        const found = bsearch.bsearch(&target, @ptrCast(items.ptr), items.len, @sizeOf(u32), compare) orelse return error.TestUnexpectedResult;
        const typed_found: *const u32 = @ptrCast(@alignCast(found));
        try std.testing.expectEqual(target, typed_found.*);
    }
}

test "phase 6 bsearch accepts runtime-selected C ABI raw comparator pointers" {
    const ascending = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };
    const descending = [_]u32{ 89, 55, 34, 21, 13, 8, 3 };
    const comparators = [_]bsearch.CRawComparator{ compareCOpaqueU32, compareCOpaqueDescendingU32 };
    const slices = [_][]const u32{ ascending[0..], descending[0..] };
    const targets = [_]u32{ 55, 34 };

    for (comparators, slices, targets) |compare, items, target| {
        const found = bsearch.bsearch(&target, @ptrCast(items.ptr), items.len, @sizeOf(u32), compare) orelse return error.TestUnexpectedResult;
        const typed_found: *const u32 = @ptrCast(@alignCast(found));
        try std.testing.expectEqual(target, typed_found.*);
    }
}

test "phase 6 bsearch exposes runtime-selected mutable typed and raw comparator write-through behavior" {
    var typed_values = [_]u32{ 89, 55, 34, 21, 13, 8, 3 };
    const typed_compare: bsearch.CComparator(u32, u32) = compareCDescendingU32;
    const typed_found = bsearch.searchMutable(u32, u32, &@as(u32, 34), typed_values[0..], typed_compare) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@intFromPtr(&typed_values[2]), @intFromPtr(typed_found));
    typed_found.* += 1;
    try std.testing.expectEqual(@as(u32, 35), typed_values[2]);

    var raw_values = [_]u32{ 89, 55, 34, 21, 13, 8, 3 };
    const raw_compare: bsearch.CRawComparator = compareCOpaqueDescendingU32;
    const raw_found = bsearch.bsearchMutable(&@as(u32, 34), @ptrCast(raw_values[0..].ptr), raw_values.len, @sizeOf(u32), raw_compare) orelse return error.TestUnexpectedResult;
    const typed_raw_found: *u32 = @ptrCast(@alignCast(raw_found));
    try std.testing.expectEqual(@intFromPtr(&raw_values[2]), @intFromPtr(typed_raw_found));
    typed_raw_found.* += 1;
    try std.testing.expectEqual(@as(u32, 35), raw_values[2]);
}
