// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub fn searchIndex(
    comptime Key: type,
    comptime T: type,
    key: *const Key,
    items: []const T,
    comptime compare: fn (*const Key, *const T) i32,
) ?usize {
    var base: usize = 0;
    var num = items.len;

    while (num > 0) {
        const pivot_index = base + (num >> 1);
        const pivot: *const T = &items[pivot_index];
        const result = compare(key, pivot);

        if (result == 0) {
            return pivot_index;
        }
        if (result > 0) {
            base = pivot_index + 1;
            num -= 1;
        }
        num >>= 1;
    }

    return null;
}

pub fn search(
    comptime Key: type,
    comptime T: type,
    key: *const Key,
    items: []const T,
    comptime compare: fn (*const Key, *const T) i32,
) ?*const T {
    const index = searchIndex(Key, T, key, items, compare) orelse return null;
    return &items[index];
}

pub fn searchMutable(
    comptime Key: type,
    comptime T: type,
    key: *const Key,
    items: []T,
    comptime compare: fn (*const Key, *const T) i32,
) ?*T {
    const index = searchIndex(Key, T, key, items, compare) orelse return null;
    return &items[index];
}

fn compareInt(key: *const i32, item: *const i32) i32 {
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

const Entry = struct {
    name: []const u8,
    value: u32,
};

fn compareName(key: *const []const u8, item: *const Entry) i32 {
    return switch (std.mem.order(u8, key.*, item.name)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

test "searchIndex finds values at the beginning middle and end of a sorted slice" {
    const values = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };

    try std.testing.expectEqual(@as(?usize, 0), searchIndex(i32, i32, &@as(i32, 2), values[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, 3), searchIndex(i32, i32, &@as(i32, 11), values[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, 6), searchIndex(i32, i32, &@as(i32, 42), values[0..], compareInt));
}

test "searchIndex returns null for empty slices and missing values" {
    const values = [_]i32{ 3, 5, 8, 13, 21 };
    const empty = [_]i32{};

    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 8), empty[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 1), values[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 9), values[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 34), values[0..], compareInt));
}

test "search returns a pointer to the matching element" {
    const values = [_]i32{ 5, 9, 12, 18, 27 };
    const found = search(i32, i32, &@as(i32, 18), values[0..], compareInt) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(i32, 18), found.*);
    try std.testing.expectEqual(@intFromPtr(&values[3]), @intFromPtr(found));
}

test "searchMutable returns a writable pointer to the matching element" {
    var values = [_]i32{ 5, 9, 12, 18, 27 };
    const found = searchMutable(i32, i32, &@as(i32, 18), values[0..], compareInt) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@intFromPtr(&values[3]), @intFromPtr(found));
    found.* = 19;
    try std.testing.expectEqual(@as(i32, 19), values[3]);
}

test "search accepts duplicate keys without claiming stable selection" {
    const values = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const index = searchIndex(i32, i32, &@as(i32, 4), values[0..], compareInt) orelse return error.TestUnexpectedResult;
    const found = search(i32, i32, &@as(i32, 4), values[0..], compareInt) orelse return error.TestUnexpectedResult;
    const found_index = (@intFromPtr(found) - @intFromPtr(&values[0])) / @sizeOf(i32);

    try std.testing.expect(index >= 1 and index <= 3);
    try std.testing.expectEqual(@as(i32, 4), values[index]);
    try std.testing.expect(found_index >= 1 and found_index <= 3);
    try std.testing.expectEqual(@as(i32, 4), found.*);
}

test "search supports heterogeneous keys through the comparator" {
    const entries = [_]Entry{
        .{ .name = "alpha", .value = 1 },
        .{ .name = "beta", .value = 2 },
        .{ .name = "delta", .value = 4 },
        .{ .name = "omega", .value = 24 },
    };

    const beta = search([]const u8, Entry, &@as([]const u8, "beta"), entries[0..], compareName) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(u32, 2), beta.value);
    try std.testing.expect(search([]const u8, Entry, &@as([]const u8, "gamma"), entries[0..], compareName) == null);
}
