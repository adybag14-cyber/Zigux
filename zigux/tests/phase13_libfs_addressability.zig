const std = @import("std");
const libfs = @import("libfs");

test "phase13 libfs descriptor now advertises addressability planning" {
    const descriptor = libfs.LibFsHelperLab.descriptor();
    try std.testing.expectEqualStrings("fs/libfs.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_addressability_planning);
    try std.testing.expect(!descriptor.touches_live_dcache);
    try std.testing.expect(!descriptor.touches_live_inode_state);
}

test "phase13 libfs addressability planning allows empty filesystems and rejects tiny blocks" {
    const empty = libfs.LibFsHelperLab.genericCheckAddressablePlan(4, 0, .{
        .sector_bits = 32,
        .page_index_bits = 32,
    });
    try std.testing.expect(empty.treats_zero_blocks_as_ok);
    try std.testing.expectEqual(@as(i32, 0), empty.return_code);
    try std.testing.expect(!empty.max_bytes_overflowed);

    const tiny = libfs.LibFsHelperLab.genericCheckAddressablePlan(8, 4, .{
        .sector_bits = 32,
        .page_index_bits = 32,
    });
    try std.testing.expect(tiny.checks_min_blocksize);
    try std.testing.expectEqual(@as(i32, -22), tiny.return_code);
    try std.testing.expect(!tiny.sector_limit_exceeded);
    try std.testing.expect(!tiny.page_limit_exceeded);
}

test "phase13 libfs addressability planning reports overflow and cap failures" {
    const overflow = libfs.LibFsHelperLab.genericCheckAddressablePlan(63, 2, .{
        .sector_bits = 64,
        .page_index_bits = 64,
    });
    try std.testing.expect(overflow.max_bytes_overflowed);
    try std.testing.expectEqual(@as(i32, -27), overflow.return_code);

    const sector_limited = libfs.LibFsHelperLab.genericCheckAddressablePlan(12, 1 << 21, .{
        .sector_bits = 20,
        .page_index_bits = 64,
    });
    try std.testing.expect(sector_limited.sector_limit_exceeded);
    try std.testing.expectEqual(@as(i32, -27), sector_limited.return_code);

    const page_limited = libfs.LibFsHelperLab.genericCheckAddressablePlan(12, 1 << 21, .{
        .sector_bits = 64,
        .page_index_bits = 8,
    });
    try std.testing.expect(page_limited.page_limit_exceeded);
    try std.testing.expectEqual(@as(i32, -27), page_limited.return_code);
}

test "phase13 libfs addressability planning accepts bounded sector and page-cache ranges" {
    const ok = libfs.LibFsHelperLab.genericCheckAddressablePlan(12, 128, .{
        .sector_bits = 32,
        .page_index_bits = 32,
    });
    try std.testing.expect(ok.checks_sector_limit);
    try std.testing.expect(ok.checks_page_limit);
    try std.testing.expect(!ok.sector_limit_exceeded);
    try std.testing.expect(!ok.page_limit_exceeded);
    try std.testing.expectEqual(@as(i32, 0), ok.return_code);
}
