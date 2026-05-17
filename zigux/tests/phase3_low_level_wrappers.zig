const std = @import("std");
const atomic = @import("atomic");
const barrier = @import("barrier");
const mmio = @import("mmio");

test "phase3 low-level wrappers keep atomic ordering, barriers, and MMIO handoffs aligned" {
    var cell: u32 = 7;
    const previous = try atomic.compareExchangeStrong(u32, &cell, 7, 13, .acq_rel, .acquire);
    try std.testing.expectEqual(@as(?u32, null), previous);

    barrier.compiler();
    barrier.release();

    var register: u32 = 0;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    mmio.write(u32, register_ptr, cell);

    barrier.acquire();
    try std.testing.expectEqual(@as(u32, 13), mmio.read(u32, register_ptr));
}

test "phase3 low-level wrappers keep masked MMIO updates explicit after compare-exchange setup" {
    var state: u16 = 0x00F0;
    try std.testing.expectEqual(
        @as(?u16, null),
        try atomic.compareExchangeWeak(u16, &state, 0x00F0, 0x0FF0, .seq_cst, .acquire),
    );

    var register: u16 = state;
    const register_ptr: *volatile u16 = @ptrCast(&register);
    const updated = mmio.writeMasked(u16, register_ptr, 0x00F0, 0x0005);

    barrier.fullFence();
    try std.testing.expectEqual(@as(u16, 0x0F05), updated);
    try std.testing.expectEqual(updated, register);
    try std.testing.expectEqual(@as(?atomic.Ordering, .seq_cst), atomic.strongestAllowedFailureOrder(.seq_cst));
}
