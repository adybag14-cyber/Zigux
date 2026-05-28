const std = @import("std");

pub const gfp_t = u32;

pub const __GFP_IO: gfp_t = @as(gfp_t, 1) << 6;
pub const __GFP_FS: gfp_t = @as(gfp_t, 1) << 7;
pub const __GFP_ZERO: gfp_t = @as(gfp_t, 1) << 8;
pub const __GFP_DIRECT_RECLAIM: gfp_t = @as(gfp_t, 1) << 10;
pub const __GFP_KSWAPD_RECLAIM: gfp_t = @as(gfp_t, 1) << 11;
pub const __GFP_RECLAIM: gfp_t = __GFP_DIRECT_RECLAIM | __GFP_KSWAPD_RECLAIM;
pub const GFP_KERNEL: gfp_t = __GFP_RECLAIM | __GFP_IO | __GFP_FS;

pub var kmalloc_nr_allocated: isize = 0;
pub var kmalloc_verbose = false;

const backing_allocator = std.heap.page_allocator;

fn allocZeroedBytes(size: usize) ?[]u8 {
    const bytes = backing_allocator.alloc(u8, size) catch return null;
    @memset(bytes, 0);
    kmalloc_nr_allocated += 1;
    return bytes;
}

pub fn kmallocBytes(size: usize, gfp: gfp_t) ?[]u8 {
    if ((gfp & __GFP_DIRECT_RECLAIM) == 0) {
        return null;
    }

    return allocZeroedBytes(size);
}

pub fn kfree(bytes: ?[]u8) void {
    if (bytes) |slice| {
        backing_allocator.free(slice);
        kmalloc_nr_allocated -= 1;
    }
}

pub fn kmallocArray(n: usize, size: usize, gfp: gfp_t) ?[]u8 {
    if ((gfp & __GFP_DIRECT_RECLAIM) == 0) {
        return null;
    }

    const total = std.math.mul(usize, n, size) catch return null;
    return allocZeroedBytes(total);
}

pub fn slabIsAvailable() bool {
    return true;
}

test "kmalloc respects reclaim flags and zeroes successful allocations" {
    kmalloc_nr_allocated = 0;
    try std.testing.expect(kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);

    const plain = kmallocBytes(8, GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
    for (plain) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const explicit_zero = kmallocBytes(8, GFP_KERNEL | __GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer kfree(explicit_zero);
    try std.testing.expectEqual(@as(isize, 2), kmalloc_nr_allocated);
    for (explicit_zero) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}

test "kmallocArray keeps the same zeroed contract" {
    kmalloc_nr_allocated = 0;

    const plain = kmallocArray(4, 2, GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
    for (plain) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const explicit_zero = kmallocArray(4, 2, GFP_KERNEL | __GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer kfree(explicit_zero);
    try std.testing.expectEqual(@as(isize, 2), kmalloc_nr_allocated);
    for (explicit_zero) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    try std.testing.expect(slabIsAvailable());
}

test "kmallocArray fail paths keep allocation counters unchanged" {
    kmalloc_nr_allocated = 0;
    try std.testing.expect(kmallocArray(4, 2, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);

    try std.testing.expect(kmallocArray(std.math.maxInt(usize), 2, GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);
}
