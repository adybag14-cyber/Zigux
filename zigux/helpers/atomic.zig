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

    try std.testing.expectEqual(@as(u32, 13), fetchMin(u32, &value, 11, .seq_cst));
    try std.testing.expectEqual(@as(u32, 11), value);

    try std.testing.expectEqual(@as(u32, 11), fetchMax(u32, &value, 17, .seq_cst));
    try std.testing.expectEqual(@as(u32, 17), value);

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
