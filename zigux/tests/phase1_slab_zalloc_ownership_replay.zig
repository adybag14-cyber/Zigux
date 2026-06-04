const std = @import("std");
const slab = @import("slab");
const zalloc = @import("zalloc");

const AllocState = struct {
    slab_start: isize,
    slab_end: isize,
    zalloc_bytes_cleared: bool,
    zalloc_value_cleared: bool,
};

test "slab and zalloc frees reset ownership without leaking counters" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const start = slab.kmalloc_nr_allocated;
    const bytes = slab.kmallocBytes(16, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(start + 1, slab.kmalloc_nr_allocated);
    @memset(bytes, 0xa5);

    slab.kfree(bytes);
    try std.testing.expectEqual(start, slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(start, slab.kmalloc_nr_allocated);

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 16);
    for (owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
}

test "zeroing aliases preserve Phase 1 ownership accounting" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const bytes = if (@hasDecl(slab, "kzallocBytes"))
        slab.kzallocBytes(12, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult
    else
        slab.kmallocBytes(12, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(bytes);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const Pair = struct {
        left: u32,
        right: bool,
    };

    var pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u32, 0), pair.?.left);
    try std.testing.expectEqual(false, pair.?.right);

    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);
    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);
}

test "array overflow and tracked zero-size owners stay fenced" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zero_slab = slab.kmallocArray(0, 32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_slab.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero_slab);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var zero_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(zero_owner != null);
    try std.testing.expectEqual(@as(usize, 0), zero_owner.?.len);
    zalloc.zfreeBytes(allocator, &zero_owner);
    try std.testing.expect(zero_owner == null);

    if (@hasDecl(slab, "kcallocBytes")) {
        const counted = slab.kcallocBytes(3, 4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
        defer slab.kfree(counted);
        try std.testing.expectEqual(@as(usize, 12), counted.len);
        for (counted) |value| {
            try std.testing.expectEqual(@as(u8, 0), value);
        }
    }
}

test "combined allocation state can be summarized after cleanup" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_bytes = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    var zbytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    const zvalue = try zalloc.zallocValue(allocator, AllocState);

    const state = AllocState{
        .slab_start = 0,
        .slab_end = slab.kmalloc_nr_allocated,
        .zalloc_bytes_cleared = std.mem.allEqual(u8, zbytes.?, 0),
        .zalloc_value_cleared = zvalue.slab_start == 0 and zvalue.slab_end == 0 and !zvalue.zalloc_bytes_cleared and !zvalue.zalloc_value_cleared,
    };

    slab.kfree(slab_bytes);
    zalloc.zfreeBytes(allocator, &zbytes);
    allocator.destroy(zvalue);

    try std.testing.expectEqual(@as(isize, 0), state.slab_start);
    try std.testing.expectEqual(@as(isize, 1), state.slab_end);
    try std.testing.expect(state.zalloc_bytes_cleared);
    try std.testing.expect(state.zalloc_value_cleared);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try std.testing.expect(zbytes == null);
}
