const std = @import("std");
const bridge = @import("../../kernel/workqueue_bridge.zig");

fn expectContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) return;
    }
    return error.TestExpectedEqual;
}

test "phase14 workqueue bridge keeps lane metadata anchored to the bounded study surface" {
    try std.testing.expectEqualStrings("P14-L04", bridge.lane_key);
    try std.testing.expectEqualStrings("Phase 14", bridge.phase);
    try std.testing.expectEqualStrings("kernel/workqueue.c", bridge.anchor);
    try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", bridge.recommended_destination);
    try std.testing.expectEqualStrings("phase14-workqueue-flush-color-followup", bridge.ready_next_gap);
    try std.testing.expectEqualStrings("phase14-workqueue-live-execution-blocker", bridge.blocked_gap);
}

test "phase14 workqueue bridge records the pending-bit submission boundary as stay-in-c governance" {
    const audit = bridge.findAudit("pending-bit-and-unbound-retry") orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(bridge.AuditKind.concurrency_audit, audit.kind);
    try std.testing.expectEqual(bridge.Ownership.stay_in_c, audit.ownership);
    try expectContains(audit.symbols, "try_to_grab_pending");
    try expectContains(audit.symbols, "queue_work_on");
    try expectContains(audit.symbols, "__queue_work");
    try expectContains(audit.coupled_state, "WORK_STRUCT_PENDING_BIT");
    try expectContains(audit.coupled_state, "WORK_OFFQ_CANCELING");
    try expectContains(audit.coupled_state, "pwq->refcnt");
}

test "phase14 workqueue bridge records the drain cancel boundary as a stay-in-c audit" {
    const audit = bridge.findAudit("flush-drain-cancel-boundary") orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(bridge.AuditKind.concurrency_audit, audit.kind);
    try std.testing.expectEqual(bridge.Ownership.stay_in_c, audit.ownership);
    try expectContains(audit.symbols, "drain_workqueue");
    try expectContains(audit.symbols, "__flush_work");
    try expectContains(audit.symbols, "__cancel_work_sync");
    try expectContains(audit.coupled_state, "wq->work_color");
    try expectContains(audit.coupled_state, "pwq->nr_in_flight");
}

test "phase14 workqueue bridge keeps live execution blocked behind worker_pool ownership" {
    const audit = bridge.findAudit("rescuer-and-scheduler-hooks") orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(bridge.Ownership.blocked_on_live_concurrency, audit.ownership);
    try expectContains(audit.symbols, "manage_workers");
    try expectContains(audit.symbols, "rescuer_thread");
    try expectContains(audit.symbols, "wq_worker_running");
    try expectContains(audit.coupled_state, "worker_pool state machine");
}
