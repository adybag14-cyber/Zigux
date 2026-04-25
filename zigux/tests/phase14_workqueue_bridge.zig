const std = @import("std");
const workqueue_bridge = @import("workqueue_bridge");

test "phase14 workqueue bridge descriptor stays boundary-map only" {
    const descriptor = workqueue_bridge.WorkqueueBridgeLab.descriptor();

    try std.testing.expectEqualStrings("workqueue_boundary_map_lab", descriptor.name);
    try std.testing.expectEqualStrings("kernel/workqueue.c", descriptor.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", descriptor.posture);
    try std.testing.expect(descriptor.provides_boundary_map);
    try std.testing.expect(descriptor.provides_concurrency_audit_outline);
    try std.testing.expect(descriptor.provides_stay_in_c_decisions);
    try std.testing.expect(!descriptor.touches_live_worker_pools);
    try std.testing.expect(!descriptor.touches_live_work_execution);
    try std.testing.expect(!descriptor.touches_scheduler_hooks);
}

test "phase14 workqueue bridge boundary map keeps the first stay-in-c edges explicit" {
    const map = workqueue_bridge.WorkqueueBridgeLab.boundaryMap();

    try std.testing.expectEqual(@as(usize, 5), map.areas.len);
    try std.testing.expectEqualStrings("submission-routing", map.areas[0].id);
    try std.testing.expect(map.areas[0].ownership == .boundary_map_only);
    try std.testing.expectEqualStrings("__queue_work", map.areas[0].anchor_symbols[1]);
    try std.testing.expectEqualStrings("worker-pool-concurrency", map.areas[3].id);
    try std.testing.expect(map.areas[3].ownership == .stay_in_c);
    try std.testing.expectEqual(@as(usize, 2), workqueue_bridge.WorkqueueBridgeLab.stayInCDecisionCount());
}

test "phase14 workqueue bridge audit checklist stays inside stay-in-c ownership" {
    const checklist = workqueue_bridge.WorkqueueBridgeLab.concurrencyAuditChecklist();

    try std.testing.expectEqual(@as(usize, 3), checklist.len);
    for (checklist) |checkpoint| {
        try std.testing.expect(checkpoint.expected_owner == .stay_in_c);
    }

    try std.testing.expectEqualStrings("pool-lock-ownership", checklist[0].id);
    try std.testing.expectEqualStrings("worker-pool-concurrency", checklist[0].boundary_area_id);
    try std.testing.expectEqualStrings("manage_workers", checklist[0].anchor_symbols[0]);

    try std.testing.expectEqualStrings("rescuer-mayday-path", checklist[1].id);
    try std.testing.expectEqualStrings("send_mayday", checklist[1].anchor_symbols[1]);

    try std.testing.expectEqualStrings("scheduler-hook-pairing", checklist[2].id);
    try std.testing.expectEqualStrings("WORKER_NOT_RUNNING", checklist[2].anchor_symbols[2]);
}

test "phase14 workqueue bridge next audit focus still points at the concurrency handoff" {
    const focus = workqueue_bridge.WorkqueueBridgeLab.nextAuditFocus();

    try std.testing.expect(std.mem.indexOf(u8, focus, "manage_workers()") != null);
    try std.testing.expect(std.mem.indexOf(u8, focus, "rescuer_thread()") != null);
    try std.testing.expect(std.mem.indexOf(u8, focus, "wq_worker_running()") != null);
}
