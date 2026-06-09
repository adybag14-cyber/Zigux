const std = @import("std");
const atomic = @import("atomic_helpers");

const Ordering = atomic.Ordering;

fn expectBounds(success: Ordering, weakest: ?Ordering, strongest: ?Ordering) !void {
    try std.testing.expectEqual(weakest, atomic.weakestAllowedFailureOrder(success));
    try std.testing.expectEqual(strongest, atomic.strongestAllowedFailureOrder(success));

    if (weakest) |order| {
        try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(success, order));
    }
    if (strongest) |order| {
        try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(success, order));
    }
}

test "phase3 atomic failure bounds classify every success ordering" {
    try expectBounds(.unordered, null, null);
    try expectBounds(.monotonic, .monotonic, .monotonic);
    try expectBounds(.release, .monotonic, .monotonic);
    try expectBounds(.acquire, .monotonic, .acquire);
    try expectBounds(.acq_rel, .monotonic, .acquire);
    try expectBounds(.seq_cst, .monotonic, .seq_cst);
}

test "phase3 atomic failure bounds stay within valid failure orderings" {
    const success_orders = [_]Ordering{ .monotonic, .release, .acquire, .acq_rel, .seq_cst };
    const invalid_failure_orders = [_]Ordering{ .unordered, .release, .acq_rel };

    for (success_orders) |success| {
        for (invalid_failure_orders) |failure| {
            try std.testing.expect(!atomic.compareExchangeFailureOrderAllowed(success, failure));
        }
    }

    try std.testing.expect(!atomic.compareExchangeFailureOrderAllowed(.unordered, .monotonic));
    try std.testing.expect(!atomic.compareExchangeFailureOrderAllowed(.unordered, .seq_cst));
}

test "phase3 atomic failure bounds bracket allowed failure choices" {
    try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(.monotonic, .monotonic));
    try std.testing.expect(!atomic.compareExchangeFailureOrderAllowed(.monotonic, .acquire));
    try std.testing.expect(!atomic.compareExchangeFailureOrderAllowed(.monotonic, .seq_cst));

    try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(.acquire, .monotonic));
    try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(.acquire, .acquire));
    try std.testing.expect(!atomic.compareExchangeFailureOrderAllowed(.acquire, .seq_cst));

    try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(.acq_rel, .monotonic));
    try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(.acq_rel, .acquire));
    try std.testing.expect(!atomic.compareExchangeFailureOrderAllowed(.acq_rel, .seq_cst));

    try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(.seq_cst, .monotonic));
    try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(.seq_cst, .acquire));
    try std.testing.expect(atomic.compareExchangeFailureOrderAllowed(.seq_cst, .seq_cst));
}
