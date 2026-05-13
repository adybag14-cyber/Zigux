const std = @import("std");
const bsearch = @import("bsearch");
const fixtures = @import("fixtures/phase6_bsearch_vectors.zig");

const RawRecord = extern struct {
    key: u32,
    value: u32,
};

const CountedKey = struct {
    target: u32,
    comparisons: *usize,
};

const CountedOpaqueKey = struct {
    target: u32,
    comparisons: *usize,
};

fn comparisonBudget(len: usize) usize {
    if (len <= 1) return len;
    return std.math.log2_int_ceil(usize, len) + 1;
}

fn compareAscendingC(key: *const CountedKey, item: *const u32) callconv(.c) i32 {
    key.comparisons.* += 1;
    return switch (std.math.order(key.target, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareDescendingC(key: *const CountedKey, item: *const u32) callconv(.c) i32 {
    key.comparisons.* += 1;
    return switch (std.math.order(item.*, key.target)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareOpaqueAscendingC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    const typed_key: *const CountedOpaqueKey = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    typed_key.comparisons.* += 1;
    return switch (std.math.order(typed_key.target, typed_item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareOpaqueDescendingC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    const typed_key: *const CountedOpaqueKey = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    typed_key.comparisons.* += 1;
    return switch (std.math.order(typed_item.*, typed_key.target)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareOpaqueRecordAscendingC(key: *const anyopaque, item: *const anyopaque) callconv(.c) i32 {
    const typed_key: *const CountedOpaqueKey = @ptrCast(@alignCast(key));
    const typed_item: *const RawRecord = @ptrCast(@alignCast(item));
    typed_key.comparisons.* += 1;
    return switch (std.math.order(typed_key.target, typed_item.key)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn fillAscending(storage: []u32) void {
    for (storage, 0..) |*slot, index| slot.* = @as(u32, @intCast(index * 2));
}

fn fillDescending(storage: []u32) void {
    for (storage, 0..) |*slot, index| slot.* = @as(u32, @intCast((storage.len - 1 - index) * 2));
}

fn fillRecords(storage: []RawRecord) void {
    for (storage, 0..) |*slot, index| {
        const key = @as(u32, @intCast(index * 2));
        slot.* = .{ .key = key, .value = key * 16 };
    }
}

fn expectedIndexAscending(items: []const u32, target: u32) ?usize {
    for (items, 0..) |item, index| {
        if (item == target) return index;
    }
    return null;
}

fn expectedIndexDescending(items: []const u32, target: u32) ?usize {
    for (items, 0..) |item, index| {
        if (item == target) return index;
    }
    return null;
}

fn expectedIndexRecord(items: []const RawRecord, target: u32) ?usize {
    for (items, 0..) |item, index| {
        if (item.key == target) return index;
    }
    return null;
}

test "phase 6 bsearch direct c abi equality helpers stay inside a binary-search budget" {
    var ascending_storage: [32]u32 = undefined;
    var descending_storage: [32]u32 = undefined;
    var record_storage: [32]RawRecord = undefined;

    for (fixtures.dynamic_case_lengths) |len| {
        fillAscending(ascending_storage[0..len]);
        fillDescending(descending_storage[0..len]);
        fillRecords(record_storage[0..len]);
        const budget = comparisonBudget(len);
        const max_probe: u32 = if (len == 0) 1 else @as(u32, @intCast((len * 2) + 1));
        var probe: u32 = 0;
        while (probe <= max_probe) : (probe += 1) {
            var ascending_comparisons: usize = 0;
            const ascending_key = CountedKey{ .target = probe, .comparisons = &ascending_comparisons };
            try std.testing.expectEqual(expectedIndexAscending(ascending_storage[0..len], probe), bsearch.searchIndex(CountedKey, u32, &ascending_key, ascending_storage[0..len], compareAscendingC));
            try std.testing.expect(ascending_comparisons <= budget);

            var descending_comparisons: usize = 0;
            const descending_key = CountedKey{ .target = probe, .comparisons = &descending_comparisons };
            try std.testing.expectEqual(expectedIndexDescending(descending_storage[0..len], probe), bsearch.searchIndex(CountedKey, u32, &descending_key, descending_storage[0..len], compareDescendingC));
            try std.testing.expect(descending_comparisons <= budget);

            var raw_ascending_comparisons: usize = 0;
            const raw_ascending_key = CountedOpaqueKey{ .target = probe, .comparisons = &raw_ascending_comparisons };
            try std.testing.expectEqual(expectedIndexAscending(ascending_storage[0..len], probe), bsearch.bsearchIndex(&raw_ascending_key, @ptrCast(ascending_storage[0..len].ptr), len, @sizeOf(u32), compareOpaqueAscendingC));
            try std.testing.expect(raw_ascending_comparisons <= budget);

            var raw_descending_comparisons: usize = 0;
            const raw_descending_key = CountedOpaqueKey{ .target = probe, .comparisons = &raw_descending_comparisons };
            try std.testing.expectEqual(expectedIndexDescending(descending_storage[0..len], probe), bsearch.bsearchIndex(&raw_descending_key, @ptrCast(descending_storage[0..len].ptr), len, @sizeOf(u32), compareOpaqueDescendingC));
            try std.testing.expect(raw_descending_comparisons <= budget);

            var raw_record_comparisons: usize = 0;
            const raw_record_key = CountedOpaqueKey{ .target = probe, .comparisons = &raw_record_comparisons };
            try std.testing.expectEqual(expectedIndexRecord(record_storage[0..len], probe), bsearch.bsearchIndex(&raw_record_key, @ptrCast(record_storage[0..len].ptr), len, @sizeOf(RawRecord), compareOpaqueRecordAscendingC));
            try std.testing.expect(raw_record_comparisons <= budget);
        }
    }
}
