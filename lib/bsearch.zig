// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub fn indexOf(comptime T: type, key: anytype, base: []const T, compare: anytype) ?usize {
    var offset: usize = 0;
    var remaining = base.len;

    while (remaining > 0) {
        const half = remaining >> 1;
        const pivot_index = offset + half;
        const result: std.math.Order = compare(key, &base[pivot_index]);

        switch (result) {
            .eq => return pivot_index,
            .gt => {
                offset = pivot_index + 1;
                remaining -= 1;
            },
            .lt => {},
        }

        remaining >>= 1;
    }

    return null;
}

pub fn bsearch(comptime T: type, key: anytype, base: []const T, compare: anytype) ?*const T {
    const found_index = indexOf(T, key, base, compare) orelse return null;
    return &base[found_index];
}

pub fn bsearchMut(comptime T: type, key: anytype, base: []T, compare: anytype) ?*T {
    const found_index = indexOf(T, key, base, compare) orelse return null;
    return &base[found_index];
}

fn compareInt(target: i32, candidate: *const i32) std.math.Order {
    return std.math.order(target, candidate.*);
}

const NamedValue = struct {
    name: []const u8,
    value: u8,
};

fn compareByName(target: []const u8, candidate: *const NamedValue) std.math.Order {
    return std.mem.order(u8, target, candidate.name);
}

const CountedKey = struct {
    target: u32,
    comparisons: *usize,
};

fn compareCounted(key: CountedKey, candidate: *const u32) std.math.Order {
    key.comparisons.* += 1;
    return std.math.order(key.target, candidate.*);
}

test "bsearch returns a pointer to the matched integer element" {
    const values = [_]i32{ 3, 7, 11, 19, 42, 108 };
    const found = bsearch(i32, 19, values[0..], compareInt) orelse return error.ExpectedMatch;

    try std.testing.expectEqual(@as(i32, 19), found.*);
    try std.testing.expectEqual(@intFromPtr(&values[3]), @intFromPtr(found));
}

test "bsearch can compare a distinct key type against struct fields" {
    const values = [_]NamedValue{
        .{ .name = "alpha", .value = 1 },
        .{ .name = "beta", .value = 2 },
        .{ .name = "delta", .value = 4 },
        .{ .name = "omega", .value = 9 },
    };
    const found = bsearch(NamedValue, "delta", values[0..], compareByName) orelse return error.ExpectedMatch;

    try std.testing.expectEqualStrings("delta", found.name);
    try std.testing.expectEqual(@as(u8, 4), found.value);
}

test "bsearchMut preserves caller ownership by returning a writable alias" {
    var values = [_]NamedValue{
        .{ .name = "alpha", .value = 1 },
        .{ .name = "beta", .value = 2 },
        .{ .name = "delta", .value = 4 },
    };
    const found = bsearchMut(NamedValue, "beta", values[0..], compareByName) orelse return error.ExpectedMatch;

    found.value = 7;
    try std.testing.expectEqual(@as(u8, 7), values[1].value);
    try std.testing.expectEqual(@intFromPtr(&values[1]), @intFromPtr(found));
}

test "indexOf reports misses without inventing a neighbor match" {
    const values = [_]i32{ 2, 4, 6, 8, 10 };

    try std.testing.expectEqual(@as(?usize, null), indexOf(i32, 5, values[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, null), indexOf(i32, -1, values[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, null), indexOf(i32, 11, values[0..], compareInt));
}

test "bsearch keeps comparison counts within a binary-search perf gate for hits and misses" {
    var values: [1024]u32 = undefined;
    for (&values, 0..) |*slot, index| {
        slot.* = @as(u32, @intCast(index * 2));
    }

    var hit_comparisons: usize = 0;
    const hit = bsearch(u32, CountedKey{
        .target = 872,
        .comparisons = &hit_comparisons,
    }, values[0..], compareCounted) orelse return error.ExpectedMatch;
    try std.testing.expectEqual(@as(u32, 872), hit.*);
    try std.testing.expect(hit_comparisons <= 11);

    var miss_comparisons: usize = 0;
    try std.testing.expectEqual(@as(?*const u32, null), bsearch(u32, CountedKey{
        .target = 873,
        .comparisons = &miss_comparisons,
    }, values[0..], compareCounted));
    try std.testing.expect(miss_comparisons <= 11);
}

test "bsearch on an empty slice performs no comparisons" {
    const values = [_]u32{};
    var comparisons: usize = 0;

    try std.testing.expectEqual(@as(?*const u32, null), bsearch(u32, CountedKey{
        .target = 1,
        .comparisons = &comparisons,
    }, values[0..], compareCounted));
    try std.testing.expectEqual(@as(usize, 0), comparisons);
}
