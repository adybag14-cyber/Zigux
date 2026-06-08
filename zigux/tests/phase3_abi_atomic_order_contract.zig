const std = @import("std");

const atomic = @import("atomic_helpers");

const OrderingCase = struct {
    order: atomic.Ordering,
    load: bool,
    store: bool,
    rmw: bool,
};

test "phase3 abi atomic order contract keeps load store and rmw domains explicit" {
    const cases = [_]OrderingCase{
        .{ .order = .unordered, .load = false, .store = false, .rmw = false },
        .{ .order = .monotonic, .load = true, .store = true, .rmw = true },
        .{ .order = .acquire, .load = true, .store = false, .rmw = true },
        .{ .order = .release, .load = false, .store = true, .rmw = true },
        .{ .order = .acq_rel, .load = false, .store = false, .rmw = true },
        .{ .order = .seq_cst, .load = true, .store = true, .rmw = true },
    };

    inline for (cases) |case| {
        try std.testing.expectEqual(case.load, atomic.loadOrderAllowed(case.order));
        try std.testing.expectEqual(case.store, atomic.storeOrderAllowed(case.order));
        try std.testing.expectEqual(case.rmw, atomic.rmwOrderAllowed(case.order));
    }
}

test "phase3 abi atomic order contract keeps validation error tags stable" {
    try atomic.validateLoadOrder(.monotonic);
    try atomic.validateLoadOrder(.acquire);
    try atomic.validateLoadOrder(.seq_cst);
    try std.testing.expectError(error.InvalidLoadOrdering, atomic.validateLoadOrder(.unordered));
    try std.testing.expectError(error.InvalidLoadOrdering, atomic.validateLoadOrder(.release));
    try std.testing.expectError(error.InvalidLoadOrdering, atomic.validateLoadOrder(.acq_rel));

    try atomic.validateStoreOrder(.monotonic);
    try atomic.validateStoreOrder(.release);
    try atomic.validateStoreOrder(.seq_cst);
    try std.testing.expectError(error.InvalidStoreOrdering, atomic.validateStoreOrder(.unordered));
    try std.testing.expectError(error.InvalidStoreOrdering, atomic.validateStoreOrder(.acquire));
    try std.testing.expectError(error.InvalidStoreOrdering, atomic.validateStoreOrder(.acq_rel));

    try atomic.validateRmwOrder(.monotonic);
    try atomic.validateRmwOrder(.acquire);
    try atomic.validateRmwOrder(.release);
    try atomic.validateRmwOrder(.acq_rel);
    try atomic.validateRmwOrder(.seq_cst);
    try std.testing.expectError(error.InvalidRmwOrdering, atomic.validateRmwOrder(.unordered));
}

test "phase3 abi atomic order contract keeps compare exchange failure bounds explicit" {
    const success_orders = [_]atomic.Ordering{
        .monotonic,
        .release,
        .acquire,
        .acq_rel,
        .seq_cst,
        .unordered,
    };
    const weakest = [_]?atomic.Ordering{
        .monotonic,
        .monotonic,
        .monotonic,
        .monotonic,
        .monotonic,
        null,
    };
    const strongest = [_]?atomic.Ordering{
        .monotonic,
        .monotonic,
        .acquire,
        .acquire,
        .seq_cst,
        null,
    };

    inline for (success_orders, weakest, strongest) |success, expected_weakest, expected_strongest| {
        try std.testing.expectEqual(expected_weakest, atomic.weakestAllowedFailureOrder(success));
        try std.testing.expectEqual(expected_strongest, atomic.strongestAllowedFailureOrder(success));
    }

    try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(.monotonic, .monotonic));
    try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(.release, .monotonic));
    try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(.acquire, .acquire));
    try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(.acq_rel, .acquire));
    try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(.seq_cst, .seq_cst));

    try std.testing.expect(!atomic.compareExchangeFailureOrderAllowed(.monotonic, .acquire));
    try std.testing.expect(!atomic.compareExchangeFailureOrderAllowed(.release, .acquire));
    try std.testing.expect(!atomic.compareExchangeFailureOrderAllowed(.acq_rel, .seq_cst));
    try std.testing.expect(!atomic.compareExchangeFailureOrderAllowed(.seq_cst, .release));
    try std.testing.expect(!atomic.compareExchangeFailureOrderAllowed(.seq_cst, .acq_rel));
    try std.testing.expect(!atomic.compareExchangeFailureOrderAllowed(.unordered, .monotonic));
}
