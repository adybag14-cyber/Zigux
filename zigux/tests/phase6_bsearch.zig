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
