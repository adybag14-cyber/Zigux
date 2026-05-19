const std = @import("std");
const slab = @import("slab");

test "phase1 slab replay keeps live allocation counters stable across rejected paths" {
    slab.kmalloc_nr_allocated = 0;

    const live = slab.kmallocBytes(8, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer {
        slab.kfree(live);
        slab.kmalloc_nr_allocated = 0;
    }

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "phase1 slab replay keeps zeroed array allocations freeable and counter-balanced" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocArray(4, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer {
        slab.kfree(bytes);
        slab.kmalloc_nr_allocated = 0;
    }

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.slabIsAvailable());
}

test "phase1 slab replay keeps GFP_ZERO byte allocations zeroed after earlier dirty frees" {
    slab.kmalloc_nr_allocated = 0;

    const dirty = slab.kmallocBytes(8, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    @memset(dirty, 0xaa);
    slab.kfree(dirty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocBytes(8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer {
        slab.kfree(zeroed);
        slab.kmalloc_nr_allocated = 0;
    }

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (zeroed) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}
