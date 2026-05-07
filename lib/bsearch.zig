// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub fn Comparator(comptime Key: type, comptime T: type) type {
    return *const fn (*const Key, *const T) i32;
}

pub fn CComparator(comptime Key: type, comptime T: type) type {
    return *const fn (*const Key, *const T) callconv(.c) i32;
}

pub const RawComparator = *const fn (*const anyopaque, *const anyopaque) i32;
pub const CRawComparator = *const fn (*const anyopaque, *const anyopaque) callconv(.c) i32;

fn validateComparator(comptime Key: type, comptime T: type, comptime Compare: type) void {
    const NativeFn = fn (*const Key, *const T) i32;
    const CFn = fn (*const Key, *const T) callconv(.c) i32;

    if (Compare != NativeFn and Compare != Comparator(Key, T) and Compare != CFn and Compare != CComparator(Key, T)) {
        @compileError(std.fmt.comptimePrint(
            "unsupported bsearch comparator type {s}; expected {s}, {s}, {s}, or {s}",
            .{
                @typeName(Compare),
                @typeName(NativeFn),
                @typeName(Comparator(Key, T)),
                @typeName(CFn),
                @typeName(CComparator(Key, T)),
            },
        ));
    }
}

fn validateRawComparator(comptime Compare: type) void {
    const NativeFn = fn (*const anyopaque, *const anyopaque) i32;
    const CFn = fn (*const anyopaque, *const anyopaque) callconv(.c) i32;

    if (Compare != NativeFn and Compare != RawComparator and Compare != CFn and Compare != CRawComparator) {
        @compileError(std.fmt.comptimePrint(
            "unsupported raw bsearch comparator type {s}; expected {s}, {s}, {s}, or {s}",
            .{
                @typeName(Compare),
                @typeName(RawComparator),
                @typeName(NativeFn),
                @typeName(CFn),
                @typeName(CRawComparator),
            },
        ));
    }
}

pub fn searchIndex(
    comptime Key: type,
    comptime T: type,
    key: *const Key,
    items: []const T,
    compare: anytype,
) ?usize {
    comptime validateComparator(Key, T, @TypeOf(compare));

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
    compare: anytype,
) ?*const T {
    const index = searchIndex(Key, T, key, items, compare) orelse return null;
    return &items[index];
}

pub fn searchMutable(
    comptime Key: type,
    comptime T: type,
    key: *const Key,
    items: []T,
    compare: anytype,
) ?*T {
    const index = searchIndex(Key, T, key, items, compare) orelse return null;
    return &items[index];
}

pub fn bsearchIndex(
    key: *const anyopaque,
    base: [*]const u8,
    num_members: usize,
    member_size: usize,
    compare: anytype,
) ?usize {
    comptime validateRawComparator(@TypeOf(compare));

    if (num_members == 0) {
        return null;
    }
    std.debug.assert(member_size > 0);

    var base_index: usize = 0;
    var num = num_members;

    while (num > 0) {
        const pivot_index = base_index + (num >> 1);
        const pivot: *const anyopaque = @ptrCast(base + (pivot_index * member_size));
        const result = compare(key, pivot);

        if (result == 0) {
            return pivot_index;
        }
        if (result > 0) {
            base_index = pivot_index + 1;
            num -= 1;
        }
        num >>= 1;
    }

    return null;
}

pub fn bsearch(
    key: *const anyopaque,
    base: [*]const u8,
    num_members: usize,
    member_size: usize,
    compare: anytype,
) ?*const anyopaque {
    const index = bsearchIndex(key, base, num_members, member_size, compare) orelse return null;
    return @ptrCast(base + (index * member_size));
}

pub fn bsearchMutable(
    key: *const anyopaque,
    base: [*]u8,
    num_members: usize,
    member_size: usize,
    compare: anytype,
) ?*anyopaque {
    const index = bsearchIndex(key, base, num_members, member_size, compare) orelse return null;
    return @ptrCast(base + (index * member_size));
}

fn compareInt(key: *const i32, item: *const i32) i32 {
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareIntAlias(key: *const i32, item: *const i32) i32 {
    return compareInt(key, item);
}

fn compareIntC(key: *const i32, item: *const i32) callconv(.c) i32 {
    return compareInt(key, item);
}

fn compareOpaqueInt(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const i32 = @ptrCast(@alignCast(key));
    const typed_item: *const i32 = @ptrCast(@alignCast(item));
    return compareInt(typed_key, typed_item);
}

fn compareOpaqueIntAlias(key: *const anyopaque, item: *const anyopaque) i32 {
    return compareOpaqueInt(key, item);
}

var compare_call_count: usize = 0;
var raw_compare_call_count: usize = 0;

fn compareIntCounted(key: *const i32, item: *const i32) i32 {
    compare_call_count += 1;
    return compareInt(key, item);
}

fn compareIntDescending(key: *const i32, item: *const i32) i32 {
    return compareInt(item, key);
}

fn compareIntDescendingAlias(key: *const i32, item: *const i32) i32 {
    return compareIntDescending(key, item);
}

fn compareIntDescendingCounted(key: *const i32, item: *const i32) i32 {
    compare_call_count += 1;
    return compareIntDescending(key, item);
}

fn compareOpaqueIntCounted(key: *const anyopaque, item: *const anyopaque) i32 {
    raw_compare_call_count += 1;
    return compareOpaqueInt(key, item);
}

fn compareOpaqueIntDescending(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const i32 = @ptrCast(@alignCast(key));
    const typed_item: *const i32 = @ptrCast(@alignCast(item));
    return compareIntDescending(typed_key, typed_item);
}

fn compareOpaqueIntDescendingAlias(key: *const anyopaque, item: *const anyopaque) i32 {
    return compareOpaqueIntDescending(key, item);
}

fn compareOpaqueIntDescendingCounted(key: *const anyopaque, item: *const anyopaque) i32 {
    raw_compare_call_count += 1;
    return compareOpaqueIntDescending(key, item);
}

fn compareOpaqueIntC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    return compareOpaqueInt(key, item);
}

fn compareOpaqueIntDescendingC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    return compareOpaqueIntDescending(key, item);
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

fn binarySearchBudget(len: usize) usize {
    if (len == 0) {
        return 0;
    }

    var budget: usize = 0;
    var span: usize = 1;
    while (span < len + 1) : (span <<= 1) {
        budget += 1;
    }

    return budget;
}

fn linearSearchIndex(
    comptime Key: type,
    comptime T: type,
    key: *const Key,
    items: []const T,
    compare: anytype,
) ?usize {
    for (items, 0..) |_, index| {
        if (compare(key, &items[index]) == 0) {
            return index;
        }
    }

    return null;
}

fn linearRawSearchIndexI32(
    key: *const anyopaque,
    base: [*]const u8,
    num_members: usize,
    member_size: usize,
    compare: anytype,
) ?usize {
    for (0..num_members) |index| {
        const item: *const anyopaque = @ptrCast(base + (index * member_size));
        if (compare(key, item) == 0) {
            return index;
        }
    }

    return null;
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

test "searchMutable returns a mutable pointer to the matching element" {
    var values = [_]i32{ 5, 9, 12, 18, 27 };
    const found = searchMutable(i32, i32, &@as(i32, 18), values[0..], compareInt) orelse return error.TestUnexpectedResult;

    found.* = 19;
    try std.testing.expectEqual(@as(i32, 19), values[3]);
    try std.testing.expectEqual(@intFromPtr(&values[3]), @intFromPtr(found));
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

test "search accepts explicitly typed native comparator pointers" {
    const values = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };
    const comparators = [_]Comparator(i32, i32){ compareInt, compareIntAlias };

    for (comparators) |compare| {
        try std.testing.expectEqual(@as(?usize, 3), searchIndex(i32, i32, &@as(i32, 11), values[0..], compare));
        const found = search(i32, i32, &@as(i32, 23), values[0..], compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(@as(i32, 23), found.*);
    }
}

test "search accepts explicitly typed c abi comparator pointers" {
    const values = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };
    const comparators = [_]CComparator(i32, i32){ compareIntC, compareIntC };

    for (comparators) |compare| {
        try std.testing.expectEqual(@as(?usize, 4), searchIndex(i32, i32, &@as(i32, 16), values[0..], compare));
        const found = search(i32, i32, &@as(i32, 7), values[0..], compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(@as(i32, 7), found.*);
    }
}

test "search accepts runtime-selected descending native comparator pointers" {
    var values = [_]i32{ 42, 23, 16, 11, 7, 4, 2 };
    const comparators = [_]Comparator(i32, i32){ compareIntDescending, compareIntDescendingAlias };

    for (comparators) |compare| {
        try std.testing.expectEqual(@as(?usize, 3), searchIndex(i32, i32, &@as(i32, 11), values[0..], compare));

        const found = search(i32, i32, &@as(i32, 7), values[0..], compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(@as(i32, 7), found.*);
        try std.testing.expectEqual(@intFromPtr(&values[4]), @intFromPtr(found));

        try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 10), values[0..], compare));
        try std.testing.expect(search(i32, i32, &@as(i32, 10), values[0..], compare) == null);

        const mutable = searchMutable(i32, i32, &@as(i32, 16), values[0..], compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(@intFromPtr(&values[2]), @intFromPtr(mutable));
        mutable.* = 17;
        try std.testing.expectEqual(@as(i32, 17), values[2]);
        mutable.* = 16;
    }
}

test "search singleton found and miss paths stay inside a one-compare budget" {
    var values = [_]i32{11};

    compare_call_count = 0;
    try std.testing.expectEqual(@as(?usize, 0), searchIndex(i32, i32, &@as(i32, 11), values[0..], compareIntCounted));
    try std.testing.expectEqual(@as(usize, 1), compare_call_count);

    compare_call_count = 0;
    const found = search(i32, i32, &@as(i32, 11), values[0..], compareIntCounted) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 11), found.*);
    try std.testing.expectEqual(@intFromPtr(&values[0]), @intFromPtr(found));
    try std.testing.expectEqual(@as(usize, 1), compare_call_count);

    compare_call_count = 0;
    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 10), values[0..], compareIntCounted));
    try std.testing.expectEqual(@as(usize, 1), compare_call_count);

    compare_call_count = 0;
    try std.testing.expect(search(i32, i32, &@as(i32, 10), values[0..], compareIntCounted) == null);
    try std.testing.expectEqual(@as(usize, 1), compare_call_count);

    compare_call_count = 0;
    const mutable = searchMutable(i32, i32, &@as(i32, 11), values[0..], compareIntCounted) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), compare_call_count);
    mutable.* = 12;
    try std.testing.expectEqual(@as(i32, 12), values[0]);
}

test "descending singleton typed and raw lookup paths stay inside a one-compare budget" {
    var values = [_]i32{11};
    const raw_values: [*]u8 = @ptrCast(values[0..].ptr);

    compare_call_count = 0;
    try std.testing.expectEqual(@as(?usize, 0), searchIndex(i32, i32, &@as(i32, 11), values[0..], compareIntDescendingCounted));
    try std.testing.expectEqual(@as(usize, 1), compare_call_count);

    compare_call_count = 0;
    const found = search(i32, i32, &@as(i32, 11), values[0..], compareIntDescendingCounted) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 11), found.*);
    try std.testing.expectEqual(@intFromPtr(&values[0]), @intFromPtr(found));
    try std.testing.expectEqual(@as(usize, 1), compare_call_count);

    compare_call_count = 0;
    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 10), values[0..], compareIntDescendingCounted));
    try std.testing.expectEqual(@as(usize, 1), compare_call_count);

    compare_call_count = 0;
    try std.testing.expect(search(i32, i32, &@as(i32, 10), values[0..], compareIntDescendingCounted) == null);
    try std.testing.expectEqual(@as(usize, 1), compare_call_count);

    compare_call_count = 0;
    const mutable = searchMutable(i32, i32, &@as(i32, 11), values[0..], compareIntDescendingCounted) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), compare_call_count);
    mutable.* = 12;
    try std.testing.expectEqual(@as(i32, 12), values[0]);
    mutable.* = 11;

    raw_compare_call_count = 0;
    try std.testing.expectEqual(
        @as(?usize, 0),
        bsearchIndex(&@as(i32, 11), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueIntDescendingCounted),
    );
    try std.testing.expectEqual(@as(usize, 1), raw_compare_call_count);

    raw_compare_call_count = 0;
    const raw_found = bsearch(&@as(i32, 11), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueIntDescendingCounted) orelse return error.TestUnexpectedResult;
    const typed_raw_found: *const i32 = @ptrCast(@alignCast(raw_found));
    try std.testing.expectEqual(@as(i32, 11), typed_raw_found.*);
    try std.testing.expectEqual(@intFromPtr(&values[0]), @intFromPtr(typed_raw_found));
    try std.testing.expectEqual(@as(usize, 1), raw_compare_call_count);

    raw_compare_call_count = 0;
    try std.testing.expectEqual(
        @as(?usize, null),
        bsearchIndex(&@as(i32, 10), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueIntDescendingCounted),
    );
    try std.testing.expectEqual(@as(usize, 1), raw_compare_call_count);

    raw_compare_call_count = 0;
    try std.testing.expect(
        bsearch(&@as(i32, 10), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueIntDescendingCounted) == null,
    );
    try std.testing.expectEqual(@as(usize, 1), raw_compare_call_count);

    raw_compare_call_count = 0;
    const raw_mutable = bsearchMutable(&@as(i32, 11), raw_values, values.len, @sizeOf(i32), compareOpaqueIntDescendingCounted) orelse return error.TestUnexpectedResult;
    const typed_raw_mutable: *i32 = @ptrCast(@alignCast(raw_mutable));
    try std.testing.expectEqual(@intFromPtr(&values[0]), @intFromPtr(typed_raw_mutable));
    try std.testing.expectEqual(@as(usize, 1), raw_compare_call_count);
    typed_raw_mutable.* = 12;
    try std.testing.expectEqual(@as(i32, 12), values[0]);
}

test "searchIndex keeps representative ascending and descending probes inside a binary-search budget" {
    const ascending = [_]i32{ 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45 };
    const descending = [_]i32{ 45, 42, 39, 36, 33, 30, 27, 24, 21, 18, 15, 12, 9, 6, 3 };

    compare_call_count = 0;
    try std.testing.expectEqual(@as(?usize, 0), searchIndex(i32, i32, &@as(i32, 3), ascending[0..], compareIntCounted));
    try std.testing.expect(compare_call_count <= 4);

    compare_call_count = 0;
    try std.testing.expectEqual(@as(?usize, 7), searchIndex(i32, i32, &@as(i32, 24), ascending[0..], compareIntCounted));
    try std.testing.expect(compare_call_count <= 4);

    compare_call_count = 0;
    try std.testing.expectEqual(@as(?usize, 14), searchIndex(i32, i32, &@as(i32, 45), ascending[0..], compareIntCounted));
    try std.testing.expect(compare_call_count <= 4);

    compare_call_count = 0;
    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 26), ascending[0..], compareIntCounted));
    try std.testing.expect(compare_call_count <= 4);

    compare_call_count = 0;
    try std.testing.expectEqual(@as(?usize, 0), searchIndex(i32, i32, &@as(i32, 45), descending[0..], compareIntDescendingCounted));
    try std.testing.expect(compare_call_count <= 4);

    compare_call_count = 0;
    try std.testing.expectEqual(@as(?usize, 7), searchIndex(i32, i32, &@as(i32, 24), descending[0..], compareIntDescendingCounted));
    try std.testing.expect(compare_call_count <= 4);

    compare_call_count = 0;
    try std.testing.expectEqual(@as(?usize, 14), searchIndex(i32, i32, &@as(i32, 3), descending[0..], compareIntDescendingCounted));
    try std.testing.expect(compare_call_count <= 4);

    compare_call_count = 0;
    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 26), descending[0..], compareIntDescendingCounted));
    try std.testing.expect(compare_call_count <= 4);
}

test "searchIndex matches linear equality probes across bounded ascending and descending ranges" {
    var ascending_storage: [32]i32 = undefined;
    var descending_storage: [32]i32 = undefined;

    for (0..ascending_storage.len + 1) |len| {
        for (0..len) |index| {
            const value = @as(i32, @intCast((index + 1) * 2));
            ascending_storage[index] = value;
            descending_storage[len - 1 - index] = value;
        }

        const ascending = ascending_storage[0..len];
        const descending = descending_storage[0..len];
        const budget = binarySearchBudget(len);
        const max_probe: i32 = if (len == 0) 1 else @as(i32, @intCast((len * 2) + 1));

        var probe: i32 = 1;
        while (probe <= max_probe) : (probe += 1) {
            compare_call_count = 0;
            const expected_ascending = linearSearchIndex(i32, i32, &probe, ascending, compareInt);
            try std.testing.expectEqual(expected_ascending, searchIndex(i32, i32, &probe, ascending, compareIntCounted));
            try std.testing.expect(compare_call_count <= budget);

            compare_call_count = 0;
            const expected_descending = linearSearchIndex(i32, i32, &probe, descending, compareIntDescending);
            try std.testing.expectEqual(expected_descending, searchIndex(i32, i32, &probe, descending, compareIntDescendingCounted));
            try std.testing.expect(compare_call_count <= budget);
        }
    }
}

test "raw helpers short-circuit empty input and accept c abi comparator pointers" {
    const empty = [_]i32{};

    raw_compare_call_count = 0;
    try std.testing.expectEqual(
        @as(?usize, null),
        bsearchIndex(&@as(i32, 5), @ptrCast(empty[0..].ptr), empty.len, @sizeOf(i32), compareOpaqueIntCounted),
    );
    try std.testing.expectEqual(@as(usize, 0), raw_compare_call_count);
    try std.testing.expect(
        bsearch(&@as(i32, 5), @ptrCast(empty[0..].ptr), empty.len, @sizeOf(i32), compareOpaqueIntCounted) == null,
    );
    try std.testing.expectEqual(@as(usize, 0), raw_compare_call_count);

    const values = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const comparators = [_]CRawComparator{ compareOpaqueIntC, compareOpaqueIntC };

    for (comparators) |compare| {
        const index = bsearchIndex(&@as(i32, 4), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare) orelse return error.TestUnexpectedResult;
        try std.testing.expect(index >= 1 and index <= 3);
        try std.testing.expectEqual(@as(i32, 4), values[index]);

        const found = bsearch(&@as(i32, 4), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare) orelse return error.TestUnexpectedResult;
        const typed_found: *const i32 = @ptrCast(@alignCast(found));
        const found_index = (@intFromPtr(typed_found) - @intFromPtr(&values[0])) / @sizeOf(i32);
        try std.testing.expect(found_index >= 1 and found_index <= 3);
        try std.testing.expectEqual(@as(i32, 4), typed_found.*);
        try std.testing.expectEqual(
            @as(?usize, null),
            bsearchIndex(&@as(i32, 5), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare),
        );
        try std.testing.expect(
            bsearch(&@as(i32, 5), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare) == null,
        );
    }
}

test "raw helpers short-circuit empty input and accept descending c abi comparator pointers" {
    var values = [_]i32{ 42, 23, 16, 11, 7, 4, 2 };
    const comparators = [_]CRawComparator{ compareOpaqueIntDescendingC, compareOpaqueIntDescendingC };

    for (comparators) |compare| {
        const index = bsearchIndex(&@as(i32, 11), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(@as(usize, 3), index);

        const found = bsearch(&@as(i32, 7), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare) orelse return error.TestUnexpectedResult;
        const typed_found: *const i32 = @ptrCast(@alignCast(found));
        try std.testing.expectEqual(@as(i32, 7), typed_found.*);
        try std.testing.expectEqual(@intFromPtr(&values[4]), @intFromPtr(typed_found));

        try std.testing.expectEqual(
            @as(?usize, null),
            bsearchIndex(&@as(i32, 10), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare),
        );
        try std.testing.expect(
            bsearch(&@as(i32, 10), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare) == null,
        );

        const mutable = bsearchMutable(&@as(i32, 16), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare) orelse return error.TestUnexpectedResult;
        const typed_mutable: *i32 = @ptrCast(@alignCast(mutable));
        try std.testing.expectEqual(@intFromPtr(&values[2]), @intFromPtr(typed_mutable));
        typed_mutable.* = 17;
        try std.testing.expectEqual(@as(i32, 17), values[2]);
        typed_mutable.* = 16;
    }
}

test "raw helpers accept runtime-selected native comparator pointers" {
    const values = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };
    const comparators = [_]RawComparator{ compareOpaqueInt, compareOpaqueIntAlias };

    for (comparators) |compare| {
        try std.testing.expectEqual(
            @as(?usize, 4),
            bsearchIndex(&@as(i32, 16), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare),
        );
        const found = bsearch(&@as(i32, 23), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare) orelse return error.TestUnexpectedResult;
        const typed_found: *const i32 = @ptrCast(@alignCast(found));
        try std.testing.expectEqual(@as(i32, 23), typed_found.*);
        try std.testing.expectEqual(
            @as(?usize, null),
            bsearchIndex(&@as(i32, 19), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare),
        );
        try std.testing.expect(
            bsearch(&@as(i32, 19), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare) == null,
        );
    }
}

test "raw helpers accept runtime-selected descending native comparator pointers" {
    var values = [_]i32{ 42, 23, 16, 11, 7, 4, 2 };
    const comparators = [_]RawComparator{ compareOpaqueIntDescending, compareOpaqueIntDescendingAlias };

    for (comparators) |compare| {
        try std.testing.expectEqual(
            @as(?usize, 3),
            bsearchIndex(&@as(i32, 11), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare),
        );

        const found = bsearch(&@as(i32, 7), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare) orelse return error.TestUnexpectedResult;
        const typed_found: *const i32 = @ptrCast(@alignCast(found));
        try std.testing.expectEqual(@as(i32, 7), typed_found.*);
        try std.testing.expectEqual(@intFromPtr(&values[4]), @intFromPtr(typed_found));

        try std.testing.expectEqual(
            @as(?usize, null),
            bsearchIndex(&@as(i32, 10), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare),
        );
        try std.testing.expect(
            bsearch(&@as(i32, 10), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare) == null,
        );

        const mutable = bsearchMutable(&@as(i32, 16), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare) orelse return error.TestUnexpectedResult;
        const typed_mutable: *i32 = @ptrCast(@alignCast(mutable));
        try std.testing.expectEqual(@intFromPtr(&values[2]), @intFromPtr(typed_mutable));
        typed_mutable.* = 17;
        try std.testing.expectEqual(@as(i32, 17), values[2]);
        typed_mutable.* = 16;
    }
}

test "bsearchIndex keeps representative ascending and descending probes inside a binary-search budget" {
    const ascending = [_]i32{ 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45 };
    const descending = [_]i32{ 45, 42, 39, 36, 33, 30, 27, 24, 21, 18, 15, 12, 9, 6, 3 };

    raw_compare_call_count = 0;
    try std.testing.expectEqual(
        @as(?usize, 0),
        bsearchIndex(&@as(i32, 3), @ptrCast(ascending[0..].ptr), ascending.len, @sizeOf(i32), compareOpaqueIntCounted),
    );
    try std.testing.expect(raw_compare_call_count <= 4);

    raw_compare_call_count = 0;
    try std.testing.expectEqual(
        @as(?usize, 7),
        bsearchIndex(&@as(i32, 24), @ptrCast(ascending[0..].ptr), ascending.len, @sizeOf(i32), compareOpaqueIntCounted),
    );
    try std.testing.expect(raw_compare_call_count <= 4);

    raw_compare_call_count = 0;
    try std.testing.expectEqual(
        @as(?usize, 14),
        bsearchIndex(&@as(i32, 45), @ptrCast(ascending[0..].ptr), ascending.len, @sizeOf(i32), compareOpaqueIntCounted),
    );
    try std.testing.expect(raw_compare_call_count <= 4);

    raw_compare_call_count = 0;
    try std.testing.expectEqual(
        @as(?usize, null),
        bsearchIndex(&@as(i32, 26), @ptrCast(ascending[0..].ptr), ascending.len, @sizeOf(i32), compareOpaqueIntCounted),
    );
    try std.testing.expect(raw_compare_call_count <= 4);

    raw_compare_call_count = 0;
    try std.testing.expectEqual(
        @as(?usize, 0),
        bsearchIndex(&@as(i32, 45), @ptrCast(descending[0..].ptr), descending.len, @sizeOf(i32), compareOpaqueIntDescendingCounted),
    );
    try std.testing.expect(raw_compare_call_count <= 4);

    raw_compare_call_count = 0;
    try std.testing.expectEqual(
        @as(?usize, 7),
        bsearchIndex(&@as(i32, 24), @ptrCast(descending[0..].ptr), descending.len, @sizeOf(i32), compareOpaqueIntDescendingCounted),
    );
    try std.testing.expect(raw_compare_call_count <= 4);

    raw_compare_call_count = 0;
    try std.testing.expectEqual(
        @as(?usize, 14),
        bsearchIndex(&@as(i32, 3), @ptrCast(descending[0..].ptr), descending.len, @sizeOf(i32), compareOpaqueIntDescendingCounted),
    );
    try std.testing.expect(raw_compare_call_count <= 4);

    raw_compare_call_count = 0;
    try std.testing.expectEqual(
        @as(?usize, null),
        bsearchIndex(&@as(i32, 26), @ptrCast(descending[0..].ptr), descending.len, @sizeOf(i32), compareOpaqueIntDescendingCounted),
    );
    try std.testing.expect(raw_compare_call_count <= 4);
}

test "bsearchIndex matches linear equality probes across bounded ascending and descending ranges" {
    var ascending_storage: [32]i32 = undefined;
    var descending_storage: [32]i32 = undefined;

    for (0..ascending_storage.len + 1) |len| {
        for (0..len) |index| {
            const value = @as(i32, @intCast((index + 1) * 2));
            ascending_storage[index] = value;
            descending_storage[len - 1 - index] = value;
        }

        const ascending = ascending_storage[0..len];
        const descending = descending_storage[0..len];
        const budget = binarySearchBudget(len);
        const max_probe: i32 = if (len == 0) 1 else @as(i32, @intCast((len * 2) + 1));

        var probe: i32 = 1;
        while (probe <= max_probe) : (probe += 1) {
            raw_compare_call_count = 0;
            const expected_ascending = linearRawSearchIndexI32(&probe, @ptrCast(ascending.ptr), ascending.len, @sizeOf(i32), compareOpaqueInt);
            try std.testing.expectEqual(
                expected_ascending,
                bsearchIndex(&probe, @ptrCast(ascending.ptr), ascending.len, @sizeOf(i32), compareOpaqueIntCounted),
            );
            try std.testing.expect(raw_compare_call_count <= budget);

            raw_compare_call_count = 0;
            const expected_descending = linearRawSearchIndexI32(&probe, @ptrCast(descending.ptr), descending.len, @sizeOf(i32), compareOpaqueIntDescending);
            try std.testing.expectEqual(
                expected_descending,
                bsearchIndex(&probe, @ptrCast(descending.ptr), descending.len, @sizeOf(i32), compareOpaqueIntDescendingCounted),
            );
            try std.testing.expect(raw_compare_call_count <= budget);
        }
    }
}

test "bsearchMutable returns a mutable pointer to the matching element" {
    var values = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };
    const found = bsearchMutable(&@as(i32, 16), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueInt) orelse return error.TestUnexpectedResult;
    const typed_found: *i32 = @ptrCast(@alignCast(found));

    typed_found.* = 17;
    try std.testing.expectEqual(@as(i32, 17), values[4]);
    try std.testing.expectEqual(@intFromPtr(&values[4]), @intFromPtr(typed_found));
}
