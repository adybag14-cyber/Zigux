const std = @import("std");
const testing = std.testing;

const atomic = @import("atomic");

test "atomic starter packet keeps compare-exchange routes reviewable" {
    try testing.expect(atomic.compareExchangeFailureOrderAllowed(.monotonic, .monotonic));
    try testing.expect(atomic.compareExchangeFailureOrderAllowed(.release, .monotonic));
    try testing.expect(atomic.compareExchangeFailureOrderAllowed(.acq_rel, .acquire));

    try testing.expect(!atomic.compareExchangeFailureOrderAllowed(.release, .acquire));
    try testing.expect(!atomic.compareExchangeFailureOrderAllowed(.seq_cst, .acq_rel));
    try testing.expectEqual(@as(?atomic.Ordering, .acquire), atomic.strongestAllowedFailureOrder(.acq_rel));
}

test "atomic starter packet exercises the wrapper on a bounded integer cell" {
    var cell: u32 = 7;

    try testing.expectEqual(@as(?u32, null), try atomic.compareExchangeStrong(u32, &cell, 7, 9, .seq_cst, .acquire));
    try testing.expectEqual(@as(u32, 9), cell);

    try testing.expectEqual(@as(?u32, 9), try atomic.compareExchangeStrong(u32, &cell, 7, 11, .seq_cst, .acquire));
    try testing.expectEqual(@as(u32, 9), cell);

    try testing.expectError(
        error.InvalidFailureOrdering,
        atomic.compareExchangeStrong(u32, &cell, 9, 12, .release, .acquire),
    );
    try testing.expectEqual(@as(u32, 9), cell);
}
