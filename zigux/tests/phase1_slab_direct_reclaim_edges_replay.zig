const std = @import("std");
const slab = @import("slab");

test "phase1 slab replay still requires direct reclaim even when zeroing flags are present" {
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocBytes(8, slab.__GFP_ZERO) == null);
    try std.testing.expect(slab.kmallocArray(2, 4, slab.__GFP_ZERO | slab.__GFP_KSWAPD_RECLAIM) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "phase1 slab replay accepts direct-reclaim-only zero-length allocations and frees" {
    slab.kmalloc_nr_allocated = 0;

    const empty_bytes = slab.kmallocBytes(0, slab.__GFP_DIRECT_RECLAIM) orelse
        return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const empty_array = slab.kmallocArray(3, 0, slab.__GFP_DIRECT_RECLAIM | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(empty_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "phase1 slab replay zeroes direct-only array routes without io or fs flags" {
    slab.kmalloc_nr_allocated = 0;

    const zeroed = slab.kmallocArray(2, 3, slab.__GFP_DIRECT_RECLAIM | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);

    try std.testing.expectEqual(@as(usize, 6), zeroed.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    try std.testing.expect(slab.slabIsAvailable());
}

test "phase1 slab replay keeps counters balanced across mixed direct-reclaim routes" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocBytes(0, slab.__GFP_DIRECT_RECLAIM) orelse
        return error.TestUnexpectedResult;
    const bytes = slab.kmallocBytes(5, slab.__GFP_DIRECT_RECLAIM) orelse
        return error.TestUnexpectedResult;
    const zeroed_array = slab.kmallocArray(2, 2, slab.__GFP_DIRECT_RECLAIM | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(isize, 3), slab.kmalloc_nr_allocated);

    @memset(bytes, 0xaa);
    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(zeroed_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
