const std = @import("std");

const atomic = @import("atomic_helpers");
const barrier = @import("barrier_helpers");
const mmio = @import("mmio_helpers");
const narrow = @import("narrow_unsafe");

test "phase3 low-level wrappers cover the shipped helper surface directly" {
    var value: u32 = 5;

    try std.testing.expectEqual(@as(u32, 5), atomic.load(u32, &value, .seq_cst));
    atomic.store(u32, &value, 8, .seq_cst);
    try std.testing.expectEqual(@as(u32, 8), value);
    try std.testing.expectEqual(@as(u32, 8), atomic.exchange(u32, &value, 13, .seq_cst));
    try std.testing.expectEqual(@as(u32, 13), value);
    try std.testing.expectEqual(@as(u32, 13), atomic.fetchAdd(u32, &value, 4, .seq_cst));
    try std.testing.expectEqual(@as(u32, 17), value);
    try std.testing.expectEqual(@as(u32, 17), atomic.fetchSub(u32, &value, 3, .seq_cst));
    try std.testing.expectEqual(@as(u32, 14), value);
    try std.testing.expectEqual(@as(u32, 14), atomic.fetchAnd(u32, &value, 12, .seq_cst));
    try std.testing.expectEqual(@as(u32, 12), value);
    try std.testing.expectEqual(@as(u32, 12), atomic.fetchOr(u32, &value, 3, .seq_cst));
    try std.testing.expectEqual(@as(u32, 15), value);
    try std.testing.expectEqual(@as(u32, 15), atomic.fetchXor(u32, &value, 6, .seq_cst));
    try std.testing.expectEqual(@as(u32, 9), value);
    try std.testing.expectEqual(@as(u32, 9), atomic.fetchMin(u32, &value, 4, .seq_cst));
    try std.testing.expectEqual(@as(u32, 4), value);
    try std.testing.expectEqual(@as(u32, 4), atomic.fetchMax(u32, &value, 19, .seq_cst));
    try std.testing.expectEqual(@as(u32, 19), value);

    value = 13;
    const seq_cst_swap = atomic.compareExchange(u32, &value, 13, 21, .seq_cst, .seq_cst);
    try std.testing.expectEqual(@as(?u32, null), seq_cst_swap);
    try std.testing.expectEqual(@as(u32, 21), value);

    const mismatch = atomic.compareExchange(u32, &value, 9, 19, .seq_cst, .seq_cst);
    try std.testing.expectEqual(@as(?u32, 21), mismatch);
    try std.testing.expectEqual(@as(u32, 21), value);

    var weak_value: u32 = 21;
    var attempts: usize = 0;
    while (true) {
        attempts += 1;
        if (atomic.compareExchangeWeak(u32, &weak_value, 21, 34, .seq_cst, .seq_cst) == null) break;
        try std.testing.expectEqual(@as(u32, 21), weak_value);
        try std.testing.expect(attempts < 16);
    }
    try std.testing.expectEqual(@as(u32, 34), weak_value);

    barrier.acquire();
    barrier.release();
    barrier.full();
    barrier.acquireRelease();

    var bytes = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const base = narrow.addressOf(&bytes[0]);
    const aligned_halfword: *align(1) const u16 = @ptrCast(&bytes[2]);
    const aligned_word: *align(1) const u32 = @ptrCast(&bytes[@sizeOf(u32)]);
    const byte_desc = mmio.range(base, 8, 1);
    const halfword_desc = mmio.range(base, 8, 2);
    const desc = mmio.range(base, 8, 4);

    try std.testing.expectEqual(base, byte_desc.base_addr);
    try std.testing.expectEqual(@as(u32, 8), byte_desc.length);
    try std.testing.expectEqual(@as(u32, 1), byte_desc.stride);
    try std.testing.expectEqual(base, halfword_desc.base_addr);
    try std.testing.expectEqual(@as(u32, 8), halfword_desc.length);
    try std.testing.expectEqual(@as(u32, 2), halfword_desc.stride);
    try std.testing.expectEqual(base, desc.base_addr);
    try std.testing.expectEqual(@as(u32, 8), desc.length);
    try std.testing.expectEqual(@as(u32, 4), desc.stride);

    mmio.write8(base, 1, 0x5a);
    try std.testing.expectEqual(@as(u8, 0x5a), bytes[1]);
    try std.testing.expectEqual(@as(u8, 0x5a), mmio.read8(base, 1));

    mmio.write16(base, 2, 0xbeef);
    try std.testing.expectEqual(@as(u16, 0xbeef), aligned_halfword.*);
    try std.testing.expectEqual(@as(u16, 0xbeef), mmio.read16(base, 2));

    mmio.write32(base, @sizeOf(u32), 0xfeedbeef);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), aligned_word.*);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), mmio.read32(base, @sizeOf(u32)));

    const odd_halfword: *align(1) const u16 = @ptrCast(&bytes[1]);
    mmio.write16(base, 1, 0x1234);
    try std.testing.expectEqual(@as(u16, 0x1234), odd_halfword.*);
    try std.testing.expectEqual(@as(u16, 0x1234), mmio.read16(base, 1));

    const odd_word: *align(1) const u32 = @ptrCast(&bytes[3]);
    mmio.write32(base, 3, 0x89abcdef);
    try std.testing.expectEqual(@as(u32, 0x89abcdef), odd_word.*);
    try std.testing.expectEqual(@as(u32, 0x89abcdef), mmio.read32(base, 3));

    const odd_doubleword: *align(1) const u64 = @ptrCast(&bytes[5]);
    mmio.write64(base, 5, 0x0123_4567_89ab_cdef);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), odd_doubleword.*);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), mmio.read64(base, 5));
}

test "phase3 low-level wrappers keep non-seq-cst orderings and signed atomic edges reviewable" {
    var handoff_value: u32 = 0;
    atomic.store(u32, &handoff_value, 41, .release);
    try std.testing.expectEqual(@as(u32, 41), atomic.load(u32, &handoff_value, .acquire));

    var signed_value: i32 = 4;
    try std.testing.expectEqual(@as(i32, 4), atomic.fetchMin(i32, &signed_value, -3, .seq_cst));
    try std.testing.expectEqual(@as(i32, -3), signed_value);
    try std.testing.expectEqual(@as(i32, -3), atomic.fetchMax(i32, &signed_value, 6, .seq_cst));
    try std.testing.expectEqual(@as(i32, 6), signed_value);

    var signed_arithmetic_value: i32 = -2;
    try std.testing.expectEqual(@as(i32, -2), atomic.fetchAdd(i32, &signed_arithmetic_value, 5, .seq_cst));
    try std.testing.expectEqual(@as(i32, 3), signed_arithmetic_value);
    try std.testing.expectEqual(@as(i32, 3), atomic.fetchSub(i32, &signed_arithmetic_value, 7, .seq_cst));
    try std.testing.expectEqual(@as(i32, -4), signed_arithmetic_value);

    var monotonic_value: u32 = 5;
    try std.testing.expectEqual(
        @as(?u32, null),
        atomic.compareExchange(u32, &monotonic_value, 5, 7, .monotonic, .monotonic),
    );
    try std.testing.expectEqual(@as(u32, 7), monotonic_value);
    const monotonic_mismatch = atomic.compareExchange(
        u32,
        &monotonic_value,
        5,
        9,
        .monotonic,
        .monotonic,
    );
    try std.testing.expectEqual(@as(?u32, 7), monotonic_mismatch);
    try std.testing.expectEqual(@as(u32, 7), monotonic_value);

    var acq_rel_value: u32 = 7;
    try std.testing.expectEqual(
        @as(?u32, null),
        atomic.compareExchange(u32, &acq_rel_value, 7, 11, .acq_rel, .acquire),
    );
    try std.testing.expectEqual(@as(u32, 11), acq_rel_value);
    const acq_rel_mismatch = atomic.compareExchange(
        u32,
        &acq_rel_value,
        7,
        15,
        .acq_rel,
        .acquire,
    );
    try std.testing.expectEqual(@as(?u32, 11), acq_rel_mismatch);
    try std.testing.expectEqual(@as(u32, 11), acq_rel_value);

    var weak_release_value: u32 = 13;
    var attempts: usize = 0;
    while (true) {
        attempts += 1;
        if (atomic.compareExchangeWeak(u32, &weak_release_value, 13, 19, .release, .monotonic) == null) break;
        try std.testing.expectEqual(@as(u32, 13), weak_release_value);
        try std.testing.expect(attempts < 16);
    }
    try std.testing.expectEqual(@as(u32, 19), weak_release_value);

    const weak_release_mismatch = atomic.compareExchangeWeak(
        u32,
        &weak_release_value,
        13,
        23,
        .release,
        .monotonic,
    );
    try std.testing.expectEqual(@as(?u32, 19), weak_release_mismatch);
    try std.testing.expectEqual(@as(u32, 19), weak_release_value);
}

test "phase3 low-level wrappers keep barrier locality reviewable" {
    var left: u8 = 7;
    var right: u8 = 19;
    const before_left = left;
    const before_right = right;

    barrier.acquire();
    barrier.release();
    barrier.full();
    barrier.acquireRelease();

    try std.testing.expectEqual(before_left, left);
    try std.testing.expectEqual(before_right, right);

    left +%= 1;
    right +%= 2;
    barrier.acquireRelease();

    try std.testing.expectEqual(@as(u8, 8), left);
    try std.testing.expectEqual(@as(u8, 21), right);
}
