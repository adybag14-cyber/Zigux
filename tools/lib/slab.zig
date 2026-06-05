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

pub fn kzallocBytes(size: usize, gfp: gfp_t) ?[]u8 {
    return kmallocBytes(size, gfp | __GFP_ZERO);
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
    if ((gfp & __GFP_ZERO) != 0) {
        @memset(bytes, 0);
    }
    return bytes;
}

pub fn kcallocBytes(n: usize, size: usize, gfp: gfp_t) ?[]u8 {
    return kmallocArray(n, size, gfp | __GFP_ZERO);
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

test "kmallocArray only zeroes when __GFP_ZERO is requested" {
    kmalloc_nr_allocated = 0;

    const plain = kmallocArray(4, 2, GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
    @memset(plain, 0xaa);

    const zeroed = kmallocArray(4, 2, GFP_KERNEL | __GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 2), kmalloc_nr_allocated);
    for (zeroed) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    try std.testing.expect(slabIsAvailable());
}

test "kmalloc zero-size allocations and null frees keep counters balanced" {
    kmalloc_nr_allocated = 0;

    kfree(null);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);

    const bytes = kmallocBytes(0, GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), bytes.len);
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
    kfree(bytes);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);

    const array = kmallocArray(0, 16, GFP_KERNEL | __GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), array.len);
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
    kfree(array);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);

    kfree(null);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);
}

test "zeroing aliases request __GFP_ZERO while preserving allocation accounting" {
    kmalloc_nr_allocated = 0;

    const single = kzallocBytes(8, GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
    for (single) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    kfree(single);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);

    const array = kcallocBytes(4, 2, GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer kfree(array);
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
    for (array) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    try std.testing.expect(kzallocBytes(8, 0) == null);
    try std.testing.expect(kcallocBytes(std.math.maxInt(usize), 2, GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
}

test "kmallocArray failure paths preserve live owners and counters" {
    kmalloc_nr_allocated = 0;

    const first = kmallocArray(2, 4, GFP_KERNEL | __GFP_ZERO) orelse return error.TestUnexpectedResult;
    const second = kmallocArray(3, 2, GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), kmalloc_nr_allocated);

    @memset(first, 0x11);
    @memset(second, 0x22);

    try std.testing.expect(kmallocArray(4, 4, __GFP_ZERO) == null);
    try std.testing.expect(kmallocArray(std.math.maxInt(usize), 2, GFP_KERNEL | __GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 2), kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11 }, first);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x22, 0x22, 0x22, 0x22, 0x22, 0x22 }, second);

    kfree(second);
    try std.testing.expectEqual(@as(isize, 1), kmalloc_nr_allocated);
    kfree(first);
    try std.testing.expectEqual(@as(isize, 0), kmalloc_nr_allocated);
}
