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
    const values = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };
    const comparators = [_]bsearch.CComparator(u32, u32){ compareU32C, compareU32C };

    for (comparators) |compare| {
        try std.testing.expectEqual(@as(?usize, 4), bsearch.searchIndex(u32, u32, &@as(u32, 34), values[0..], compare));
        const found = bsearch.search(u32, u32, &@as(u32, 13), values[0..], compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(@as(u32, 13), found.*);
        try std.testing.expect(bsearch.search(u32, u32, &@as(u32, 7), values[0..], compare) == null);
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
