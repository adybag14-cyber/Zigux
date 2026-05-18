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

pub fn kmallocBytes(size: usize, gfp: gfp_t) ?[]u8 {
    if ((gfp & __GFP_DIRECT_RECLAIM) == 0) {
        return null;
    }

    const bytes = backing_allocator.alloc(u8, size) catch return null;
    kmalloc_nr_allocated += 1;
    if ((gfp & __GFP_ZERO) != 0) {
        @memset(bytes, 0);
    }
    return bytes;
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
    const bytes = backing_allocator.alloc(u8, total) catch return null;
    kmalloc_nr_allocated += 1;
    @memset(bytes, 0);
    return bytes;
}

pub fn slabIsAvailable() bool {
    return true;
}

test "kmalloc respects reclaim flags and zeroing" {
    kmalloc_nr_allocated = 0;
    try std.testing.expect(kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);

    const plain = kmallocBytes(8, GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);

    @memset(plain, 0xaa);
    kfree(plain);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);

    const zeroed = kmallocBytes(8, GFP_KERNEL | __GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer kfree(zeroed);
    for (zeroed) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}

test "kmallocArray returns zeroed memory and updates counters" {
    kmalloc_nr_allocated = 0;
    const bytes = kmallocArray(4, 2, GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer kfree(bytes);

    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
    for (bytes) |value| {
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

test "kfree ignores null slices without changing counters" {
    kmalloc_nr_allocated = 0;
    kfree(null);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);
}

test "kfree ignores null while real allocations stay live" {
    kmalloc_nr_allocated = 0;

    const live = kmallocBytes(4, GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);

    kfree(null);
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);

    kfree(live);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);
}

test "zero-sized allocations stay freeable and keep counters balanced" {
    kmalloc_nr_allocated = 0;

    const zero_bytes = kmallocBytes(0, GFP_KERNEL | __GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
    kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);

    const zero_array = kmallocArray(0, 8, GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_array.len);
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
    kfree(zero_array);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);
}

test "kmallocArray treats zero-sized elements as freeable zero-sized allocations" {
    kmalloc_nr_allocated = 0;

    const zero_sized = kmallocArray(std.math.maxInt(usize), 0, GFP_KERNEL) orelse
        return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_sized.len);
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
    kfree(zero_sized);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);
}

test "kmallocArray zeroes fresh allocations after earlier dirty frees" {
    kmalloc_nr_allocated = 0;

    const first = kmallocArray(4, 1, GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
    @memset(first, 0xaa);
    kfree(first);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);

    const second = kmallocArray(4, 1, GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer kfree(second);
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0, 0 }, second);
}
