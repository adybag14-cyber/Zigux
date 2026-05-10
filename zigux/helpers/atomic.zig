const std = @import("std");

pub fn load(comptime T: type, ptr: *const T, comptime order: std.builtin.AtomicOrder) T {
    return @atomicLoad(T, ptr, order);
}

pub fn store(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) void {
    @atomicStore(T, ptr, value, order);
}

pub fn exchange(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {
    return @atomicRmw(T, ptr, .Xchg, value, order);
}

pub fn fetchAdd(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {
    return @atomicRmw(T, ptr, .Add, value, order);
}

pub fn fetchSub(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {
    return @atomicRmw(T, ptr, .Sub, value, order);
}

pub fn fetchAnd(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {
    return @atomicRmw(T, ptr, .And, value, order);
}

pub fn fetchOr(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {
    return @atomicRmw(T, ptr, .Or, value, order);
}

pub fn fetchXor(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {
    return @atomicRmw(T, ptr, .Xor, value, order);
}

pub fn fetchNand(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {
    return @atomicRmw(T, ptr, .Nand, value, order);
}

pub fn fetchMin(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {
    return @atomicRmw(T, ptr, .Min, value, order);
}

pub fn fetchMax(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {
    return @atomicRmw(T, ptr, .Max, value, order);
}

pub fn compareExchange(
    comptime T: type,
    ptr: *T,
    expected_value: T,
    new_value: T,
    comptime success_order: std.builtin.AtomicOrder,
    comptime failure_order: std.builtin.AtomicOrder,
) ?T {
    return @cmpxchgStrong(T, ptr, expected_value, new_value, success_order, failure_order);
}

pub fn compareExchangeWeak(
    comptime T: type,
    ptr: *T,
    expected_value: T,
    new_value: T,
    comptime success_order: std.builtin.AtomicOrder,
    comptime failure_order: std.builtin.AtomicOrder,
) ?T {
    return @cmpxchgWeak(T, ptr, expected_value, new_value, success_order, failure_order);
}

test "phase3 atomic wrappers behave predictably" {
    var value: u32 = 1;
    try std.testing.expectEqual(@as(u32, 1), load(u32, &value, .seq_cst));

    store(u32, &value, 7, .seq_cst);
    try std.testing.expectEqual(@as(u32, 7), value);

    try std.testing.expectEqual(@as(u32, 7), exchange(u32, &value, 9, .seq_cst));
    try std.testing.expectEqual(@as(u32, 9), value);

    try std.testing.expectEqual(@as(u32, 9), fetchAdd(u32, &value, 2, .seq_cst));
    try std.testing.expectEqual(@as(u32, 11), value);

    try std.testing.expectEqual(@as(u32, 11), fetchSub(u32, &value, 4, .seq_cst));
    try std.testing.expectEqual(@as(u32, 7), value);

    try std.testing.expectEqual(@as(u32, 7), fetchAnd(u32, &value, 6, .seq_cst));
    try std.testing.expectEqual(@as(u32, 6), value);

    try std.testing.expectEqual(@as(u32, 6), fetchOr(u32, &value, 8, .seq_cst));
    try std.testing.expectEqual(@as(u32, 14), value);

    try std.testing.expectEqual(@as(u32, 14), fetchXor(u32, &value, 3, .seq_cst));
    try std.testing.expectEqual(@as(u32, 13), value);

    var nand_value: u32 = 0x0000_000c;
    try std.testing.expectEqual(@as(u32, 0x0000_000c), fetchNand(u32, &nand_value, 0x0000_000a, .seq_cst));
    try std.testing.expectEqual(@as(u32, 0xffff_fff7), nand_value);

    try std.testing.expectEqual(@as(u32, 13), fetchMin(u32, &value, 11, .seq_cst));
    try std.testing.expectEqual(@as(u32, 11), value);

    try std.testing.expectEqual(@as(u32, 11), fetchMax(u32, &value, 17, .seq_cst));
    try std.testing.expectEqual(@as(u32, 17), value);

    var signed_value: i32 = 4;
    try std.testing.expectEqual(@as(i32, 4), fetchMin(i32, &signed_value, -3, .seq_cst));
    try std.testing.expectEqual(@as(i32, -3), signed_value);
    try std.testing.expectEqual(@as(i32, -3), fetchMax(i32, &signed_value, 6, .seq_cst));
    try std.testing.expectEqual(@as(i32, 6), signed_value);

    var signed_arithmetic_value: i32 = -2;
    try std.testing.expectEqual(@as(i32, -2), fetchAdd(i32, &signed_arithmetic_value, 5, .seq_cst));
    try std.testing.expectEqual(@as(i32, 3), signed_arithmetic_value);
    try std.testing.expectEqual(@as(i32, 3), fetchSub(i32, &signed_arithmetic_value, 7, .seq_cst));
    try std.testing.expectEqual(@as(i32, -4), signed_arithmetic_value);

    try std.testing.expectEqual(@as(?u32, null), compareExchange(u32, &value, 17, 19, .seq_cst, .seq_cst));
    try std.testing.expectEqual(@as(u32, 19), value);

    const mismatch = compareExchange(u32, &value, 17, 21, .seq_cst, .seq_cst);
    try std.testing.expectEqual(@as(?u32, 19), mismatch);
    try std.testing.expectEqual(@as(u32, 19), value);

    const weak_result = compareExchangeWeak(u32, &value, 19, 23, .seq_cst, .seq_cst);
    try std.testing.expect(weak_result == null or weak_result == 19);
    if (weak_result == null) {
        try std.testing.expectEqual(@as(u32, 23), value);
    } else {
        try std.testing.expectEqual(@as(u32, 19), value);
    }
}

test "phase3 atomic wrappers keep non-seq-cst orderings reviewable" {
    var handoff_value: u32 = 0;
    store(u32, &handoff_value, 41, .release);
    try std.testing.expectEqual(@as(u32, 41), load(u32, &handoff_value, .acquire));

    var monotonic_value: u32 = 5;
    try std.testing.expectEqual(@as(?u32, null), compareExchange(u32, &monotonic_value, 5, 7, .monotonic, .monotonic));
    try std.testing.expectEqual(@as(u32, 7), monotonic_value);
    const monotonic_mismatch = compareExchange(u32, &monotonic_value, 5, 9, .monotonic, .monotonic);
    try std.testing.expectEqual(@as(?u32, 7), monotonic_mismatch);
    try std.testing.expectEqual(@as(u32, 7), monotonic_value);

    var monotonic_nand_value: u32 = 0x0000_00ff;
    try std.testing.expectEqual(@as(u32, 0x0000_00ff), fetchNand(u32, &monotonic_nand_value, 0x0000_0f0f, .monotonic));
    try std.testing.expectEqual(@as(u32, 0xffff_fff0), monotonic_nand_value);

    var acq_rel_value: u32 = 7;
    try std.testing.expectEqual(@as(?u32, null), compareExchange(u32, &acq_rel_value, 7, 11, .acq_rel, .acquire));
    try std.testing.expectEqual(@as(u32, 11), acq_rel_value);
    const acq_rel_mismatch = compareExchange(u32, &acq_rel_value, 7, 15, .acq_rel, .acquire);
    try std.testing.expectEqual(@as(?u32, 11), acq_rel_mismatch);
    try std.testing.expectEqual(@as(u32, 11), acq_rel_value);

    var weak_release_value: u32 = 13;
    var attempts: usize = 0;
    while (true) {
        attempts += 1;
        if (compareExchangeWeak(u32, &weak_release_value, 13, 19, .release, .monotonic) == null) break;
        try std.testing.expectEqual(@as(u32, 13), weak_release_value);
        try std.testing.expect(attempts < 16);
    }
    try std.testing.expectEqual(@as(u32, 19), weak_release_value);

    const weak_mismatch = compareExchangeWeak(u32, &weak_release_value, 13, 23, .release, .monotonic);
    try std.testing.expectEqual(@as(?u32, 19), weak_mismatch);
    try std.testing.expectEqual(@as(u32, 19), weak_release_value);
}

test "phase3 atomic wrappers keep weak acq_rel compare-exchange reviewable" {
    var weak_acq_rel_value: u32 = 29;
    var attempts: usize = 0;
    while (true) {
        attempts += 1;
        if (compareExchangeWeak(u32, &weak_acq_rel_value, 29, 31, .acq_rel, .acquire) == null) break;
        try std.testing.expectEqual(@as(u32, 29), weak_acq_rel_value);
        try std.testing.expect(attempts < 16);
    }
    try std.testing.expectEqual(@as(u32, 31), weak_acq_rel_value);

    const weak_acq_rel_mismatch = compareExchangeWeak(
        u32,
        &weak_acq_rel_value,
        29,
        37,
        .acq_rel,
        .acquire,
    );
    try std.testing.expectEqual(@as(?u32, 31), weak_acq_rel_mismatch);
    try std.testing.expectEqual(@as(u32, 31), weak_acq_rel_value);
}

test "phase3 atomic wrappers keep non-seq-cst fetch orderings reviewable" {
    var signed_value: i32 = -4;
    try std.testing.expectEqual(@as(i32, -4), fetchAdd(i32, &signed_value, 6, .monotonic));
    try std.testing.expectEqual(@as(i32, 2), signed_value);
    try std.testing.expectEqual(@as(i32, 2), fetchSub(i32, &signed_value, 3, .release));
    try std.testing.expectEqual(@as(i32, -1), signed_value);
    try std.testing.expectEqual(@as(i32, -1), fetchMin(i32, &signed_value, -7, .acquire));
    try std.testing.expectEqual(@as(i32, -7), signed_value);
    try std.testing.expectEqual(@as(i32, -7), fetchMax(i32, &signed_value, 5, .acq_rel));
    try std.testing.expectEqual(@as(i32, 5), signed_value);

    var bitwise_value: u32 = 0b1010;
    try std.testing.expectEqual(@as(u32, 0b1010), fetchOr(u32, &bitwise_value, 0b0100, .release));
    try std.testing.expectEqual(@as(u32, 0b1110), bitwise_value);
    try std.testing.expectEqual(@as(u32, 0b1110), fetchAnd(u32, &bitwise_value, 0b0110, .acquire));
    try std.testing.expectEqual(@as(u32, 0b0110), bitwise_value);
    try std.testing.expectEqual(@as(u32, 0b0110), fetchXor(u32, &bitwise_value, 0b0011, .acq_rel));
    try std.testing.expectEqual(@as(u32, 0b0101), bitwise_value);

    var bitwise_nand_value: u32 = 0b1100;
    try std.testing.expectEqual(@as(u32, 0b1100), fetchNand(u32, &bitwise_nand_value, 0b1010, .release));
    try std.testing.expectEqual(@as(u32, 0xffff_fff7), bitwise_nand_value);
}

test "phase3 atomic wrappers keep fetch min-max no-op edges reviewable" {
    var unsigned_value: u32 = 12;
    try std.testing.expectEqual(@as(u32, 12), fetchMin(u32, &unsigned_value, 18, .monotonic));
    try std.testing.expectEqual(@as(u32, 12), unsigned_value);
    try std.testing.expectEqual(@as(u32, 12), fetchMax(u32, &unsigned_value, 4, .acq_rel));
    try std.testing.expectEqual(@as(u32, 12), unsigned_value);

    var signed_value: i32 = -3;
    try std.testing.expectEqual(@as(i32, -3), fetchMin(i32, &signed_value, 6, .acquire));
    try std.testing.expectEqual(@as(i32, -3), signed_value);
    try std.testing.expectEqual(@as(i32, -3), fetchMax(i32, &signed_value, -7, .release));
    try std.testing.expectEqual(@as(i32, -3), signed_value);
}
