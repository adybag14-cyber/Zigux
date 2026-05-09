const std = @import("std");
const bsearch = @import("./bsearch.zig");

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

fn compareU32AliasC(key: *const u32, item: *const u32) callconv(.c) i32 {
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

fn compareDescendingU32AliasC(key: *const u32, item: *const u32) callconv(.c) i32 {
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

fn compareOpaqueU32AliasC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
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

fn compareDescendingOpaqueU32AliasC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
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

fn compareRawRecordKeyAliasC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
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

fn compareU32CountedAliasC(key: *const u32, item: *const u32) callconv(.c) i32 {
    typed_c_compare_calls += 1;
    return compareU32(key, item);
}

fn compareDescendingU32CountedAliasC(key: *const u32, item: *const u32) callconv(.c) i32 {
    typed_c_compare_calls += 1;
    return compareDescendingU32(key, item);
}

fn compareOpaqueU32CountedAliasC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    raw_c_compare_calls += 1;
    return compareOpaqueU32(key, item);
}

fn compareDescendingOpaqueU32CountedAliasC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    raw_c_compare_calls += 1;
    return compareDescendingOpaqueU32(key, item);
}

fn compareRawRecordKeyCountedAliasC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    raw_c_compare_calls += 1;
    return compareRawRecordKey(key, item);
}

fn binarySearchBudget(len: usize) usize {
    if (len == 0) return 0;

    var budget: usize = 0;
    var span: usize = 1;
    while (span < len + 1) : (span <<= 1) {
        budget += 1;
    }
    return budget;
}

fn linearLowerBoundIndexU32(key: *const u32, items: []const u32, compare: anytype) usize {
    for (items, 0..) |_, index| {
        if (compare(key, &items[index]) <= 0) return index;
    }
    return items.len;
}

fn linearRawLowerBoundIndexU32(
    key: *const anyopaque,
    base: [*]const u8,
    num_members: usize,
    member_size: usize,
    compare: anytype,
) usize {
    for (0..num_members) |index| {
        const item: *const anyopaque = @ptrCast(base + (index * member_size));
        if (compare(key, item) <= 0) return index;
    }
    return num_members;
}

fn linearUpperBoundIndexU32(key: *const u32, items: []const u32, compare: anytype) usize {
    for (items, 0..) |_, index| {
        if (compare(key, &items[index]) < 0) return index;
    }
    return items.len;
}

fn linearRawUpperBoundIndexU32(
    key: *const anyopaque,
    base: [*]const u8,
    num_members: usize,
    member_size: usize,
    compare: anytype,
) usize {
    for (0..num_members) |index| {
        const item: *const anyopaque = @ptrCast(base + (index * member_size));
        if (compare(key, item) < 0) return index;
    }
    return num_members;
}

test "phase 6 bsearch lower-bound helpers accept runtime-selected c abi comparator pointers" {
    const ascending = [_]u32{ 1, 4, 4, 4, 9, 16 };
    const descending = [_]u32{ 16, 9, 4, 4, 4, 1 };
    const ascending_comparators = [_]bsearch.CComparator(u32, u32){ compareU32C, compareU32AliasC };
    const descending_comparators = [_]bsearch.CComparator(u32, u32){ compareDescendingU32C, compareDescendingU32AliasC };

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
    const ascending_comparators = [_]bsearch.CRawComparator{ compareOpaqueU32C, compareOpaqueU32AliasC };
    const descending_comparators = [_]bsearch.CRawComparator{ compareDescendingOpaqueU32C, compareDescendingOpaqueU32AliasC };
    const record_comparators = [_]bsearch.CRawComparator{ compareRawRecordKeyC, compareRawRecordKeyAliasC };

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

test "phase 6 bsearch lower-bound c abi alias comparator pointers keep empty and singleton bounds" {
    const empty = [_]u32{};
    const singleton = [_]u32{4};
    const descending_singleton = [_]u32{4};
    const record_singleton = [_]RawRecord{.{ .key = 4, .tag = 11, .flags = 1, .value = 40 }};

    const ascending_alias = [_]bsearch.CComparator(u32, u32){compareU32CountedAliasC};
    const descending_alias = [_]bsearch.CComparator(u32, u32){compareDescendingU32CountedAliasC};
    const raw_ascending_alias = [_]bsearch.CRawComparator{compareOpaqueU32CountedAliasC};
    const raw_descending_alias = [_]bsearch.CRawComparator{compareDescendingOpaqueU32CountedAliasC};
    const raw_record_alias = [_]bsearch.CRawComparator{compareRawRecordKeyCountedAliasC};

    for (ascending_alias) |compare| {
        typed_c_compare_calls = 0;
        try std.testing.expectEqual(@as(usize, 0), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 4), empty[0..], compare));
        try std.testing.expectEqual(@as(usize, 0), typed_c_compare_calls);

        typed_c_compare_calls = 0;
        try std.testing.expectEqual(@as(usize, 0), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 3), singleton[0..], compare));
        try std.testing.expect(typed_c_compare_calls <= 1);

        typed_c_compare_calls = 0;
        try std.testing.expectEqual(@as(usize, 1), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 5), singleton[0..], compare));
        try std.testing.expect(typed_c_compare_calls <= 1);
    }

    for (descending_alias) |compare| {
        typed_c_compare_calls = 0;
        try std.testing.expectEqual(@as(usize, 0), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 4), empty[0..], compare));
        try std.testing.expectEqual(@as(usize, 0), typed_c_compare_calls);

        typed_c_compare_calls = 0;
        try std.testing.expectEqual(@as(usize, 1), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 3), descending_singleton[0..], compare));
        try std.testing.expect(typed_c_compare_calls <= 1);

        typed_c_compare_calls = 0;
        try std.testing.expectEqual(@as(usize, 0), bsearch.lowerBoundIndex(u32, u32, &@as(u32, 5), descending_singleton[0..], compare));
        try std.testing.expect(typed_c_compare_calls <= 1);
    }

    for (raw_ascending_alias) |compare| {
        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 0),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 4), @ptrCast(empty[0..].ptr), empty.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(@as(usize, 0), raw_c_compare_calls);

        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 0),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 3), @ptrCast(singleton[0..].ptr), singleton.len, @sizeOf(u32), compare),
        );
        try std.testing.expect(raw_c_compare_calls <= 1);

        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 1),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 5), @ptrCast(singleton[0..].ptr), singleton.len, @sizeOf(u32), compare),
        );
        try std.testing.expect(raw_c_compare_calls <= 1);
    }

    for (raw_descending_alias) |compare| {
        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 0),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 4), @ptrCast(empty[0..].ptr), empty.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(@as(usize, 0), raw_c_compare_calls);

        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 1),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 3), @ptrCast(descending_singleton[0..].ptr), descending_singleton.len, @sizeOf(u32), compare),
        );
        try std.testing.expect(raw_c_compare_calls <= 1);

        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 0),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 5), @ptrCast(descending_singleton[0..].ptr), descending_singleton.len, @sizeOf(u32), compare),
        );
        try std.testing.expect(raw_c_compare_calls <= 1);
    }

    for (raw_record_alias) |compare| {
        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 0),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 4), @ptrCast(record_singleton[0..].ptr), record_singleton.len, @sizeOf(RawRecord), compare),
        );
        try std.testing.expect(raw_c_compare_calls <= 1);

        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 1),
            bsearch.bsearchLowerBoundIndex(&@as(u32, 5), @ptrCast(record_singleton[0..].ptr), record_singleton.len, @sizeOf(RawRecord), compare),
        );
        try std.testing.expect(raw_c_compare_calls <= 1);
    }
}

test "phase 6 bsearch lower-bound c abi helpers match bounded insertion points across ascending and descending ranges" {
    var ascending_storage: [32]u32 = undefined;
    var descending_storage: [32]u32 = undefined;

    for (0..ascending_storage.len + 1) |len| {
        for (0..len) |index| {
            const value = @as(u32, @intCast((index + 1) * 2));
            ascending_storage[index] = value;
            descending_storage[len - 1 - index] = value;
        }

        const ascending = ascending_storage[0..len];
        const descending = descending_storage[0..len];
        const budget = binarySearchBudget(len);
        const max_probe: u32 = if (len == 0) 1 else @as(u32, @intCast((len * 2) + 2));
        const ascending_raw: [*]const u8 = @ptrCast(ascending.ptr);
        const descending_raw: [*]const u8 = @ptrCast(descending.ptr);

        var probe: u32 = 0;
        while (probe <= max_probe) : (probe += 1) {
            typed_c_compare_calls = 0;
            const expected_ascending = linearLowerBoundIndexU32(&probe, ascending, compareU32);
            try std.testing.expectEqual(
                expected_ascending,
                bsearch.lowerBoundIndex(u32, u32, &probe, ascending, compareU32CountedC),
            );
            try std.testing.expect(typed_c_compare_calls <= budget);

            typed_c_compare_calls = 0;
            const expected_descending = linearLowerBoundIndexU32(&probe, descending, compareDescendingU32);
            try std.testing.expectEqual(
                expected_descending,
                bsearch.lowerBoundIndex(u32, u32, &probe, descending, compareDescendingU32CountedC),
            );
            try std.testing.expect(typed_c_compare_calls <= budget);

            raw_c_compare_calls = 0;
            const expected_raw_ascending = linearRawLowerBoundIndexU32(
                &probe,
                ascending_raw,
                ascending.len,
                @sizeOf(u32),
                compareOpaqueU32,
            );
            try std.testing.expectEqual(
                expected_raw_ascending,
                bsearch.bsearchLowerBoundIndex(&probe, ascending_raw, ascending.len, @sizeOf(u32), compareOpaqueU32CountedC),
            );
            try std.testing.expect(raw_c_compare_calls <= budget);

            raw_c_compare_calls = 0;
            const expected_raw_descending = linearRawLowerBoundIndexU32(
                &probe,
                descending_raw,
                descending.len,
                @sizeOf(u32),
                compareDescendingOpaqueU32,
            );
            try std.testing.expectEqual(
                expected_raw_descending,
                bsearch.bsearchLowerBoundIndex(&probe, descending_raw, descending.len, @sizeOf(u32), compareDescendingOpaqueU32CountedC),
            );
            try std.testing.expect(raw_c_compare_calls <= budget);
        }
    }
}

test "phase 6 bsearch lower-bound c abi record member_size replay stays inside a binary-search budget" {
    var record_storage: [32]RawRecord = undefined;

    for (0..record_storage.len + 1) |len| {
        for (0..len) |index| {
            const key = @as(u32, @intCast((index + 1) * 2));
            record_storage[index] = .{
                .key = key,
                .tag = @as(u16, @intCast(100 + index)),
                .flags = @as(u16, @intCast(index & 3)),
                .value = key * 10,
            };
        }

        const records = record_storage[0..len];
        const budget = binarySearchBudget(len);
        const raw_records: [*]const u8 = @ptrCast(records.ptr);
        const max_probe: u32 = if (len == 0) 1 else @as(u32, @intCast((len * 2) + 2));

        var probe: u32 = 0;
        while (probe <= max_probe) : (probe += 1) {
            raw_c_compare_calls = 0;
            const expected = linearRawLowerBoundIndexU32(
                &probe,
                raw_records,
                records.len,
                @sizeOf(RawRecord),
                compareRawRecordKey,
            );
            try std.testing.expectEqual(
                expected,
                bsearch.bsearchLowerBoundIndex(&probe, raw_records, records.len, @sizeOf(RawRecord), compareRawRecordKeyCountedC),
            );
            try std.testing.expect(raw_c_compare_calls <= budget);
        }
    }
}

test "phase 6 bsearch upper-bound helpers accept runtime-selected c abi comparator pointers" {
    const ascending = [_]u32{ 1, 4, 4, 4, 9, 16 };
    const descending = [_]u32{ 16, 9, 4, 4, 4, 1 };
    const ascending_comparators = [_]bsearch.CComparator(u32, u32){ compareU32C, compareU32AliasC };
    const descending_comparators = [_]bsearch.CComparator(u32, u32){ compareDescendingU32C, compareDescendingU32AliasC };

    for (ascending_comparators) |compare| {
        try std.testing.expectEqual(@as(usize, 0), bsearch.upperBoundIndex(u32, u32, &@as(u32, 0), ascending[0..], compare));
        try std.testing.expectEqual(@as(usize, 4), bsearch.upperBoundIndex(u32, u32, &@as(u32, 4), ascending[0..], compare));
        try std.testing.expectEqual(@as(usize, 4), bsearch.upperBoundIndex(u32, u32, &@as(u32, 5), ascending[0..], compare));
        try std.testing.expectEqual(@as(usize, ascending.len), bsearch.upperBoundIndex(u32, u32, &@as(u32, 20), ascending[0..], compare));
    }

    for (descending_comparators) |compare| {
        try std.testing.expectEqual(@as(usize, 0), bsearch.upperBoundIndex(u32, u32, &@as(u32, 20), descending[0..], compare));
        try std.testing.expectEqual(@as(usize, 5), bsearch.upperBoundIndex(u32, u32, &@as(u32, 4), descending[0..], compare));
        try std.testing.expectEqual(@as(usize, 5), bsearch.upperBoundIndex(u32, u32, &@as(u32, 3), descending[0..], compare));
        try std.testing.expectEqual(@as(usize, descending.len), bsearch.upperBoundIndex(u32, u32, &@as(u32, 0), descending[0..], compare));
    }
}

test "phase 6 bsearch raw upper-bound helpers accept runtime-selected c abi comparator pointers" {
    const ascending = [_]u32{ 1, 4, 4, 4, 9, 16 };
    const descending = [_]u32{ 16, 9, 4, 4, 4, 1 };
    const records = [_]RawRecord{
        .{ .key = 1, .tag = 10, .flags = 0, .value = 10 },
        .{ .key = 4, .tag = 11, .flags = 1, .value = 40 },
        .{ .key = 4, .tag = 12, .flags = 0, .value = 41 },
        .{ .key = 11, .tag = 13, .flags = 2, .value = 110 },
        .{ .key = 16, .tag = 14, .flags = 0, .value = 160 },
    };
    const ascending_comparators = [_]bsearch.CRawComparator{ compareOpaqueU32C, compareOpaqueU32AliasC };
    const descending_comparators = [_]bsearch.CRawComparator{ compareDescendingOpaqueU32C, compareDescendingOpaqueU32AliasC };
    const record_comparators = [_]bsearch.CRawComparator{ compareRawRecordKeyC, compareRawRecordKeyAliasC };

    for (ascending_comparators) |compare| {
        try std.testing.expectEqual(
            @as(usize, 0),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 0), @ptrCast(ascending[0..].ptr), ascending.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(
            @as(usize, 4),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 4), @ptrCast(ascending[0..].ptr), ascending.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(
            @as(usize, 4),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 5), @ptrCast(ascending[0..].ptr), ascending.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(
            @as(usize, ascending.len),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 20), @ptrCast(ascending[0..].ptr), ascending.len, @sizeOf(u32), compare),
        );
    }

    for (descending_comparators) |compare| {
        try std.testing.expectEqual(
            @as(usize, 0),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 20), @ptrCast(descending[0..].ptr), descending.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(
            @as(usize, 5),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 4), @ptrCast(descending[0..].ptr), descending.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(
            @as(usize, 5),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 3), @ptrCast(descending[0..].ptr), descending.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(
            @as(usize, descending.len),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 0), @ptrCast(descending[0..].ptr), descending.len, @sizeOf(u32), compare),
        );
    }

    for (record_comparators) |compare| {
        try std.testing.expectEqual(
            @as(usize, 3),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 4), @ptrCast(records[0..].ptr), records.len, @sizeOf(RawRecord), compare),
        );
        try std.testing.expectEqual(
            @as(usize, 3),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 10), @ptrCast(records[0..].ptr), records.len, @sizeOf(RawRecord), compare),
        );
        try std.testing.expectEqual(
            @as(usize, records.len),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 42), @ptrCast(records[0..].ptr), records.len, @sizeOf(RawRecord), compare),
        );
    }
}

test "phase 6 bsearch upper-bound c abi helpers short-circuit empty input and keep singleton insertion edges bounded" {
    const empty = [_]u32{};
    const singleton = [_]u32{4};
    const descending_singleton = [_]u32{4};
    const record_singleton = [_]RawRecord{.{ .key = 4, .tag = 11, .flags = 1, .value = 40 }};

    typed_c_compare_calls = 0;
    try std.testing.expectEqual(@as(usize, 0), bsearch.upperBoundIndex(u32, u32, &@as(u32, 4), empty[0..], compareU32CountedC));
    try std.testing.expectEqual(@as(usize, 0), typed_c_compare_calls);

    typed_c_compare_calls = 0;
    try std.testing.expectEqual(@as(usize, 0), bsearch.upperBoundIndex(u32, u32, &@as(u32, 4), empty[0..], compareDescendingU32CountedC));
    try std.testing.expectEqual(@as(usize, 0), typed_c_compare_calls);

    typed_c_compare_calls = 0;
    try std.testing.expectEqual(@as(usize, 0), bsearch.upperBoundIndex(u32, u32, &@as(u32, 3), singleton[0..], compareU32CountedC));
    try std.testing.expect(typed_c_compare_calls <= 1);

    typed_c_compare_calls = 0;
    try std.testing.expectEqual(@as(usize, 1), bsearch.upperBoundIndex(u32, u32, &@as(u32, 4), singleton[0..], compareU32CountedC));
    try std.testing.expect(typed_c_compare_calls <= 1);

    typed_c_compare_calls = 0;
    try std.testing.expectEqual(@as(usize, 1), bsearch.upperBoundIndex(u32, u32, &@as(u32, 3), descending_singleton[0..], compareDescendingU32CountedC));
    try std.testing.expect(typed_c_compare_calls <= 1);

    typed_c_compare_calls = 0;
    try std.testing.expectEqual(@as(usize, 1), bsearch.upperBoundIndex(u32, u32, &@as(u32, 4), descending_singleton[0..], compareDescendingU32CountedC));
    try std.testing.expect(typed_c_compare_calls <= 1);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 0),
        bsearch.bsearchUpperBoundIndex(&@as(u32, 4), @ptrCast(empty[0..].ptr), empty.len, @sizeOf(u32), compareOpaqueU32CountedC),
    );
    try std.testing.expectEqual(@as(usize, 0), raw_c_compare_calls);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 0),
        bsearch.bsearchUpperBoundIndex(&@as(u32, 4), @ptrCast(empty[0..].ptr), empty.len, @sizeOf(u32), compareDescendingOpaqueU32CountedC),
    );
    try std.testing.expectEqual(@as(usize, 0), raw_c_compare_calls);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 0),
        bsearch.bsearchUpperBoundIndex(&@as(u32, 3), @ptrCast(singleton[0..].ptr), singleton.len, @sizeOf(u32), compareOpaqueU32CountedC),
    );
    try std.testing.expect(raw_c_compare_calls <= 1);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 1),
        bsearch.bsearchUpperBoundIndex(&@as(u32, 4), @ptrCast(singleton[0..].ptr), singleton.len, @sizeOf(u32), compareOpaqueU32CountedC),
    );
    try std.testing.expect(raw_c_compare_calls <= 1);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 1),
        bsearch.bsearchUpperBoundIndex(&@as(u32, 3), @ptrCast(descending_singleton[0..].ptr), descending_singleton.len, @sizeOf(u32), compareDescendingOpaqueU32CountedC),
    );
    try std.testing.expect(raw_c_compare_calls <= 1);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 1),
        bsearch.bsearchUpperBoundIndex(&@as(u32, 4), @ptrCast(descending_singleton[0..].ptr), descending_singleton.len, @sizeOf(u32), compareDescendingOpaqueU32CountedC),
    );
    try std.testing.expect(raw_c_compare_calls <= 1);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 1),
        bsearch.bsearchUpperBoundIndex(&@as(u32, 4), @ptrCast(record_singleton[0..].ptr), record_singleton.len, @sizeOf(RawRecord), compareRawRecordKeyCountedC),
    );
    try std.testing.expect(raw_c_compare_calls <= 1);

    raw_c_compare_calls = 0;
    try std.testing.expectEqual(
        @as(usize, 1),
        bsearch.bsearchUpperBoundIndex(&@as(u32, 5), @ptrCast(record_singleton[0..].ptr), record_singleton.len, @sizeOf(RawRecord), compareRawRecordKeyCountedC),
    );
    try std.testing.expect(raw_c_compare_calls <= 1);
}

test "phase 6 bsearch upper-bound c abi alias comparator pointers keep empty and singleton bounds" {
    const empty = [_]u32{};
    const singleton = [_]u32{4};
    const descending_singleton = [_]u32{4};
    const record_singleton = [_]RawRecord{.{ .key = 4, .tag = 11, .flags = 1, .value = 40 }};

    const ascending_alias = [_]bsearch.CComparator(u32, u32){compareU32CountedAliasC};
    const descending_alias = [_]bsearch.CComparator(u32, u32){compareDescendingU32CountedAliasC};
    const raw_ascending_alias = [_]bsearch.CRawComparator{compareOpaqueU32CountedAliasC};
    const raw_descending_alias = [_]bsearch.CRawComparator{compareDescendingOpaqueU32CountedAliasC};
    const raw_record_alias = [_]bsearch.CRawComparator{compareRawRecordKeyCountedAliasC};

    for (ascending_alias) |compare| {
        typed_c_compare_calls = 0;
        try std.testing.expectEqual(@as(usize, 0), bsearch.upperBoundIndex(u32, u32, &@as(u32, 4), empty[0..], compare));
        try std.testing.expectEqual(@as(usize, 0), typed_c_compare_calls);

        typed_c_compare_calls = 0;
        try std.testing.expectEqual(@as(usize, 0), bsearch.upperBoundIndex(u32, u32, &@as(u32, 3), singleton[0..], compare));
        try std.testing.expect(typed_c_compare_calls <= 1);

        typed_c_compare_calls = 0;
        try std.testing.expectEqual(@as(usize, 1), bsearch.upperBoundIndex(u32, u32, &@as(u32, 4), singleton[0..], compare));
        try std.testing.expect(typed_c_compare_calls <= 1);
    }

    for (descending_alias) |compare| {
        typed_c_compare_calls = 0;
        try std.testing.expectEqual(@as(usize, 0), bsearch.upperBoundIndex(u32, u32, &@as(u32, 4), empty[0..], compare));
        try std.testing.expectEqual(@as(usize, 0), typed_c_compare_calls);

        typed_c_compare_calls = 0;
        try std.testing.expectEqual(@as(usize, 1), bsearch.upperBoundIndex(u32, u32, &@as(u32, 3), descending_singleton[0..], compare));
        try std.testing.expect(typed_c_compare_calls <= 1);

        typed_c_compare_calls = 0;
        try std.testing.expectEqual(@as(usize, 1), bsearch.upperBoundIndex(u32, u32, &@as(u32, 4), descending_singleton[0..], compare));
        try std.testing.expect(typed_c_compare_calls <= 1);
    }

    for (raw_ascending_alias) |compare| {
        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 0),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 4), @ptrCast(empty[0..].ptr), empty.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(@as(usize, 0), raw_c_compare_calls);

        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 0),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 3), @ptrCast(singleton[0..].ptr), singleton.len, @sizeOf(u32), compare),
        );
        try std.testing.expect(raw_c_compare_calls <= 1);

        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 1),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 4), @ptrCast(singleton[0..].ptr), singleton.len, @sizeOf(u32), compare),
        );
        try std.testing.expect(raw_c_compare_calls <= 1);
    }

    for (raw_descending_alias) |compare| {
        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 0),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 4), @ptrCast(empty[0..].ptr), empty.len, @sizeOf(u32), compare),
        );
        try std.testing.expectEqual(@as(usize, 0), raw_c_compare_calls);

        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 1),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 3), @ptrCast(descending_singleton[0..].ptr), descending_singleton.len, @sizeOf(u32), compare),
        );
        try std.testing.expect(raw_c_compare_calls <= 1);

        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 1),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 4), @ptrCast(descending_singleton[0..].ptr), descending_singleton.len, @sizeOf(u32), compare),
        );
        try std.testing.expect(raw_c_compare_calls <= 1);
    }

    for (raw_record_alias) |compare| {
        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 1),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 4), @ptrCast(record_singleton[0..].ptr), record_singleton.len, @sizeOf(RawRecord), compare),
        );
        try std.testing.expect(raw_c_compare_calls <= 1);

        raw_c_compare_calls = 0;
        try std.testing.expectEqual(
            @as(usize, 1),
            bsearch.bsearchUpperBoundIndex(&@as(u32, 5), @ptrCast(record_singleton[0..].ptr), record_singleton.len, @sizeOf(RawRecord), compare),
        );
        try std.testing.expect(raw_c_compare_calls <= 1);
    }
}

test "phase 6 bsearch upper-bound c abi helpers match bounded insertion points across ascending and descending ranges" {
    var ascending_storage: [32]u32 = undefined;
    var descending_storage: [32]u32 = undefined;

    for (0..ascending_storage.len + 1) |len| {
        for (0..len) |index| {
            const value = @as(u32, @intCast((index + 1) * 2));
            ascending_storage[index] = value;
            descending_storage[len - 1 - index] = value;
        }

        const ascending = ascending_storage[0..len];
        const descending = descending_storage[0..len];
        const budget = binarySearchBudget(len);
        const max_probe: u32 = if (len == 0) 1 else @as(u32, @intCast((len * 2) + 2));
        const ascending_raw: [*]const u8 = @ptrCast(ascending.ptr);
        const descending_raw: [*]const u8 = @ptrCast(descending.ptr);

        var probe: u32 = 0;
        while (probe <= max_probe) : (probe += 1) {
            typed_c_compare_calls = 0;
            const expected_ascending = linearUpperBoundIndexU32(&probe, ascending, compareU32);
            try std.testing.expectEqual(
                expected_ascending,
                bsearch.upperBoundIndex(u32, u32, &probe, ascending, compareU32CountedC),
            );
            try std.testing.expect(typed_c_compare_calls <= budget);

            typed_c_compare_calls = 0;
            const expected_descending = linearUpperBoundIndexU32(&probe, descending, compareDescendingU32);
            try std.testing.expectEqual(
                expected_descending,
                bsearch.upperBoundIndex(u32, u32, &probe, descending, compareDescendingU32CountedC),
            );
            try std.testing.expect(typed_c_compare_calls <= budget);

            raw_c_compare_calls = 0;
            const expected_raw_ascending = linearRawUpperBoundIndexU32(
                &probe,
                ascending_raw,
                ascending.len,
                @sizeOf(u32),
                compareOpaqueU32,
            );
            try std.testing.expectEqual(
                expected_raw_ascending,
                bsearch.bsearchUpperBoundIndex(&probe, ascending_raw, ascending.len, @sizeOf(u32), compareOpaqueU32CountedC),
            );
            try std.testing.expect(raw_c_compare_calls <= budget);

            raw_c_compare_calls = 0;
            const expected_raw_descending = linearRawUpperBoundIndexU32(
                &probe,
                descending_raw,
                descending.len,
                @sizeOf(u32),
                compareDescendingOpaqueU32,
            );
            try std.testing.expectEqual(
                expected_raw_descending,
                bsearch.bsearchUpperBoundIndex(&probe, descending_raw, descending.len, @sizeOf(u32), compareDescendingOpaqueU32CountedC),
            );
            try std.testing.expect(raw_c_compare_calls <= budget);
        }
    }
}

test "phase 6 bsearch upper-bound c abi record member_size replay stays inside a binary-search budget" {
    var record_storage: [32]RawRecord = undefined;

    for (0..record_storage.len + 1) |len| {
        for (0..len) |index| {
            const key = @as(u32, @intCast((index + 1) * 2));
            record_storage[index] = .{
                .key = key,
                .tag = @as(u16, @intCast(100 + index)),
                .flags = @as(u16, @intCast(index & 3)),
                .value = key * 10,
            };
        }

        const records = record_storage[0..len];
        const budget = binarySearchBudget(len);
        const raw_records: [*]const u8 = @ptrCast(records.ptr);
        const max_probe: u32 = if (len == 0) 1 else @as(u32, @intCast((len * 2) + 2));

        var probe: u32 = 0;
        while (probe <= max_probe) : (probe += 1) {
            raw_c_compare_calls = 0;
            const expected = linearRawUpperBoundIndexU32(
                &probe,
                raw_records,
                records.len,
                @sizeOf(RawRecord),
                compareRawRecordKey,
            );
            try std.testing.expectEqual(
                expected,
                bsearch.bsearchUpperBoundIndex(&probe, raw_records, records.len, @sizeOf(RawRecord), compareRawRecordKeyCountedC),
            );
            try std.testing.expect(raw_c_compare_calls <= budget);
        }
    }
}
