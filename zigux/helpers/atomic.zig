const std = @import("std");

pub const Ordering = std.builtin.AtomicOrder;
pub const CompareExchangeError = error{
    InvalidFailureOrdering,
};
pub const LoadError = error{
    InvalidLoadOrdering,
};
pub const StoreError = error{
    InvalidStoreOrdering,
};
pub const RmwError = error{
    InvalidRmwOrdering,
};

fn failureStrength(order: Ordering) ?u8 {
    return switch (order) {
        .monotonic => 0,
        .acquire => 1,
        .seq_cst => 2,
        .unordered, .release, .acq_rel => null,
    };
}

fn successStrength(order: Ordering) ?u8 {
    return switch (order) {
        .monotonic, .release => 0,
        .acquire, .acq_rel => 1,
        .seq_cst => 2,
        .unordered => null,
    };
}

pub fn compareExchangeSuccessOrderAllowed(order: Ordering) bool {
    return switch (order) {
        .monotonic, .acquire, .release, .acq_rel, .seq_cst => true,
        .unordered => false,
    };
}

pub fn compareExchangeFailureOrderAllowed(success: Ordering, failure: Ordering) bool {
    if (!compareExchangeSuccessOrderAllowed(success)) return false;
    const failure_strength = failureStrength(failure) orelse return false;
    const success_strength = successStrength(success) orelse return false;
    return failure_strength <= success_strength;
}

pub fn validateCompareExchangeOrders(
    comptime success: Ordering,
    comptime failure: Ordering,
) CompareExchangeError!void {
    if (comptime !compareExchangeFailureOrderAllowed(success, failure)) {
        return error.InvalidFailureOrdering;
    }
}

pub fn strongestAllowedFailureOrder(success: Ordering) ?Ordering {
    return switch (success) {
        .monotonic, .release => .monotonic,
        .acquire, .acq_rel => .acquire,
        .seq_cst => .seq_cst,
        .unordered => null,
    };
}

pub fn weakestAllowedFailureOrder(success: Ordering) ?Ordering {
    return switch (success) {
        .monotonic, .release, .acquire, .acq_rel, .seq_cst => .monotonic,
        .unordered => null,
    };
}

pub fn loadOrderAllowed(order: Ordering) bool {
    return switch (order) {
        .monotonic, .acquire, .seq_cst => true,
        .unordered, .release, .acq_rel => false,
    };
}

pub fn validateLoadOrder(comptime order: Ordering) LoadError!void {
    if (comptime !loadOrderAllowed(order)) {
        return error.InvalidLoadOrdering;
    }
}

pub fn storeOrderAllowed(order: Ordering) bool {
    return switch (order) {
        .monotonic, .release, .seq_cst => true,
        .unordered, .acquire, .acq_rel => false,
    };
}

pub fn validateStoreOrder(comptime order: Ordering) StoreError!void {
    if (comptime !storeOrderAllowed(order)) {
        return error.InvalidStoreOrdering;
    }
}

pub fn rmwOrderAllowed(order: Ordering) bool {
    return switch (order) {
        .monotonic, .acquire, .release, .acq_rel, .seq_cst => true,
        .unordered => false,
    };
}

pub fn validateRmwOrder(comptime order: Ordering) RmwError!void {
    if (comptime !rmwOrderAllowed(order)) {
        return error.InvalidRmwOrdering;
    }
}

pub fn load(comptime T: type, ptr: *const T, comptime order: Ordering) LoadError!T {
    if (comptime loadOrderAllowed(order)) {
        try validateLoadOrder(order);
        return @atomicLoad(T, ptr, order);
    }
    return error.InvalidLoadOrdering;
}

pub fn store(comptime T: type, ptr: *T, value: T, comptime order: Ordering) StoreError!void {
    if (comptime storeOrderAllowed(order)) {
        try validateStoreOrder(order);
        @atomicStore(T, ptr, value, order);
        return;
    }
    return error.InvalidStoreOrdering;
}

pub fn exchange(
    comptime T: type,
    ptr: *T,
    value: T,
    comptime order: Ordering,
) RmwError!T {
    if (comptime rmwOrderAllowed(order)) {
        try validateRmwOrder(order);
        return @atomicRmw(T, ptr, .Xchg, value, order);
    }
    return error.InvalidRmwOrdering;
}

pub fn compareExchangeStrong(
    comptime T: type,
    ptr: *T,
    expected_value: T,
    desired_value: T,
    comptime success: Ordering,
    comptime failure: Ordering,
) CompareExchangeError!?T {
    if (comptime compareExchangeFailureOrderAllowed(success, failure)) {
        return @cmpxchgStrong(T, ptr, expected_value, desired_value, success, failure);
    }
    return error.InvalidFailureOrdering;
}

pub fn compareExchangeWeak(
    comptime T: type,
    ptr: *T,
    expected_value: T,
    desired_value: T,
    comptime success: Ordering,
    comptime failure: Ordering,
) CompareExchangeError!?T {
    if (comptime compareExchangeFailureOrderAllowed(success, failure)) {
        return @cmpxchgWeak(T, ptr, expected_value, desired_value, success, failure);
    }
    return error.InvalidFailureOrdering;
}

pub fn fetchAdd(
    comptime T: type,
    ptr: *T,
    operand: T,
    comptime order: Ordering,
) RmwError!T {
    if (comptime rmwOrderAllowed(order)) {
        try validateRmwOrder(order);
        return @atomicRmw(T, ptr, .Add, operand, order);
    }
    return error.InvalidRmwOrdering;
}

pub fn fetchSub(
    comptime T: type,
    ptr: *T,
    operand: T,
    comptime order: Ordering,
) RmwError!T {
    if (comptime rmwOrderAllowed(order)) {
        try validateRmwOrder(order);
        return @atomicRmw(T, ptr, .Sub, operand, order);
    }
    return error.InvalidRmwOrdering;
}

pub fn fetchNand(
    comptime T: type,
    ptr: *T,
    operand: T,
    comptime order: Ordering,
) RmwError!T {
    if (comptime rmwOrderAllowed(order)) {
        try validateRmwOrder(order);
        return @atomicRmw(T, ptr, .Nand, operand, order);
    }
    return error.InvalidRmwOrdering;
}

pub fn fetchOr(
    comptime T: type,
    ptr: *T,
    operand: T,
    comptime order: Ordering,
) RmwError!T {
    if (comptime rmwOrderAllowed(order)) {
        try validateRmwOrder(order);
        return @atomicRmw(T, ptr, .Or, operand, order);
    }
    return error.InvalidRmwOrdering;
}

pub fn fetchAnd(
    comptime T: type,
    ptr: *T,
    operand: T,
    comptime order: Ordering,
) RmwError!T {
    if (comptime rmwOrderAllowed(order)) {
        try validateRmwOrder(order);
        return @atomicRmw(T, ptr, .And, operand, order);
    }
    return error.InvalidRmwOrdering;
}

pub fn fetchXor(
    comptime T: type,
    ptr: *T,
    operand: T,
    comptime order: Ordering,
) RmwError!T {
    if (comptime rmwOrderAllowed(order)) {
        try validateRmwOrder(order);
        return @atomicRmw(T, ptr, .Xor, operand, order);
    }
    return error.InvalidRmwOrdering;
}

pub fn fetchMin(
    comptime T: type,
    ptr: *T,
    operand: T,
    comptime order: Ordering,
) RmwError!T {
    if (comptime rmwOrderAllowed(order)) {
        try validateRmwOrder(order);
        return @atomicRmw(T, ptr, .Min, operand, order);
    }
    return error.InvalidRmwOrdering;
}

pub fn fetchMax(
    comptime T: type,
    ptr: *T,
    operand: T,
    comptime order: Ordering,
) RmwError!T {
    if (comptime rmwOrderAllowed(order)) {
        try validateRmwOrder(order);
        return @atomicRmw(T, ptr, .Max, operand, order);
    }
    return error.InvalidRmwOrdering;
}

test "phase3 atomic helper keeps compare-exchange success ordering rules explicit" {
    try std.testing.expect(compareExchangeSuccessOrderAllowed(.monotonic));
    try std.testing.expect(compareExchangeSuccessOrderAllowed(.acquire));
    try std.testing.expect(compareExchangeSuccessOrderAllowed(.release));
    try std.testing.expect(compareExchangeSuccessOrderAllowed(.acq_rel));
    try std.testing.expect(compareExchangeSuccessOrderAllowed(.seq_cst));
    try std.testing.expect(!compareExchangeSuccessOrderAllowed(.unordered));
}

test "phase3 atomic helper keeps compare-exchange ordering rules explicit" {
    try std.testing.expect(compareExchangeFailureOrderAllowed(.monotonic, .monotonic));
    try std.testing.expect(compareExchangeFailureOrderAllowed(.release, .monotonic));
    try std.testing.expect(compareExchangeFailureOrderAllowed(.acquire, .monotonic));
    try std.testing.expect(compareExchangeFailureOrderAllowed(.acquire, .acquire));
    try std.testing.expect(compareExchangeFailureOrderAllowed(.acq_rel, .acquire));
    try std.testing.expect(compareExchangeFailureOrderAllowed(.seq_cst, .seq_cst));

    try std.testing.expect(!compareExchangeFailureOrderAllowed(.monotonic, .acquire));
    try std.testing.expect(!compareExchangeFailureOrderAllowed(.release, .acquire));
    try std.testing.expect(!compareExchangeFailureOrderAllowed(.acq_rel, .seq_cst));
    try std.testing.expect(!compareExchangeFailureOrderAllowed(.seq_cst, .release));
    try std.testing.expect(!compareExchangeFailureOrderAllowed(.seq_cst, .acq_rel));
    try std.testing.expect(!compareExchangeFailureOrderAllowed(.unordered, .monotonic));
}

test "phase3 atomic helper exposes reusable compare-exchange order validation" {
    try validateCompareExchangeOrders(.monotonic, .monotonic);
    try validateCompareExchangeOrders(.release, .monotonic);
    try validateCompareExchangeOrders(.acquire, .acquire);
    try validateCompareExchangeOrders(.seq_cst, .seq_cst);

    try std.testing.expectError(error.InvalidFailureOrdering, validateCompareExchangeOrders(.monotonic, .acquire));
    try std.testing.expectError(error.InvalidFailureOrdering, validateCompareExchangeOrders(.release, .acquire));
    try std.testing.expectError(error.InvalidFailureOrdering, validateCompareExchangeOrders(.acq_rel, .seq_cst));
    try std.testing.expectError(error.InvalidFailureOrdering, validateCompareExchangeOrders(.seq_cst, .release));
    try std.testing.expectError(error.InvalidFailureOrdering, validateCompareExchangeOrders(.unordered, .monotonic));
}

test "phase3 atomic helper reports allowed failure-order bounds" {
    try std.testing.expectEqual(@as(?Ordering, .monotonic), weakestAllowedFailureOrder(.monotonic));
    try std.testing.expectEqual(@as(?Ordering, .monotonic), strongestAllowedFailureOrder(.monotonic));
    try std.testing.expectEqual(@as(?Ordering, .monotonic), weakestAllowedFailureOrder(.release));
    try std.testing.expectEqual(@as(?Ordering, .monotonic), strongestAllowedFailureOrder(.release));
    try std.testing.expectEqual(@as(?Ordering, .monotonic), weakestAllowedFailureOrder(.acquire));
    try std.testing.expectEqual(@as(?Ordering, .acquire), strongestAllowedFailureOrder(.acquire));
    try std.testing.expectEqual(@as(?Ordering, .monotonic), weakestAllowedFailureOrder(.acq_rel));
    try std.testing.expectEqual(@as(?Ordering, .acquire), strongestAllowedFailureOrder(.acq_rel));
    try std.testing.expectEqual(@as(?Ordering, .monotonic), weakestAllowedFailureOrder(.seq_cst));
    try std.testing.expectEqual(@as(?Ordering, .seq_cst), strongestAllowedFailureOrder(.seq_cst));
    try std.testing.expectEqual(@as(?Ordering, null), weakestAllowedFailureOrder(.unordered));
    try std.testing.expectEqual(@as(?Ordering, null), strongestAllowedFailureOrder(.unordered));
}

test "phase3 atomic helper keeps release and acq-rel compare-exchange handoffs explicit" {
    var release_value: u32 = 0x10;
    try std.testing.expectEqual(
        @as(?u32, null),
        try compareExchangeStrong(u32, &release_value, 0x10, 0x20, .release, .monotonic),
    );
    try std.testing.expectEqual(@as(u32, 0x20), release_value);
    try std.testing.expectEqual(
        @as(?u32, 0x20),
        try compareExchangeWeak(u32, &release_value, 0x10, 0x30, .release, .monotonic),
    );
    try std.testing.expectEqual(@as(u32, 0x20), release_value);

    var acq_rel_value: u32 = 0x44;
    try std.testing.expectEqual(
        @as(?u32, null),
        try compareExchangeWeak(u32, &acq_rel_value, 0x44, 0x55, .acq_rel, .acquire),
    );
    try std.testing.expectEqual(@as(u32, 0x55), acq_rel_value);
    try std.testing.expectEqual(
        @as(?u32, 0x55),
        try compareExchangeStrong(u32, &acq_rel_value, 0x44, 0x66, .acq_rel, .acquire),
    );
    try std.testing.expectEqual(@as(u32, 0x55), acq_rel_value);

    var denied_value: u32 = 0xAA;
    try std.testing.expectError(
        error.InvalidFailureOrdering,
        compareExchangeStrong(u32, &denied_value, 0xAA, 0xBB, .release, .acquire),
    );
    try std.testing.expectError(
        error.InvalidFailureOrdering,
        compareExchangeWeak(u32, &denied_value, 0xAA, 0xCC, .acq_rel, .seq_cst),
    );
    try std.testing.expectEqual(@as(u32, 0xAA), denied_value);
}

test "phase3 atomic helper keeps load ordering rules explicit" {
    try std.testing.expect(loadOrderAllowed(.monotonic));
    try std.testing.expect(loadOrderAllowed(.acquire));
    try std.testing.expect(loadOrderAllowed(.seq_cst));

    try std.testing.expect(!loadOrderAllowed(.unordered));
    try std.testing.expect(!loadOrderAllowed(.release));
    try std.testing.expect(!loadOrderAllowed(.acq_rel));
}

test "phase3 atomic helper exposes reusable load order validation" {
    try validateLoadOrder(.monotonic);
    try validateLoadOrder(.acquire);
    try validateLoadOrder(.seq_cst);

    try std.testing.expectError(error.InvalidLoadOrdering, validateLoadOrder(.unordered));
    try std.testing.expectError(error.InvalidLoadOrdering, validateLoadOrder(.release));
    try std.testing.expectError(error.InvalidLoadOrdering, validateLoadOrder(.acq_rel));
}

test "phase3 atomic helper keeps store ordering rules explicit" {
    try std.testing.expect(storeOrderAllowed(.monotonic));
    try std.testing.expect(storeOrderAllowed(.release));
    try std.testing.expect(storeOrderAllowed(.seq_cst));

    try std.testing.expect(!storeOrderAllowed(.unordered));
    try std.testing.expect(!storeOrderAllowed(.acquire));
    try std.testing.expect(!storeOrderAllowed(.acq_rel));
}

test "phase3 atomic helper exposes reusable store order validation" {
    try validateStoreOrder(.monotonic);
    try validateStoreOrder(.release);
    try validateStoreOrder(.seq_cst);

    try std.testing.expectError(error.InvalidStoreOrdering, validateStoreOrder(.unordered));
    try std.testing.expectError(error.InvalidStoreOrdering, validateStoreOrder(.acquire));
    try std.testing.expectError(error.InvalidStoreOrdering, validateStoreOrder(.acq_rel));
}

test "phase3 atomic helper keeps RMW ordering rules explicit" {
    try std.testing.expect(rmwOrderAllowed(.monotonic));
    try std.testing.expect(rmwOrderAllowed(.acquire));
    try std.testing.expect(rmwOrderAllowed(.release));
    try std.testing.expect(rmwOrderAllowed(.acq_rel));
    try std.testing.expect(rmwOrderAllowed(.seq_cst));

    try std.testing.expect(!rmwOrderAllowed(.unordered));
}

test "phase3 atomic helper exposes reusable RMW order validation" {
    try validateRmwOrder(.monotonic);
    try validateRmwOrder(.acquire);
    try validateRmwOrder(.release);
    try validateRmwOrder(.acq_rel);
    try validateRmwOrder(.seq_cst);

    try std.testing.expectError(error.InvalidRmwOrdering, validateRmwOrder(.unordered));
}

test "phase3 atomic helper wraps atomic loads without widening ordering semantics" {
    var value: u32 = 0x1234_5678;

    try std.testing.expectEqual(@as(u32, 0x1234_5678), try load(u32, &value, .monotonic));
    value = 0xCAFE_BABE;
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), try load(u32, &value, .seq_cst));

    try std.testing.expectError(error.InvalidLoadOrdering, load(u32, &value, .release));
    try std.testing.expectError(error.InvalidLoadOrdering, load(u32, &value, .acq_rel));
}

test "phase3 atomic helper wraps atomic stores without widening ordering semantics" {
    var value: u32 = 1;

    try store(u32, &value, 7, .monotonic);
    try std.testing.expectEqual(@as(u32, 7), value);

    try store(u32, &value, 19, .release);
    try std.testing.expectEqual(@as(u32, 19), value);

    try store(u32, &value, 23, .seq_cst);
    try std.testing.expectEqual(@as(u32, 23), value);

    try std.testing.expectError(error.InvalidStoreOrdering, store(u32, &value, 29, .unordered));
    try std.testing.expectError(error.InvalidStoreOrdering, store(u32, &value, 31, .acquire));
    try std.testing.expectError(error.InvalidStoreOrdering, store(u32, &value, 37, .acq_rel));
    try std.testing.expectEqual(@as(u32, 23), value);
}

test "phase3 atomic helper keeps exchange ordering explicit" {
    var value: u32 = 1;

    try std.testing.expectEqual(@as(u32, 1), try exchange(u32, &value, 7, .release));
    try std.testing.expectEqual(@as(u32, 7), value);

    try std.testing.expectEqual(@as(u32, 7), try exchange(u32, &value, 19, .acq_rel));
    try std.testing.expectEqual(@as(u32, 19), value);

    try std.testing.expectEqual(@as(u32, 19), try exchange(u32, &value, 23, .seq_cst));
    try std.testing.expectEqual(@as(u32, 23), value);
    try std.testing.expectError(error.InvalidRmwOrdering, exchange(u32, &value, 29, .unordered));
    try std.testing.expectEqual(@as(u32, 23), value);
}

test "phase3 atomic helper wraps compare-exchange without widening failure semantics" {
    var value: u32 = 1;

    try std.testing.expectEqual(@as(?u32, null), try compareExchangeStrong(u32, &value, 1, 2, .acq_rel, .acquire));
    try std.testing.expectEqual(@as(u32, 2), value);

    try std.testing.expectEqual(@as(?u32, 2), try compareExchangeStrong(u32, &value, 1, 4, .seq_cst, .acquire));
    try std.testing.expectEqual(@as(u32, 2), value);

    try std.testing.expectError(
        error.InvalidFailureOrdering,
        compareExchangeStrong(u32, &value, 2, 5, .release, .acquire),
    );
    try std.testing.expectError(
        error.InvalidFailureOrdering,
        compareExchangeWeak(u32, &value, 2, 5, .seq_cst, .release),
    );
    try std.testing.expectEqual(@as(u32, 2), value);
}

test "phase3 atomic helper keeps weak compare-exchange mismatch returns explicit" {
    var value: u32 = 9;

    try std.testing.expectEqual(@as(?u32, 9), try compareExchangeWeak(u32, &value, 7, 11, .acq_rel, .acquire));
    try std.testing.expectEqual(@as(u32, 9), value);

    try std.testing.expectEqual(@as(?u32, null), try compareExchangeWeak(u32, &value, 9, 11, .release, .monotonic));
    try std.testing.expectEqual(@as(u32, 11), value);
}

test "phase3 atomic helper keeps fetch-add updates explicit" {
    var value: u16 = 12;

    try std.testing.expectEqual(@as(u16, 12), try fetchAdd(u16, &value, 5, .monotonic));
    try std.testing.expectEqual(@as(u16, 17), value);

    try std.testing.expectEqual(@as(u16, 17), try fetchAdd(u16, &value, 8, .acq_rel));
    try std.testing.expectEqual(@as(u16, 25), value);

    try std.testing.expectError(error.InvalidRmwOrdering, fetchAdd(u16, &value, 3, .unordered));
    try std.testing.expectEqual(@as(u16, 25), value);
}

test "phase3 atomic helper keeps fetch-sub updates explicit" {
    var value: u16 = 40;

    try std.testing.expectEqual(@as(u16, 40), try fetchSub(u16, &value, 5, .release));
    try std.testing.expectEqual(@as(u16, 35), value);

    try std.testing.expectEqual(@as(u16, 35), try fetchSub(u16, &value, 11, .acq_rel));
    try std.testing.expectEqual(@as(u16, 24), value);

    try std.testing.expectError(error.InvalidRmwOrdering, fetchSub(u16, &value, 1, .unordered));
    try std.testing.expectEqual(@as(u16, 24), value);
}

test "phase3 atomic helper keeps fetch-nand updates explicit" {
    var value: u8 = 0b1111_0000;

    try std.testing.expectEqual(@as(u8, 0b1111_0000), try fetchNand(u8, &value, 0b1100_1100, .seq_cst));
    try std.testing.expectEqual(@as(u8, 0b0011_1111), value);

    try std.testing.expectEqual(@as(u8, 0b0011_1111), try fetchNand(u8, &value, 0b0000_1111, .monotonic));
    try std.testing.expectEqual(@as(u8, 0b1111_0000), value);
    try std.testing.expectError(error.InvalidRmwOrdering, fetchNand(u8, &value, 0b1111_1111, .unordered));
    try std.testing.expectEqual(@as(u8, 0b1111_0000), value);
}

test "phase3 atomic helper keeps fetch-or bit publication explicit" {
    var value: u16 = 0x0104;

    try std.testing.expectEqual(@as(u16, 0x0104), try fetchOr(u16, &value, 0x0018, .release));
    try std.testing.expectEqual(@as(u16, 0x011C), value);

    try std.testing.expectEqual(@as(u16, 0x011C), try fetchOr(u16, &value, 0x8000, .monotonic));
    try std.testing.expectEqual(@as(u16, 0x811C), value);

    try std.testing.expectError(error.InvalidRmwOrdering, fetchOr(u16, &value, 0x0001, .unordered));
    try std.testing.expectEqual(@as(u16, 0x811C), value);
}

test "phase3 atomic helper keeps fetch-and bit clearing explicit" {
    var value: u16 = 0xFF3C;

    try std.testing.expectEqual(@as(u16, 0xFF3C), try fetchAnd(u16, &value, 0x0F3F, .acquire));
    try std.testing.expectEqual(@as(u16, 0x0F3C), value);

    try std.testing.expectEqual(@as(u16, 0x0F3C), try fetchAnd(u16, &value, 0x00FF, .seq_cst));
    try std.testing.expectEqual(@as(u16, 0x003C), value);

    try std.testing.expectError(error.InvalidRmwOrdering, fetchAnd(u16, &value, 0x000F, .unordered));
    try std.testing.expectEqual(@as(u16, 0x003C), value);
}

test "phase3 atomic helper keeps fetch-xor bit toggles explicit" {
    var value: u16 = 0x0F3C;

    try std.testing.expectEqual(@as(u16, 0x0F3C), try fetchXor(u16, &value, 0x00FF, .release));
    try std.testing.expectEqual(@as(u16, 0x0FC3), value);

    try std.testing.expectEqual(@as(u16, 0x0FC3), try fetchXor(u16, &value, 0x0F00, .acq_rel));
    try std.testing.expectEqual(@as(u16, 0x00C3), value);

    try std.testing.expectError(error.InvalidRmwOrdering, fetchXor(u16, &value, 0x000F, .unordered));
    try std.testing.expectEqual(@as(u16, 0x00C3), value);
}

test "phase3 atomic helper keeps fetch-min floor updates explicit" {
    var value: i16 = 14;

    try std.testing.expectEqual(@as(i16, 14), try fetchMin(i16, &value, 9, .release));
    try std.testing.expectEqual(@as(i16, 9), value);

    try std.testing.expectEqual(@as(i16, 9), try fetchMin(i16, &value, 11, .acquire));
    try std.testing.expectEqual(@as(i16, 9), value);

    try std.testing.expectError(error.InvalidRmwOrdering, fetchMin(i16, &value, 3, .unordered));
    try std.testing.expectEqual(@as(i16, 9), value);
}

test "phase3 atomic helper keeps fetch-max ceiling updates explicit" {
    var value: i16 = -4;

    try std.testing.expectEqual(@as(i16, -4), try fetchMax(i16, &value, 7, .release));
    try std.testing.expectEqual(@as(i16, 7), value);

    try std.testing.expectEqual(@as(i16, 7), try fetchMax(i16, &value, 3, .acquire));
    try std.testing.expectEqual(@as(i16, 7), value);

    try std.testing.expectError(error.InvalidRmwOrdering, fetchMax(i16, &value, 9, .unordered));
    try std.testing.expectEqual(@as(i16, 7), value);
}
