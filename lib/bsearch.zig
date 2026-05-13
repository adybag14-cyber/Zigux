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

pub const IndexRange = struct {
    lower: usize,
    upper: usize,

    pub fn len(self: @This()) usize {
        return self.upper - self.lower;
    }

    pub fn isEmpty(self: @This()) bool {
        return self.lower == self.upper;
    }

    pub fn sliceConst(self: @This(), comptime T: type, items: []const T) []const T {
        std.debug.assert(self.lower <= self.upper);
        std.debug.assert(self.upper <= items.len);
        return items[self.lower..self.upper];
    }

    pub fn sliceMutable(self: @This(), comptime T: type, items: []T) []T {
        std.debug.assert(self.lower <= self.upper);
        std.debug.assert(self.upper <= items.len);
        return items[self.lower..self.upper];
    }

    pub fn bytes(self: @This(), base: [*]const u8, size: usize) []const u8 {
        std.debug.assert(self.lower <= self.upper);
        return base[(self.lower * size)..(self.upper * size)];
    }

    pub fn bytesMutable(self: @This(), base: [*]u8, size: usize) []u8 {
        std.debug.assert(self.lower <= self.upper);
        return base[(self.lower * size)..(self.upper * size)];
    }
};

fn advanceSearchWindow(start: *usize, count: *usize, pivot_index: usize, result: i32) bool {
    if (result == 0) {
        return true;
    }
    if (result > 0) {
        start.* = pivot_index + 1;
        count.* -= 1;
    }
    count.* >>= 1;
    return false;
}

fn advanceLowerBoundWindow(start: *usize, count: *usize, pivot_index: usize, result: i32) void {
    const half = count.* >> 1;
    if (result > 0) {
        start.* = pivot_index + 1;
        count.* -= half + 1;
    } else {
        count.* = half;
    }
}

fn advanceUpperBoundWindow(start: *usize, count: *usize, pivot_index: usize, result: i32) void {
    const half = count.* >> 1;
    if (result >= 0) {
        start.* = pivot_index + 1;
        count.* -= half + 1;
    } else {
        count.* = half;
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
    var start: usize = 0;
    var count = items.len;

    while (count > 0) {
        const pivot_index = start + (count >> 1);
        const pivot: *const T = &items[pivot_index];
        if (advanceSearchWindow(&start, &count, pivot_index, compare(key, pivot))) {
            return pivot_index;
        }
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

pub fn lowerBoundIndex(
    comptime Key: type,
    comptime T: type,
    key: *const Key,
    items: []const T,
    compare: anytype,
) usize {
    comptime validateComparator(Key, T, @TypeOf(compare));
    var start: usize = 0;
    var count = items.len;

    while (count > 0) {
        const pivot_index = start + (count >> 1);
        const pivot: *const T = &items[pivot_index];
        advanceLowerBoundWindow(&start, &count, pivot_index, compare(key, pivot));
    }

    return start;
}

pub fn upperBoundIndex(
    comptime Key: type,
    comptime T: type,
    key: *const Key,
    items: []const T,
    compare: anytype,
) usize {
    comptime validateComparator(Key, T, @TypeOf(compare));
    var start: usize = 0;
    var count = items.len;

    while (count > 0) {
        const pivot_index = start + (count >> 1);
        const pivot: *const T = &items[pivot_index];
        advanceUpperBoundWindow(&start, &count, pivot_index, compare(key, pivot));
    }

    return start;
}

pub fn equalRangeIndex(
    comptime Key: type,
    comptime T: type,
    key: *const Key,
    items: []const T,
    compare: anytype,
) IndexRange {
    return .{
        .lower = lowerBoundIndex(Key, T, key, items, compare),
        .upper = upperBoundIndex(Key, T, key, items, compare),
    };
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
        if (advanceSearchWindow(&start, &count, pivot_index, compare(key, pivot_ptr))) {
            return pivot_index;
        }
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
    const index = bsearchIndex(key, base, num, size, compare) orelse return null;
    return @ptrCast(base + (index * size));
}

pub fn bsearchLowerBoundIndex(
    key: *const anyopaque,
    base: [*]const u8,
    num: usize,
    size: usize,
    compare: anytype,
) usize {
    comptime validateRawComparator(@TypeOf(compare));
    var start: usize = 0;
    var count = num;

    while (count > 0) {
        const pivot_index = start + (count >> 1);
        const pivot_ptr: *const anyopaque = @ptrCast(base + (pivot_index * size));
        advanceLowerBoundWindow(&start, &count, pivot_index, compare(key, pivot_ptr));
    }

    return start;
}

pub fn bsearchUpperBoundIndex(
    key: *const anyopaque,
    base: [*]const u8,
    num: usize,
    size: usize,
    compare: anytype,
) usize {
    comptime validateRawComparator(@TypeOf(compare));
    var start: usize = 0;
    var count = num;

    while (count > 0) {
        const pivot_index = start + (count >> 1);
        const pivot_ptr: *const anyopaque = @ptrCast(base + (pivot_index * size));
        advanceUpperBoundWindow(&start, &count, pivot_index, compare(key, pivot_ptr));
    }

    return start;
}

pub fn bsearchEqualRangeIndex(
    key: *const anyopaque,
    base: [*]const u8,
    num: usize,
    size: usize,
    compare: anytype,
) IndexRange {
    return .{
        .lower = bsearchLowerBoundIndex(key, base, num, size, compare),
        .upper = bsearchUpperBoundIndex(key, base, num, size, compare),
    };
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
    return compareDescendingInt(key, item);
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

fn compareOpaqueName(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const []const u8 = @ptrCast(@alignCast(key));
    const typed_item: *const Entry = @ptrCast(@alignCast(item));
    return compareName(typed_key, typed_item);
}

test "search keeps native and C comparator pointer support" {
    const ascending = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };
    const descending = [_]i32{ 42, 23, 16, 11, 7, 4, 2 };

    const native_comparators = [_]Comparator(i32, i32){ compareInt, compareDescendingInt };
    const native_slices = [_][]const i32{ ascending[0..], descending[0..] };
    const native_targets = [_]i32{ 23, 7 };
    const native_indexes = [_]usize{ 5, 4 };

    for (native_comparators, native_slices, native_targets, native_indexes) |compare, items, target, expected_index| {
        try std.testing.expectEqual(@as(?usize, expected_index), searchIndex(i32, i32, &target, items, compare));
        const found = search(i32, i32, &target, items, compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(@intFromPtr(&items[expected_index]), @intFromPtr(found));
    }

    const c_comparators = [_]CComparator(i32, i32){ compareCInt, compareCDescendingInt };
    const c_slices = [_][]const i32{ ascending[0..], descending[0..] };
    const c_targets = [_]i32{ 16, 11 };
    const c_indexes = [_]usize{ 4, 3 };

    for (c_comparators, c_slices, c_targets, c_indexes) |compare, items, target, expected_index| {
        try std.testing.expectEqual(@as(?usize, expected_index), searchIndex(i32, i32, &target, items, compare));
        const found = search(i32, i32, &target, items, compare) orelse return error.TestUnexpectedResult;
        try std.testing.expectEqual(@intFromPtr(&items[expected_index]), @intFromPtr(found));
    }
}

test "searchMutable preserves write-through aliases" {
    var values = [_]i32{ 5, 9, 12, 18, 27 };
    const found = searchMutable(i32, i32, &@as(i32, 18), values[0..], compareInt) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@intFromPtr(&values[3]), @intFromPtr(found));
    found.* = 19;
    try std.testing.expectEqual(@as(i32, 19), values[3]);
}

test "typed lower and upper bounds stay stable for ascending and descending duplicates" {
    const ascending = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const descending = [_]i32{ 16, 9, 4, 4, 4, 1 };

    const ascending_comparators = [_]Comparator(i32, i32){compareInt};
    for (ascending_comparators) |compare| {
        try std.testing.expectEqual(@as(usize, 1), lowerBoundIndex(i32, i32, &@as(i32, 4), ascending[0..], compare));
        try std.testing.expectEqual(@as(usize, 4), upperBoundIndex(i32, i32, &@as(i32, 4), ascending[0..], compare));
        try std.testing.expectEqual(@as(usize, 4), lowerBoundIndex(i32, i32, &@as(i32, 5), ascending[0..], compare));
        try std.testing.expectEqual(@as(usize, ascending.len), upperBoundIndex(i32, i32, &@as(i32, 20), ascending[0..], compare));
    }

    const descending_comparators = [_]Comparator(i32, i32){compareDescendingInt};
    for (descending_comparators) |compare| {
        try std.testing.expectEqual(@as(usize, 2), lowerBoundIndex(i32, i32, &@as(i32, 4), descending[0..], compare));
        try std.testing.expectEqual(@as(usize, 5), upperBoundIndex(i32, i32, &@as(i32, 4), descending[0..], compare));
        try std.testing.expectEqual(@as(usize, 0), lowerBoundIndex(i32, i32, &@as(i32, 20), descending[0..], compare));
        try std.testing.expectEqual(@as(usize, descending.len), upperBoundIndex(i32, i32, &@as(i32, 0), descending[0..], compare));
    }
}

test "equalRangeIndex reports duplicate spans and empty insertion points" {
    const ascending = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const descending = [_]i32{ 16, 9, 4, 4, 4, 1 };

    const ascending_range = equalRangeIndex(i32, i32, &@as(i32, 4), ascending[0..], compareInt);
    try std.testing.expectEqual(IndexRange{ .lower = 1, .upper = 4 }, ascending_range);
    try std.testing.expectEqual(@as(usize, 3), ascending_range.len());
    try std.testing.expect(!ascending_range.isEmpty());

    const ascending_missing = equalRangeIndex(i32, i32, &@as(i32, 5), ascending[0..], compareInt);
    try std.testing.expectEqual(IndexRange{ .lower = 4, .upper = 4 }, ascending_missing);
    try std.testing.expectEqual(@as(usize, 0), ascending_missing.len());
    try std.testing.expect(ascending_missing.isEmpty());

    const descending_range = equalRangeIndex(i32, i32, &@as(i32, 4), descending[0..], compareDescendingInt);
    try std.testing.expectEqual(IndexRange{ .lower = 2, .upper = 5 }, descending_range);
    try std.testing.expectEqual(@as(usize, 3), descending_range.len());

    const descending_missing = equalRangeIndex(i32, i32, &@as(i32, 20), descending[0..], compareDescendingInt);
    try std.testing.expectEqual(IndexRange{ .lower = 0, .upper = 0 }, descending_missing);
    try std.testing.expect(descending_missing.isEmpty());
}

test "IndexRange slice helpers keep typed duplicate spans and empty insertion points direct" {
    const ascending = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const duplicate_view = equalRangeIndex(i32, i32, &@as(i32, 4), ascending[0..], compareInt).sliceConst(i32, ascending[0..]);
    try std.testing.expectEqual(@as(usize, 3), duplicate_view.len);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 4, 4 }, duplicate_view);

    const missing_view = equalRangeIndex(i32, i32, &@as(i32, 5), ascending[0..], compareInt).sliceConst(i32, ascending[0..]);
    try std.testing.expectEqual(@as(usize, 0), missing_view.len);
    try std.testing.expectEqual(@intFromPtr(&ascending[4]), @intFromPtr(missing_view.ptr));

    var mutable = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const mutable_view = equalRangeIndex(i32, i32, &@as(i32, 4), mutable[0..], compareInt).sliceMutable(i32, mutable[0..]);
    try std.testing.expectEqual(@as(usize, 3), mutable_view.len);
    mutable_view[1] = 6;
    try std.testing.expectEqual(@as(i32, 6), mutable[2]);
}

test "IndexRange byte helpers keep raw duplicate spans and write-through aliases" {
    const ascending = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const ascending_raw: [*]const u8 = @ptrCast(ascending[0..].ptr);
    const duplicate_bytes = bsearchEqualRangeIndex(&@as(i32, 4), ascending_raw, ascending.len, @sizeOf(i32), compareOpaqueInt).bytes(ascending_raw, @sizeOf(i32));
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(i32)), duplicate_bytes.len);
    const typed_bytes: [*]const i32 = @ptrCast(@alignCast(duplicate_bytes.ptr));
    try std.testing.expectEqual(@as(i32, 4), typed_bytes[0]);
    try std.testing.expectEqual(@as(i32, 4), typed_bytes[2]);

    const missing_bytes = bsearchEqualRangeIndex(&@as(i32, 5), ascending_raw, ascending.len, @sizeOf(i32), compareOpaqueInt).bytes(ascending_raw, @sizeOf(i32));
    try std.testing.expectEqual(@as(usize, 0), missing_bytes.len);
    try std.testing.expectEqual(@intFromPtr(ascending_raw + (4 * @sizeOf(i32))), @intFromPtr(missing_bytes.ptr));

    var mutable = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const mutable_raw: [*]u8 = @ptrCast(mutable[0..].ptr);
    const mutable_bytes = bsearchEqualRangeIndex(&@as(i32, 4), mutable_raw, mutable.len, @sizeOf(i32), compareOpaqueInt).bytesMutable(mutable_raw, @sizeOf(i32));
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(i32)), mutable_bytes.len);
    const typed_mutable: [*]i32 = @ptrCast(@alignCast(mutable_bytes.ptr));
    typed_mutable[1] = 7;
    try std.testing.expectEqual(@as(i32, 7), mutable[2]);
}

test "raw search helpers keep pointer and mutable contracts" {
    const values = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };
    const key = @as(i32, 16);

    try std.testing.expectEqual(@as(?usize, 4), bsearchIndex(&key, @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueInt));
    const found = bsearch(&key, @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueInt) orelse return error.TestUnexpectedResult;
    const typed_found: *const i32 = @ptrCast(@alignCast(found));
    try std.testing.expectEqual(@intFromPtr(&values[4]), @intFromPtr(typed_found));

    var mutable_values = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };
    const mutable = bsearchMutable(&@as(i32, 11), @ptrCast(mutable_values[0..].ptr), mutable_values.len, @sizeOf(i32), compareOpaqueInt) orelse return error.TestUnexpectedResult;
    const typed_mutable: *i32 = @ptrCast(@alignCast(mutable));
    typed_mutable.* = 12;
    try std.testing.expectEqual(@as(i32, 12), mutable_values[3]);
}

test "raw lower and upper bounds stay stable for ascending and descending duplicates" {
    const ascending = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const descending = [_]i32{ 16, 9, 4, 4, 4, 1 };
    const ascending_raw: [*]const u8 = @ptrCast(ascending[0..].ptr);
    const descending_raw: [*]const u8 = @ptrCast(descending[0..].ptr);

    try std.testing.expectEqual(@as(usize, 1), bsearchLowerBoundIndex(&@as(i32, 4), ascending_raw, ascending.len, @sizeOf(i32), compareOpaqueInt));
    try std.testing.expectEqual(@as(usize, 4), bsearchUpperBoundIndex(&@as(i32, 4), ascending_raw, ascending.len, @sizeOf(i32), compareOpaqueInt));
    try std.testing.expectEqual(@as(usize, 4), bsearchLowerBoundIndex(&@as(i32, 5), ascending_raw, ascending.len, @sizeOf(i32), compareOpaqueInt));
    try std.testing.expectEqual(@as(usize, ascending.len), bsearchUpperBoundIndex(&@as(i32, 20), ascending_raw, ascending.len, @sizeOf(i32), compareOpaqueInt));

    try std.testing.expectEqual(@as(usize, 2), bsearchLowerBoundIndex(&@as(i32, 4), descending_raw, descending.len, @sizeOf(i32), compareOpaqueDescendingInt));
    try std.testing.expectEqual(@as(usize, 5), bsearchUpperBoundIndex(&@as(i32, 4), descending_raw, descending.len, @sizeOf(i32), compareOpaqueDescendingInt));
    try std.testing.expectEqual(@as(usize, 0), bsearchLowerBoundIndex(&@as(i32, 20), descending_raw, descending.len, @sizeOf(i32), compareOpaqueDescendingInt));
    try std.testing.expectEqual(@as(usize, descending.len), bsearchUpperBoundIndex(&@as(i32, 0), descending_raw, descending.len, @sizeOf(i32), compareOpaqueDescendingInt));
}

test "bsearchEqualRangeIndex reports duplicate spans and empty insertion points" {
    const ascending = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const descending = [_]i32{ 16, 9, 4, 4, 4, 1 };
    const ascending_raw: [*]const u8 = @ptrCast(ascending[0..].ptr);
    const descending_raw: [*]const u8 = @ptrCast(descending[0..].ptr);

    const ascending_range = bsearchEqualRangeIndex(&@as(i32, 4), ascending_raw, ascending.len, @sizeOf(i32), compareOpaqueInt);
    try std.testing.expectEqual(IndexRange{ .lower = 1, .upper = 4 }, ascending_range);
    try std.testing.expectEqual(@as(usize, 3), ascending_range.len());
    try std.testing.expect(!ascending_range.isEmpty());

    const ascending_missing = bsearchEqualRangeIndex(&@as(i32, 5), ascending_raw, ascending.len, @sizeOf(i32), compareOpaqueInt);
    try std.testing.expectEqual(IndexRange{ .lower = 4, .upper = 4 }, ascending_missing);
    try std.testing.expect(ascending_missing.isEmpty());

    const descending_range = bsearchEqualRangeIndex(&@as(i32, 4), descending_raw, descending.len, @sizeOf(i32), compareCOpaqueDescendingInt);
    try std.testing.expectEqual(IndexRange{ .lower = 2, .upper = 5 }, descending_range);
    try std.testing.expectEqual(@as(usize, 3), descending_range.len());

    const descending_missing = bsearchEqualRangeIndex(&@as(i32, 20), descending_raw, descending.len, @sizeOf(i32), compareCOpaqueDescendingInt);
    try std.testing.expectEqual(IndexRange{ .lower = 0, .upper = 0 }, descending_missing);
    try std.testing.expect(descending_missing.isEmpty());
}

test "raw comparator aliases accept native and C calling conventions" {
    const values = [_]i32{ 89, 55, 34, 21, 13, 8, 3 };
    const raw_comparators = [_]RawComparator{compareOpaqueDescendingInt};
    const c_raw_comparators = [_]CRawComparator{compareCOpaqueDescendingInt};

    for (raw_comparators) |compare| {
        try std.testing.expectEqual(@as(?usize, 3), bsearchIndex(&@as(i32, 21), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare));
        const found = bsearch(&@as(i32, 13), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare) orelse return error.TestUnexpectedResult;
        const typed_found: *const i32 = @ptrCast(@alignCast(found));
        try std.testing.expectEqual(@as(i32, 13), typed_found.*);
    }

    for (c_raw_comparators) |compare| {
        try std.testing.expectEqual(@as(?usize, 2), bsearchIndex(&@as(i32, 34), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare));
        const found = bsearch(&@as(i32, 8), @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compare) orelse return error.TestUnexpectedResult;
        const typed_found: *const i32 = @ptrCast(@alignCast(found));
        try std.testing.expectEqual(@as(i32, 8), typed_found.*);
    }
}

test "typed and raw helpers support heterogeneous keys" {
    var entries = [_]Entry{
        .{ .name = "alpha", .value = 1 },
        .{ .name = "beta", .value = 2 },
        .{ .name = "delta", .value = 4 },
        .{ .name = "omega", .value = 24 },
    };
    const typed_found = search([]const u8, Entry, &@as([]const u8, "delta"), entries[0..], compareName) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(u32, 4), typed_found.value);

    const raw_found = bsearch(@ptrCast(&@as([]const u8, "beta")), @ptrCast(entries[0..].ptr), entries.len, @sizeOf(Entry), compareOpaqueName) orelse return error.TestUnexpectedResult;
    const typed_raw_found: *const Entry = @ptrCast(@alignCast(raw_found));
    try std.testing.expectEqual(@as(u32, 2), typed_raw_found.value);
}
