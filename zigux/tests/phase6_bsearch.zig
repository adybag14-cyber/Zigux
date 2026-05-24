const std = @import("std");
const bsearch = @import("bsearch");
const fixtures = @import("fixtures/phase6_bsearch_vectors.zig");

fn compareDirectInt(key: *const u32, item: *const u32) i32 {
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareDirectDescendingInt(key: *const u32, item: *const u32) i32 {
    return switch (std.math.order(item.*, key.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareDirectOrderInt(key: *const u32, item: *const u32) std.math.Order {
    return std.math.order(key.*, item.*);
}

fn compareDirectDescendingOrderInt(key: *const u32, item: *const u32) std.math.Order {
    return std.math.order(item.*, key.*);
}

fn compareCDirectInt(key: *const u32, item: *const u32) callconv(.c) c_int {
    return @as(c_int, compareDirectInt(key, item));
}

fn compareCDirectDescendingInt(key: *const u32, item: *const u32) callconv(.c) c_int {
    return @as(c_int, compareDirectDescendingInt(key, item));
}

fn compareDirectOpaqueOrderInt(key: *const anyopaque, item: *const anyopaque) std.math.Order {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareDirectOrderInt(typed_key, typed_item);
}

fn compareDirectOpaqueDescendingOrderInt(key: *const anyopaque, item: *const anyopaque) std.math.Order {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareDirectDescendingOrderInt(typed_key, typed_item);
}

fn compareDirectOpaqueInt(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareDirectInt(typed_key, typed_item);
}

fn compareCOpaqueInt(key: *const anyopaque, item: *const anyopaque) callconv(.c) c_int {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return @as(c_int, compareDirectInt(typed_key, typed_item));
}

fn compareCOpaqueDescendingInt(key: *const anyopaque, item: *const anyopaque) callconv(.c) c_int {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return @as(c_int, compareDirectDescendingInt(typed_key, typed_item));
}

test "phase 6 bsearch runtime-selected native order comparator pointers keep mutable aliases write-through aligned" {
    const typed_ascending_compare = compareDirectOrderInt;
    const typed_descending_compare = compareDirectDescendingOrderInt;
    const raw_ascending_compare: bsearch.RawOrderComparator = compareDirectOpaqueOrderInt;
    const raw_descending_compare: bsearch.RawOrderComparator = compareDirectOpaqueDescendingOrderInt;

    var typed_values = fixtures.representative_ascending_values;
    const typed_key = @as(u32, 24);
    const typed_hit = bsearch.searchMutable(u32, u32, &typed_key, typed_values[0..], typed_ascending_compare) orelse return error.ExpectedMatch;
    typed_hit.* = 25;
    try std.testing.expectEqual(@as(u32, 25), typed_values[7]);

    const raw_key = @as(u32, 25);
    const raw_hit = bsearch.bsearchMutable(&raw_key, @ptrCast(typed_values[0..].ptr), typed_values.len, @sizeOf(u32), raw_ascending_compare) orelse return error.ExpectedMatch;
    const typed_raw_hit: *u32 = @ptrCast(@alignCast(raw_hit));
    typed_raw_hit.* = 26;
    try std.testing.expectEqual(@as(u32, 26), typed_values[7]);

    var ascending_duplicates = fixtures.representative_duplicate_values;
    const ascending_duplicate_key = @as(u32, 21);
    const typed_lower = bsearch.lowerBoundMutable(u32, u32, &ascending_duplicate_key, ascending_duplicates[0..], typed_ascending_compare) orelse return error.ExpectedMatch;
    typed_lower.* = 22;
    try std.testing.expectEqual(@as(u32, 22), ascending_duplicates[4]);

    const typed_upper = bsearch.upperBoundMutable(u32, u32, &ascending_duplicate_key, ascending_duplicates[0..], typed_ascending_compare) orelse return error.ExpectedMatch;
    typed_upper.* = 23;
    try std.testing.expectEqual(@as(u32, 23), ascending_duplicates[7]);

    var raw_ascending_duplicates = fixtures.representative_duplicate_values;
    const raw_lower = bsearch.bsearchLowerBoundMutable(&ascending_duplicate_key, @ptrCast(raw_ascending_duplicates[0..].ptr), raw_ascending_duplicates.len, @sizeOf(u32), raw_ascending_compare) orelse return error.ExpectedMatch;
    const typed_raw_lower: *u32 = @ptrCast(@alignCast(raw_lower));
    typed_raw_lower.* = 22;
    try std.testing.expectEqual(@as(u32, 22), raw_ascending_duplicates[4]);

    const raw_upper = bsearch.bsearchUpperBoundMutable(&ascending_duplicate_key, @ptrCast(raw_ascending_duplicates[0..].ptr), raw_ascending_duplicates.len, @sizeOf(u32), raw_ascending_compare) orelse return error.ExpectedMatch;
    const typed_raw_upper: *u32 = @ptrCast(@alignCast(raw_upper));
    typed_raw_upper.* = 23;
    try std.testing.expectEqual(@as(u32, 23), raw_ascending_duplicates[7]);

    var typed_descending_duplicates = fixtures.representative_descending_duplicate_values;
    const descending_duplicate_key = @as(u32, 21);
    const typed_descending_range = bsearch.equalRangeMutable(u32, u32, &descending_duplicate_key, typed_descending_duplicates[0..], typed_descending_compare);
    try std.testing.expectEqual(@as(usize, 3), typed_descending_range.len);
    try std.testing.expectEqualSlices(u32, &[_]u32{ 21, 21, 21 }, typed_descending_range);
    typed_descending_range[0] = 22;
    typed_descending_range[typed_descending_range.len - 1] = 20;
    try std.testing.expectEqualSlices(u32, &[_]u32{ 45, 42, 39, 22, 21, 20, 12, 9, 6, 3 }, typed_descending_duplicates[0..]);

    var raw_descending_duplicates = fixtures.representative_descending_duplicate_values;
    const raw_descending_bytes = bsearch.bsearchEqualRangeMutable(&descending_duplicate_key, @ptrCast(raw_descending_duplicates[0..].ptr), raw_descending_duplicates.len, @sizeOf(u32), raw_descending_compare);
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(u32)), raw_descending_bytes.len);
    const typed_raw_descending_ptr: [*]u32 = @ptrCast(@alignCast(raw_descending_bytes.ptr));
    const typed_raw_descending = typed_raw_descending_ptr[0 .. raw_descending_bytes.len / @sizeOf(u32)];
    try std.testing.expectEqualSlices(u32, &[_]u32{ 21, 21, 21 }, typed_raw_descending);
    typed_raw_descending[0] = 22;
    typed_raw_descending[typed_raw_descending.len - 1] = 20;
    try std.testing.expectEqualSlices(u32, &[_]u32{ 45, 42, 39, 22, 21, 20, 12, 9, 6, 3 }, raw_descending_duplicates[0..]);
}

test "phase 6 bsearch runtime-selected c abi comparator pointers keep mutable aliases write-through aligned" {
    const typed_ascending_compare = compareCDirectInt;
    const typed_descending_compare = compareCDirectDescendingInt;
    const raw_ascending_compare: bsearch.CRawComparator = compareCOpaqueInt;
    const raw_descending_compare: bsearch.CRawComparator = compareCOpaqueDescendingInt;

    var typed_values = fixtures.representative_ascending_values;
    const typed_key = @as(u32, 24);
    const typed_hit = bsearch.searchMutable(u32, u32, &typed_key, typed_values[0..], typed_ascending_compare) orelse return error.ExpectedMatch;
    typed_hit.* = 25;
    try std.testing.expectEqual(@as(u32, 25), typed_values[7]);

    const raw_key = @as(u32, 25);
    const raw_hit = bsearch.bsearchMutable(&raw_key, @ptrCast(typed_values[0..].ptr), typed_values.len, @sizeOf(u32), raw_ascending_compare) orelse return error.ExpectedMatch;
    const typed_raw_hit: *u32 = @ptrCast(@alignCast(raw_hit));
    typed_raw_hit.* = 26;
    try std.testing.expectEqual(@as(u32, 26), typed_values[7]);

    var ascending_duplicates = fixtures.representative_duplicate_values;
    const ascending_duplicate_key = @as(u32, 21);
    const typed_lower = bsearch.lowerBoundMutable(u32, u32, &ascending_duplicate_key, ascending_duplicates[0..], typed_ascending_compare) orelse return error.ExpectedMatch;
    typed_lower.* = 22;
    try std.testing.expectEqual(@as(u32, 22), ascending_duplicates[4]);

    const typed_upper = bsearch.upperBoundMutable(u32, u32, &ascending_duplicate_key, ascending_duplicates[0..], typed_ascending_compare) orelse return error.ExpectedMatch;
    typed_upper.* = 23;
    try std.testing.expectEqual(@as(u32, 23), ascending_duplicates[7]);

    var raw_ascending_duplicates = fixtures.representative_duplicate_values;
    const raw_lower = bsearch.bsearchLowerBoundMutable(&ascending_duplicate_key, @ptrCast(raw_ascending_duplicates[0..].ptr), raw_ascending_duplicates.len, @sizeOf(u32), raw_ascending_compare) orelse return error.ExpectedMatch;
    const typed_raw_lower: *u32 = @ptrCast(@alignCast(raw_lower));
    typed_raw_lower.* = 22;
    try std.testing.expectEqual(@as(u32, 22), raw_ascending_duplicates[4]);

    const raw_upper = bsearch.bsearchUpperBoundMutable(&ascending_duplicate_key, @ptrCast(raw_ascending_duplicates[0..].ptr), raw_ascending_duplicates.len, @sizeOf(u32), raw_ascending_compare) orelse return error.ExpectedMatch;
    const typed_raw_upper: *u32 = @ptrCast(@alignCast(raw_upper));
    typed_raw_upper.* = 23;
    try std.testing.expectEqual(@as(u32, 23), raw_ascending_duplicates[7]);

    var typed_descending_duplicates = fixtures.representative_descending_duplicate_values;
    const descending_duplicate_key = @as(u32, 21);
    const typed_descending_range = bsearch.equalRangeMutable(u32, u32, &descending_duplicate_key, typed_descending_duplicates[0..], typed_descending_compare);
    try std.testing.expectEqual(@as(usize, 3), typed_descending_range.len);
    try std.testing.expectEqualSlices(u32, &[_]u32{ 21, 21, 21 }, typed_descending_range);
    typed_descending_range[0] = 22;
    typed_descending_range[typed_descending_range.len - 1] = 20;
    try std.testing.expectEqualSlices(u32, &[_]u32{ 45, 42, 39, 22, 21, 20, 12, 9, 6, 3 }, typed_descending_duplicates[0..]);

    var raw_descending_duplicates = fixtures.representative_descending_duplicate_values;
    const raw_descending_bytes = bsearch.bsearchEqualRangeMutable(&descending_duplicate_key, @ptrCast(raw_descending_duplicates[0..].ptr), raw_descending_duplicates.len, @sizeOf(u32), raw_descending_compare);
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(u32)), raw_descending_bytes.len);
    const typed_raw_descending_ptr: [*]u32 = @ptrCast(@alignCast(raw_descending_bytes.ptr));
    const typed_raw_descending = typed_raw_descending_ptr[0 .. raw_descending_bytes.len / @sizeOf(u32)];
    try std.testing.expectEqualSlices(u32, &[_]u32{ 21, 21, 21 }, typed_raw_descending);
    typed_raw_descending[0] = 22;
    typed_raw_descending[typed_raw_descending.len - 1] = 20;
    try std.testing.expectEqualSlices(u32, &[_]u32{ 45, 42, 39, 22, 21, 20, 12, 9, 6, 3 }, raw_descending_duplicates[0..]);
}
