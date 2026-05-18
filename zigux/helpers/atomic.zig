const std = @import("std");

pub const Ordering = std.builtin.AtomicOrder;
pub const CompareExchangeError = error{
    InvalidFailureOrdering,
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

pub fn compareExchangeFailureOrderAllowed(success: Ordering, failure: Ordering) bool {
    const failure_strength = failureStrength(failure) orelse return false;
    const success_strength = successStrength(success) orelse return false;
    return failure_strength <= success_strength;
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

pub fn compareExchangeStrong(
    comptime T: type,
    ptr: *T,
    expected_value: T,
    desired_value: T,
    comptime success: Ordering,
    comptime failure: Ordering,
) CompareExchangeError!?T {
    if (comptime !compareExchangeFailureOrderAllowed(success, failure)) {
        return error.InvalidFailureOrdering;
    }
    return @cmpxchgStrong(T, ptr, expected_value, desired_value, success, failure);
}

pub fn compareExchangeWeak(
    comptime T: type,
    ptr: *T,
    expected_value: T,
    desired_value: T,
    comptime success: Ordering,
    comptime failure: Ordering,
) CompareExchangeError!?T {
    if (comptime !compareExchangeFailureOrderAllowed(success, failure)) {
        return error.InvalidFailureOrdering;
    }
    return @cmpxchgWeak(T, ptr, expected_value, desired_value, success, failure);
}

pub fn fetchNand(
    comptime T: type,
    ptr: *T,
    operand: T,
    comptime order: Ordering,
) T {
    return @atomicRmw(T, ptr, .Nand, operand, order);
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

test "phase3 atomic helper reports allowed failure-order bounds" {
    try std.testing.expectEqual(@as(?Ordering, .monotonic), weakestAllowedFailureOrder(.monotonic));
    try std.testing.expectEqual(@as(?Ordering, .monotonic), strongestAllowedFailureOrder(.monotonic));
    try std.testing.expectEqual(@as(?Ordering, .monotonic), strongestAllowedFailureOrder(.release));
    try std.testing.expectEqual(@as(?Ordering, .acquire), strongestAllowedFailureOrder(.acquire));
    try std.testing.expectEqual(@as(?Ordering, .acquire), strongestAllowedFailureOrder(.acq_rel));
    try std.testing.expectEqual(@as(?Ordering, .seq_cst), strongestAllowedFailureOrder(.seq_cst));
    try std.testing.expectEqual(@as(?Ordering, null), strongestAllowedFailureOrder(.unordered));
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

test "phase3 atomic helper keeps fetch-nand updates explicit" {
    var value: u8 = 0b1111_0000;

    try std.testing.expectEqual(@as(u8, 0b1111_0000), fetchNand(u8, &value, 0b1100_1100, .seq_cst));
    try std.testing.expectEqual(@as(u8, 0b0011_1111), value);

    try std.testing.expectEqual(@as(u8, 0b0011_1111), fetchNand(u8, &value, 0b0000_1111, .monotonic));
    try std.testing.expectEqual(@as(u8, 0b1111_0000), value);
}
