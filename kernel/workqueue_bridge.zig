const std = @import("std");

pub const Ownership = enum {
    boundary_map_only,
    stay_in_c,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    posture: []const u8,
    provides_boundary_map: bool,
    provides_concurrency_audit_outline: bool,
    provides_stay_in_c_decisions: bool,
    touches_live_worker_pools: bool,
    touches_live_work_execution: bool,
    touches_scheduler_hooks: bool,
};

pub const BoundaryArea = struct {
    id: []const u8,
    summary: []const u8,
    ownership: Ownership,
    anchor_symbols: []const []const u8,
    rationale: []const u8,
};

pub const BoundaryMap = struct {
    anchor: []const u8,
    posture: []const u8,
    areas: []const BoundaryArea,
};

const boundary_areas = [_]BoundaryArea{
    .{
        .id = "submission-routing",
        .summary = "Map the public queueing entrypoints and the internal pwq handoff without claiming live enqueue execution.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "queue_work_on", "__queue_work" },
        .rationale = "This is the smallest honest starting point for workqueue.c because it records where work submission crosses from callers into pool_workqueue routing before any locking, pool wakeup, or worker execution is mirrored in Zig.",
    },
    .{
        .id = "allocation-and-attrs",
        .summary = "Document the workqueue allocation and attribute surface as a future wrapper candidate, not a live allocator port.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "__alloc_workqueue", "devm_alloc_workqueue" },
        .rationale = "Allocation and attribute shaping are reviewable as metadata boundaries, but the real implementation still depends on worker_pool lifetime, rescue policy, pod affinity, and memory-ordering rules that remain in C.",
    },
    .{
        .id = "flush-and-cancel",
        .summary = "Capture flush and cancellation coordination as boundary-map checkpoints before any completion or draining behavior is wrapped.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "__flush_workqueue", "cancel_work_sync" },
        .rationale = "Flush and cancel are caller-facing synchronization surfaces, but their correctness depends on active-color accounting, pool state, and worker progress that should stay under the existing C implementation for now.",
    },
    .{
        .id = "worker-pool-concurrency",
        .summary = "Keep worker-pool concurrency management explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "manage_workers", "struct worker_pool" },
        .rationale = "The pool manager owns worker creation, idle culling, busy hashing, forward-progress checks, and lock-protected state transitions; this is the central concurrency boundary that Zigux should only audit before any wrapper work grows deeper.",
    },
    .{
        .id = "rescuer-and-scheduler-hooks",
        .summary = "Keep rescuer threads and scheduler-facing hooks explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "rescuer_thread", "wq_worker_running", "wq_worker_sleeping" },
        .rationale = "These hooks coordinate scheduler-visible worker state, rescue behavior, CPU association, and watchdog-adjacent progress signals, so Phase 14 should record them as stay-in-C decisions rather than pretend a wrapper can safely own them yet.",
    },
};

pub const WorkqueueBridgeLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "workqueue_boundary_map_lab",
            .anchor = "kernel/workqueue.c",
            .posture = "boundary_map_only",
            .provides_boundary_map = true,
            .provides_concurrency_audit_outline = true,
            .provides_stay_in_c_decisions = true,
            .touches_live_worker_pools = false,
            .touches_live_work_execution = false,
            .touches_scheduler_hooks = false,
        };
    }

    pub fn boundaryMap() BoundaryMap {
        return .{
            .anchor = descriptor().anchor,
            .posture = descriptor().posture,
            .areas = boundary_areas[0..],
        };
    }

    pub fn stayInCDecisionCount() usize {
        var count: usize = 0;
        for (boundary_areas) |area| {
            if (area.ownership == .stay_in_c) {
                count += 1;
            }
        }
        return count;
    }

    pub fn nextAuditFocus() []const u8 {
        return "Audit manage_workers(), worker_pool lock ownership, rescuer_thread(), and wq_worker_running()/wq_worker_sleeping() transitions before any wrapper leaves the boundary-map-only posture.";
    }
};

test "workqueue bridge descriptor stays boundary-map only" {
    const descriptor = WorkqueueBridgeLab.descriptor();

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

test "workqueue bridge boundary map records stay-in-c decisions" {
    const map = WorkqueueBridgeLab.boundaryMap();

    try std.testing.expectEqualStrings("kernel/workqueue.c", map.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", map.posture);
    try std.testing.expectEqual(@as(usize, 5), map.areas.len);
    try std.testing.expectEqual(@as(usize, 2), WorkqueueBridgeLab.stayInCDecisionCount());
    try std.testing.expect(std.mem.indexOf(u8, WorkqueueBridgeLab.nextAuditFocus(), "manage_workers()") != null);
    try std.testing.expect(std.mem.indexOf(u8, WorkqueueBridgeLab.nextAuditFocus(), "rescuer_thread()") != null);

    try std.testing.expectEqualStrings("submission-routing", map.areas[0].id);
    try std.testing.expect(map.areas[0].ownership == .boundary_map_only);
    try std.testing.expectEqualStrings("queue_work_on", map.areas[0].anchor_symbols[0]);
    try std.testing.expectEqualStrings("__queue_work", map.areas[0].anchor_symbols[1]);

    try std.testing.expectEqualStrings("worker-pool-concurrency", map.areas[3].id);
    try std.testing.expect(map.areas[3].ownership == .stay_in_c);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[3].rationale, "forward-progress") != null);

    try std.testing.expectEqualStrings("rescuer-and-scheduler-hooks", map.areas[4].id);
    try std.testing.expect(map.areas[4].ownership == .stay_in_c);
    try std.testing.expectEqualStrings("wq_worker_running", map.areas[4].anchor_symbols[1]);
    try std.testing.expectEqualStrings("wq_worker_sleeping", map.areas[4].anchor_symbols[2]);
}
