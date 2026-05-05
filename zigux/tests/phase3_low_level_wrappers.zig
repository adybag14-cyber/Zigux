const std = @import("std");

const atomic = @import("atomic_helpers");
const barrier = @import("barrier_helpers");
const mmio = @import("mmio_helpers");
const narrow = @import("narrow_unsafe");

test "phase3 low-level wrappers stay inside the current helper surface" {
    var value: u32 = 5;

    try std.testing.expectEqual(@as(u32, 5), atomic.load(u32, &value, .seq_cst));
    atomic.store(u32, &value, 8, .seq_cst);
    try std.testing.expectEqual(@as(u32, 8), value);
    try std.testing.expectEqual(@as(u32, 8), atomic.exchange(u32, &value, 13, .seq_cst));
    try std.testing.expectEqual(@as(u32, 13), value);

    try std.testing.expectEqual(
        @as(?u32, null),
        atomic.compareExchange(u32, &value, 13, 21, .seq_cst, .seq_cst),
    );
    try std.testing.expectEqual(@as(u32, 21), value);

    const mismatch = atomic.compareExchange(u32, &value, 9, 19, .seq_cst, .seq_cst);
    try std.testing.expectEqual(@as(?u32, 21), mismatch);
    try std.testing.expectEqual(@as(u32, 21), value);

    barrier.acquire();
    barrier.release();
    barrier.full();

    var regs = [_]u32{ 0, 0 };
    const base = narrow.addressOf(&regs[0]);
    const desc = mmio.range(base, 8, 4);

    try std.testing.expectEqual(base, desc.base_addr);
    try std.testing.expectEqual(@as(u32, 8), desc.length);
    try std.testing.expectEqual(@as(u32, 4), desc.stride);

    mmio.write32(base, @sizeOf(u32), 0xfeedbeef);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), regs[1]);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), mmio.read32(base, @sizeOf(u32)));
}
