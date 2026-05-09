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

pub const AuditGuard = enum {
    pool_lock_held,
    pool_lock_released_and_reacquired,
    pending_bit_claim_window,
    unbound_pwq_refcnt_retry,
    delayed_submission_alias_window,
    timer_expiry_handoff,
    delayed_requeue_state_window,
    flush_drain_color_window,
    last_pool_lock_handoff,
    callback_execution_outside_pool_lock,
    idle_sleep_transition,
    scheduler_callback_under_pool_lock,
    mayday_lock_then_pool_lock,
};

pub const AuditCheckpoint = struct {
    id: []const u8,
    anchor_symbol: []const u8,
    summary: []const u8,
    guard: AuditGuard,
    observed_fields: []const []const u8,
    blocked_by: []const u8,
    ownership: Ownership,
};

pub const ConcurrencyAudit = struct {
    anchor: []const u8,
    posture: []const u8,
    checkpoints: []const AuditCheckpoint,
    blocked_live_behaviors: []const []const u8,
    next_step: []const u8,
};

pub const RescuerGovernance = struct {
    boundary: BoundaryArea,
    checkpoint_ids: []const []const u8,
    blocked_behaviors: []const []const u8,
    next_step: []const u8,
};

const boundary_areas = [_]BoundaryArea{
    .{
        .id = "submission-routing",
        .summary = "Map the public queueing entrypoints and the internal pool_workqueue handoff without claiming live enqueue execution.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "queue_work_on", "__queue_work" },
        .rationale = "This is the smallest honest starting point for kernel/workqueue.c because it records where caller submission crosses into pool routing before any wakeup, execution, or scheduler-visible state is mirrored in Zig.",
    },
    .{
        .id = "allocation-and-attrs",
        .summary = "Document workqueue allocation and attribute shaping as a future wrapper candidate, not a live allocator port.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "__alloc_workqueue", "devm_alloc_workqueue" },
        .rationale = "Allocation and attrs are reviewable metadata boundaries, but the real implementation still depends on worker_pool lifetime, rescue policy, pod affinity, and memory-ordering rules that remain in C.",
    },
    .{
        .id = "delayed-requeue-governance",
        .summary = "Keep delayed-work requeue state and flush-drain governance explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "mod_delayed_work_on", "__flush_workqueue", "drain_workqueue" },
        .rationale = "Delayed rearm, timer-base ownership, CPU affinity preservation, and active-color flush progression remain too coupled to live worker_pool and workqueue state for a Zig wrapper claim.",
    },
    .{
        .id = "hotplug-topology-rebinding",
        .summary = "Keep POOL_DISASSOCIATED transitions and topology rebinding explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "POOL_DISASSOCIATED", "wq_online_cpumask", "wq_unbound_cpumask", "unbound_wq_update_pwq" },
        .rationale = "Hotplug-driven worker migration and unbound topology rebinding still belong to the existing C implementation and should stay named as stay-in-C governance only.",
    },
    .{
        .id = "max-active-reconfiguration",
        .summary = "Keep runtime max_active retuning and ordered-workqueue rebalance ownership explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "workqueue_set_max_active", "pwq_adjust_max_active" },
        .rationale = "Runtime max_active retuning can rebalance inactive_works against execution-eligible state under the shipped C locking model, so Zigux should record the boundary without claiming ownership of the retune path.",
    },
    .{
        .id = "flush-and-cancel",
        .summary = "Capture flush and cancellation coordination as boundary-map checkpoints before any completion or draining behavior is wrapped.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "__flush_workqueue", "cancel_work_sync" },
        .rationale = "Flush and cancel are caller-facing synchronization surfaces, but their correctness still depends on active-color accounting, pool state, and worker progress under the shipped C implementation.",
    },
    .{
        .id = "worker-pool-concurrency",
        .summary = "Keep worker-pool concurrency management explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "manage_workers", "struct worker_pool" },
        .rationale = "The pool manager owns worker creation, idle culling, busy hashing, and forward-progress checks, so this is the central concurrency boundary that Zigux should audit rather than execute.",
    },
    .{
        .id = "rescuer-and-scheduler-hooks",
        .summary = "Keep rescuer threads and scheduler-visible worker hooks explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "rescuer_thread", "wq_worker_running", "wq_worker_sleeping" },
        .rationale = "These hooks coordinate scheduler-visible worker state, rescue behavior, idle wakeups, and mayday recovery, so Phase 14 should record them as stay-in-C decisions rather than pretend Zig owns them.",
    },
};

const boundary_map_only_area_ids = [_][]const u8{
    "submission-routing",
    "allocation-and-attrs",
    "flush-and-cancel",
};

const stay_in_c_area_ids = [_][]const u8{
    "delayed-requeue-governance",
    "hotplug-topology-rebinding",
    "max-active-reconfiguration",
    "worker-pool-concurrency",
    "rescuer-and-scheduler-hooks",
};

const audit_checkpoints = [_]AuditCheckpoint{
    .{
        .id = "manager-role-serialization",
        .anchor_symbol = "manage_workers",
        .summary = "Record that only one manager may own a pool at a time even though worker creation can drop and reacquire the pool lock.",
        .guard = .pool_lock_released_and_reacquired,
        .observed_fields = &[_][]const u8{ "pool->flags", "pool->manager" },
        .blocked_by = "manage_workers() flips POOL_MANAGER_ACTIVE and pool->manager before maybe_create_worker() drops and reacquires pool->lock, so Zigux should audit the single-manager contract rather than claim a live wrapper.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "worker-pool-forward-progress",
        .anchor_symbol = "struct worker_pool",
        .summary = "Keep forward-progress and runnable-worker accounting under the existing worker_pool lock discipline.",
        .guard = .pool_lock_held,
        .observed_fields = &[_][]const u8{ "pool->last_progress_ts", "pool->nr_running", "pool->worklist" },
        .blocked_by = "worker_pool forward-progress timestamps, runnable counts, and pending worklist state are lock-coupled and watchdog-adjacent, so Phase 14 should only name the fields and leave live updates in C.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "max-active-ordering-gate",
        .anchor_symbol = "__queue_work",
        .summary = "Keep max_active throttling and ordered-workqueue inactive-list placement under the existing pool and pwq lock discipline.",
        .guard = .pool_lock_held,
        .observed_fields = &[_][]const u8{ "pwq->inactive_works", "pwq->nr_active", "wq->max_active", "pool->lock" },
        .blocked_by = "__queue_work() decides between pool->worklist and pwq->inactive_works while holding pool->lock, preserving ordered-workqueue sequencing and leaving workqueue_set_max_active() review-only.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "max-active-reconfiguration-gate",
        .anchor_symbol = "workqueue_set_max_active/pwq_adjust_max_active",
        .summary = "Keep runtime max_active retuning and inactive-list rebalance decisions under the existing workqueue and pwq locking model.",
        .guard = .pool_lock_held,
        .observed_fields = &[_][]const u8{ "wq->max_active", "pwq->max_active", "pwq->inactive_works", "pwq->nr_active" },
        .blocked_by = "workqueue_set_max_active() and pwq_adjust_max_active() can rebalance inactive_works against execution-eligible state while ordered-workqueue limits remain enforced under the shipped C locking model, so Zigux should record the retuning seam without claiming ownership.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "pending-bit-claim-handoff",
        .anchor_symbol = "try_to_grab_pending/queue_work_on",
        .summary = "Keep the pending-bit claim window under the existing atomic and local-IRQ rules.",
        .guard = .pending_bit_claim_window,
        .observed_fields = &[_][]const u8{ "work->data", "WORK_STRUCT_PENDING", "irq_flags", "pool->lock" },
        .blocked_by = "try_to_grab_pending() and queue_work_on() both rely on owning the pending bit while local IRQs stay disabled, so Zigux should audit the submission handoff rather than claim live control.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "unbound-pwq-refcnt-retry",
        .anchor_symbol = "__queue_work",
        .summary = "Record the unbound pwq refcount retry loop before any wrapper claims stable submission ownership.",
        .guard = .unbound_pwq_refcnt_retry,
        .observed_fields = &[_][]const u8{ "pwq->refcnt", "wq->cpu_pwq", "pool->lock", "req_cpu" },
        .blocked_by = "__queue_work() may observe pwq->refcnt == 0 after locking pool->lock, drop the lock, retry after cpu_relax(), and reselect the target pwq, so Zigux should record the retry seam instead of claiming stable unbound ownership.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "delayed-submission-alias-handoff",
        .anchor_symbol = "queue_delayed_work_on/mod_delayed_work_on/__queue_delayed_work",
        .summary = "Record delayed submission helpers as alias layers over timer-backed queueing rather than independent execution ownership.",
        .guard = .delayed_submission_alias_window,
        .observed_fields = &[_][]const u8{ "dwork->timer", "work->data", "delay", "cpu" },
        .blocked_by = "queue_delayed_work_on(), mod_delayed_work_on(), and __queue_delayed_work() share the same pending ownership and timer-gated handoff before execution returns through __queue_work().",
        .ownership = .stay_in_c,
    },
    .{
        .id = "delayed-timer-expiry-handoff",
        .anchor_symbol = "delayed_work_timer_fn",
        .summary = "Record delayed timer expiry and its handoff back into __queue_work() as a review-only ownership boundary.",
        .guard = .timer_expiry_handoff,
        .observed_fields = &[_][]const u8{ "dwork->timer", "work->data", "dwork->cpu", "pool->lock" },
        .blocked_by = "delayed_work_timer_fn() fires after delayed submission parks the item on dwork->timer and rejoins __queue_work(), so Zigux should record the timer-base handoff instead of claiming CPU-affinity or requeue ownership.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "delayed-requeue-ownership-gate",
        .anchor_symbol = "mod_delayed_work_on",
        .summary = "Keep delayed requeue ownership, CPU affinity, and immediate queueing fallthrough explicitly in C.",
        .guard = .delayed_requeue_state_window,
        .observed_fields = &[_][]const u8{ "WORK_CANCEL_DELAYED", "timer-base", "dwork->wq", "cpu" },
        .blocked_by = "mod_delayed_work_on() decides whether timer state is modified in place, CPU affinity must be preserved, or the path falls through to immediate queueing, so the requeue state window stays in C.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "flush-drain-color-ownership",
        .anchor_symbol = "__flush_workqueue/drain_workqueue",
        .summary = "Keep active-color ownership and drain completion under the existing workqueue mutex and in-flight accounting rules.",
        .guard = .flush_drain_color_window,
        .observed_fields = &[_][]const u8{ "wq->work_color", "wq->flush_color", "pwq->nr_in_flight", "wq->first_flusher" },
        .blocked_by = "__flush_workqueue() and drain_workqueue() still own work_color, flush_color, chained flusher coordination, and pwq->nr_in_flight accounting, so Zigux should keep the flush-drain active-color governance note review-only.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "last-pool-reentrancy-handoff",
        .anchor_symbol = "__queue_work",
        .summary = "Record how __queue_work() may lock the previous pool first to preserve non-reentrancy before handing back to the selected pwq or pool.",
        .guard = .last_pool_lock_handoff,
        .observed_fields = &[_][]const u8{ "last_pool->lock", "worker->current_pwq", "pwq->refcnt", "work->data" },
        .blocked_by = "__queue_work() can grab last_pool->lock, inspect find_worker_executing_work(), and then either stay on worker->current_pwq or relock the selected pool, so Phase 14 should record the lock handoff instead of claiming live enqueue control across pools.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "process-one-work-execution-window",
        .anchor_symbol = "process_one_work",
        .summary = "Keep the callback execution window under the existing unlock, relock, and in-flight accounting discipline.",
        .guard = .callback_execution_outside_pool_lock,
        .observed_fields = &[_][]const u8{ "worker->current_work", "worker->current_pwq", "pwq->stats[PWQ_STAT_STARTED]", "pwq->nr_in_flight" },
        .blocked_by = "process_one_work() clears PENDING, drops pool->lock before callback execution, then reacquires pool->lock before completion accounting, so Zigux should audit the execution window rather than claim a live callback wrapper.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "worker-thread-idle-sleep-handoff",
        .anchor_symbol = "worker_thread",
        .summary = "Track the idle entry and wakeup path that sets TASK_IDLE before pool->lock is released and schedule() runs.",
        .guard = .idle_sleep_transition,
        .observed_fields = &[_][]const u8{ "worker->flags", "pool->worklist", "pool->lock", "worker->scheduled" },
        .blocked_by = "worker_thread() enters idle, sets TASK_IDLE while holding pool->lock, releases the lock, and only then sleeps until wakeup reacquires the same lock, so the sleep transition remains a stay-in-C concurrency boundary.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "scheduler-running-hooks",
        .anchor_symbol = "wq_worker_running/wq_worker_sleeping",
        .summary = "Track scheduler-visible running and sleeping callbacks as a separate audit surface tied to worker flags and nr_running transitions.",
        .guard = .scheduler_callback_under_pool_lock,
        .observed_fields = &[_][]const u8{ "WORKER_NOT_RUNNING", "pool->nr_running", "worker->flags", "wake_up_worker" },
        .blocked_by = "The scheduler-visible hooks adjust WORKER_NOT_RUNNING state and pool->nr_running while coordinating wakeups under pool->lock, which is exactly the sort of live concurrency ownership Zigux should keep in C.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "rescuer-mayday-handoff",
        .anchor_symbol = "rescuer_thread",
        .summary = "Capture the rescuer mayday-list handoff into pool-locked rescue work without claiming the execution loop itself.",
        .guard = .mayday_lock_then_pool_lock,
        .observed_fields = &[_][]const u8{ "wq->maydays", "pwq->nr_active", "pwq->mayday_cursor", "pool->lock" },
        .blocked_by = "rescuer_thread() walks wq->maydays, attaches to a pool, rescues pending work, and then kicks regular workers again, so the entire mayday handoff remains a stay-in-C concurrency boundary.",
        .ownership = .stay_in_c,
    },
};

const blocked_live_behaviors = [_][]const u8{
    "live worker_pool execution",
    "runtime max_active retuning ownership",
    "pool draining and flush completion",
    "delayed-work requeue ownership",
    "scheduler callback parity",
    "rescuer execution ownership",
    "hotplug-driven worker migration",
};

const rescuer_checkpoint_ids = [_][]const u8{
    "scheduler-running-hooks",
    "rescuer-mayday-handoff",
};

const rescuer_blocked_behaviors = [_][]const u8{
    "scheduler callback parity",
    "rescuer execution ownership",
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

    pub fn concurrencyAudit() ConcurrencyAudit {
        return .{
            .anchor = descriptor().anchor,
            .posture = descriptor().posture,
            .checkpoints = audit_checkpoints[0..],
            .blocked_live_behaviors = blocked_live_behaviors[0..],
            .next_step = nextAuditFocus(),
        };
    }

    pub fn boundaryMapOnlyAreaCount() usize {
        return boundary_map_only_area_ids.len;
    }

    pub fn boundaryMapOnlyAreaIds() []const []const u8 {
        return boundary_map_only_area_ids[0..];
    }

    pub fn rescuerGovernance() RescuerGovernance {
        return .{
            .boundary = boundaryAreaById("rescuer-and-scheduler-hooks").?,
            .checkpoint_ids = rescuer_checkpoint_ids[0..],
            .blocked_behaviors = rescuer_blocked_behaviors[0..],
            .next_step = "If this lane reopens, keep the next study step limited to rescuer_thread() or mayday ownership notes instead of live execution claims.",
        };
    }

    pub fn rescuerGovernanceTracksCheckpoint(id: []const u8) bool {
        for (rescuer_checkpoint_ids) |checkpoint_id| {
            if (std.mem.eql(u8, checkpoint_id, id)) return true;
        }
        return false;
    }

    pub fn stayInCAreaIds() []const []const u8 {
        return stay_in_c_area_ids[0..];
    }

    pub fn stayInCDecisionCount() usize {
        return stay_in_c_area_ids.len;
    }

    pub fn auditCheckpointCount() usize {
        return audit_checkpoints.len;
    }

    pub fn boundaryAreaById(id: []const u8) ?BoundaryArea {
        for (boundary_areas) |area| {
            if (std.mem.eql(u8, area.id, id)) return area;
        }
        return null;
    }

    pub fn checkpointById(id: []const u8) ?AuditCheckpoint {
        for (audit_checkpoints) |checkpoint| {
            if (std.mem.eql(u8, checkpoint.id, id)) return checkpoint;
        }
        return null;
    }

    pub fn blocksLiveBehavior(behavior: []const u8) bool {
        for (blocked_live_behaviors) |blocked| {
            if (std.mem.eql(u8, blocked, behavior)) return true;
        }
        return false;
    }

    pub fn nextAuditFocus() []const u8 {
        return "Leave this lane in blocked maintenance unless the shared Phase 14 smoke packet or this workqueue survey drifts; any reopen should stay review-only and keep the flush-drain active-color governance note, timer-base, CPU-affinity, delayed-work requeue ownership, the runtime max_active retuning boundary, and live execution in C.";
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

test "workqueue bridge current phase14 packet counts stay aligned" {
    const map = WorkqueueBridgeLab.boundaryMap();
    const audit = WorkqueueBridgeLab.concurrencyAudit();

    try std.testing.expectEqual(@as(usize, 8), map.areas.len);
    try std.testing.expectEqual(@as(usize, 3), WorkqueueBridgeLab.boundaryMapOnlyAreaCount());
    try std.testing.expectEqual(@as(usize, 5), WorkqueueBridgeLab.stayInCDecisionCount());
    try std.testing.expectEqual(@as(usize, 15), audit.checkpoints.len);
    try std.testing.expectEqual(@as(usize, 7), audit.blocked_live_behaviors.len);
    try std.testing.expect(std.mem.indexOf(u8, WorkqueueBridgeLab.nextAuditFocus(), "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, WorkqueueBridgeLab.nextAuditFocus(), "flush-drain active-color governance note") != null);
    try std.testing.expect(std.mem.indexOf(u8, WorkqueueBridgeLab.nextAuditFocus(), "runtime max_active retuning boundary") != null);
}

test "workqueue bridge boundary-map packet keeps roadmap-owned areas queryable" {
    const boundary_map_only_ids = WorkqueueBridgeLab.boundaryMapOnlyAreaIds();
    try std.testing.expectEqual(@as(usize, 3), boundary_map_only_ids.len);
    try std.testing.expectEqualStrings("submission-routing", boundary_map_only_ids[0]);
    try std.testing.expectEqualStrings("allocation-and-attrs", boundary_map_only_ids[1]);
    try std.testing.expectEqualStrings("flush-and-cancel", boundary_map_only_ids[2]);

    for (boundary_map_only_ids) |id| {
        const area = WorkqueueBridgeLab.boundaryAreaById(id).?;
        try std.testing.expect(area.ownership == .boundary_map_only);
    }

    const stay_in_c_ids = WorkqueueBridgeLab.stayInCAreaIds();
    try std.testing.expectEqual(@as(usize, 5), stay_in_c_ids.len);
    try std.testing.expectEqualStrings("delayed-requeue-governance", stay_in_c_ids[0]);
    try std.testing.expectEqualStrings("hotplug-topology-rebinding", stay_in_c_ids[1]);
    try std.testing.expectEqualStrings("max-active-reconfiguration", stay_in_c_ids[2]);
    try std.testing.expectEqualStrings("worker-pool-concurrency", stay_in_c_ids[3]);
    try std.testing.expectEqualStrings("rescuer-and-scheduler-hooks", stay_in_c_ids[4]);

    for (stay_in_c_ids) |id| {
        const area = WorkqueueBridgeLab.boundaryAreaById(id).?;
        try std.testing.expect(area.ownership == .stay_in_c);
    }
}

test "workqueue bridge boundary areas keep core stay-in-c seams explicit" {
    const hotplug = WorkqueueBridgeLab.boundaryAreaById("hotplug-topology-rebinding").?;
    try std.testing.expect(hotplug.ownership == .stay_in_c);
    try std.testing.expectEqualStrings("POOL_DISASSOCIATED", hotplug.anchor_symbols[0]);
    try std.testing.expect(std.mem.indexOf(u8, hotplug.rationale, "unbound topology rebinding") != null);

    const max_active = WorkqueueBridgeLab.boundaryAreaById("max-active-reconfiguration").?;
    try std.testing.expect(max_active.ownership == .stay_in_c);
    try std.testing.expectEqualStrings("workqueue_set_max_active", max_active.anchor_symbols[0]);
    try std.testing.expect(std.mem.indexOf(u8, max_active.summary, "ordered-workqueue") != null);
    try std.testing.expect(std.mem.indexOf(u8, max_active.rationale, "inactive_works") != null);

    const rescuer = WorkqueueBridgeLab.boundaryAreaById("rescuer-and-scheduler-hooks").?;
    try std.testing.expect(rescuer.ownership == .stay_in_c);
    try std.testing.expectEqualStrings("rescuer_thread", rescuer.anchor_symbols[0]);
    try std.testing.expectEqualStrings("wq_worker_running", rescuer.anchor_symbols[1]);
    try std.testing.expectEqualStrings("wq_worker_sleeping", rescuer.anchor_symbols[2]);
    try std.testing.expect(std.mem.indexOf(u8, rescuer.rationale, "scheduler-visible worker state") != null);

    try std.testing.expect(WorkqueueBridgeLab.boundaryAreaById("not-a-real-boundary") == null);
    try std.testing.expect(WorkqueueBridgeLab.blocksLiveBehavior("runtime max_active retuning ownership"));
    try std.testing.expect(WorkqueueBridgeLab.blocksLiveBehavior("scheduler callback parity"));
    try std.testing.expect(WorkqueueBridgeLab.blocksLiveBehavior("rescuer execution ownership"));
    try std.testing.expect(WorkqueueBridgeLab.blocksLiveBehavior("hotplug-driven worker migration"));
    try std.testing.expect(!WorkqueueBridgeLab.blocksLiveBehavior("synthetic behavior"));
}

test "workqueue bridge rescuer governance stays review-only" {
    const governance = WorkqueueBridgeLab.rescuerGovernance();

    try std.testing.expectEqualStrings("rescuer-and-scheduler-hooks", governance.boundary.id);
    try std.testing.expect(governance.boundary.ownership == .stay_in_c);
    try std.testing.expectEqualStrings("rescuer_thread", governance.boundary.anchor_symbols[0]);
    try std.testing.expectEqualStrings("wq_worker_running", governance.boundary.anchor_symbols[1]);
    try std.testing.expectEqualStrings("wq_worker_sleeping", governance.boundary.anchor_symbols[2]);
    try std.testing.expectEqual(@as(usize, 2), governance.checkpoint_ids.len);
    try std.testing.expectEqualStrings("scheduler-running-hooks", governance.checkpoint_ids[0]);
    try std.testing.expectEqualStrings("rescuer-mayday-handoff", governance.checkpoint_ids[1]);
    try std.testing.expectEqual(@as(usize, 2), governance.blocked_behaviors.len);
    try std.testing.expectEqualStrings("scheduler callback parity", governance.blocked_behaviors[0]);
    try std.testing.expectEqualStrings("rescuer execution ownership", governance.blocked_behaviors[1]);
    try std.testing.expect(std.mem.indexOf(u8, governance.next_step, "rescuer_thread()") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance.next_step, "mayday ownership notes") != null);
    try std.testing.expect(WorkqueueBridgeLab.rescuerGovernanceTracksCheckpoint("scheduler-running-hooks"));
    try std.testing.expect(WorkqueueBridgeLab.rescuerGovernanceTracksCheckpoint("rescuer-mayday-handoff"));
    try std.testing.expect(!WorkqueueBridgeLab.rescuerGovernanceTracksCheckpoint("flush-drain-color-ownership"));
}
