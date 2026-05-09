const std = @import("std");
const bsearch = @import("bsearch");

const RawRecord = extern struct {
    key: u32,
    tag: u16,
    flags: u16,
    value: u32,
};

var typed_c_compare_calls: usize = 0;
var raw_c_compare_calls: usize = 0;

fn compareU32(key: *const u32, item: *const u32) i32 {
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareDescendingU32(key: *const u32, item: *const u32) i32 {
    return switch (std.math.order(item.*, key.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareOpaqueU32(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareU32(typed_key, typed_item);
}

fn compareDescendingOpaqueU32(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const u32 = @ptrCast(@alignCast(item));
    return compareDescendingU32(typed_key, typed_item);
}

fn compareRawRecordKey(key: *const anyopaque, item: *const anyopaque) i32 {
    const typed_key: *const u32 = @ptrCast(@alignCast(key));
    const typed_item: *const RawRecord = @ptrCast(@alignCast(item));
    return compareU32(typed_key, &typed_item.key);
}

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

fn linearSearchIndexU32(key: *const u32, items: []const u32, compare: anytype) ?usize {
    for (items, 0..) |_, index| {
        if (compare(key, &items[index]) == 0) return index;
    }
    return null;
}

fn linearRawSearchIndexU32(
    key: *const anyopaque,
    base: [*]const u8,
    num_members: usize,
    member_size: usize,
    compare: anytype,
) ?usize {
    for (0..num_members) |index| {
        const item: *const anyopaque = @ptrCast(base + (index * member_size));
        if (compare(key, item) == 0) return index;
    }
    return null;
}

test "phase 6 bsearch direct c abi equality helpers stay inside a binary-search budget" {
    var ascending_storage: [32]u32 = undefined;
    var descending_storage: [32]u32 = undefined;
    var record_storage: [32]RawRecord = undefined;

    const ascending_comparators = [_]bsearch.CComparator(u32, u32){ compareU32CountedC, compareU32CountedAliasC };
    const descending_comparators = [_]bsearch.CComparator(u32, u32){ compareDescendingU32CountedC, compareDescendingU32CountedAliasC };
    const raw_ascending_comparators = [_]bsearch.CRawComparator{ compareOpaqueU32CountedC, compareOpaqueU32CountedAliasC };
    const raw_descending_comparators = [_]bsearch.CRawComparator{ compareDescendingOpaqueU32CountedC, compareDescendingOpaqueU32CountedAliasC };
    const raw_record_comparators = [_]bsearch.CRawComparator{ compareRawRecordKeyCountedC, compareRawRecordKeyCountedAliasC };

    for (0..ascending_storage.len + 1) |len| {
        for (0..len) |index| {
            const value = @as(u32, @intCast((index + 1) * 2));
            ascending_storage[index] = value;
            descending_storage[len - 1 - index] = value;
            record_storage[index] = .{
                .key = value,
                .tag = @as(u16, @intCast(100 + index)),
                .flags = @as(u16, @intCast(index & 3)),
                .value = value * 10,
            };
        }

        const ascending = ascending_storage[0..len];
        const descending = descending_storage[0..len];
        const records = record_storage[0..len];
        const budget = binarySearchBudget(len);
        const max_probe: u32 = if (len == 0) 1 else @as(u32, @intCast((len * 2) + 1));
        const ascending_raw: [*]const u8 = @ptrCast(ascending.ptr);
        const descending_raw: [*]const u8 = @ptrCast(descending.ptr);
        const record_raw: [*]const u8 = @ptrCast(records.ptr);

        var probe: u32 = 1;
        while (probe <= max_probe) : (probe += 1) {
            for (ascending_comparators) |compare| {
                typed_c_compare_calls = 0;
                try std.testing.expectEqual(
                    linearSearchIndexU32(&probe, ascending, compareU32),
                    bsearch.searchIndex(u32, u32, &probe, ascending, compare),
                );
                try std.testing.expect(typed_c_compare_calls <= budget);
            }

            for (descending_comparators) |compare| {
                typed_c_compare_calls = 0;
                try std.testing.expectEqual(
                    linearSearchIndexU32(&probe, descending, compareDescendingU32),
                    bsearch.searchIndex(u32, u32, &probe, descending, compare),
                );
                try std.testing.expect(typed_c_compare_calls <= budget);
            }

            for (raw_ascending_comparators) |compare| {
                raw_c_compare_calls = 0;
                try std.testing.expectEqual(
                    linearRawSearchIndexU32(&probe, ascending_raw, ascending.len, @sizeOf(u32), compareOpaqueU32),
                    bsearch.bsearchIndex(&probe, ascending_raw, ascending.len, @sizeOf(u32), compare),
                );
                try std.testing.expect(raw_c_compare_calls <= budget);
            }

            for (raw_descending_comparators) |compare| {
                raw_c_compare_calls = 0;
                try std.testing.expectEqual(
                    linearRawSearchIndexU32(&probe, descending_raw, descending.len, @sizeOf(u32), compareDescendingOpaqueU32),
                    bsearch.bsearchIndex(&probe, descending_raw, descending.len, @sizeOf(u32), compare),
                );
                try std.testing.expect(raw_c_compare_calls <= budget);
            }

            for (raw_record_comparators) |compare| {
                raw_c_compare_calls = 0;
                try std.testing.expectEqual(
                    linearRawSearchIndexU32(&probe, record_raw, records.len, @sizeOf(RawRecord), compareRawRecordKey),
                    bsearch.bsearchIndex(&probe, record_raw, records.len, @sizeOf(RawRecord), compare),
                );
                try std.testing.expect(raw_c_compare_calls <= budget);
            }
        }
    }
}
