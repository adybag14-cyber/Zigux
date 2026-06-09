const std = @import("std");
const atomic = @import("atomic");

pub const AtomicOrderAdmissionError = error{
    InvalidLoadOrdering,
    InvalidStoreOrdering,
    InvalidRmwOrdering,
    InvalidCompareExchangeSuccessOrdering,
    InvalidCompareExchangeFailureOrdering,
};

pub const AtomicOrderAdmissionKind = enum(u8) {
    invalid_load,
    invalid_store,
    invalid_rmw,
    invalid_compare_exchange_success,
    invalid_compare_exchange_failure,
    load,
    store,
    rmw,
    compare_exchange_success,
    compare_exchange_failure,
};

pub const AtomicOrderAdmission = struct {
    order: atomic.Ordering,
    success_order: ?atomic.Ordering = null,
    kind: AtomicOrderAdmissionKind,

    pub fn admitted(self: AtomicOrderAdmission) bool {
        return switch (self.kind) {
            .load,
            .store,
            .rmw,
            .compare_exchange_success,
            .compare_exchange_failure,
            => true,
            .invalid_load,
            .invalid_store,
            .invalid_rmw,
            .invalid_compare_exchange_success,
            .invalid_compare_exchange_failure,
            => false,
        };
    }
};

pub fn classifyLoadOrder(order: atomic.Ordering) AtomicOrderAdmissionKind {
    return if (atomic.loadOrderAllowed(order)) .load else .invalid_load;
}

pub fn inspectLoadOrder(order: atomic.Ordering) AtomicOrderAdmission {
    return .{
        .order = order,
        .kind = classifyLoadOrder(order),
    };
}

pub fn classifyStoreOrder(order: atomic.Ordering) AtomicOrderAdmissionKind {
    return if (atomic.storeOrderAllowed(order)) .store else .invalid_store;
}

pub fn inspectStoreOrder(order: atomic.Ordering) AtomicOrderAdmission {
    return .{
        .order = order,
        .kind = classifyStoreOrder(order),
    };
}

pub fn classifyRmwOrder(order: atomic.Ordering) AtomicOrderAdmissionKind {
    return if (atomic.rmwOrderAllowed(order)) .rmw else .invalid_rmw;
}

pub fn inspectRmwOrder(order: atomic.Ordering) AtomicOrderAdmission {
    return .{
        .order = order,
        .kind = classifyRmwOrder(order),
    };
}

pub fn classifyCompareExchangeSuccessOrder(order: atomic.Ordering) AtomicOrderAdmissionKind {
    return if (atomic.compareExchangeSuccessOrderAllowed(order))
        .compare_exchange_success
    else
        .invalid_compare_exchange_success;
}

pub fn inspectCompareExchangeSuccessOrder(order: atomic.Ordering) AtomicOrderAdmission {
    return .{
        .order = order,
        .kind = classifyCompareExchangeSuccessOrder(order),
    };
}

pub fn classifyCompareExchangeFailureOrder(
    success: atomic.Ordering,
    failure: atomic.Ordering,
) AtomicOrderAdmissionKind {
    if (!atomic.compareExchangeSuccessOrderAllowed(success)) {
        return .invalid_compare_exchange_success;
    }
    return if (atomic.compareExchangeFailureOrderAllowed(success, failure))
        .compare_exchange_failure
    else
        .invalid_compare_exchange_failure;
}

pub fn inspectCompareExchangeFailureOrder(
    success: atomic.Ordering,
    failure: atomic.Ordering,
) AtomicOrderAdmission {
    return .{
        .order = failure,
        .success_order = success,
        .kind = classifyCompareExchangeFailureOrder(success, failure),
    };
}

pub fn loadOrderIsAdmitted(order: atomic.Ordering) bool {
    return inspectLoadOrder(order).admitted();
}

pub fn storeOrderIsAdmitted(order: atomic.Ordering) bool {
    return inspectStoreOrder(order).admitted();
}

pub fn rmwOrderIsAdmitted(order: atomic.Ordering) bool {
    return inspectRmwOrder(order).admitted();
}

pub fn compareExchangeSuccessOrderIsAdmitted(order: atomic.Ordering) bool {
    return inspectCompareExchangeSuccessOrder(order).admitted();
}

pub fn compareExchangeFailureOrderIsAdmitted(
    success: atomic.Ordering,
    failure: atomic.Ordering,
) bool {
    return inspectCompareExchangeFailureOrder(success, failure).admitted();
}

pub fn requireLoadOrder(order: atomic.Ordering) AtomicOrderAdmissionError!void {
    if (!loadOrderIsAdmitted(order)) {
        return error.InvalidLoadOrdering;
    }
}

pub fn requireStoreOrder(order: atomic.Ordering) AtomicOrderAdmissionError!void {
    if (!storeOrderIsAdmitted(order)) {
        return error.InvalidStoreOrdering;
    }
}

pub fn requireRmwOrder(order: atomic.Ordering) AtomicOrderAdmissionError!void {
    if (!rmwOrderIsAdmitted(order)) {
        return error.InvalidRmwOrdering;
    }
}

pub fn requireCompareExchangeSuccessOrder(order: atomic.Ordering) AtomicOrderAdmissionError!void {
    if (!compareExchangeSuccessOrderIsAdmitted(order)) {
        return error.InvalidCompareExchangeSuccessOrdering;
    }
}

pub fn requireCompareExchangeFailureOrder(
    success: atomic.Ordering,
    failure: atomic.Ordering,
) AtomicOrderAdmissionError!void {
    switch (classifyCompareExchangeFailureOrder(success, failure)) {
        .compare_exchange_failure => {},
        .invalid_compare_exchange_success => return error.InvalidCompareExchangeSuccessOrdering,
        else => return error.InvalidCompareExchangeFailureOrdering,
    }
}

pub fn canonicalizeLoadOrder(order: atomic.Ordering) AtomicOrderAdmissionError!atomic.Ordering {
    try requireLoadOrder(order);
    return order;
}

pub fn canonicalizeStoreOrder(order: atomic.Ordering) AtomicOrderAdmissionError!atomic.Ordering {
    try requireStoreOrder(order);
    return order;
}

pub fn canonicalizeRmwOrder(order: atomic.Ordering) AtomicOrderAdmissionError!atomic.Ordering {
    try requireRmwOrder(order);
    return order;
}

pub fn canonicalizeCompareExchangeSuccessOrder(order: atomic.Ordering) AtomicOrderAdmissionError!atomic.Ordering {
    try requireCompareExchangeSuccessOrder(order);
    return order;
}

pub fn canonicalizeCompareExchangeFailureOrder(
    success: atomic.Ordering,
    failure: atomic.Ordering,
) AtomicOrderAdmissionError!atomic.Ordering {
    try requireCompareExchangeFailureOrder(success, failure);
    return failure;
}

test "phase3 atomic guard classifies standalone operation orders" {
    try std.testing.expectEqual(AtomicOrderAdmissionKind.load, classifyLoadOrder(.acquire));
    try std.testing.expectEqual(AtomicOrderAdmissionKind.invalid_load, classifyLoadOrder(.release));

    try std.testing.expectEqual(AtomicOrderAdmissionKind.store, classifyStoreOrder(.release));
    try std.testing.expectEqual(AtomicOrderAdmissionKind.invalid_store, classifyStoreOrder(.acquire));

    try std.testing.expectEqual(AtomicOrderAdmissionKind.rmw, classifyRmwOrder(.acq_rel));
    try std.testing.expectEqual(AtomicOrderAdmissionKind.invalid_rmw, classifyRmwOrder(.unordered));
}

test "phase3 atomic guard classifies compare-exchange order pairs" {
    try std.testing.expectEqual(
        AtomicOrderAdmissionKind.compare_exchange_success,
        classifyCompareExchangeSuccessOrder(.release),
    );
    try std.testing.expectEqual(
        AtomicOrderAdmissionKind.invalid_compare_exchange_success,
        classifyCompareExchangeSuccessOrder(.unordered),
    );
    try std.testing.expectEqual(
        AtomicOrderAdmissionKind.compare_exchange_failure,
        classifyCompareExchangeFailureOrder(.acq_rel, .acquire),
    );
    try std.testing.expectEqual(
        AtomicOrderAdmissionKind.invalid_compare_exchange_failure,
        classifyCompareExchangeFailureOrder(.acq_rel, .seq_cst),
    );
    try std.testing.expectEqual(
        AtomicOrderAdmissionKind.invalid_compare_exchange_success,
        classifyCompareExchangeFailureOrder(.unordered, .monotonic),
    );
}

test "phase3 atomic guard inspect rows mirror live atomic predicates" {
    const load_admission = inspectLoadOrder(.seq_cst);
    try std.testing.expect(load_admission.admitted());
    try std.testing.expectEqual(AtomicOrderAdmissionKind.load, load_admission.kind);
    try std.testing.expectEqual(atomic.Ordering.seq_cst, load_admission.order);
    try std.testing.expectEqual(atomic.loadOrderAllowed(.seq_cst), loadOrderIsAdmitted(.seq_cst));

    const store_admission = inspectStoreOrder(.acq_rel);
    try std.testing.expect(!store_admission.admitted());
    try std.testing.expectEqual(AtomicOrderAdmissionKind.invalid_store, store_admission.kind);
    try std.testing.expectEqual(atomic.storeOrderAllowed(.acq_rel), storeOrderIsAdmitted(.acq_rel));

    const failure_admission = inspectCompareExchangeFailureOrder(.release, .monotonic);
    try std.testing.expect(failure_admission.admitted());
    try std.testing.expectEqual(AtomicOrderAdmissionKind.compare_exchange_failure, failure_admission.kind);
    try std.testing.expectEqual(atomic.Ordering.release, failure_admission.success_order.?);
    try std.testing.expectEqual(atomic.Ordering.monotonic, failure_admission.order);
    try std.testing.expectEqual(
        atomic.compareExchangeFailureOrderAllowed(.release, .monotonic),
        compareExchangeFailureOrderIsAdmitted(.release, .monotonic),
    );
}

test "phase3 atomic guard requires and canonicalizes valid orders" {
    try requireLoadOrder(.monotonic);
    try requireStoreOrder(.release);
    try requireRmwOrder(.seq_cst);
    try requireCompareExchangeSuccessOrder(.acq_rel);
    try requireCompareExchangeFailureOrder(.seq_cst, .acquire);

    try std.testing.expectEqual(atomic.Ordering.acquire, try canonicalizeLoadOrder(.acquire));
    try std.testing.expectEqual(atomic.Ordering.release, try canonicalizeStoreOrder(.release));
    try std.testing.expectEqual(atomic.Ordering.acq_rel, try canonicalizeRmwOrder(.acq_rel));
    try std.testing.expectEqual(atomic.Ordering.release, try canonicalizeCompareExchangeSuccessOrder(.release));
    try std.testing.expectEqual(
        atomic.Ordering.acquire,
        try canonicalizeCompareExchangeFailureOrder(.seq_cst, .acquire),
    );
}

test "phase3 atomic guard rejects invalid orders with precise errors" {
    try std.testing.expectError(error.InvalidLoadOrdering, requireLoadOrder(.release));
    try std.testing.expectError(error.InvalidStoreOrdering, requireStoreOrder(.acquire));
    try std.testing.expectError(error.InvalidRmwOrdering, requireRmwOrder(.unordered));
    try std.testing.expectError(
        error.InvalidCompareExchangeSuccessOrdering,
        requireCompareExchangeSuccessOrder(.unordered),
    );
    try std.testing.expectError(
        error.InvalidCompareExchangeFailureOrdering,
        requireCompareExchangeFailureOrder(.release, .acquire),
    );
    try std.testing.expectError(
        error.InvalidCompareExchangeSuccessOrdering,
        requireCompareExchangeFailureOrder(.unordered, .monotonic),
    );
    try std.testing.expectError(error.InvalidLoadOrdering, canonicalizeLoadOrder(.acq_rel));
    try std.testing.expectError(
        error.InvalidCompareExchangeFailureOrdering,
        canonicalizeCompareExchangeFailureOrder(.acq_rel, .seq_cst),
    );
}
