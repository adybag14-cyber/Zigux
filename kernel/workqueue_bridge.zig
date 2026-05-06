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
    delayed_submission_alias_window,
    unbound_pwq_refcnt_retry,
    timer_expiry_handoff,
    delayed_requeue_state_window,
    last_pool_lock_handoff,
    callback_execution_outside_pool_lock,
    idle_sleep_transition,
    mayday_lock_then_pool_lock,
    scheduler_callback_under_pool_lock,
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

const boundary_areas = [_]BoundaryArea{
    .{
        .id = "submission-routing",
        .summary = "Map the public queueing entrypoints and the internal pwq handoff without claiming live enqueue execution.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "queue_work_on", "__queue_work" },
        .rationale = "This is the smallest honest starting point for workqueue.c because it records where work submission crosses from callers into pool_workqueue routing before any locking, pool wakeup, or worker execution is mirrored in Zig.",
    },
    .{
        .id = "delayed-submission-aliases",
        .summary = "Record the delayed-work submission aliases before claiming any timer-driven enqueue behavior.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "queue_delayed_work_on", "mod_delayed_work_on", "__queue_delayed_work" },
        .rationale = "These entrypoints decide whether delayed work stays on the timer path or falls back to immediate queueing, but the live timer-base choice, expiry ownership, and requeue behavior remain in C for Phase 14.",
    },
    .{
        .id = "delayed-requeue-ownership",
        .summary = "Keep delayed-work requeue ownership explicitly in C even after the timer-expiry handoff has been mapped.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "mod_delayed_work_on", "__queue_delayed_work", "delayed_work_timer_fn" },
        .rationale = "The mod_delayed_work_on() path decides whether to steal pending state, retarget the timer base, preserve CPU affinity, or fall through to immediate queueing, so Zigux should record that ownership boundary rather than pretend a wrapper can safely own delayed-work requeue rules.",
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

const audit_checkpoints = [_]AuditCheckpoint{
    .{
        .id = "manager-role-serialization",
        .anchor_symbol = "manage_workers",
        .summary = "Record that only one manager may own a pool at a time even though worker creation can drop and reacquire the pool lock.",
        .guard = .pool_lock_released_and_reacquired,
        .observed_fields = &[_][]const u8{ "pool->flags", "pool->manager" },
        .blocked_by = "manage_workers() flips POOL_MANAGER_ACTIVE and pool->manager before maybe_create_worker() drops and regrabs pool->lock, so Zigux should audit the single-manager contract rather than claim a live wrapper.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "worker-pool-forward-progress",
        .anchor_symbol = "struct worker_pool",
        .summary = "Keep forward-progress and runnable-worker accounting under the existing worker_pool lock discipline.",
        .guard = .pool_lock_held,
        .observed_fields = &[_][]const u8{ "pool->last_progress_ts", "pool->nr_running", "pool->worklist" },
        .blocked_by = "worker_pool forward-progress timestamps, runnable counts, and pending worklist state are all lock-coupled and watchdog-adjacent, so Phase 14 should only name the fields and leave the live updates in C.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "max-active-ordering-gate",
        .anchor_symbol = "__queue_work",
        .summary = "Keep max_active throttling and ordered-workqueue inactive-list placement under the existing pool and pwq lock discipline.",
        .guard = .pool_lock_held,
        .observed_fields = &[_][]const u8{ "pwq->inactive_works", "pwq->nr_active", "wq->max_active", "pool->last_progress_ts" },
        .blocked_by = "__queue_work() decides between pool->worklist and pwq->inactive_works while holding pool->lock, and the same gate preserves ordered-workqueue sequencing when max_active changes, so Zigux should audit the inactive-list and max_active seam rather than claim a live enqueue wrapper.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "pending-bit-claim-handoff",
        .anchor_symbol = "try_to_grab_pending/queue_work_on",
        .summary = "Keep the pending-bit claim window and disable-or-offline checks under the existing irq-disabled handoff before pool routing begins.",
        .guard = .pending_bit_claim_window,
        .observed_fields = &[_][]const u8{ "work->data", "WORK_STRUCT_PENDING", "WORK_OFFQ_DISABLE_BITS" },
        .blocked_by = "queue_work_on() relies on try_to_grab_pending() to claim PENDING while irq state, cancel state, and off-queue disable bits are still authoritative, so Zigux should record the claim window instead of pretending a wrapper can safely own the first submission race.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "unbound-pwq-refcnt-retry",
        .anchor_symbol = "__queue_work",
        .summary = "Record the retry contract that keeps an unbound pwq referenced while pool selection can be retried under changing affinity or pod state.",
        .guard = .unbound_pwq_refcnt_retry,
        .observed_fields = &[_][]const u8{ "pwq->refcnt", "wq->dfl_pwq", "pwq->pool" },
        .blocked_by = "Unbound __queue_work() can loop until get_unbound_pool() and the selected pwq remain stable, and that retry depends on pwq->refcnt ownership plus pool selection that still belongs to the C worker topology.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "delayed-submission-alias-handoff",
        .anchor_symbol = "queue_delayed_work_on/mod_delayed_work_on/__queue_delayed_work",
        .summary = "Record how delayed-work submission aliases share one timer-gated enqueue handoff without claiming live timer expiry ownership.",
        .guard = .delayed_submission_alias_window,
        .observed_fields = &[_][]const u8{ "dwork->timer", "dwork->wq", "dwork->cpu", "work->data" },
        .blocked_by = "queue_delayed_work_on() and mod_delayed_work_on() both funnel through __queue_delayed_work(), where timer state, target CPU selection, and the final queue handoff still depend on C-owned delayed_work rules, so Zigux should audit the alias fan-in rather than pretend a wrapper owns timer-driven submission.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "delayed-timer-expiry-handoff",
        .anchor_symbol = "delayed_work_timer_fn",
        .summary = "Record the timer-expiry handoff that clears timer-owned state and re-enters __queue_work() without claiming live delayed-work requeue ownership.",
        .guard = .timer_expiry_handoff,
        .observed_fields = &[_][]const u8{ "dwork->timer", "dwork->wq", "dwork->cpu", "work->data" },
        .blocked_by = "delayed_work_timer_fn() decides whether timer expiry may queue the embedded work, clears timer-owned state, and then hands back into __queue_work(), so timer-base, CPU-affinity, and requeue ownership remain C-owned even after Zigux records the handoff.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "delayed-requeue-ownership-gate",
        .anchor_symbol = "mod_delayed_work_on",
        .summary = "Record that delayed-work requeue ownership still belongs to C when mod_delayed_work_on() decides whether to retarget the timer, preserve CPU affinity, or queue immediately.",
        .guard = .delayed_requeue_state_window,
        .observed_fields = &[_][]const u8{ "dwork->timer", "dwork->cpu", "dwork->wq", "work->data" },
        .blocked_by = "mod_delayed_work_on() may steal pending state, decide whether the timer can be modified in place, preserve or retarget CPU affinity, or fall through to immediate queueing, so Zigux should record that requeue gate rather than claim ownership of delayed-work rearm semantics.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "last-pool-reentrancy-handoff",
        .anchor_symbol = "__queue_work",
        .summary = "Record how __queue_work() may lock the previous pool first to preserve non-reentrancy before handing back to the selected pwq or pool.",
        .guard = .last_pool_lock_handoff,
        .observed_fields = &[_][]const u8{ "last_pool->lock", "worker->current_pwq", "pwq->refcnt", "work->data" },
        .blocked_by = "__queue_work() can grab last_pool->lock, inspect find_worker_executing_work(), and then either stay on worker->current_pwq or unlock and relock the selected pool, so Phase 14 should record that lock handoff instead of claiming a live enqueue wrapper across pools.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "process-one-work-execution-window",
        .anchor_symbol = "process_one_work",
        .summary = "Keep the callback execution window under the existing unlock, relock, and in-flight accounting discipline.",
        .guard = .callback_execution_outside_pool_lock,
        .observed_fields = &[_][]const u8{ "worker->current_work", "worker->current_pwq", "pwq->stats[PWQ_STAT_STARTED]", "pwq->nr_in_flight" },
        .blocked_by = "process_one_work() clears PENDING, drops pool->lock before worker->current_func(work), then reacquires pool->lock before completion stats and pwq_dec_nr_in_flight(), so Zigux should audit the execution window rather than claim a live callback wrapper.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "worker-thread-idle-sleep-handoff",
        .anchor_symbol = "worker_thread",
        .summary = "Track the idle entry and wakeup path that sets TASK_IDLE before pool->lock is released and schedule() runs.",
        .guard = .idle_sleep_transition,
        .observed_fields = &[_][]const u8{ "worker->flags", "pool->worklist", "pool->lock", "worker->scheduled" },
        .blocked_by = "worker_thread() enters idle, sets TASK_IDLE while holding pool->lock, releases the lock, and only then sleeps until a wakeup reacquires the same lock and calls worker_leave_idle(), so the sleep or wake transition remains a stay-in-C concurrency boundary.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "scheduler-running-hooks",
        .anchor_symbol = "wq_worker_running/wq_worker_sleeping",
        .summary = "Track the scheduler-facing running and sleeping callbacks as a separate audit surface tied to worker flags and nr_running transitions.",
        .guard = .scheduler_callback_under_pool_lock,
        .observed_fields = &[_][]const u8{ "worker->flags", "pool->nr_running" },
        .blocked_by = "The scheduler-visible hooks adjust WORKER_NOT_RUNNING state and nr_running while coordinating wakeups under pool->lock, which is exactly the sort of live concurrency ownership Zigux should keep in C.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "rescuer-mayday-handoff",
        .anchor_symbol = "rescuer_thread",
        .summary = "Capture the rescuer's mayday-list handoff into pool-locked rescue work without claiming the execution loop itself.",
        .guard = .mayday_lock_then_pool_lock,
        .observed_fields = &[_][]const u8{ "wq->maydays", "pwq->nr_active", "pwq->mayday_cursor" },
        .blocked_by = "rescuer_thread() walks wq->maydays, attaches to a pool, rescues pending work, and then kicks regular workers again, so the whole handoff remains a stay-in-C concurrency boundary.",
        .ownership = .stay_in_c,
    },
};

const blocked_live_behaviors = [_][]const u8{
    "live worker_pool execution",
    "pool draining and flush completion",
    "delayed-work requeue ownership",
    "scheduler callback parity",
    "rescuer execution ownership",
    "hotplug-driven worker migration",
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

    pub fn stayInCDecisionCount() usize {
        var count: usize = 0;
        for (boundary_areas) |area| {
            if (area.ownership == .stay_in_c) {
                count += 1;
            }
        }
        return count;
    }

    pub fn auditCheckpointCount() usize {
        return audit_checkpoints.len;
    }

    pub fn nextAuditFocus() []const u8 {
        return "Leave this lane in blocked maintenance; hotplug-driven worker migration and flush-drain ownership stay in C even after the delayed_work_timer_fn() handoff and mod_delayed_work_on() requeue governance note.";
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
    try std.testing.expectEqual(@as(usize, 7), map.areas.len);
    try std.testing.expectEqual(@as(usize, 3), WorkqueueBridgeLab.stayInCDecisionCount());
    try std.testing.expect(std.mem.indexOf(u8, WorkqueueBridgeLab.nextAuditFocus(), "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, WorkqueueBridgeLab.nextAuditFocus(), "mod_delayed_work_on()") != null);

    try std.testing.expectEqualStrings("submission-routing", map.areas[0].id);
    try std.testing.expect(map.areas[0].ownership == .boundary_map_only);
    try std.testing.expectEqualStrings("queue_work_on", map.areas[0].anchor_symbols[0]);
    try std.testing.expectEqualStrings("__queue_work", map.areas[0].anchor_symbols[1]);

    try std.testing.expectEqualStrings("delayed-submission-aliases", map.areas[1].id);
    try std.testing.expect(map.areas[1].ownership == .boundary_map_only);
    try std.testing.expectEqualStrings("queue_delayed_work_on", map.areas[1].anchor_symbols[0]);
    try std.testing.expectEqualStrings("__queue_delayed_work", map.areas[1].anchor_symbols[2]);

    try std.testing.expectEqualStrings("delayed-requeue-ownership", map.areas[2].id);
    try std.testing.expect(map.areas[2].ownership == .stay_in_c);
    try std.testing.expectEqualStrings("mod_delayed_work_on", map.areas[2].anchor_symbols[0]);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[2].rationale, "CPU affinity") != null);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[2].rationale, "immediate queueing") != null);

    try std.testing.expectEqualStrings("worker-pool-concurrency", map.areas[5].id);
    try std.testing.expect(map.areas[5].ownership == .stay_in_c);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[5].rationale, "forward-progress") != null);

    try std.testing.expectEqualStrings("rescuer-and-scheduler-hooks", map.areas[6].id);
    try std.testing.expect(map.areas[6].ownership == .stay_in_c);
    try std.testing.expectEqualStrings("wq_worker_running", map.areas[6].anchor_symbols[1]);
    try std.testing.expectEqualStrings("wq_worker_sleeping", map.areas[6].anchor_symbols[2]);
}

test "workqueue bridge concurrency audit stays review-only" {
    const audit = WorkqueueBridgeLab.concurrencyAudit();

    try std.testing.expectEqualStrings("kernel/workqueue.c", audit.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", audit.posture);
    try std.testing.expectEqual(@as(usize, 13), audit.checkpoints.len);
    try std.testing.expectEqual(@as(usize, 6), audit.blocked_live_behaviors.len);
    try std.testing.expectEqual(@as(usize, 13), WorkqueueBridgeLab.auditCheckpointCount());
    try std.testing.expect(std.mem.indexOf(u8, audit.next_step, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.next_step, "hotplug-driven worker migration") != null);

    try std.testing.expectEqualStrings("manager-role-serialization", audit.checkpoints[0].id);
    try std.testing.expect(audit.checkpoints[0].guard == .pool_lock_released_and_reacquired);
    try std.testing.expectEqualStrings("pool->manager", audit.checkpoints[0].observed_fields[1]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[0].blocked_by, "POOL_MANAGER_ACTIVE") != null);

    try std.testing.expectEqualStrings("worker-pool-forward-progress", audit.checkpoints[1].id);
    try std.testing.expect(audit.checkpoints[1].guard == .pool_lock_held);
    try std.testing.expectEqualStrings("pool->last_progress_ts", audit.checkpoints[1].observed_fields[0]);

    try std.testing.expectEqualStrings("max-active-ordering-gate", audit.checkpoints[2].id);
    try std.testing.expect(audit.checkpoints[2].guard == .pool_lock_held);
    try std.testing.expectEqualStrings("pwq->inactive_works", audit.checkpoints[2].observed_fields[0]);
    try std.testing.expectEqualStrings("wq->max_active", audit.checkpoints[2].observed_fields[2]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[2].blocked_by, "ordered-workqueue") != null);

    try std.testing.expectEqualStrings("pending-bit-claim-handoff", audit.checkpoints[3].id);
    try std.testing.expect(audit.checkpoints[3].guard == .pending_bit_claim_window);
    try std.testing.expectEqualStrings("WORK_STRUCT_PENDING", audit.checkpoints[3].observed_fields[1]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[3].blocked_by, "first submission race") != null);

    try std.testing.expectEqualStrings("unbound-pwq-refcnt-retry", audit.checkpoints[4].id);
    try std.testing.expect(audit.checkpoints[4].guard == .unbound_pwq_refcnt_retry);
    try std.testing.expectEqualStrings("pwq->refcnt", audit.checkpoints[4].observed_fields[0]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[4].blocked_by, "get_unbound_pool()") != null);

    try std.testing.expectEqualStrings("delayed-submission-alias-handoff", audit.checkpoints[5].id);
    try std.testing.expect(audit.checkpoints[5].guard == .delayed_submission_alias_window);
    try std.testing.expectEqualStrings("dwork->timer", audit.checkpoints[5].observed_fields[0]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[5].blocked_by, "alias fan-in") != null);

    try std.testing.expectEqualStrings("delayed-timer-expiry-handoff", audit.checkpoints[6].id);
    try std.testing.expect(audit.checkpoints[6].guard == .timer_expiry_handoff);
    try std.testing.expectEqualStrings("dwork->wq", audit.checkpoints[6].observed_fields[1]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[6].blocked_by, "timer-base") != null);

    try std.testing.expectEqualStrings("delayed-requeue-ownership-gate", audit.checkpoints[7].id);
    try std.testing.expect(audit.checkpoints[7].guard == .delayed_requeue_state_window);
    try std.testing.expectEqualStrings("dwork->cpu", audit.checkpoints[7].observed_fields[1]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[7].blocked_by, "immediate queueing") != null);

    try std.testing.expectEqualStrings("last-pool-reentrancy-handoff", audit.checkpoints[8].id);
    try std.testing.expect(audit.checkpoints[8].guard == .last_pool_lock_handoff);
    try std.testing.expectEqualStrings("pwq->refcnt", audit.checkpoints[8].observed_fields[2]);

    try std.testing.expectEqualStrings("process-one-work-execution-window", audit.checkpoints[9].id);
    try std.testing.expect(audit.checkpoints[9].guard == .callback_execution_outside_pool_lock);
    try std.testing.expectEqualStrings("pwq->nr_in_flight", audit.checkpoints[9].observed_fields[3]);

    try std.testing.expectEqualStrings("worker-thread-idle-sleep-handoff", audit.checkpoints[10].id);
    try std.testing.expect(audit.checkpoints[10].guard == .idle_sleep_transition);
    try std.testing.expectEqualStrings("pool->lock", audit.checkpoints[10].observed_fields[2]);

    try std.testing.expectEqualStrings("scheduler-running-hooks", audit.checkpoints[11].id);
    try std.testing.expect(audit.checkpoints[11].guard == .scheduler_callback_under_pool_lock);
    try std.testing.expectEqualStrings("pool->nr_running", audit.checkpoints[11].observed_fields[1]);

    try std.testing.expectEqualStrings("rescuer-mayday-handoff", audit.checkpoints[12].id);
    try std.testing.expect(audit.checkpoints[12].guard == .mayday_lock_then_pool_lock);
    try std.testing.expectEqualStrings("pwq->mayday_cursor", audit.checkpoints[12].observed_fields[2]);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].blocked_by, "kicks regular workers") != null);
}
