const std = @import("std");

fn ensureLoadOrder(comptime order: std.builtin.AtomicOrder) void {
    switch (order) {
        .unordered, .monotonic, .acquire, .seq_cst => {},
        .release, .acq_rel => @compileError("atomic load only accepts unordered, monotonic, acquire, or seq_cst ordering"),
    }
}

fn ensureStoreOrder(comptime order: std.builtin.AtomicOrder) void {
    switch (order) {
        .unordered, .monotonic, .release, .seq_cst => {},
        .acquire, .acq_rel => @compileError("atomic store only accepts unordered, monotonic, release, or seq_cst ordering"),
    }
}

fn ensureCompareExchangeSuccessOrder(comptime order: std.builtin.AtomicOrder) void {
    switch (order) {
        .monotonic, .acquire, .release, .acq_rel, .seq_cst => {},
        .unordered => @compileError("compareExchange success ordering must be monotonic or stricter"),
    }
}

fn ensureCompareExchangeFailureOrder(comptime order: std.builtin.AtomicOrder) void {
    switch (order) {
        .unordered, .monotonic, .acquire, .seq_cst => {},
        .release, .acq_rel => @compileError("compareExchange failure ordering only accepts unordered, monotonic, acquire, or seq_cst"),
    }
}

pub fn load(comptime T: type, ptr: *const T, comptime order: std.builtin.AtomicOrder) T {
    ensureLoadOrder(order);
    return @atomicLoad(T, ptr, order);
}

pub fn store(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) void {
    ensureStoreOrder(order);
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
    ensureCompareExchangeSuccessOrder(success_order);
    ensureCompareExchangeFailureOrder(failure_order);
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
    ensureCompareExchangeSuccessOrder(success_order);
    ensureCompareExchangeFailureOrder(failure_order);
    return @cmpxchgWeak(T, ptr, expected_value, new_value, success_order, failure_order);
}

test "phase3 atomic wrappers behave predictably" {
    var value: u32 = 1;
    try std.testing.expectEqual(@as(u32, 1), load(u32, &value, .seq_cst));
    store(u32, &value, 7, .seq_cst);
    try std.testing.expectEqual(@as(u32, 7), value);
    try std.testing.expectEqual(@as(u32, 7), exchange(u32, &value, 9, .seq_cst));
    try std.testing.expectEqual(@as(u32, 9), value);
    try std.testing.expectEqual(@as(u32, 9), fetchAdd(u32, &value, 4, .seq_cst));
    try std.testing.expectEqual(@as(u32, 13), value);
    try std.testing.expectEqual(@as(u32, 13), fetchSub(u32, &value, 2, .seq_cst));
    try std.testing.expectEqual(@as(u32, 11), value);
    try std.testing.expectEqual(@as(u32, 11), fetchOr(u32, &value, 0b1000, .seq_cst));
    try std.testing.expectEqual(@as(u32, 11), value);
    try std.testing.expectEqual(@as(u32, 11), fetchAnd(u32, &value, 0b0111, .seq_cst));
    try std.testing.expectEqual(@as(u32, 3), value);
    try std.testing.expectEqual(@as(u32, 3), fetchXor(u32, &value, 0b1111, .seq_cst));
    try std.testing.expectEqual(@as(u32, 12), value);

    try std.testing.expectEqual(@as(?u32, null), compareExchange(u32, &value, 12, 15, .seq_cst, .seq_cst));
    try std.testing.expectEqual(@as(u32, 15), value);

    const mismatch = compareExchange(u32, &value, 9, 19, .seq_cst, .seq_cst);
    try std.testing.expectEqual(@as(?u32, 15), mismatch);
    try std.testing.expectEqual(@as(u32, 15), value);

    try std.testing.expectEqual(@as(?u32, null), compareExchangeWeak(u32, &value, 15, 23, .seq_cst, .seq_cst));
    try std.testing.expectEqual(@as(u32, 23), value);

    const weak_mismatch = compareExchangeWeak(u32, &value, 15, 27, .seq_cst, .seq_cst);
    try std.testing.expectEqual(@as(?u32, 23), weak_mismatch);
    try std.testing.expectEqual(@as(u32, 23), value);

    try std.testing.expectEqual(@as(u32, 23), fetchMax(u32, &value, 31, .seq_cst));
    try std.testing.expectEqual(@as(u32, 31), value);
    try std.testing.expectEqual(@as(u32, 31), fetchMax(u32, &value, 29, .seq_cst));
    try std.testing.expectEqual(@as(u32, 31), value);
    try std.testing.expectEqual(@as(u32, 31), fetchMin(u32, &value, 17, .seq_cst));
    try std.testing.expectEqual(@as(u32, 17), value);
    try std.testing.expectEqual(@as(u32, 17), fetchMin(u32, &value, 19, .seq_cst));
    try std.testing.expectEqual(@as(u32, 17), value);
}

test "phase3 atomic wrappers accept valid non-seq-cst orderings" {
    var value: u32 = 0;
    store(u32, &value, 9, .release);
    try std.testing.expectEqual(@as(u32, 9), load(u32, &value, .acquire));

    var cmp: u32 = 3;
    try std.testing.expectEqual(@as(?u32, null), compareExchange(u32, &cmp, 3, 5, .acq_rel, .acquire));
    try std.testing.expectEqual(@as(u32, 5), cmp);

    var monotonic_cmp: u32 = 5;
    try std.testing.expectEqual(@as(?u32, null), compareExchange(u32, &monotonic_cmp, 5, 7, .monotonic, .monotonic));
    try std.testing.expectEqual(@as(u32, 7), monotonic_cmp);

    var weak_cmp: u32 = 7;
    while (compareExchangeWeak(u32, &weak_cmp, 7, 11, .release, .monotonic)) |_| {
        try std.testing.expectEqual(@as(u32, 7), weak_cmp);
    }
    try std.testing.expectEqual(@as(u32, 11), weak_cmp);
}
