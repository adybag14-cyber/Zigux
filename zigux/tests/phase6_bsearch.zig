const std = @import("std");
const bsearch = @import("bsearch");

const Symbol = struct {
    name: []const u8,
    address: usize,
};

var counted_compare_calls: usize = 0;
var counted_raw_compare_calls: usize = 0;

fn compareU32(key: *const u32, item: *const u32) i32 {
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareU32Alias(key: *const u32, item: *const u32) i32 {
    return compareU32(key, item);
}

fn compareU32C(key: *const u32, item: *const u32) callconv(.c) i32 {
    return compareU32(key, item);
}

fn compareOpaqueU32(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareU32(typed_key, typed_item);
}

fn compareOpaqueU32Counted(key: *const anyopaque, item: *const anyopaque) i32 {
    counted_raw_compare_calls += 1;
    return compareOpaqueU32(key, item);
}

fn compareOpaqueU32C(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    return compareOpaqueU32(key, item);
}

fn compareDescendingU32(key: *const u32, item: *const u32) i32 {
    return switch (std.math.order(item.*, key.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareDescendingU32C(key: *const u32, item: *const u32) callconv(.c) i32 {
    return compareDescendingU32(key, item);
}

fn compareDescendingOpaqueU32(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareDescendingU32(typed_key, typed_item);
}

fn compareDescendingOpaqueU32C(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    return compareDescendingOpaqueU32(key, item);
}

fn compareSymbolName(key: *const []const u8, item: *const Symbol) i32 {
    return switch (std.mem.order(u8, key.*, item.name)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareU32Counted(key: *const u32, item: *const u32) i32 {
    counted_compare_calls += 1;
    return compareU32(key, item);
}

fn compareDescendingU32Counted(key: *const u32, item: *const u32) i32 {
    counted_compare_calls += 1;
    return compareDescendingU32(key, item);
}

fn compareDescendingOpaqueU32Counted(key: *const anyopaque, item: *const anyopaque) i32 {
    counted_raw_compare_calls += 1;
    return compareDescendingOpaqueU32(key, item);
}

fn binarySearchBudget(len: usize) usize {
    if (len == 0) return 0;

    var budget: usize = 0;
    var span: usize = 1;
    while (span < len + 1) : (span <<= 1) {
        budget += 1;
    }
    return budget;
}

fn linearSearchIndexU32(
    key: *const u32,
    items: []const u32,
    compare: anytype,
) ?usize {
    for (items, 0..) |_, index| {
        if (compare(key, &items[index]) == 0) return index;
    }
    return null;
}

fn linearRawSearchIndexU32(
    key: *const anyopaque,
    base: [*]const u8,
    num_members: usize,
    member_size: usize,
    compare: anytype,
) ?usize {
    for (0..num_members) |index| {
        const item: *const anyopaque = @ptrCast(base + (index * member_size));
        if (compare(key, item) == 0) return index;
    }
    return null;
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

test "phase 6 bsearch honors comparator-driven descending order" {
    const values = [_]u32{ 89, 55, 34, 21, 13, 8, 3 };

    try std.testing.expectEqual(@as(?usize, 0), bsearch.searchIndex(u32, u32, &@as(u32, 89), values[0..], compareDescendingU32));
    try std.testing.expectEqual(@as(?usize, 3), bsearch.searchIndex(u32, u32, &@as(u32, 21), values[0..], compareDescendingU32));
    try std.testing.expectEqual(@as(?usize, 6), bsearch.searchIndex(u32, u32, &@as(u32, 3), values[0..], compareDescendingU32));

    const found = bsearch.search(u32, u32, &@as(u32, 34), values[0..], compareDescendingU32) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(u32, 34), found.*);
    try std.testing.expect(bsearch.search(u32, u32, &@as(u32, 22), values[0..], compareDescendingU32) == null);
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

test "phase 6 bsearch mutable typed lookup supports write-through" {
    var values = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };
    const found = bsearch.searchMutable(u32, u32, &@as(u32, 34), values[0..], compareU32) orelse return error.TestUnexpectedResult;

    found.* = 35;
    try std.testing.expectEqual(@as(u32, 35), values[4]);
    try std.testing.expectEqual(@intFromPtr(&values[4]), @intFromPtr(found));
}

test "phase 6 bsearch treats duplicate keys as found-or-null without claiming stable selection" {
    const values = [_]u32{ 2, 7, 7, 7, 12, 18 };
    const index = bsearch.searchIndex(u32, u32, &@as(u32, 7), values[0..], compareU32) orelse return error.TestUnexpectedResult;
    const found = bsearch.search(u32, u32, &@as(u32, 7), values[0..], compareU32) orelse return error.TestUnexpectedResult;
    const found_index = (@intFromPtr(found) - @intFromPtr(&values[0])) / @sizeOf(u32);

    try std.testing.expect(index >= 1 and index <= 3);
    try std.testing.expectEqual(@as(u32, 7), values[index]);
    try std.testing.expect(found_index >= 1 and found_index <= 3);
    try std.testing.expectEqual(@as(u32, 7), found.*);
}

test "phase 6 bsearch singleton typed and raw lookup paths stay inside a one-compare budget" {
    var values = [_]u32{11};
    const raw_values: [*]u8 = @ptrCast(values[0..].ptr);

    counted_compare_calls = 0;
    try std.testing.expectEqual(@as(?usize, 0), bsearch.searchIndex(u32, u32, &@as(u32, 11), values[0..], compareU32Counted));
    try std.testing.expectEqual(@as(usize, 1), counted_compare_calls);

    counted_compare_calls = 0;
    const found = bsearch.search(u32, u32, &@as(u32, 11), values[0..], compareU32Counted) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(u32, 11), found.*);
    try std.testing.expectEqual(@intFromPtr(&values[0]), @intFromPtr(found));
    try std.testing.expectEqual(@as(usize, 1), counted_compare_calls);

    counted_compare_calls = 0;
    try std.testing.expectEqual(@as(?usize, null), bsearch.searchIndex(u32, u32, &@as(u32, 10), values[0..], compareU32Counted));
    try std.testing.expectEqual(@as(usize, 1), counted_compare_calls);

    counted_compare_calls = 0;
    try std.testing.expect(bsearch.search(u32, u32, &@as(u32, 10), values[0..], compareU32Counted) == null);
    try std.testing.expectEqual(@as(usize, 1), counted_compare_calls);

    counted_compare_calls = 0;
    const mutable = bsearch.searchMutable(u32, u32, &@as(u32, 11), values[0..], compareU32Counted) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), counted_compare_calls);
    mutable.* = 12;
    try std.testing.expectEqual(@as(u32, 12), values[0]);
    mutable.* = 11;

    counted_raw_compare_calls = 0;
    try std.testing.expectEqual(
        @as(?usize, 0),
        bsearch.bsearchIndex(&@as(u32, 11), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compareOpaqueU32Counted),
    );
    try std.testing.expectEqual(@as(usize, 1), counted_raw_compare_calls);

    counted_raw_compare_calls = 0;
    const raw_found = bsearch.bsearch(&@as(u32, 11), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compareOpaqueU32Counted) orelse return error.TestUnexpectedResult;
    const typed_raw_found: *const u32 = @ptrCast(@alignCast(raw_found));
    try std.testing.expectEqual(@as(u32, 11), typed_raw_found.*);
    try std.testing.expectEqual(@intFromPtr(&values[0]), @intFromPtr(typed_raw_found));
    try std.testing.expectEqual(@as(usize, 1), counted_raw_compare_calls);

    counted_raw_compare_calls = 0;
    try std.testing.expectEqual(
        @as(?usize, null),
        bsearch.bsearchIndex(&@as(u32, 10), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compareOpaqueU32Counted),
    );
    try std.testing.expectEqual(@as(usize, 1), counted_raw_compare_calls);

    counted_raw_compare_calls = 0;
    try std.testing.expect(
        bsearch.bsearch(&@as(u32, 10), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compareOpaqueU32Counted) == null,
    );
    try std.testing.expectEqual(@as(usize, 1), counted_raw_compare_calls);

    counted_raw_compare_calls = 0;
    const raw_mutable = bsearch.bsearchMutable(&@as(u32, 11), raw_values, values.len, @sizeOf(u32), compareOpaqueU32Counted) orelse return error.TestUnexpectedResult;
    const typed_raw_mutable: *u32 = @ptrCast(@alignCast(raw_mutable));
    try std.testing.expectEqual(@intFromPtr(&values[0]), @intFromPtr(typed_raw_mutable));
    try std.testing.expectEqual(@as(usize, 1), counted_raw_compare_calls);
    typed_raw_mutable.* = 12;
    try std.testing.expectEqual(@as(u32, 12), values[0]);
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

test "phase 6 bsearch keeps descending lookup work inside a binary-search budget" {
    const values = [_]u32{ 45, 42, 39, 36, 33, 30, 27, 24, 21, 18, 15, 12, 9, 6, 3 };
    const raw_values: [*]const u8 = @ptrCast(values[0..].ptr);

    counted_compare_calls = 0;
    try std.testing.expectEqual(@as(?usize, 0), bsearch.searchIndex(u32, u32, &@as(u32, 45), values[0..], compareDescendingU32Counted));
    try std.testing.expect(counted_compare_calls <= 4);

    counted_compare_calls = 0;
    try std.testing.expectEqual(@as(?usize, 7), bsearch.searchIndex(u32, u32, &@as(u32, 24), values[0..], compareDescendingU32Counted));
    try std.testing.expect(counted_compare_calls <= 4);

    counted_compare_calls = 0;
    try std.testing.expectEqual(@as(?usize, 14), bsearch.searchIndex(u32, u32, &@as(u32, 3), values[0..], compareDescendingU32Counted));
    try std.testing.expect(counted_compare_calls <= 4);

    counted_compare_calls = 0;
    try std.testing.expectEqual(@as(?usize, null), bsearch.searchIndex(u32, u32, &@as(u32, 26), values[0..], compareDescendingU32Counted));
    try std.testing.expect(counted_compare_calls <= 4);

    counted_compare_calls = 0;
    try std.testing.expectEqual(@as(?usize, null), bsearch.searchIndex(u32, u32, &@as(u32, 50), values[0..], compareDescendingU32Counted));
    try std.testing.expect(counted_compare_calls <= 4);

    counted_raw_compare_calls = 0;
    try std.testing.expectEqual(
        @as(?usize, 0),
        bsearch.bsearchIndex(&@as(u32, 45), raw_values, values.len, @sizeOf(u32), compareDescendingOpaqueU32Counted),
    );
    try std.testing.expect(counted_raw_compare_calls <= 4);

    counted_raw_compare_calls = 0;
    try std.testing.expectEqual(
        @as(?usize, 7),
        bsearch.bsearchIndex(&@as(u32, 24), raw_values, values.len, @sizeOf(u32), compareDescendingOpaqueU32Counted),
    );
    try std.testing.expect(counted_raw_compare_calls <= 4);

    counted_raw_compare_calls = 0;
    try std.testing.expectEqual(
        @as(?usize, 14),
        bsearch.bsearchIndex(&@as(u32, 3), raw_values, values.len, @sizeOf(u32), compareDescendingOpaqueU32Counted),
    );
    try std.testing.expect(counted_raw_compare_calls <= 4);

    counted_raw_compare_calls = 0;
    try std.testing.expectEqual(
        @as(?usize, null),
        bsearch.bsearchIndex(&@as(u32, 26), raw_values, values.len, @sizeOf(u32), compareDescendingOpaqueU32Counted),
    );
    try std.testing.expect(counted_raw_compare_calls <= 4);

    counted_raw_compare_calls = 0;
    try std.testing.expectEqual(
        @as(?usize, null),
        bsearch.bsearchIndex(&@as(u32, 50), raw_values, values.len, @sizeOf(u32), compareDescendingOpaqueU32Counted),
    );
    try std.testing.expect(counted_raw_compare_calls <= 4);
}

test "phase 6 bsearch raw lookup returns null for empty input without invoking the comparator" {
    const empty = [_]u32{};

    counted_raw_compare_calls = 0;
    try std.testing.expectEqual(
        @as(?usize, null),
        bsearch.bsearchIndex(&@as(u32, 5), @ptrCast(empty[0..].ptr), empty.len, @sizeOf(u32), compareOpaqueU32Counted),
    );
    try std.testing.expectEqual(@as(usize, 0), counted_raw_compare_calls);
    try std.testing.expect(
        bsearch.bsearch(&@as(u32, 5), @ptrCast(empty[0..].ptr), empty.len, @sizeOf(u32), compareOpaqueU32Counted) == null,
    );
    try std.testing.expectEqual(@as(usize, 0), counted_raw_compare_calls);
}

test "phase 6 bsearch raw lookup keeps representative work inside a binary-search budget" {
    const values = [_]u32{ 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45 };
    const raw_values: [*]const u8 = @ptrCast(values[0..].ptr);

    counted_raw_compare_calls = 0;
    try std.testing.expectEqual(
        @as(?usize, 0),
        bsearch.bsearchIndex(&@as(u32, 3), raw_values, values.len, @sizeOf(u32), compareOpaqueU32Counted),
    );
    try std.testing.expect(counted_raw_compare_calls <= 4);

    counted_raw_compare_calls = 0;
    try std.testing.expectEqual(
        @as(?usize, 7),
        bsearch.bsearchIndex(&@as(u32, 24), raw_values, values.len, @sizeOf(u32), compareOpaqueU32Counted),
    );
    try std.testing.expect(counted_raw_compare_calls <= 4);

    counted_raw_compare_calls = 0;
    try std.testing.expectEqual(
        @as(?usize, 14),
        bsearch.bsearchIndex(&@as(u32, 45), raw_values, values.len, @sizeOf(u32), compareOpaqueU32Counted),
    );
    try std.testing.expect(counted_raw_compare_calls <= 4);

    counted_raw_compare_calls = 0;
    try std.testing.expectEqual(
        @as(?usize, null),
        bsearch.bsearchIndex(&@as(u32, 26), raw_values, values.len, @sizeOf(u32), compareOpaqueU32Counted),
    );
    try std.testing.expect(counted_raw_compare_calls <= 4);

    counted_raw_compare_calls = 0;
    try std.testing.expectEqual(
        @as(?usize, null),
        bsearch.bsearchIndex(&@as(u32, 50), raw_values, values.len, @sizeOf(u32), compareOpaqueU32Counted),
    );
    try std.testing.expect(counted_raw_compare_calls <= 4);
}

test "phase 6 bsearch bounded typed and raw equality probes stay inside a binary-search budget" {
    var ascending_storage: [32]u32 = undefined;
    var descending_storage: [32]u32 = undefined;

    for (0..ascending_storage.len + 1) |len| {
        for (0..len) |index| {
            const value = @as(u32, @intCast((index + 1) * 2));
            ascending_storage[index] = value;
            descending_storage[len - 1 - index] = value;
        }

        const ascending = ascending_storage[0..len];
        const descending = descending_storage[0..len];
        const budget = binarySearchBudget(len);
        const max_probe: u32 = if (len == 0) 1 else @as(u32, @intCast((len * 2) + 1));
        const ascending_raw: [*]const u8 = @ptrCast(ascending.ptr);
        const descending_raw: [*]const u8 = @ptrCast(descending.ptr);

        var probe: u32 = 1;
        while (probe <= max_probe) : (probe += 1) {
            counted_compare_calls = 0;
            const expected_ascending = linearSearchIndexU32(&probe, ascending, compareU32);
            try std.testing.expectEqual(
                expected_ascending,
                bsearch.searchIndex(u32, u32, &probe, ascending, compareU32Counted),
            );
            try std.testing.expect(counted_compare_calls <= budget);

            counted_compare_calls = 0;
            const expected_descending = linearSearchIndexU32(&probe, descending, compareDescendingU32);
            try std.testing.expectEqual(
                expected_descending,
                bsearch.searchIndex(u32, u32, &probe, descending, compareDescendingU32Counted),
            );
            try std.testing.expect(counted_compare_calls <= budget);

            counted_raw_compare_calls = 0;
            const expected_raw_ascending = linearRawSearchIndexU32(
                &probe,
                ascending_raw,
                ascending.len,
                @sizeOf(u32),
                compareOpaqueU32,
            );
            try std.testing.expectEqual(
                expected_raw_ascending,
                bsearch.bsearchIndex(&probe, ascending_raw, ascending.len, @sizeOf(u32), compareOpaqueU32Counted),
            );
            try std.testing.expect(counted_raw_compare_calls <= budget);

            counted_raw_compare_calls = 0;
            const expected_raw_descending = linearRawSearchIndexU32(
                &probe,
                descending_raw,
                descending.len,
                @sizeOf(u32),
                compareDescendingOpaqueU32,
            );
            try std.testing.expectEqual(
                expected_raw_descending,
                bsearch.bsearchIndex(&probe, descending_raw, descending.len, @sizeOf(u32), compareDescendingOpaqueU32Counted),
            );
            try std.testing.expect(counted_raw_compare_calls <= budget);
        }
    }
}

test "phase 6 bsearch accepts runtime-selected native comparator pointers" {
    const values = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };
    const comparators = [_]bsearch.Comparator(u32, u32){ compareU32, compareU32Alias };

    for (comparators) |compare| {
        try std.testing.expectEqual(@as(?usize, 3), bsearch.searchIndex(u32, u32, &@as(u32, 21), values[0..], compare));
        const found = bsearch.search(u32, u32, &@as(u32, 55), values[0..], compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(@as(u32, 55), found.*);
        try std.testing.expect(bsearch.search(u32, u32, &@as(u32, 22), values[0..], compare) == null);
    }
}

test "phase 6 bsearch accepts runtime-selected c abi comparator pointers" {
    const values = [_]u32{ 89, 55, 34, 21, 13, 8, 3 };
    const ascending_comparators = [_]bsearch.CComparator(u32, u32){ compareU32C, compareU32C };
    const descending_comparators = [_]bsearch.CComparator(u32, u32){ compareDescendingU32C, compareDescendingU32C };

    for (ascending_comparators) |compare| {
        const ascending_values = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };
        try std.testing.expectEqual(@as(?usize, 4), bsearch.searchIndex(u32, u32, &@as(u32, 34), ascending_values[0..], compare));
        const found = bsearch.search(u32, u32, &@as(u32, 13), ascending_values[0..], compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(@as(u32, 13), found.*);
        try std.testing.expect(bsearch.search(u32, u32, &@as(u32, 7), ascending_values[0..], compare) == null);
    }

    for (descending_comparators) |compare| {
        try std.testing.expectEqual(@as(?usize, 3), bsearch.searchIndex(u32, u32, &@as(u32, 21), values[0..], compare));
        const found = bsearch.search(u32, u32, &@as(u32, 13), values[0..], compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(@as(u32, 13), found.*);
        try std.testing.expect(bsearch.search(u32, u32, &@as(u32, 22), values[0..], compare) == null);
    }
}

test "phase 6 bsearch accepts runtime-selected raw native comparator pointers" {
    const values = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };
    const comparators = [_]bsearch.RawComparator{ compareOpaqueU32, compareOpaqueU32 };

    for (comparators) |compare| {
        try std.testing.expectEqual(
            @as(?usize, 4),
            bsearch.bsearchIndex(&@as(u32, 34), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compare),
        );
        const found = bsearch.bsearch(&@as(u32, 13), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compare) orelse return error.TestUnexpectedResult;
        const typed_found: *const u32 = @ptrCast(@alignCast(found));
        try std.testing.expectEqual(@as(u32, 13), typed_found.*);
        try std.testing.expectEqual(
            @as(?usize, null),
            bsearch.bsearchIndex(&@as(u32, 7), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compare),
        );
    }
}

test "phase 6 bsearch mutable raw lookup supports descending write-through" {
    var values = [_]u32{ 89, 55, 34, 21, 13, 8, 3 };
    const comparators = [_]bsearch.RawComparator{ compareDescendingOpaqueU32, compareDescendingOpaqueU32 };

    for (comparators) |compare| {
        const index = bsearch.bsearchIndex(
            &@as(u32, 21),
            @ptrCast(values[0..].ptr),
            values.len,
            @sizeOf(u32),
            compare,
        ) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(@as(usize, 3), index);

        const found = bsearch.bsearch(
            &@as(u32, 13),
            @ptrCast(values[0..].ptr),
            values.len,
            @sizeOf(u32),
            compare,
        ) orelse return error.TestUnexpectedResult;
        const typed_found: *const u32 = @ptrCast(@alignCast(found));
        try std.testing.expectEqual(@as(u32, 13), typed_found.*);
        try std.testing.expectEqual(@intFromPtr(&values[4]), @intFromPtr(typed_found));

        try std.testing.expectEqual(
            @as(?usize, null),
            bsearch.bsearchIndex(
                &@as(u32, 22),
                @ptrCast(values[0..].ptr),
                values.len,
                @sizeOf(u32),
                compare,
            ),
        );
        try std.testing.expect(
            bsearch.bsearch(
                &@as(u32, 22),
                @ptrCast(values[0..].ptr),
                values.len,
                @sizeOf(u32),
                compare,
            ) == null,
        );

        const mutable = bsearch.bsearchMutable(
            &@as(u32, 34),
            @ptrCast(values[0..].ptr),
            values.len,
            @sizeOf(u32),
            compare,
        ) orelse return error.TestUnexpectedResult;
        const typed_mutable: *u32 = @ptrCast(@alignCast(mutable));
        try std.testing.expectEqual(@intFromPtr(&values[2]), @intFromPtr(typed_mutable));
        typed_mutable.* = 35;
        try std.testing.expectEqual(@as(u32, 35), values[2]);
        typed_mutable.* = 34;
    }
}

test "phase 6 bsearch accepts runtime-selected raw c abi comparator pointers" {
    const values = [_]u32{ 2, 7, 7, 7, 12, 18 };
    const comparators = [_]bsearch.CRawComparator{ compareOpaqueU32C, compareOpaqueU32C };

    for (comparators) |compare| {
        const index = bsearch.bsearchIndex(&@as(u32, 7), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compare) orelse return error.TestUnexpectedResult;
        try std.testing.expect(index >= 1 and index <= 3);
        try std.testing.expectEqual(@as(u32, 7), values[index]);

        const found = bsearch.bsearch(&@as(u32, 7), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compare) orelse return error.TestUnexpectedResult;
        const typed_found: *const u32 = @ptrCast(@alignCast(found));
        const found_index = (@intFromPtr(typed_found) - @intFromPtr(&values[0])) / @sizeOf(u32);
        try std.testing.expect(found_index >= 1 and found_index <= 3);
        try std.testing.expectEqual(@as(u32, 7), typed_found.*);
        try std.testing.expectEqual(
            @as(?usize, null),
            bsearch.bsearchIndex(&@as(u32, 8), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compare),
        );
        try std.testing.expect(
            bsearch.bsearch(&@as(u32, 8), @ptrCast(values[0..].ptr), values.len, @sizeOf(u32), compare) == null,
        );
    }
}

test "phase 6 bsearch accepts runtime-selected descending raw c abi comparator pointers" {
    var values = [_]u32{ 89, 55, 34, 21, 21, 21, 13, 8, 3 };
    const comparators = [_]bsearch.CRawComparator{ compareDescendingOpaqueU32C, compareDescendingOpaqueU32C };

    for (comparators) |compare| {
        const index = bsearch.bsearchIndex(
            &@as(u32, 21),
            @ptrCast(values[0..].ptr),
            values.len,
            @sizeOf(u32),
            compare,
        ) orelse return error.TestUnexpectedResult;
        try std.testing.expect(index >= 3 and index <= 5);
        try std.testing.expectEqual(@as(u32, 21), values[index]);

        const found = bsearch.bsearch(
            &@as(u32, 21),
            @ptrCast(values[0..].ptr),
            values.len,
            @sizeOf(u32),
            compare,
        ) orelse return error.TestUnexpectedResult;
        const typed_found: *const u32 = @ptrCast(@alignCast(found));
        const found_index = (@intFromPtr(typed_found) - @intFromPtr(&values[0])) / @sizeOf(u32);
        try std.testing.expect(found_index >= 3 and found_index <= 5);
        try std.testing.expectEqual(@as(u32, 21), typed_found.*);

        try std.testing.expectEqual(
            @as(?usize, null),
            bsearch.bsearchIndex(
                &@as(u32, 22),
                @ptrCast(values[0..].ptr),
                values.len,
                @sizeOf(u32),
                compare,
            ),
        );
        try std.testing.expect(
            bsearch.bsearch(
                &@as(u32, 22),
                @ptrCast(values[0..].ptr),
                values.len,
                @sizeOf(u32),
                compare,
            ) == null,
        );

        const mutable = bsearch.bsearchMutable(
            &@as(u32, 34),
            @ptrCast(values[0..].ptr),
            values.len,
            @sizeOf(u32),
            compare,
        ) orelse return error.TestUnexpectedResult;
        const typed_mutable: *u32 = @ptrCast(@alignCast(mutable));
        try std.testing.expectEqual(@intFromPtr(&values[2]), @intFromPtr(typed_mutable));
        typed_mutable.* = 35;
        try std.testing.expectEqual(@as(u32, 35), values[2]);
        typed_mutable.* = 34;
    }
}

test "phase 6 bsearch mutable raw c abi lookup supports write-through" {
    var values = [_]u32{ 2, 7, 7, 7, 12, 18 };
    const found = bsearch.bsearchMutable(
        &@as(u32, 7),
        @ptrCast(values[0..].ptr),
        values.len,
        @sizeOf(u32),
        compareOpaqueU32C,
    ) orelse return error.TestUnexpectedResult;
    const typed_found: *u32 = @ptrCast(@alignCast(found));
    const found_index = (@intFromPtr(typed_found) - @intFromPtr(&values[0])) / @sizeOf(u32);

    try std.testing.expect(found_index >= 1 and found_index <= 3);
    typed_found.* = 70;
    try std.testing.expectEqual(@as(u32, 70), values[found_index]);
}
