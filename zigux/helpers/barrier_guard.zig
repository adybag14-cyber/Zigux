const std = @import("std");
const barrier = @import("barrier");

pub const FenceAdmissionError = error{
    InvalidFenceOrdering,
};

pub const FenceAdmissionKind = enum(u8) {
    invalid,
    acquire,
    release,
    acquire_release,
    sequentially_consistent,
};

pub const FenceAdmission = struct {
    order: barrier.Ordering,
    kind: FenceAdmissionKind,

    pub fn admitted(self: FenceAdmission) bool {
        return self.kind != .invalid;
    }
};

pub fn classifyFenceOrder(order: barrier.Ordering) FenceAdmissionKind {
    return switch (order) {
        .acquire => .acquire,
        .release => .release,
        .acq_rel => .acquire_release,
        .seq_cst => .sequentially_consistent,
        .unordered, .monotonic => .invalid,
    };
}

pub fn inspectFenceOrder(order: barrier.Ordering) FenceAdmission {
    return .{
        .order = order,
        .kind = classifyFenceOrder(order),
    };
}

pub fn fenceOrderIsAdmitted(order: barrier.Ordering) bool {
    return inspectFenceOrder(order).admitted();
}

pub fn requireFenceOrder(order: barrier.Ordering) FenceAdmissionError!void {
    if (!fenceOrderIsAdmitted(order)) {
        return error.InvalidFenceOrdering;
    }
}

pub fn requireFenceOrderComptime(comptime order: barrier.Ordering) FenceAdmissionError!void {
    try barrier.validateFenceOrder(order);
}

pub fn canonicalizeFenceOrder(order: barrier.Ordering) FenceAdmissionError!barrier.Ordering {
    try requireFenceOrder(order);
    return order;
}

test "phase3 barrier guard classifies fence admission rows" {
    try std.testing.expectEqual(FenceAdmissionKind.acquire, classifyFenceOrder(.acquire));
    try std.testing.expectEqual(FenceAdmissionKind.release, classifyFenceOrder(.release));
    try std.testing.expectEqual(FenceAdmissionKind.acquire_release, classifyFenceOrder(.acq_rel));
    try std.testing.expectEqual(FenceAdmissionKind.sequentially_consistent, classifyFenceOrder(.seq_cst));
    try std.testing.expectEqual(FenceAdmissionKind.invalid, classifyFenceOrder(.unordered));
    try std.testing.expectEqual(FenceAdmissionKind.invalid, classifyFenceOrder(.monotonic));
}

test "phase3 barrier guard mirrors live barrier order admission" {
    const Row = struct {
        order: barrier.Ordering,
        kind: FenceAdmissionKind,
        admitted: bool,
    };

    const rows = [_]Row{
        .{ .order = .acquire, .kind = .acquire, .admitted = true },
        .{ .order = .release, .kind = .release, .admitted = true },
        .{ .order = .acq_rel, .kind = .acquire_release, .admitted = true },
        .{ .order = .seq_cst, .kind = .sequentially_consistent, .admitted = true },
        .{ .order = .unordered, .kind = .invalid, .admitted = false },
        .{ .order = .monotonic, .kind = .invalid, .admitted = false },
    };

    for (rows) |row| {
        const admission = inspectFenceOrder(row.order);
        try std.testing.expectEqual(row.kind, admission.kind);
        try std.testing.expectEqual(row.order, admission.order);
        try std.testing.expectEqual(row.admitted, admission.admitted());
        try std.testing.expectEqual(barrier.fenceOrderAllowed(row.order), fenceOrderIsAdmitted(row.order));
    }
}

test "phase3 barrier guard requires and canonicalizes valid fence orders" {
    try requireFenceOrder(.acquire);
    try requireFenceOrder(.release);
    try requireFenceOrder(.acq_rel);
    try requireFenceOrder(.seq_cst);
    try requireFenceOrderComptime(.acquire);
    try requireFenceOrderComptime(.seq_cst);

    try std.testing.expectEqual(barrier.Ordering.acquire, try canonicalizeFenceOrder(.acquire));
    try std.testing.expectEqual(barrier.Ordering.release, try canonicalizeFenceOrder(.release));
    try std.testing.expectEqual(barrier.Ordering.acq_rel, try canonicalizeFenceOrder(.acq_rel));
    try std.testing.expectEqual(barrier.Ordering.seq_cst, try canonicalizeFenceOrder(.seq_cst));

    try std.testing.expectError(error.InvalidFenceOrdering, requireFenceOrder(.unordered));
    try std.testing.expectError(error.InvalidFenceOrdering, requireFenceOrder(.monotonic));
    try std.testing.expectError(error.InvalidFenceOrdering, canonicalizeFenceOrder(.unordered));
    try std.testing.expectError(error.InvalidFenceOrdering, canonicalizeFenceOrder(.monotonic));
}
