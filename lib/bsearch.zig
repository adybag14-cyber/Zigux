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
    const fn_info = switch (@typeInfo(Compare)) {
        .@"fn" => |info| info,
        .pointer => |pointer| switch (@typeInfo(pointer.child)) {
            .@"fn" => |info| info,
            else => @compileError("bsearch comparator must be a function or function pointer"),
        },
        else => @compileError("bsearch comparator must be a function or function pointer"),
    };

    if (fn_info.params.len != 2) {
        @compileError("bsearch comparator must accept exactly two parameters");
    }
    if (fn_info.params[0].type orelse @compileError("bsearch comparator key parameter must be typed") != *const Key) {
        @compileError("bsearch comparator first parameter must be *const Key");
    }
    if (fn_info.params[1].type orelse @compileError("bsearch comparator item parameter must be typed") != *const T) {
        @compileError("bsearch comparator second parameter must be *const T");
    }
    if (fn_info.return_type orelse @compileError("bsearch comparator return type must be explicit") != i32) {
        @compileError("bsearch comparator return type must be i32");
    }
}

fn validateRawComparator(comptime Compare: type) void {
    const fn_info = switch (@typeInfo(Compare)) {
        .@"fn" => |info| info,
        .pointer => |pointer| switch (@typeInfo(pointer.child)) {
            .@"fn" => |info| info,
            else => @compileError("bsearch raw comparator must be a function or function pointer"),
        },
        else => @compileError("bsearch raw comparator must be a function or function pointer"),
    };

    if (fn_info.params.len != 2) {
        @compileError("bsearch raw comparator must accept exactly two parameters");
    }
    if (fn_info.params[0].type orelse @compileError("bsearch raw comparator key parameter must be typed") != *const anyopaque) {
        @compileError("bsearch raw comparator first parameter must be *const anyopaque");
    }
    if (fn_info.params[1].type orelse @compileError("bsearch raw comparator item parameter must be typed") != *const anyopaque) {
        @compileError("bsearch raw comparator second parameter must be *const anyopaque");
    }
    if (fn_info.return_type orelse @compileError("bsearch raw comparator return type must be explicit") != i32) {
        @compileError("bsearch raw comparator return type must be i32");
    }
}

pub fn bsearchIndex(
    key: *const anyopaque,
    base: [*]const u8,
    num: usize,
    size: usize,
    compare: anytype,
) ?usize {
    comptime validateRawComparator(@TypeOf(compare));
    var start: usize = 0;
    var count = num;

    while (count > 0) {
        const pivot_index = start + (count >> 1);
        const pivot_ptr: *const anyopaque = @ptrCast(base + (pivot_index * size));
        const result = compare(key, pivot_ptr);

        if (result == 0) {
            return pivot_index;
        }
        if (result > 0) {
            start = pivot_index + 1;
            count -= 1;
        }
        count >>= 1;
    }

    return null;
}

pub fn bsearch(
    key: *const anyopaque,
    base: [*]const u8,
    num: usize,
    size: usize,
    compare: anytype,
) ?*const anyopaque {
    comptime validateRawComparator(@TypeOf(compare));
    const index = bsearchIndex(key, base, num, size, compare) orelse return null;
    return @ptrCast(base + (index * size));
}

pub fn bsearchMutable(
    key: *const anyopaque,
    base: [*]u8,
    num: usize,
    size: usize,
    compare: anytype,
) ?*anyopaque {
    comptime validateRawComparator(@TypeOf(compare));
    const index = bsearchIndex(key, base, num, size, compare) orelse return null;
    return @ptrCast(base + (index * size));
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
    comptime validateComparator(Key, T, @TypeOf(compare));
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
    comptime validateComparator(Key, T, @TypeOf(compare));
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

fn compareDescendingInt(key: *const i32, item: *const i32) i32 {
    return compareInt(item, key);
}

fn compareCInt(key: *const i32, item: *const i32) callconv(.c) i32 {
    return compareInt(key, item);
}

fn compareCDescendingInt(key: *const i32, item: *const i32) callconv(.c) i32 {
    return compareInt(item, key);
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

fn compareOpaqueInt(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const i32 = @ptrCast(@alignCast(key));
    const typed_item: *const i32 = @ptrCast(@alignCast(item));
    return compareInt(typed_key, typed_item);
}

fn compareOpaqueDescendingInt(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const i32 = @ptrCast(@alignCast(key));
    const typed_item: *const i32 = @ptrCast(@alignCast(item));
    return compareDescendingInt(typed_key, typed_item);
}

fn compareCOpaqueInt(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    return compareOpaqueInt(key, item);
}

fn compareCOpaqueDescendingInt(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    return compareOpaqueDescendingInt(key, item);
}

fn compareOpaqueName(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const []const u8 = @ptrCast(@alignCast(key));
    const typed_item: *const Entry = @ptrCast(@alignCast(item));
    return compareName(typed_key, typed_item);
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

test "searchIndex handles singleton slices without widening the contract" {
    const singleton = [_]i32{21};

    try std.testing.expectEqual(@as(?usize, 0), searchIndex(i32, i32, &@as(i32, 21), singleton[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 20), singleton[0..], compareInt));
    try std.testing.expectEqual(@as(?usize, null), searchIndex(i32, i32, &@as(i32, 22), singleton[0..], compareInt));
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

test "search and searchMutable keep singleton and empty slices on the found-or-null boundary" {
    const empty = [_]i32{};
    var singleton = [_]i32{21};

    const found = search(i32, i32, &@as(i32, 21), singleton[0..], compareInt) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@intFromPtr(&singleton[0]), @intFromPtr(found));

    const found_mutable = searchMutable(i32, i32, &@as(i32, 21), singleton[0..], compareInt) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@intFromPtr(&singleton[0]), @intFromPtr(found_mutable));
    found_mutable.* = 22;
    try std.testing.expectEqual(@as(i32, 22), singleton[0]);

    try std.testing.expect(search(i32, i32, &@as(i32, 21), empty[0..], compareInt) == null);
    try std.testing.expect(searchMutable(i32, i32, &@as(i32, 21), singleton[0..0], compareInt) == null);
}

test "search accepts duplicate keys across beginning middle and end runs without claiming stable selection" {
    const cases = [_]struct {
        values: [6]i32,
        needle: i32,
        lower: usize,
        upper: usize,
    }{
        .{ .values = .{ 4, 4, 4, 9, 16, 25 }, .needle = 4, .lower = 0, .upper = 2 },
        .{ .values = .{ 1, 4, 4, 4, 9, 16 }, .needle = 4, .lower = 1, .upper = 3 },
        .{ .values = .{ 1, 4, 9, 16, 16, 16 }, .needle = 16, .lower = 3, .upper = 5 },
    };

    for (cases) |case| {
        const values = case.values;
        const index = searchIndex(i32, i32, &case.needle, values[0..], compareInt) orelse return error.TestUnexpectedResult;
        const found = search(i32, i32, &case.needle, values[0..], compareInt) orelse return error.TestUnexpectedResult;
        const found_index = (@intFromPtr(found) - @intFromPtr(&values[0])) / @sizeOf(i32);

        try std.testing.expect(index >= case.lower and index <= case.upper);
        try std.testing.expectEqual(case.needle, values[index]);
        try std.testing.expect(found_index >= case.lower and found_index <= case.upper);
        try std.testing.expectEqual(case.needle, found.*);
    }
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

test "bsearchIndex and bsearch expose the raw Linux-style helper contract" {
    const values = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };
    const key = @as(i32, 16);

    try std.testing.expectEqual(@as(?usize, 4), bsearchIndex(&key, @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueInt));

    const found = bsearch(&key, @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueInt) orelse return error.TestUnexpectedResult;
    const typed_found: *const i32 = @ptrCast(@alignCast(found));
    try std.testing.expectEqual(@as(i32, 16), typed_found.*);
    try std.testing.expectEqual(@intFromPtr(&values[4]), @intFromPtr(typed_found));
}

test "bsearch raw helpers keep empty singleton and miss cases on the null-or-hit boundary" {
    const empty = [_]i32{};
    const values = [_]i32{ 3, 5, 8, 13, 21 };
    var singleton = [_]i32{21};

    try std.testing.expectEqual(@as(?usize, null), bsearchIndex(&@as(i32, 8), @ptrCast(empty[0..].ptr), empty.len, @sizeOf(i32), compareOpaqueInt));
    try std.testing.expectEqual(@as(?usize, null), bsearchIndex(&@as(i32, 1), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueInt));
    try std.testing.expectEqual(@as(?usize, null), bsearchIndex(&@as(i32, 9), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueInt));
    try std.testing.expectEqual(@as(?usize, null), bsearchIndex(&@as(i32, 34), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueInt));
    try std.testing.expectEqual(@as(?usize, 0), bsearchIndex(&@as(i32, 21), @ptrCast(singleton[0..].ptr), singleton.len, @sizeOf(i32), compareOpaqueInt));

    try std.testing.expect(bsearch(&@as(i32, 21), @ptrCast(empty[0..].ptr), empty.len, @sizeOf(i32), compareOpaqueInt) == null);
    try std.testing.expect(bsearch(&@as(i32, 20), @ptrCast(singleton[0..].ptr), singleton.len, @sizeOf(i32), compareOpaqueInt) == null);

    const found = bsearchMutable(&@as(i32, 21), @ptrCast(singleton[0..].ptr), singleton.len, @sizeOf(i32), compareOpaqueInt) orelse return error.TestUnexpectedResult;
    const typed_found: *i32 = @ptrCast(@alignCast(found));
    try std.testing.expectEqual(@intFromPtr(&singleton[0]), @intFromPtr(typed_found));
    typed_found.* = 22;
    try std.testing.expectEqual(@as(i32, 22), singleton[0]);
}

test "bsearch raw helpers accept duplicate keys without claiming stable selection" {
    const cases = [_]struct {
        values: [6]i32,
        needle: i32,
        lower: usize,
        upper: usize,
    }{
        .{ .values = .{ 4, 4, 4, 9, 16, 25 }, .needle = 4, .lower = 0, .upper = 2 },
        .{ .values = .{ 1, 4, 4, 4, 9, 16 }, .needle = 4, .lower = 1, .upper = 3 },
        .{ .values = .{ 1, 4, 9, 16, 16, 16 }, .needle = 16, .lower = 3, .upper = 5 },
    };

    for (cases) |case| {
        var values = case.values;
        const index = bsearchIndex(&case.needle, @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueInt) orelse return error.TestUnexpectedResult;
        const found = bsearchMutable(&case.needle, @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueInt) orelse return error.TestUnexpectedResult;
        const typed_found: *i32 = @ptrCast(@alignCast(found));
        const found_index = (@intFromPtr(typed_found) - @intFromPtr(&values[0])) / @sizeOf(i32);

        try std.testing.expect(index >= case.lower and index <= case.upper);
        try std.testing.expectEqual(case.needle, values[index]);
        try std.testing.expect(found_index >= case.lower and found_index <= case.upper);
        try std.testing.expectEqual(case.needle, typed_found.*);
    }
}

test "bsearch supports heterogeneous keys and mutable raw pointers" {
    var entries = [_]Entry{
        .{ .name = "alpha", .value = 1 },
        .{ .name = "beta", .value = 2 },
        .{ .name = "delta", .value = 4 },
        .{ .name = "omega", .value = 24 },
    };
    const key = @as([]const u8, "delta");

    const found = bsearch(@ptrCast(&key), @ptrCast(entries[0..].ptr), entries.len, @sizeOf(Entry), compareOpaqueName) orelse return error.TestUnexpectedResult;
    const typed_found: *const Entry = @ptrCast(@alignCast(found));
    try std.testing.expectEqual(@as(u32, 4), typed_found.value);

    const found_mutable = bsearchMutable(@ptrCast(&key), @ptrCast(entries[0..].ptr), entries.len, @sizeOf(Entry), compareOpaqueName) orelse return error.TestUnexpectedResult;
    const typed_found_mutable: *Entry = @ptrCast(@alignCast(found_mutable));
    typed_found_mutable.value = 5;
    try std.testing.expectEqual(@as(u32, 5), entries[2].value);
}

test "search accepts runtime-selected comparator function pointers" {
    const ascending = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };
    const descending = [_]i32{ 42, 23, 16, 11, 7, 4, 2 };
    const comparators = [_]Comparator(i32, i32){ compareInt, compareDescendingInt };
    const slices = [_][]const i32{ ascending[0..], descending[0..] };
    const targets = [_]i32{ 23, 7 };

    for (comparators, slices, targets) |compare, items, target| {
        const found = search(i32, i32, &target, items, compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(target, found.*);
    }
}

test "search accepts runtime-selected C ABI comparator function pointers" {
    const ascending = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };
    const descending = [_]i32{ 42, 23, 16, 11, 7, 4, 2 };
    const comparators = [_]CComparator(i32, i32){ compareCInt, compareCDescendingInt };
    const slices = [_][]const i32{ ascending[0..], descending[0..] };
    const targets = [_]i32{ 16, 11 };

    for (comparators, slices, targets) |compare, items, target| {
        const found = search(i32, i32, &target, items, compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(target, found.*);
    }
}

test "bsearch accepts runtime-selected raw comparator function pointers for ascending and descending slices" {
    const ascending = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };
    const descending = [_]i32{ 42, 23, 16, 11, 7, 4, 2 };
    const comparators = [_]RawComparator{ compareOpaqueInt, compareOpaqueDescendingInt };
    const slices = [_][]const i32{ ascending[0..], descending[0..] };
    const targets = [_]i32{ 23, 7 };

    for (comparators, slices, targets) |compare, items, target| {
        const found = bsearch(&target, @ptrCast(items.ptr), items.len, @sizeOf(i32), compare) orelse return error.TestUnexpectedResult;
        const typed_found: *const i32 = @ptrCast(@alignCast(found));
        try std.testing.expectEqual(target, typed_found.*);
    }
}

test "bsearch accepts runtime-selected C ABI raw comparator function pointers for ascending and descending slices" {
    const ascending = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };
    const descending = [_]i32{ 42, 23, 16, 11, 7, 4, 2 };
    const comparators = [_]CRawComparator{ compareCOpaqueInt, compareCOpaqueDescendingInt };
    const slices = [_][]const i32{ ascending[0..], descending[0..] };
    const targets = [_]i32{ 23, 7 };

    for (comparators, slices, targets) |compare, items, target| {
        const found = bsearch(&target, @ptrCast(items.ptr), items.len, @sizeOf(i32), compare) orelse return error.TestUnexpectedResult;
        const typed_found: *const i32 = @ptrCast(@alignCast(found));
        try std.testing.expectEqual(target, typed_found.*);
    }
}
