// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

const CComparatorResult = c_int;

pub fn Comparator(comptime Key: type, comptime T: type) type {
    return *const fn (*const Key, *const T) i32;
}

pub fn CComparator(comptime Key: type, comptime T: type) type {
    return *const fn (*const Key, *const T) callconv(.c) CComparatorResult;
}

pub const RawComparator = *const fn (*const anyopaque, *const anyopaque) i32;
pub const CRawComparator = *const fn (*const anyopaque, *const anyopaque) callconv(.c) CComparatorResult;

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

fn expectedComparatorReturnType(comptime fn_info: std.builtin.Type.Fn) type {
    return if (fn_info.calling_convention.eql(std.builtin.CallingConvention.c)) CComparatorResult else i32;
}

fn validateComparator(comptime Key: type, comptime T: type, comptime Compare: type) void {
    const fn_info = switch (@typeInfo(Compare)) {
        .@"fn" => |info| info,
        .pointer => |pointer| switch (@typeInfo(pointer.child)) {
            .@"fn" => |info| info,
            else => @compileError("bsearch comparator must be a function or function pointer"),
        },
        else => @compileError("bsearch comparator must be a function or function pointer"),
    };

    if (fn_info.params.len != 2) @compileError("bsearch comparator must accept exactly two parameters");
    if (fn_info.params[0].type orelse @compileError("bsearch comparator key parameter must be typed") != *const Key) {
        @compileError("bsearch comparator first parameter must be *const Key");
    }
    if (fn_info.params[1].type orelse @compileError("bsearch comparator item parameter must be typed") != *const T) {
        @compileError("bsearch comparator second parameter must be *const T");
    }
    if (fn_info.return_type orelse @compileError("bsearch comparator return type must be explicit") != expectedComparatorReturnType(fn_info)) {
        @compileError("bsearch comparator return type must be i32 for native callconv or c_int for C ABI callconv");
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

    if (fn_info.params.len != 2) @compileError("bsearch raw comparator must accept exactly two parameters");
    if (fn_info.params[0].type orelse @compileError("bsearch raw comparator key parameter must be typed") != *const anyopaque) {
        @compileError("bsearch raw comparator first parameter must be *const anyopaque");
    }
    if (fn_info.params[1].type orelse @compileError("bsearch raw comparator item parameter must be typed") != *const anyopaque) {
        @compileError("bsearch raw comparator second parameter must be *const anyopaque");
    }
    if (fn_info.return_type orelse @compileError("bsearch raw comparator return type must be explicit") != expectedComparatorReturnType(fn_info)) {
        @compileError("bsearch raw comparator return type must be i32 for native callconv or c_int for C ABI callconv");
    }
}

fn normalizeCompareResult(result: anytype) i32 {
    return if (result < 0) -1 else if (result > 0) 1 else 0;
}

fn advanceSearchWindow(start: *usize, count: *usize, pivot_index: usize, result: i32) bool {
    if (result == 0) return true;
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

pub fn searchIndex(comptime Key: type, comptime T: type, key: *const Key, items: []const T, compare: anytype) ?usize {
    comptime validateComparator(Key, T, @TypeOf(compare));
    var start: usize = 0;
    var count = items.len;
    while (count > 0) {
        const pivot_index = start + (count >> 1);
        if (advanceSearchWindow(&start, &count, pivot_index, normalizeCompareResult(compare(key, &items[pivot_index])))) {
            return pivot_index;
        }
    }
    return null;
}

pub fn search(comptime Key: type, comptime T: type, key: *const Key, items: []const T, compare: anytype) ?*const T {
    const index = searchIndex(Key, T, key, items, compare) orelse return null;
    return &items[index];
}

pub fn searchMutable(comptime Key: type, comptime T: type, key: *const Key, items: []T, compare: anytype) ?*T {
    const index = searchIndex(Key, T, key, items, compare) orelse return null;
    return &items[index];
}

pub fn lowerBoundIndex(comptime Key: type, comptime T: type, key: *const Key, items: []const T, compare: anytype) usize {
    comptime validateComparator(Key, T, @TypeOf(compare));
    var start: usize = 0;
    var count = items.len;
    while (count > 0) {
        const pivot_index = start + (count >> 1);
        advanceLowerBoundWindow(&start, &count, pivot_index, normalizeCompareResult(compare(key, &items[pivot_index])));
    }
    return start;
}

pub fn lowerBound(comptime Key: type, comptime T: type, key: *const Key, items: []const T, compare: anytype) ?*const T {
    const index = lowerBoundIndex(Key, T, key, items, compare);
    if (index == items.len) return null;
    return &items[index];
}

pub fn lowerBoundMutable(comptime Key: type, comptime T: type, key: *const Key, items: []T, compare: anytype) ?*T {
    const index = lowerBoundIndex(Key, T, key, items, compare);
    if (index == items.len) return null;
    return &items[index];
}

pub fn upperBoundIndex(comptime Key: type, comptime T: type, key: *const Key, items: []const T, compare: anytype) usize {
    comptime validateComparator(Key, T, @TypeOf(compare));
    var start: usize = 0;
    var count = items.len;
    while (count > 0) {
        const pivot_index = start + (count >> 1);
        advanceUpperBoundWindow(&start, &count, pivot_index, normalizeCompareResult(compare(key, &items[pivot_index])));
    }
    return start;
}

pub fn upperBound(comptime Key: type, comptime T: type, key: *const Key, items: []const T, compare: anytype) ?*const T {
    const index = upperBoundIndex(Key, T, key, items, compare);
    if (index == items.len) return null;
    return &items[index];
}

pub fn upperBoundMutable(comptime Key: type, comptime T: type, key: *const Key, items: []T, compare: anytype) ?*T {
    const index = upperBoundIndex(Key, T, key, items, compare);
    if (index == items.len) return null;
    return &items[index];
}

pub fn equalRangeIndex(comptime Key: type, comptime T: type, key: *const Key, items: []const T, compare: anytype) IndexRange {
    return .{
        .lower = lowerBoundIndex(Key, T, key, items, compare),
        .upper = upperBoundIndex(Key, T, key, items, compare),
    };
}

pub fn equalRange(comptime Key: type, comptime T: type, key: *const Key, items: []const T, compare: anytype) []const T {
    return equalRangeIndex(Key, T, key, items, compare).sliceConst(T, items);
}

pub fn equalRangeMutable(comptime Key: type, comptime T: type, key: *const Key, items: []T, compare: anytype) []T {
    return equalRangeIndex(Key, T, key, items, compare).sliceMutable(T, items);
}

pub fn bsearchIndex(key: *const anyopaque, base: [*]const u8, num: usize, size: usize, compare: anytype) ?usize {
    comptime validateRawComparator(@TypeOf(compare));
    var start: usize = 0;
    var count = num;
    while (count > 0) {
        const pivot_index = start + (count >> 1);
        const pivot_ptr: *const anyopaque = @ptrCast(base + (pivot_index * size));
        if (advanceSearchWindow(&start, &count, pivot_index, normalizeCompareResult(compare(key, pivot_ptr)))) {
            return pivot_index;
        }
    }
    return null;
}

pub fn bsearch(key: *const anyopaque, base: [*]const u8, num: usize, size: usize, compare: anytype) ?*const anyopaque {
    const index = bsearchIndex(key, base, num, size, compare) orelse return null;
    return @ptrCast(base + (index * size));
}

pub fn bsearchMutable(key: *const anyopaque, base: [*]u8, num: usize, size: usize, compare: anytype) ?*anyopaque {
    const index = bsearchIndex(key, base, num, size, compare) orelse return null;
    return @ptrCast(base + (index * size));
}

pub fn bsearchLowerBoundIndex(key: *const anyopaque, base: [*]const u8, num: usize, size: usize, compare: anytype) usize {
    comptime validateRawComparator(@TypeOf(compare));
    var start: usize = 0;
    var count = num;
    while (count > 0) {
        const pivot_index = start + (count >> 1);
        const pivot_ptr: *const anyopaque = @ptrCast(base + (pivot_index * size));
        advanceLowerBoundWindow(&start, &count, pivot_index, normalizeCompareResult(compare(key, pivot_ptr)));
    }
    return start;
}

pub fn bsearchLowerBound(key: *const anyopaque, base: [*]const u8, num: usize, size: usize, compare: anytype) ?*const anyopaque {
    const index = bsearchLowerBoundIndex(key, base, num, size, compare);
    if (index == num) return null;
    return @ptrCast(base + (index * size));
}

pub fn bsearchLowerBoundMutable(key: *const anyopaque, base: [*]u8, num: usize, size: usize, compare: anytype) ?*anyopaque {
    const index = bsearchLowerBoundIndex(key, base, num, size, compare);
    if (index == num) return null;
    return @ptrCast(base + (index * size));
}

pub fn bsearchUpperBoundIndex(key: *const anyopaque, base: [*]const u8, num: usize, size: usize, compare: anytype) usize {
    comptime validateRawComparator(@TypeOf(compare));
    var start: usize = 0;
    var count = num;
    while (count > 0) {
        const pivot_index = start + (count >> 1);
        const pivot_ptr: *const anyopaque = @ptrCast(base + (pivot_index * size));
        advanceUpperBoundWindow(&start, &count, pivot_index, normalizeCompareResult(compare(key, pivot_ptr)));
    }
    return start;
}

pub fn bsearchUpperBound(key: *const anyopaque, base: [*]const u8, num: usize, size: usize, compare: anytype) ?*const anyopaque {
    const index = bsearchUpperBoundIndex(key, base, num, size, compare);
    if (index == num) return null;
    return @ptrCast(base + (index * size));
}

pub fn bsearchUpperBoundMutable(key: *const anyopaque, base: [*]u8, num: usize, size: usize, compare: anytype) ?*anyopaque {
    const index = bsearchUpperBoundIndex(key, base, num, size, compare);
    if (index == num) return null;
    return @ptrCast(base + (index * size));
}

pub fn bsearchEqualRangeIndex(key: *const anyopaque, base: [*]const u8, num: usize, size: usize, compare: anytype) IndexRange {
    return .{
        .lower = bsearchLowerBoundIndex(key, base, num, size, compare),
        .upper = bsearchUpperBoundIndex(key, base, num, size, compare),
    };
}

pub fn bsearchEqualRange(key: *const anyopaque, base: [*]const u8, num: usize, size: usize, compare: anytype) []const u8 {
    return bsearchEqualRangeIndex(key, base, num, size, compare).bytes(base, size);
}

pub fn bsearchEqualRangeMutable(key: *const anyopaque, base: [*]u8, num: usize, size: usize, compare: anytype) []u8 {
    return bsearchEqualRangeIndex(key, base, num, size, compare).bytesMutable(base, size);
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

fn compareCInt(key: *const i32, item: *const i32) callconv(.c) CComparatorResult {
    return @as(CComparatorResult, compareInt(key, item));
}

fn compareCDescendingInt(key: *const i32, item: *const i32) callconv(.c) CComparatorResult {
    return @as(CComparatorResult, compareDescendingInt(key, item));
}

fn compareCOpaqueInt(key: *const anyopaque, item: *const anyopaque) callconv(.c) CComparatorResult {
    const typed_key: *const i32 = @ptrCast(@alignCast(key));
    const typed_item: *const i32 = @ptrCast(@alignCast(item));
    return @as(CComparatorResult, compareInt(typed_key, typed_item));
}

fn compareCOpaqueDescendingInt(key: *const anyopaque, item: *const anyopaque) callconv(.c) CComparatorResult {
    const typed_key: *const i32 = @ptrCast(@alignCast(key));
    const typed_item: *const i32 = @ptrCast(@alignCast(item));
    return @as(CComparatorResult, compareDescendingInt(typed_key, typed_item));
}

fn compareOpaqueInt(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const i32 = @ptrCast(@alignCast(key));
    const typed_item: *const i32 = @ptrCast(@alignCast(item));
    return compareInt(typed_key, typed_item);
}

const CountedIntKey = struct {
    target: i32,
    comparisons: *usize,
};

fn compareCountedInt(key: *const CountedIntKey, item: *const i32) i32 {
    key.comparisons.* += 1;
    return switch (std.math.order(key.target, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareCountedOpaqueInt(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const CountedIntKey = @ptrCast(@alignCast(key));
    const typed_item: *const i32 = @ptrCast(@alignCast(item));
    typed_key.comparisons.* += 1;
    return switch (std.math.order(typed_key.target, typed_item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn expectTypedCAbiRange(items: []const i32, key: i32, expected: IndexRange, compare: CComparator(i32, i32)) !void {
    const lower = lowerBoundIndex(i32, i32, &key, items, compare);
    const upper = upperBoundIndex(i32, i32, &key, items, compare);
    const range = equalRangeIndex(i32, i32, &key, items, compare);
    const view = equalRange(i32, i32, &key, items, compare);

    try std.testing.expectEqual(expected.lower, lower);
    try std.testing.expectEqual(expected.upper, upper);
    try std.testing.expectEqual(expected, range);
    try std.testing.expectEqual(expected.len(), view.len);

    if (!expected.isEmpty()) {
        try std.testing.expectEqual(key, view[0]);
        try std.testing.expectEqual(key, view[expected.len() - 1]);
    }
}

fn expectRawCAbiRange(items: []const i32, key: i32, expected: IndexRange, compare: CRawComparator) !void {
    const base: [*]const u8 = @ptrCast(items.ptr);
    const lower = bsearchLowerBoundIndex(&key, base, items.len, @sizeOf(i32), compare);
    const upper = bsearchUpperBoundIndex(&key, base, items.len, @sizeOf(i32), compare);
    const range = bsearchEqualRangeIndex(&key, base, items.len, @sizeOf(i32), compare);
    const bytes = bsearchEqualRange(&key, base, items.len, @sizeOf(i32), compare);

    try std.testing.expectEqual(expected.lower, lower);
    try std.testing.expectEqual(expected.upper, upper);
    try std.testing.expectEqual(expected, range);
    try std.testing.expectEqual(expected.len() * @sizeOf(i32), bytes.len);

    if (!expected.isEmpty()) {
        const typed_bytes: [*]const i32 = @ptrCast(@alignCast(bytes.ptr));
        try std.testing.expectEqual(key, typed_bytes[0]);
        try std.testing.expectEqual(key, typed_bytes[expected.len() - 1]);
    }
}

test "typed and raw searches support duplicate spans and descending C ABI pointers" {
    const ascending = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const descending = [_]i32{ 16, 9, 4, 4, 4, 1 };
    const key = @as(i32, 4);

    const match_index = searchIndex(i32, i32, &key, ascending[0..], compareInt) orelse return error.TestUnexpectedResult;
    try std.testing.expect(match_index >= 1);
    try std.testing.expect(match_index < 4);
    try std.testing.expectEqual(IndexRange{ .lower = 1, .upper = 4 }, equalRangeIndex(i32, i32, &key, ascending[0..], compareInt));

    const raw_range = bsearchEqualRangeIndex(&key, @ptrCast(ascending[0..].ptr), ascending.len, @sizeOf(i32), compareOpaqueInt);
    try std.testing.expectEqual(IndexRange{ .lower = 1, .upper = 4 }, raw_range);

    const found = bsearch(&key, @ptrCast(descending[0..].ptr), descending.len, @sizeOf(i32), compareCOpaqueDescendingInt) orelse return error.TestUnexpectedResult;
    const typed_found: *const i32 = @ptrCast(@alignCast(found));
    try std.testing.expectEqual(@as(i32, 4), typed_found.*);
}

test "typed c abi comparator pointers keep duplicate spans and insertion points aligned" {
    const ascending = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const descending = [_]i32{ 16, 9, 4, 4, 4, 1 };

    const typed_cases = [_]struct {
        items: []const i32,
        key: i32,
        expected: IndexRange,
        compare: CComparator(i32, i32),
    }{
        .{ .items = ascending[0..], .key = 4, .expected = .{ .lower = 1, .upper = 4 }, .compare = compareCInt },
        .{ .items = ascending[0..], .key = 3, .expected = .{ .lower = 1, .upper = 1 }, .compare = compareCInt },
        .{ .items = descending[0..], .key = 4, .expected = .{ .lower = 2, .upper = 5 }, .compare = compareCDescendingInt },
        .{ .items = descending[0..], .key = 5, .expected = .{ .lower = 2, .upper = 2 }, .compare = compareCDescendingInt },
    };

    for (typed_cases) |case| {
        const found = search(i32, i32, &case.key, case.items, case.compare);
        if (case.expected.isEmpty()) {
            try std.testing.expectEqual(@as(?*const i32, null), found);
        } else {
            const typed_found = found orelse return error.TestUnexpectedResult;
            try std.testing.expectEqual(case.key, typed_found.*);
        }

        try expectTypedCAbiRange(case.items, case.key, case.expected, case.compare);
    }
}

test "raw c abi bounds keep duplicate spans and insertion points aligned" {
    const ascending = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const descending = [_]i32{ 16, 9, 4, 4, 4, 1 };

    try expectRawCAbiRange(ascending[0..], 4, .{ .lower = 1, .upper = 4 }, compareCOpaqueInt);
    try expectRawCAbiRange(ascending[0..], 3, .{ .lower = 1, .upper = 1 }, compareCOpaqueInt);
    try expectRawCAbiRange(descending[0..], 4, .{ .lower = 2, .upper = 5 }, compareCOpaqueDescendingInt);
    try expectRawCAbiRange(descending[0..], 5, .{ .lower = 2, .upper = 2 }, compareCOpaqueDescendingInt);
}

test "lower and upper bound wrappers return insertion-site elements across typed and raw comparators" {
    const ascending = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const descending = [_]i32{ 16, 9, 4, 4, 4, 1 };

    const typed_lower_hit_key = @as(i32, 4);
    const typed_lower_hit = lowerBound(i32, i32, &typed_lower_hit_key, ascending[0..], compareCInt) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 4), typed_lower_hit.*);
    try std.testing.expectEqual(@intFromPtr(&ascending[1]), @intFromPtr(typed_lower_hit));

    const typed_upper_hit = upperBound(i32, i32, &typed_lower_hit_key, ascending[0..], compareCInt) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 9), typed_upper_hit.*);
    try std.testing.expectEqual(@intFromPtr(&ascending[4]), @intFromPtr(typed_upper_hit));

    const typed_mid_key = @as(i32, 5);
    const typed_mid = lowerBound(i32, i32, &typed_mid_key, ascending[0..], compareCInt) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 9), typed_mid.*);
    try std.testing.expectEqual(@intFromPtr(&ascending[4]), @intFromPtr(typed_mid));

    const typed_upper_mid = upperBound(i32, i32, &typed_mid_key, ascending[0..], compareCInt) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 9), typed_upper_mid.*);
    try std.testing.expectEqual(@intFromPtr(&ascending[4]), @intFromPtr(typed_upper_mid));

    const typed_tail_key = @as(i32, 20);
    try std.testing.expectEqual(@as(?*const i32, null), lowerBound(i32, i32, &typed_tail_key, ascending[0..], compareCInt));
    try std.testing.expectEqual(@as(?*const i32, null), upperBound(i32, i32, &typed_tail_key, ascending[0..], compareCInt));

    const raw_hit_key = @as(i32, 4);
    const raw_hit = bsearchLowerBound(&raw_hit_key, @ptrCast(descending[0..].ptr), descending.len, @sizeOf(i32), compareCOpaqueDescendingInt) orelse return error.TestUnexpectedResult;
    const typed_raw_hit: *const i32 = @ptrCast(@alignCast(raw_hit));
    try std.testing.expectEqual(@as(i32, 4), typed_raw_hit.*);
    try std.testing.expectEqual(@intFromPtr(&descending[2]), @intFromPtr(typed_raw_hit));

    const raw_upper_hit = bsearchUpperBound(&raw_hit_key, @ptrCast(descending[0..].ptr), descending.len, @sizeOf(i32), compareCOpaqueDescendingInt) orelse return error.TestUnexpectedResult;
    const typed_raw_upper_hit: *const i32 = @ptrCast(@alignCast(raw_upper_hit));
    try std.testing.expectEqual(@as(i32, 1), typed_raw_upper_hit.*);
    try std.testing.expectEqual(@intFromPtr(&descending[5]), @intFromPtr(typed_raw_upper_hit));

    const raw_mid_key = @as(i32, 5);
    const raw_mid = bsearchLowerBound(&raw_mid_key, @ptrCast(descending[0..].ptr), descending.len, @sizeOf(i32), compareCOpaqueDescendingInt) orelse return error.TestUnexpectedResult;
    const typed_raw_mid: *const i32 = @ptrCast(@alignCast(raw_mid));
    try std.testing.expectEqual(@as(i32, 4), typed_raw_mid.*);
    try std.testing.expectEqual(@intFromPtr(&descending[2]), @intFromPtr(typed_raw_mid));

    const raw_upper_mid = bsearchUpperBound(&raw_mid_key, @ptrCast(descending[0..].ptr), descending.len, @sizeOf(i32), compareCOpaqueDescendingInt) orelse return error.TestUnexpectedResult;
    const typed_raw_upper_mid: *const i32 = @ptrCast(@alignCast(raw_upper_mid));
    try std.testing.expectEqual(@as(i32, 4), typed_raw_upper_mid.*);
    try std.testing.expectEqual(@intFromPtr(&descending[2]), @intFromPtr(typed_raw_upper_mid));

    const raw_tail_key = @as(i32, 0);
    try std.testing.expectEqual(@as(?*const anyopaque, null), bsearchLowerBound(&raw_tail_key, @ptrCast(descending[0..].ptr), descending.len, @sizeOf(i32), compareCOpaqueDescendingInt));
    try std.testing.expectEqual(@as(?*const anyopaque, null), bsearchUpperBound(&raw_tail_key, @ptrCast(descending[0..].ptr), descending.len, @sizeOf(i32), compareCOpaqueDescendingInt));
}

test "mutable lower and upper bound wrappers keep write-through aliases" {
    var values = [_]i32{ 2, 4, 7, 11, 16, 23, 42 };
    const key = @as(i32, 11);

    const typed = searchMutable(i32, i32, &key, values[0..], compareInt) orelse return error.TestUnexpectedResult;
    typed.* = 12;
    try std.testing.expectEqual(@as(i32, 12), values[3]);

    const raw_key = @as(i32, 12);
    const raw = bsearchMutable(&raw_key, @ptrCast(values[0..].ptr), values.len, @sizeOf(i32), compareOpaqueInt) orelse return error.TestUnexpectedResult;
    const typed_raw: *i32 = @ptrCast(@alignCast(raw));
    typed_raw.* = 13;
    try std.testing.expectEqual(@as(i32, 13), values[3]);

    var typed_duplicates = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const duplicate_key = @as(i32, 4);

    const typed_lower = lowerBoundMutable(i32, i32, &duplicate_key, typed_duplicates[0..], compareInt) orelse return error.TestUnexpectedResult;
    typed_lower.* = 5;
    try std.testing.expectEqual(@as(i32, 5), typed_duplicates[1]);

    const typed_upper = upperBoundMutable(i32, i32, &duplicate_key, typed_duplicates[0..], compareInt) orelse return error.TestUnexpectedResult;
    typed_upper.* = 10;
    try std.testing.expectEqual(@as(i32, 10), typed_duplicates[4]);

    var raw_duplicates = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const raw_lower = bsearchLowerBoundMutable(&duplicate_key, @ptrCast(raw_duplicates[0..].ptr), raw_duplicates.len, @sizeOf(i32), compareOpaqueInt) orelse return error.TestUnexpectedResult;
    const typed_raw_lower: *i32 = @ptrCast(@alignCast(raw_lower));
    typed_raw_lower.* = 6;
    try std.testing.expectEqual(@as(i32, 6), raw_duplicates[1]);

    const raw_upper = bsearchUpperBoundMutable(&duplicate_key, @ptrCast(raw_duplicates[0..].ptr), raw_duplicates.len, @sizeOf(i32), compareOpaqueInt) orelse return error.TestUnexpectedResult;
    const typed_raw_upper: *i32 = @ptrCast(@alignCast(raw_upper));
    typed_raw_upper.* = 10;
    try std.testing.expectEqual(@as(i32, 10), raw_duplicates[4]);
}

test "mutable equal-range wrappers expose whole duplicate spans for typed and raw aliases" {
    var typed_duplicates = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const key = @as(i32, 4);

    const typed_range = equalRangeMutable(i32, i32, &key, typed_duplicates[0..], compareInt);
    try std.testing.expectEqual(@as(usize, 3), typed_range.len);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 4, 4 }, typed_range);
    typed_range[0] = 5;
    typed_range[typed_range.len - 1] = 6;
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 5, 4, 6, 9, 16 }, typed_duplicates[0..]);

    var raw_duplicates = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const raw_bytes = bsearchEqualRangeMutable(&key, @ptrCast(raw_duplicates[0..].ptr), raw_duplicates.len, @sizeOf(i32), compareOpaqueInt);
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(i32)), raw_bytes.len);
    const raw_words_ptr: [*]i32 = @ptrCast(@alignCast(raw_bytes.ptr));
    const raw_words = raw_words_ptr[0 .. raw_bytes.len / @sizeOf(i32)];
    try std.testing.expectEqual(@as(usize, 3), raw_words.len);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 4, 4 }, raw_words);
    raw_words[0] = 7;
    raw_words[raw_words.len - 1] = 8;
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 7, 4, 8, 9, 16 }, raw_duplicates[0..]);
}

test "index range views keep typed and byte aliases aligned for hits and insertion sites" {
    const duplicates = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const duplicate_range = IndexRange{ .lower = 1, .upper = 4 };

    const typed_view = duplicate_range.sliceConst(i32, duplicates[0..]);
    try std.testing.expectEqual(@as(usize, 3), typed_view.len);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 4, 4 }, typed_view);
    try std.testing.expectEqual(@intFromPtr(&duplicates[1]), @intFromPtr(typed_view.ptr));

    const byte_view = duplicate_range.bytes(@ptrCast(duplicates[0..].ptr), @sizeOf(i32));
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(i32)), byte_view.len);
    try std.testing.expectEqual(
        @intFromPtr(@as([*]const u8, @ptrCast(duplicates[0..].ptr)) + @sizeOf(i32)),
        @intFromPtr(byte_view.ptr),
    );
    const typed_byte_view: [*]const i32 = @ptrCast(@alignCast(byte_view.ptr));
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 4, 4 }, typed_byte_view[0 .. byte_view.len / @sizeOf(i32)]);

    const missing_range = IndexRange{ .lower = 4, .upper = 4 };
    const missing_typed_view = missing_range.sliceConst(i32, duplicates[0..]);
    try std.testing.expectEqual(@as(usize, 0), missing_typed_view.len);
    try std.testing.expectEqual(@intFromPtr(&duplicates[4]), @intFromPtr(missing_typed_view.ptr));

    const missing_byte_view = missing_range.bytes(@ptrCast(duplicates[0..].ptr), @sizeOf(i32));
    try std.testing.expectEqual(@as(usize, 0), missing_byte_view.len);
    try std.testing.expectEqual(
        @intFromPtr(@as([*]const u8, @ptrCast(duplicates[0..].ptr)) + (4 * @sizeOf(i32))),
        @intFromPtr(missing_byte_view.ptr),
    );

    var mutable_duplicates = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const mutable_typed_view = duplicate_range.sliceMutable(i32, mutable_duplicates[0..]);
    mutable_typed_view[0] = 5;
    mutable_typed_view[mutable_typed_view.len - 1] = 6;
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 5, 4, 6, 9, 16 }, mutable_duplicates[0..]);

    var mutable_raw_duplicates = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const mutable_byte_view = duplicate_range.bytesMutable(@ptrCast(mutable_raw_duplicates[0..].ptr), @sizeOf(i32));
    const typed_mutable_byte_view: [*]i32 = @ptrCast(@alignCast(mutable_byte_view.ptr));
    const mutable_words = typed_mutable_byte_view[0 .. mutable_byte_view.len / @sizeOf(i32)];
    mutable_words[0] = 7;
    mutable_words[mutable_words.len - 1] = 8;
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 7, 4, 8, 9, 16 }, mutable_raw_duplicates[0..]);
}

test "empty and missing equal-range wrappers preserve insertion-site slices without comparator churn" {
    const empty = [_]i32{};

    var typed_comparisons: usize = 0;
    const empty_typed_key = CountedIntKey{ .target = 4, .comparisons = &typed_comparisons };
    try std.testing.expectEqual(@as(?usize, null), searchIndex(CountedIntKey, i32, &empty_typed_key, empty[0..], compareCountedInt));
    try std.testing.expectEqual(@as(?*const i32, null), search(CountedIntKey, i32, &empty_typed_key, empty[0..], compareCountedInt));
    try std.testing.expectEqual(@as(?*const i32, null), lowerBound(CountedIntKey, i32, &empty_typed_key, empty[0..], compareCountedInt));
    try std.testing.expectEqual(@as(?*const i32, null), upperBound(CountedIntKey, i32, &empty_typed_key, empty[0..], compareCountedInt));
    try std.testing.expectEqual(@as(usize, 0), typed_comparisons);

    const empty_typed_range = equalRangeIndex(CountedIntKey, i32, &empty_typed_key, empty[0..], compareCountedInt);
    try std.testing.expectEqual(IndexRange{ .lower = 0, .upper = 0 }, empty_typed_range);
    const empty_typed_view = equalRange(CountedIntKey, i32, &empty_typed_key, empty[0..], compareCountedInt);
    try std.testing.expectEqual(@as(usize, 0), empty_typed_view.len);
    try std.testing.expectEqual(@as(usize, 0), typed_comparisons);

    var raw_comparisons: usize = 0;
    const empty_raw_key = CountedIntKey{ .target = 4, .comparisons = &raw_comparisons };
    const empty_base: [*]const u8 = @ptrCast(empty[0..].ptr);
    try std.testing.expectEqual(@as(?usize, null), bsearchIndex(&empty_raw_key, empty_base, empty.len, @sizeOf(i32), compareCountedOpaqueInt));
    try std.testing.expectEqual(@as(?*const anyopaque, null), bsearch(&empty_raw_key, empty_base, empty.len, @sizeOf(i32), compareCountedOpaqueInt));
    try std.testing.expectEqual(@as(?*const anyopaque, null), bsearchLowerBound(&empty_raw_key, empty_base, empty.len, @sizeOf(i32), compareCountedOpaqueInt));
    try std.testing.expectEqual(@as(?*const anyopaque, null), bsearchUpperBound(&empty_raw_key, empty_base, empty.len, @sizeOf(i32), compareCountedOpaqueInt));
    try std.testing.expectEqual(@as(usize, 0), raw_comparisons);

    const empty_raw_range = bsearchEqualRangeIndex(&empty_raw_key, empty_base, empty.len, @sizeOf(i32), compareCountedOpaqueInt);
    try std.testing.expectEqual(IndexRange{ .lower = 0, .upper = 0 }, empty_raw_range);
    const empty_raw_bytes = bsearchEqualRange(&empty_raw_key, empty_base, empty.len, @sizeOf(i32), compareCountedOpaqueInt);
    try std.testing.expectEqual(@as(usize, 0), empty_raw_bytes.len);
    try std.testing.expectEqual(@as(usize, 0), raw_comparisons);

    const ascending = [_]i32{ 1, 4, 4, 4, 9, 16 };
    const missing_key = @as(i32, 3);
    const typed_missing = equalRange(i32, i32, &missing_key, ascending[0..], compareInt);
    try std.testing.expectEqual(@as(usize, 0), typed_missing.len);
    try std.testing.expectEqual(@intFromPtr(&ascending[1]), @intFromPtr(typed_missing.ptr));

    const missing_raw = bsearchEqualRange(&missing_key, @ptrCast(ascending[0..].ptr), ascending.len, @sizeOf(i32), compareOpaqueInt);
    try std.testing.expectEqual(@as(usize, 0), missing_raw.len);
    try std.testing.expectEqual(
        @intFromPtr(@as([*]const u8, @ptrCast(ascending[0..].ptr)) + @sizeOf(i32)),
        @intFromPtr(missing_raw.ptr),
    );
}
