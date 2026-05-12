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

fn requireUnsignedInt(comptime T: type) void {
    const info = @typeInfo(T);
    if (info != .int or info.int.signedness != .unsigned) {
        @compileError("phase3 atomic bit wrappers require an unsigned integer type");
    }
}

fn bitMask(comptime T: type, bit_index: u16) T {
    requireUnsignedInt(T);
    std.debug.assert(bit_index < @bitSizeOf(T));
    const shift: std.math.Log2Int(T) = @intCast(bit_index);
    return @as(T, 1) << shift;
}

pub fn bitSet(comptime T: type, ptr: *T, bit_index: u16, comptime order: std.builtin.AtomicOrder) u1 {
    const mask = bitMask(T, bit_index);
    const previous = @atomicRmw(T, ptr, .Or, mask, order);
    return @intFromBool((previous & mask) != 0);
}

pub fn bitReset(comptime T: type, ptr: *T, bit_index: u16, comptime order: std.builtin.AtomicOrder) u1 {
    const mask = bitMask(T, bit_index);
    const previous = @atomicRmw(T, ptr, .And, ~mask, order);
    return @intFromBool((previous & mask) != 0);
}

pub fn bitToggle(comptime T: type, ptr: *T, bit_index: u16, comptime order: std.builtin.AtomicOrder) u1 {
    const mask = bitMask(T, bit_index);
    const previous = @atomicRmw(T, ptr, .Xor, mask, order);
    return @intFromBool((previous & mask) != 0);
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

    try std.testing.expectEqual(@as(u32, 13), fetchNand(u32, &value, 10, .seq_cst));
    try std.testing.expectEqual(@as(u32, 0xffff_fff7), value);

    value = 13;
    try std.testing.expectEqual(@as(u32, 13), fetchMin(u32, &value, 11, .seq_cst));
    try std.testing.expectEqual(@as(u32, 11), value);

    try std.testing.expectEqual(@as(u32, 11), fetchMax(u32, &value, 17, .seq_cst));
    try std.testing.expectEqual(@as(u32, 17), value);

    var signed_value: i32 = 4;
    try std.testing.expectEqual(@as(i32, 4), fetchMin(i32, &signed_value, -3, .seq_cst));
    try std.testing.expectEqual(@as(i32, -3), signed_value);
    try std.testing.expectEqual(@as(i32, -3), fetchMax(i32, &signed_value, 6, .seq_cst));
    try std.testing.expectEqual(@as(i32, 6), signed_value);

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

    var monotonic_nand_value: u32 = 0x0000_00ff;
    try std.testing.expectEqual(@as(u32, 0x0000_00ff), fetchNand(u32, &monotonic_nand_value, 0x0000_0f0f, .monotonic));
    try std.testing.expectEqual(@as(u32, 0xffff_fff0), monotonic_nand_value);

    var ordered_bits_value: u32 = 0b1011_0101;
    try std.testing.expectEqual(@as(u32, 0b1011_0101), fetchAnd(u32, &ordered_bits_value, 0b1111_0000, .monotonic));
    try std.testing.expectEqual(@as(u32, 0b1011_0000), ordered_bits_value);
    try std.testing.expectEqual(@as(u32, 0b1011_0000), fetchOr(u32, &ordered_bits_value, 0b0000_1100, .release));
    try std.testing.expectEqual(@as(u32, 0b1011_1100), ordered_bits_value);
    try std.testing.expectEqual(@as(u32, 0b1011_1100), fetchXor(u32, &ordered_bits_value, 0b0011_0011, .acq_rel));
    try std.testing.expectEqual(@as(u32, 0b1000_1111), ordered_bits_value);

    var acq_rel_value: u32 = 7;
    try std.testing.expectEqual(@as(?u32, null), compareExchange(u32, &acq_rel_value, 7, 11, .acq_rel, .acquire));
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

test "phase3 atomic wrappers keep bit wrappers reviewable" {
    var flags: u8 = 0b0001_0100;

    try std.testing.expectEqual(@as(u1, 0), bitSet(u8, &flags, 1, .monotonic));
    try std.testing.expectEqual(@as(u8, 0b0001_0110), flags);
    try std.testing.expectEqual(@as(u1, 1), bitSet(u8, &flags, 2, .release));
    try std.testing.expectEqual(@as(u8, 0b0001_0110), flags);

    try std.testing.expectEqual(@as(u1, 1), bitReset(u8, &flags, 4, .acquire));
    try std.testing.expectEqual(@as(u8, 0b0000_0110), flags);
    try std.testing.expectEqual(@as(u1, 0), bitReset(u8, &flags, 7, .monotonic));
    try std.testing.expectEqual(@as(u8, 0b0000_0110), flags);

    try std.testing.expectEqual(@as(u1, 1), bitToggle(u8, &flags, 2, .acq_rel));
    try std.testing.expectEqual(@as(u8, 0b0000_0010), flags);
    try std.testing.expectEqual(@as(u1, 0), bitToggle(u8, &flags, 0, .seq_cst));
    try std.testing.expectEqual(@as(u8, 0b0000_0011), flags);
}
