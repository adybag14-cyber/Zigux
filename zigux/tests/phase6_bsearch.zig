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

fn compareSymbol(key: *const []const u8, item: *const []const u8) i32 {
    return switch (std.mem.order(u8, key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn comparePackedRecordKey(key: *const u32, item: *const fixtures.RawRecord) i32 {
    return switch (std.math.order(key.*, item.key)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn comparePackedRecordOpaque(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const fixtures.RawRecord = @ptrCast(@alignCast(item));
    return comparePackedRecordKey(typed_key, typed_item);
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

    var raw_duplicates = fixtures.representative_duplicate_values;
    const raw_lower = bsearch.bsearchLowerBoundMutable(&ascending_duplicate_key, @ptrCast(raw_duplicates[0..].ptr), raw_duplicates.len, @sizeOf(u32), raw_ascending_compare) orelse return error.ExpectedMatch;
    const typed_raw_lower: *u32 = @ptrCast(@alignCast(raw_lower));
    typed_raw_lower.* = 22;
    try std.testing.expectEqual(@as(u32, 22), raw_duplicates[4]);

    const raw_upper = bsearch.bsearchUpperBoundMutable(&ascending_duplicate_key, @ptrCast(raw_duplicates[0..].ptr), raw_duplicates.len, @sizeOf(u32), raw_ascending_compare) orelse return error.ExpectedMatch;
    const typed_raw_upper: *u32 = @ptrCast(@alignCast(raw_upper));
    typed_raw_upper.* = 23;
    try std.testing.expectEqual(@as(u32, 23), raw_duplicates[7]);

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

test "phase 6 bsearch direct equalRange wrappers keep duplicate-span and write-through coverage aligned" {
    var ascending_duplicates = fixtures.representative_duplicate_values;
    const key = @as(u32, 21);

    const typed_range = bsearch.equalRange(u32, u32, &key, ascending_duplicates[0..], compareDirectInt);
    try std.testing.expectEqual(@as(usize, 3), typed_range.len);
    try std.testing.expectEqualSlices(u32, &[_]u32{ 21, 21, 21 }, typed_range);

    const typed_range_mutable = bsearch.equalRangeMutable(u32, u32, &key, ascending_duplicates[0..], compareDirectInt);
    typed_range_mutable[0] = 22;
    typed_range_mutable[typed_range_mutable.len - 1] = 20;
    try std.testing.expectEqualSlices(u32, &[_]u32{ 3, 6, 9, 12, 22, 21, 20, 24, 27, 30, 33, 36, 39, 42, 45 }, ascending_duplicates[0..]);

    var raw_duplicates = fixtures.representative_duplicate_values;
    const raw_bytes = bsearch.bsearchEqualRangeMutable(&key, @ptrCast(raw_duplicates[0..].ptr), raw_duplicates.len, @sizeOf(u32), compareDirectOpaqueInt);
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(u32)), raw_bytes.len);
    const typed_raw_ptr: [*]u32 = @ptrCast(@alignCast(raw_bytes.ptr));
    const typed_raw = typed_raw_ptr[0 .. raw_bytes.len / @sizeOf(u32)];
    try std.testing.expectEqualSlices(u32, &[_]u32{ 21, 21, 21 }, typed_raw);
    typed_raw[0] = 22;
    typed_raw[typed_raw.len - 1] = 20;
    try std.testing.expectEqualSlices(u32, &[_]u32{ 3, 6, 9, 12, 22, 21, 20, 24, 27, 30, 33, 36, 39, 42, 45 }, raw_duplicates[0..]);
}

test "phase 6 bsearch direct descending equalRange wrappers keep duplicate-span and write-through coverage aligned" {
    var descending_duplicates = fixtures.representative_descending_duplicate_values;
    const key = @as(u32, 21);

    const typed_range = bsearch.equalRange(u32, u32, &key, descending_duplicates[0..], compareDirectDescendingInt);
    try std.testing.expectEqual(@as(usize, 3), typed_range.len);
    try std.testing.expectEqualSlices(u32, &[_]u32{ 21, 21, 21 }, typed_range);

    const typed_range_mutable = bsearch.equalRangeMutable(u32, u32, &key, descending_duplicates[0..], compareDirectDescendingInt);
    typed_range_mutable[0] = 22;
    typed_range_mutable[typed_range_mutable.len - 1] = 20;
    try std.testing.expectEqualSlices(u32, &[_]u32{ 45, 42, 39, 22, 21, 20, 12, 9, 6, 3 }, descending_duplicates[0..]);

    var raw_duplicates = fixtures.representative_descending_duplicate_values;
    const raw_bytes = bsearch.bsearchEqualRangeMutable(&key, @ptrCast(raw_duplicates[0..].ptr), raw_duplicates.len, @sizeOf(u32), compareCOpaqueDescendingInt);
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(u32)), raw_bytes.len);
    const typed_raw_ptr: [*]u32 = @ptrCast(@alignCast(raw_bytes.ptr));
    const typed_raw = typed_raw_ptr[0 .. raw_bytes.len / @sizeOf(u32)];
    try std.testing.expectEqualSlices(u32, &[_]u32{ 21, 21, 21 }, typed_raw);
    typed_raw[0] = 22;
    typed_raw[typed_raw.len - 1] = 20;
    try std.testing.expectEqualSlices(u32, &[_]u32{ 45, 42, 39, 22, 21, 20, 12, 9, 6, 3 }, raw_duplicates[0..]);
}

test "phase 6 bsearch accepts runtime-selected descending raw c abi comparator pointers" {
    const compare: bsearch.CRawComparator = compareCOpaqueDescendingInt;
    const key = @as(u32, 21);
    const hit = bsearch.bsearch(&key, @ptrCast(fixtures.representative_descending_duplicate_values[0..].ptr), fixtures.representative_descending_duplicate_values.len, @sizeOf(u32), compare) orelse return error.ExpectedMatch;
    const typed_hit: *const u32 = @ptrCast(@alignCast(hit));
    try std.testing.expectEqual(@as(u32, 21), typed_hit.*);
    try std.testing.expectEqual(@as(usize, 3), bsearch.bsearchLowerBoundIndex(&key, @ptrCast(fixtures.representative_descending_duplicate_values[0..].ptr), fixtures.representative_descending_duplicate_values.len, @sizeOf(u32), compare));
    try std.testing.expectEqual(@as(usize, 6), bsearch.bsearchUpperBoundIndex(&key, @ptrCast(fixtures.representative_descending_duplicate_values[0..].ptr), fixtures.representative_descending_duplicate_values.len, @sizeOf(u32), compare));
}

test "phase 6 bsearch accepts runtime-selected typed c abi comparator pointers" {
    const compare = compareCDirectInt;
    const key = @as(u32, 21);
    const hit = bsearch.search(u32, u32, &key, fixtures.representative_duplicate_values[0..], compare) orelse return error.ExpectedMatch;
    try std.testing.expectEqual(@as(u32, 21), hit.*);
    try std.testing.expectEqual(@as(usize, 4), bsearch.lowerBoundIndex(u32, u32, &key, fixtures.representative_duplicate_values[0..], compare));
    try std.testing.expectEqual(@as(usize, 7), bsearch.upperBoundIndex(u32, u32, &key, fixtures.representative_duplicate_values[0..], compare));
}

test "phase 6 bsearch keeps symbol fixtures searchable through typed bounds" {
    const key = @as([]const u8, "kmalloc");
    const lower = bsearch.lowerBound([]const u8, []const u8, &key, fixtures.sorted_symbols[0..], compareSymbol) orelse return error.ExpectedMatch;
    try std.testing.expectEqualStrings("kmalloc", lower.*);

    const upper = bsearch.upperBound([]const u8, []const u8, &key, fixtures.sorted_symbols[0..], compareSymbol) orelse return error.ExpectedMatch;
    try std.testing.expectEqualStrings("schedule", upper.*);

    const miss = @as([]const u8, "ksys");
    try std.testing.expectEqual(@as(usize, 2), bsearch.lowerBoundIndex([]const u8, []const u8, &miss, fixtures.sorted_symbols[0..], compareSymbol));
    try std.testing.expectEqual(@as(usize, 2), bsearch.upperBoundIndex([]const u8, []const u8, &miss, fixtures.sorted_symbols[0..], compareSymbol));
}

test "phase 6 bsearch keeps packed-record fixtures searchable through raw wrappers" {
    const key = @as(u32, 34);
    const values = fixtures.packed_record_values;
    const hit = bsearch.bsearch(&key, @ptrCast(values[0..].ptr), values.len, @sizeOf(fixtures.RawRecord), comparePackedRecordOpaque) orelse return error.ExpectedMatch;
    const typed_hit: *const fixtures.RawRecord = @ptrCast(@alignCast(hit));
    try std.testing.expectEqual(@as(u32, 34), typed_hit.key);
    try std.testing.expectEqual(@as(u32, 0x22000), typed_hit.value);

    const miss = @as(u32, 22);
    try std.testing.expectEqual(@as(usize, 4), bsearch.bsearchLowerBoundIndex(&miss, @ptrCast(values[0..].ptr), values.len, @sizeOf(fixtures.RawRecord), comparePackedRecordOpaque));
    try std.testing.expectEqual(@as(usize, 4), bsearch.bsearchUpperBoundIndex(&miss, @ptrCast(values[0..].ptr), values.len, @sizeOf(fixtures.RawRecord), comparePackedRecordOpaque));
}
