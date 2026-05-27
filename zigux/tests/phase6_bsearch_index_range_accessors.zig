const std = @import("std");
const bsearch = @import("bsearch");

fn compareDirectInt(key: *const u32, item: *const u32) i32 {
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareDirectOpaqueInt(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareDirectInt(typed_key, typed_item);
}

test "phase 6 bsearch index range accessors keep typed views and empty insertion sites aligned" {
    const duplicates = [_]u32{ 3, 6, 9, 12, 21, 21, 21, 24, 27, 30, 33, 36, 39, 42, 45 };
    const duplicate_target = @as(u32, 21);
    const range = bsearch.equalRangeIndex(u32, u32, &duplicate_target, duplicates[0..], compareDirectInt);

    try std.testing.expectEqual(bsearch.IndexRange{ .lower = 4, .upper = 7 }, range);
    try std.testing.expectEqual(@as(usize, 3), range.len());
    try std.testing.expect(!range.isEmpty());
    try std.testing.expectEqual(@intFromPtr(&duplicates[4]), @intFromPtr(range.firstConst(u32, duplicates[0..]).?));
    try std.testing.expectEqual(@intFromPtr(&duplicates[6]), @intFromPtr(range.lastConst(u32, duplicates[0..]).?));
    try std.testing.expectEqualSlices(u32, &[_]u32{ 21, 21, 21 }, range.sliceConst(u32, duplicates[0..]));

    const typed_bytes = range.bytes(@ptrCast(duplicates[0..].ptr), @sizeOf(u32));
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(u32)), typed_bytes.len);
    const typed_words: [*]const u32 = @ptrCast(@alignCast(typed_bytes.ptr));
    try std.testing.expectEqual(@as(u32, 21), typed_words[0]);
    try std.testing.expectEqual(@as(u32, 21), typed_words[2]);

    const missing_target = @as(u32, 22);
    const missing_range = bsearch.equalRangeIndex(u32, u32, &missing_target, duplicates[0..], compareDirectInt);
    try std.testing.expect(missing_range.isEmpty());
    try std.testing.expectEqual(@as(?*const u32, null), missing_range.firstConst(u32, duplicates[0..]));
    try std.testing.expectEqual(@as(?*const u32, null), missing_range.lastConst(u32, duplicates[0..]));
    try std.testing.expectEqual(@as(usize, 0), missing_range.sliceConst(u32, duplicates[0..]).len);
    try std.testing.expectEqual(@intFromPtr(&duplicates[7]), @intFromPtr(missing_range.sliceConst(u32, duplicates[0..]).ptr));

    const missing_bytes = missing_range.bytes(@ptrCast(duplicates[0..].ptr), @sizeOf(u32));
    try std.testing.expectEqual(@as(usize, 0), missing_bytes.len);
    try std.testing.expectEqual(
        @intFromPtr(@as([*]const u8, @ptrCast(duplicates[0..].ptr)) + (7 * @sizeOf(u32))),
        @intFromPtr(missing_bytes.ptr),
    );
}

test "phase 6 bsearch index range mutable accessors keep boundary writes and raw bytes aligned" {
    var duplicates = [_]u32{ 3, 6, 9, 12, 21, 21, 21, 24, 27, 30, 33, 36, 39, 42, 45 };
    const duplicate_target = @as(u32, 21);
    const range = bsearch.equalRangeIndex(u32, u32, &duplicate_target, duplicates[0..], compareDirectInt);

    const first = range.firstMutable(u32, duplicates[0..]) orelse return error.ExpectedMatch;
    const last = range.lastMutable(u32, duplicates[0..]) orelse return error.ExpectedMatch;
    first.* = 20;
    last.* = 23;
    try std.testing.expectEqual(@as(u32, 20), duplicates[4]);
    try std.testing.expectEqual(@as(u32, 23), duplicates[6]);

    var raw_duplicates = [_]u32{ 3, 6, 9, 12, 21, 21, 21, 24, 27, 30, 33, 36, 39, 42, 45 };
    const raw_range = bsearch.bsearchEqualRangeIndex(
        &duplicate_target,
        @ptrCast(raw_duplicates[0..].ptr),
        raw_duplicates.len,
        @sizeOf(u32),
        compareDirectOpaqueInt,
    );
    const raw_bytes = raw_range.bytesMutable(@ptrCast(raw_duplicates[0..].ptr), @sizeOf(u32));
    try std.testing.expectEqual(@as(usize, 3 * @sizeOf(u32)), raw_bytes.len);
    const typed_raw_words: [*]u32 = @ptrCast(@alignCast(raw_bytes.ptr));
    typed_raw_words[0] = 20;
    typed_raw_words[2] = 23;
    try std.testing.expectEqual(@as(u32, 20), raw_duplicates[4]);
    try std.testing.expectEqual(@as(u32, 23), raw_duplicates[6]);
}
