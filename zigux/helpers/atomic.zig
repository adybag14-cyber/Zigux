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

    try std.testing.expectEqual(
        @as(?u32, null),
        compareExchange(u32, &value, 12, 15, .seq_cst, .seq_cst),
    );
    try std.testing.expectEqual(@as(u32, 15), value);

    const mismatch = compareExchange(u32, &value, 9, 19, .seq_cst, .seq_cst);
    try std.testing.expectEqual(@as(?u32, 15), mismatch);
    try std.testing.expectEqual(@as(u32, 15), value);
}
