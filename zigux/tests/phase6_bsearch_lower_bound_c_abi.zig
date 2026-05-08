const std = @import("std");
const bsearch = @import("bsearch");

const RawRecord = extern struct {
    key: u32,
    tag: u16,
    flags: u16,
    value: u32,
};

fn compareU32(key: *const u32, item: *const u32) i32 {
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareU32C(key: *const u32, item: *const u32) callconv(.c) i32 {
    return compareU32(key, item);
}

fn compareDescendingU32(key: *const u32, item: *const u32) i32 {
    return switch (std.math.order(item.*, key.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareDescendingU32C(key: *const u32, item: *const u32) callconv(.c) i32 {
    return compareDescendingU32(key, item);
}

fn compareOpaqueU32(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareU32(typed_key, typed_item);
}

fn compareOpaqueU32C(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    return compareOpaqueU32(key, item);
}

fn compareDescendingOpaqueU32(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareDescendingU32(typed_key, typed_item);
}

fn compareDescendingOpaqueU32C(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    return compareDescendingOpaqueU32(key, item);
}

fn compareRawRecordKey(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const RawRecord = @ptrCast(@alignCast(item));
    return compareU32(typed_key, &typed_item.key);
}

fn compareRawRecordKeyC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    return compareRawRecordKey(key, item);
}

var typed_c_compare_calls: usize = 0;
var raw_c_compare_calls: usize = 0;

fn compareU32CountedC(key: *const u32, item: *const u32) callconv(.c) i32 {
    typed_c_compare_calls += 1;
    return compareU32(key, item);
}

fn compareDescendingU32CountedC(key: *const u32, item: *const u32) callconv(.c) i32 {
    typed_c_compare_calls += 1;
    return compareDescendingU32(key, item);
}

fn compareOpaqueU32CountedC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    raw_c_compare_calls += 1;
    return compareOpaqueU32(key, item);
}

fn compareDescendingOpaqueU32CountedC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    raw_c_compare_calls += 1;
    return compareDescendingOpaqueU32(key, item);
}

fn compareRawRecordKeyCountedC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    raw_c_compare_calls += 1;
    return compareRawRecordKey(key, item);
}

test "phase 6 bsearch lower-bound helpers accept runtime-selected c abi comparator pointers" {
    const ascending = [_]u32{ 1, 4, 4, 4, 9, 16 };
    const descending = [_]u32{ 16, 9, 4, 4, 4, 1 };
    const ascending_comparators = [_]bsearch.CComparator(u32, u32){ compareU32C, compareU32C };
    const descending_comparators = [_]bsearch.CComparator(u32, u32){ compareDescendingU32C, compareDescendingU32C };

    for (ascending_comparators) |compare| {
        try std.testing.expectEqual(@as(usize, 0), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 0), ascending[0..], compare));
        try std.testing.expectEqual(@as(usize, 1), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 4), ascending[0..], compare));
        try std.testing.expectEqual(@as(usize, 4), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 5), ascending[0..], compare));
        try std.testing.expectEqual(@as(usize, ascending.len), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 20), ascending[0..], compare));
    }

    for (descending_comparators) |compare| {
        try std.testing.expectEqual(@as(usize, 0), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 20), descending[0..], compare));
        try std.testing.expectEqual(@as(usize, 2), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 4), descending[0..], compare));
        try std.testing.expectEqual(@as(usize, 5), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 3), descending[0..], compare));
        try std.testing.expectEqual(@as(usize, descending.len), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 0), descending[0..], compare));
    }
}

test "phase 6 bsearch raw lower-bound helpers accept runtime-selected c abi comparator pointers" {
    const ascending = [_]u32{ 1, 4, 4, 4, 9, 16 };
    const descending = [_]u32{ 16, 9, 4, 4, 4, 1 };
    const records = [_]RawRecord{
        .{ .key = 1, .tag = 10, .flags = 0, .value = 10 },
        .{ .key = 4, .tag = 11, .flags = 1, .value = 40 },
        .{ .key = 4, .tag = 12, .flags = 0, .value = 41 },
        .{ .key = 11, .tag = 13, .flags = 2, .value = 110 },
        .{ .key = 16, .tag = 14, .flags = 0, .value = 160 },
    };
    const ascending_comparators = [_]bsearch.CRawComparator{ compareOpaqueU32C, compareOpaqueU32C };
    const descending_comparators = [_]bsearch.CRawComparator{ compareDescendingOpaqueU32C, compareDescendingOpaqueU32C };
    const record_comparators = [_]bsearch.CRawComparator{ compareRawRecordKeyC, compareRawRecordKeyC };

    for (ascending_comparators) |compare| {
        try std.testing.expectEqual(
            @as(usize, 0),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 0), @ptrCast(ascending[0..].ptr), ascending.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(
            @as(usize, 1),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 4), @ptrCast(ascending[0..].ptr), ascending.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(
            @as(usize, 4),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 5), @ptrCast(ascending[0..].ptr), ascending.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(
            @as(usize, ascending.len),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 20), @ptrCast(ascending[0..].ptr), ascending.len, @sizeOf(u32), compare),
        );
    }

    for (descending_comparators) |compare| {
        try std.testing.expectEqual(
            @as(usize, 0),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 20), @ptrCast(descending[0..].ptr), descending.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(
            @as(usize, 2),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 4), @ptrCast(descending[0..].ptr), descending.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(
            @as(usize, 5),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 3), @ptrCast(descending[0..].ptr), descending.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(
            @as(usize, descending.len),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 0), @ptrCast(descending[0..].ptr), descending.len, @sizeOf(u32), compare),
        );
    }

    for (record_comparators) |compare| {
        try std.testing.expectEqual(
            @as(usize, 1),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 4), @ptrCast(records[0..].ptr), records.len, @sizeOf(RawRecord), compare),
        );
        try std.testing.expectEqual(
            @as(usize, 3),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 10), @ptrCast(records[0..].ptr), records.len, @sizeOf(RawRecord), compare),
        );
        try std.testing.expectEqual(
            @as(usize, records.len),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 42), @ptrCast(records[0..].ptr), records.len, @sizeOf(RawRecord), compare),
        );
    }
}

test "phase 6 bsearch lower-bound c abi helpers short-circuit empty input and keep singleton insertion edges bounded" {
    const empty = [_]u32{};
    const singleton = [_]u32{4};
    const descending_singleton = [_]u32{4};
    const record_singleton = [_]RawRecord{.{ .key = 4, .tag = 11, .flags = 1, .value = 40 }};

    typed_c_compare_calls = 0;
    try std.testing.expectEqual(@as(usize, 0), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 4), empty[0..], compareU32CountedC));
    try std.testing.expectEqual(@as(usize, 0), typed_c_compare_calls);

    typed_c_compare_calls = 0;
    try std.testing.expectEqual(@as(usize, 0), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 4), empty[0..], compareDescendingU32CountedC));
    try std.testing.expectEqual(@as(usize, 0), typed_c_compare_calls);

    typed_c_compare_calls = 0;
    try std.testing.expectEqual(@as(usize, 0), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 3), singleton[0..], compareU32CountedC));
    try std.testing.expect(typed_c_compare_calls <= 1);

    typed_c_compare_calls = 0;
    try std.testing.expectEqual(@as(usize, 1), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 5), singleton[0..], compareU32CountedC));
    try std.testing.expect(typed_c_compare_calls <= 1);

    typed_c_compare_calls = 0;
    try std.testing.expectEqual(@as(usize, 1), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 3), descending_singleton[0..], compareDescendingU32CountedC));
    try std.testing.expect(typed_c_compare_calls <= 1);

    typed_c_compare_calls = 0;
    try std.testing.expectEqual(@as(usize, 0), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 5), descending_singleton[0..], compareDescendingU32CountedC));
    try std.testing.expect(typed_c_compare_calls <= 1);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 0),
        bsearch.bsearchLowerBoundIndex(&@as(u32, 4), @ptrCast(empty[0..].ptr), empty.len, @sizeOf(u32), compareOpaqueU32CountedC),
    );
    try std.testing.expectEqual(@as(usize, 0), raw_c_compare_calls);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 0),
        bsearch.bsearchLowerBoundIndex(&@as(u32, 4), @ptrCast(empty[0..].ptr), empty.len, @sizeOf(u32), compareDescendingOpaqueU32CountedC),
    );
    try std.testing.expectEqual(@as(usize, 0), raw_c_compare_calls);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 0),
        bsearch.bsearchLowerBoundIndex(&@as(u32, 3), @ptrCast(singleton[0..].ptr), singleton.len, @sizeOf(u32), compareOpaqueU32CountedC),
    );
    try std.testing.expect(raw_c_compare_calls <= 1);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 1),
        bsearch.bsearchLowerBoundIndex(&@as(u32, 5), @ptrCast(singleton[0..].ptr), singleton.len, @sizeOf(u32), compareOpaqueU32CountedC),
    );
    try std.testing.expect(raw_c_compare_calls <= 1);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 1),
        bsearch.bsearchLowerBoundIndex(&@as(u32, 3), @ptrCast(descending_singleton[0..].ptr), descending_singleton.len, @sizeOf(u32), compareDescendingOpaqueU32CountedC),
    );
    try std.testing.expect(raw_c_compare_calls <= 1);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 0),
        bsearch.bsearchLowerBoundIndex(&@as(u32, 5), @ptrCast(descending_singleton[0..].ptr), descending_singleton.len, @sizeOf(u32), compareDescendingOpaqueU32CountedC),
    );
    try std.testing.expect(raw_c_compare_calls <= 1);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 0),
        bsearch.bsearchLowerBoundIndex(&@as(u32, 4), @ptrCast(record_singleton[0..].ptr), record_singleton.len, @sizeOf(RawRecord), compareRawRecordKeyCountedC),
    );
    try std.testing.expect(raw_c_compare_calls <= 1);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 1),
        bsearch.bsearchLowerBoundIndex(&@as(u32, 5), @ptrCast(record_singleton[0..].ptr), record_singleton.len, @sizeOf(RawRecord), compareRawRecordKeyCountedC),
    );
    try std.testing.expect(raw_c_compare_calls <= 1);
}
