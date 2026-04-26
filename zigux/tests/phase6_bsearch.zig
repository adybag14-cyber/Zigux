const std = @import("std");
const bsearch = @import("bsearch");

const Symbol = struct {
    name: []const u8,
    address: usize,
};

fn compareU32(key: *const u32, item: *const u32) i32 {
    return switch (std.math.order(key.*, item.*)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn compareSymbolName(key: *const []const u8, item: *const Symbol) i32 {
    return switch (std.mem.order(u8, key.*, item.name)) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

test "phase 6 bsearch module imports cleanly" {
    _ = bsearch;
}

test "phase 6 bsearch finds integer keys across the slice" {
    const values = [_]u32{ 3, 8, 13, 21, 34, 55, 89 };

    try std.testing.expectEqual(@as(?usize, 0), bsearch.searchIndex(u32, u32, &@as(u32, 3), values[0..], compareU32));
    try std.testing.expectEqual(@as(?usize, 3), bsearch.searchIndex(u32, u32, &@as(u32, 21), values[0..], compareU32));
    try std.testing.expectEqual(@as(?usize, 6), bsearch.searchIndex(u32, u32, &@as(u32, 89), values[0..], compareU32));
}

test "phase 6 bsearch rejects missing integer keys without widening the contract" {
    const values = [_]u32{ 1, 4, 9, 16, 25, 36 };

    try std.testing.expectEqual(@as(?usize, null), bsearch.searchIndex(u32, u32, &@as(u32, 0), values[0..], compareU32));
    try std.testing.expectEqual(@as(?usize, null), bsearch.searchIndex(u32, u32, &@as(u32, 15), values[0..], compareU32));
    try std.testing.expectEqual(@as(?usize, null), bsearch.searchIndex(u32, u32, &@as(u32, 40), values[0..], compareU32));
}

test "phase 6 bsearch supports string keys against sorted records" {
    const symbols = [_]Symbol{
        .{ .name = "do_exit", .address = 0x1000 },
        .{ .name = "kfree", .address = 0x1200 },
        .{ .name = "kmalloc", .address = 0x1400 },
        .{ .name = "schedule", .address = 0x1800 },
    };

    const found = bsearch.search([]const u8, Symbol, &@as([]const u8, "kmalloc"), symbols[0..], compareSymbolName) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0x1400), found.address);
    try std.testing.expect(bsearch.search([]const u8, Symbol, &@as([]const u8, "vfree"), symbols[0..], compareSymbolName) == null);
}
