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
    last_pool_lock_handoff,
    callback_execution_outside_pool_lock,
    idle_sleep_transition,
    mayday_lock_then_pool_lock,
    scheduler_callback_under_pool_lock,
    pending_bit_claim_window,
    delayed_timer_handoff,
    delayed_requeue_or_immediate_fallthrough,
    flush_color_progression,
    hotplug_topology_rebind,
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
    current_slice_id: []const u8,
    next_step: []const u8,
};

pub const MaintenanceHandoff = struct {
    posture: []const u8,
    reread_surfaces: []const []const u8,
    reopen_conditions: []const []const u8,
    next_future_target: []const u8,
};

pub const CancelPathHandoff = struct {
    anchor_symbol: []const u8,
    ownership: Ownership,
    observed_fields: []const []const u8,
    blocked_by: []const u8,
};

pub const FlushDrainHandoff = struct {
    anchor_symbol: []const u8,
    ownership: Ownership,
    observed_fields: []const []const u8,
    blocked_by: []const u8,
    current_slice_id: []const u8,
    next_focus: []const u8,
};

pub const SchedulerVisibleWorkerStateHandoff = struct {
    running_anchor_symbol: []const u8,
    sleeping_anchor_symbol: []const u8,
    ownership: Ownership,
    observed_fields: []const []const u8,
    blocked_by: []const u8,
    current_slice_id: []const u8,
    next_focus: []const u8,
};

pub const MaxActiveRetuningHandoff = struct {
    anchor_symbol: []const u8,
    ownership: Ownership,
    observed_fields: []const []const u8,
    blocked_by: []const u8,
    current_slice_id: []const u8,
    next_focus: []const u8,
};

pub const WrapperCandidate = struct {
    id: []const u8,
    summary: []const u8,
    ownership: Ownership,
    anchor_symbols: []const []const u8,
    blocked_by: []const u8,
};

pub const WrapperCandidatePacket = struct {
    posture: []const u8,
    candidates: []const WrapperCandidate,
    current_slice_id: []const u8,
    next_focus: []const u8,
};

const boundary_areas = [_]BoundaryArea{
    .{
        .id = "submission-routing",
        .summary = "Map the public queueing entrypoints and the internal pwq handoff without claiming live enqueue execution.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "queue_work_on", "__queue_work" },
        .rationale = "This remains the smallest honest starting point because it records where callers cross into pool_workqueue routing before any wakeup, retry, or callback execution is mirrored in Zig.",
    },
    .{
        .id = "allocation-and-attrs",
        .summary = "Document the workqueue allocation and attribute surface as a future wrapper candidate, not a live allocator port.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "__alloc_workqueue", "devm_alloc_workqueue" },
        .rationale = "Allocation and attribute shaping are reviewable metadata boundaries, but the implementation still depends on rescue policy, affinity, lifetime, and memory-ordering rules that remain in C.",
    },
    .{
        .id = "delayed-work-timer-and-requeue",
        .summary = "Keep delayed-work timer expiry, timer rearm, CPU affinity, and requeue fallthrough explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "queue_delayed_work_on", "mod_delayed_work_on", "delayed_work_timer_fn" },
        .rationale = "Delayed-work submission now has a reviewable audit trail, but timer-base ownership, in-place rearm, and immediate queueing fallthrough remain part of the live C runtime.",
    },
    .{
        .id = "flush-drain-and-cancel",
        .summary = "Keep flush, drain, and cancellation completion ownership explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "__flush_workqueue", "drain_workqueue", "__cancel_work_sync" },
        .rationale = "The bridge can now point directly at insert_wq_barrier(), start_flush_work(), WORK_OFFQ_DISABLE_BITS, disable_work(), __flush_work(), and WORK_OFFQ_CANCELING as the flush-start plus cancel-disable-depth and cancel-completion seams, but those waits still depend on active-color progression, chained flushers, cancellation disable depth, cancellation wait state, and worker progress owned by the current C implementation.",
    },
    .{
        .id = "worker-pool-concurrency",
        .summary = "Keep worker-pool concurrency management explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "manage_workers", "struct worker_pool" },
        .rationale = "The pool manager owns worker creation, idle culling, busy hashing, forward-progress checks, and lock-protected state transitions; Zigux should continue auditing this core instead of claiming a wrapper.",
    },
    .{
        .id = "runtime-max-active-retuning",
        .summary = "Keep runtime max_active retuning and inactive-list promotion explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "workqueue_set_max_active", "__queue_work" },
        .rationale = "The bridge records the inactive-list seam, but live `max_active` tuning still interacts with ordered-workqueue sequencing and in-flight state under the existing lock model.",
    },
    .{
        .id = "hotplug-topology-rebinding",
        .summary = "Keep CPU-hotplug rebinding and unbound topology updates explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "wq_update_unbound_numa", "unbound_wq_update_pwq" },
        .rationale = "Hotplug transitions still own pool association, pod or NUMA layout, and unbound pwq rebinding in the current C implementation.",
    },
    .{
        .id = "rescuer-and-scheduler-hooks",
        .summary = "Keep rescuer threads, mayday handling, and scheduler-visible worker state explicitly in C.",
        .ownership = .stay_in_c,
        .anchor_symbols = &[_][]const u8{ "rescuer_thread", "wq_worker_running", "wq_worker_sleeping" },
        .rationale = "These hooks coordinate scheduler-visible worker state, mayday rescue, CPU association, and watchdog-adjacent progress signals, so Phase 14 should keep them review-only.",
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
        .blocked_by = "__queue_work() decides between pool->worklist and pwq->inactive_works while holding pool->lock, and the same gate preserves ordered-workqueue sequencing when max_active changes, so Zigux should audit the inactive-list seam rather than claim a live enqueue wrapper.",
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
    .{
        .id = "pending-bit-claim-window",
        .anchor_symbol = "try_to_grab_pending",
        .summary = "Record pending-bit claim, disable-irqs windows, and the unbound retry seam without claiming live submission control.",
        .guard = .pending_bit_claim_window,
        .observed_fields = &[_][]const u8{ "WORK_STRUCT_PENDING_BIT", "work->data", "pwq->refcnt" },
        .blocked_by = "try_to_grab_pending(), queue_work_on(), and the unbound __queue_work() retry path coordinate pending ownership, irq-disable state, and pwq reselection under the live C locking and refcount model.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "delayed-submission-aliases",
        .anchor_symbol = "queue_delayed_work_on/__queue_delayed_work",
        .summary = "Record delayed submission aliases as timer-backed queueing entrypoints rather than new execution ownership.",
        .guard = .pool_lock_held,
        .observed_fields = &[_][]const u8{ "dwork->wq", "timer->expires", "cpu" },
        .blocked_by = "queue_delayed_work_on(), mod_delayed_work_on(), and __queue_delayed_work() share timer-backed submission ownership that still belongs to the C runtime.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "delayed-timer-expiry-handoff",
        .anchor_symbol = "delayed_work_timer_fn",
        .summary = "Record the timer expiry handoff back into __queue_work() without claiming runtime timer ownership.",
        .guard = .delayed_timer_handoff,
        .observed_fields = &[_][]const u8{ "timer->function", "dwork->work.data", "cpu" },
        .blocked_by = "delayed_work_timer_fn() consumes timer-base ownership and CPU affinity before handing back into __queue_work(), which remains a live C boundary.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "delayed-requeue-governance",
        .anchor_symbol = "mod_delayed_work_on",
        .summary = "Keep delayed-work rearm and immediate queueing fallthrough under explicit stay-in-C governance.",
        .guard = .delayed_requeue_or_immediate_fallthrough,
        .observed_fields = &[_][]const u8{ "dwork->timer", "cpu", "delay" },
        .blocked_by = "mod_delayed_work_on() can preserve timer state, rearm in place, or fall through to immediate queueing, so CPU affinity and timer-base ownership stay in C.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "flush-drain-color-governance",
        .anchor_symbol = "start_flush_work/__flush_workqueue",
        .summary = "Keep flush barriers, flusher-color progression, cancellation disable-depth fallback, cancellation completion waits, and in-flight tracking under explicit stay-in-C governance.",
        .guard = .flush_color_progression,
        .observed_fields = &[_][]const u8{ "wq->work_color", "wq->flush_color", "wq->nr_pwqs_to_flush", "wq->first_flusher", "pwq->nr_in_flight", "WORK_OFFQ_CANCELING", "work->data", "WORK_OFFQ_DISABLE_BITS" },
        .blocked_by = "insert_wq_barrier(), start_flush_work(), __flush_workqueue(), drain_workqueue(), __cancel_work_sync(), disable_work(), and __flush_work() still coordinate active-color progression, first-flusher handoff, in-flight progression, cancellation disable depth, cancellation wait bits, WORK_OFFQ_DISABLE_BITS preservation, and WORK_OFFQ_CANCELING completion under the current C runtime.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "hotplug-topology-rebinding",
        .anchor_symbol = "unbound_wq_update_pwq",
        .summary = "Keep CPU-hotplug pool rebinding and unbound topology transitions explicitly in C.",
        .guard = .hotplug_topology_rebind,
        .observed_fields = &[_][]const u8{ "POOL_DISASSOCIATED", "wq_online_cpumask", "wq_unbound_cpumask" },
        .blocked_by = "POOL_DISASSOCIATED flips, online-cpumask updates, and unbound pwq topology rebinding still belong to the current C implementation.",
        .ownership = .stay_in_c,
    },
    .{
        .id = "scheduler-visible-worker-state-refinement",
        .anchor_symbol = "wq_worker_running/wq_worker_sleeping",
        .summary = "Keep scheduler-visible worker-state transitions and wakeup decisions explicitly in C.",
        .guard = .scheduler_callback_under_pool_lock,
        .observed_fields = &[_][]const u8{ "WORKER_NOT_RUNNING", "pool->nr_running", "pool->flags" },
        .blocked_by = "Scheduler-visible worker-state transitions still coordinate wakeups, runnable counts, and pool flags under pool->lock, so Zigux should keep them in the review-only packet.",
        .ownership = .stay_in_c,
    },
};

const blocked_live_behaviors = [_][]const u8{
    "live worker_pool execution",
    "flush, drain, and cancellation completion ownership",
    "delayed-work requeue control",
    "runtime max_active retuning ownership",
    "scheduler-visible worker-state parity",
    "rescuer execution ownership",
    "hotplug-driven worker migration and topology rebinding",
};

const maintenance_reread_surfaces = [_][]const u8{
    "kernel/workqueue_bridge.zig",
    "zigux/tests/phase14_workqueue_bridge.zig",
    "zigux/tests/phase14_workqueue_reviewability.zig",
    "zigux/tests/phase14_workqueue_bridge_manifest.json",
    "Documentation/zigux/phase14-workqueue-bridge-slice.md",
    "Documentation/zigux/phase14-workqueue-bridge-survey.md",
};

const maintenance_reopen_conditions = [_][]const u8{
    "the bridge, dedicated test, reviewability test, manifest, slice note, or survey note drifts on the blocked-maintenance posture or the blocked live-execution boundary",
    "the directly coupled shared smoke or core traceability packet reintroduces a stale owner label, ready-next record, or blocked-gap record for the workqueue anchor",
    "genuinely narrower stay-in-C evidence appears around delayed-work requeue governance, flush-drain ownership, hotplug topology rebinding, or scheduler-visible worker-state transitions without implying live execution ownership",
};

const cancel_path_observed_fields = [_][]const u8{
    "WORK_OFFQ_DISABLE_BITS",
    "work->data",
    "__flush_work()",
    "disable_work()",
};

const flush_drain_observed_fields = [_][]const u8{
    "wq->work_color",
    "wq->flush_color",
    "wq->nr_pwqs_to_flush",
    "wq->first_flusher",
    "pwq->nr_in_flight",
    "WORK_OFFQ_CANCELING",
    "work->data",
    "WORK_OFFQ_DISABLE_BITS",
};

const scheduler_visible_worker_state_observed_fields = [_][]const u8{
    "WORKER_NOT_RUNNING",
    "pool->nr_running",
    "pool->flags",
};

const max_active_retuning_observed_fields = [_][]const u8{
    "pwq->inactive_works",
    "pwq->nr_active",
    "wq->max_active",
    "pool->last_progress_ts",
};

const wrapper_candidates = [_]WrapperCandidate{
    .{
        .id = "submission-routing",
        .summary = "Keep queue submission routing explicit as the smallest wrapper-first candidate packet without claiming live enqueue or wakeup ownership.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "queue_work_on", "__queue_work" },
        .blocked_by = "queue_work_on() and __queue_work() are still coupled to pending-bit claims, cross-pool reentrancy, pwq selection, and wakeup ownership under the live C lock model, so the current Zigux surface stays descriptive rather than becoming a live wrapper.",
    },
    .{
        .id = "allocation-and-attrs",
        .summary = "Keep allocation and attribute shaping explicit as a wrapper-first candidate packet without claiming allocator or rescuer ownership.",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "__alloc_workqueue", "devm_alloc_workqueue" },
        .blocked_by = "__alloc_workqueue() and devm_alloc_workqueue() are still coupled to rescuer policy, affinity scopes, ordered-workqueue rules, lifetime ownership, and memory-ordering semantics in the current C runtime, so Zigux keeps them as reviewable metadata boundaries only.",
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

    pub fn concurrencyAudit() ConcurrencyAudit {
        return .{
            .anchor = descriptor().anchor,
            .posture = descriptor().posture,
            .checkpoints = audit_checkpoints[0..],
            .blocked_live_behaviors = blocked_live_behaviors[0..],
            .current_slice_id = currentSliceId(),
            .next_step = nextAuditFocus(),
        };
    }

    pub fn maintenanceHandoff() MaintenanceHandoff {
        return .{
            .posture = "blocked_maintenance",
            .reread_surfaces = maintenance_reread_surfaces[0..],
            .reopen_conditions = maintenance_reopen_conditions[0..],
            .next_future_target = "Keep the packet in blocked maintenance and reread the bridge, dedicated tests, manifest, slice note, and survey note together before touching any broader Phase 14 shared reminder surface.",
        };
    }

    pub fn cancelPathHandoff() CancelPathHandoff {
        return .{
            .anchor_symbol = "__cancel_work_sync",
            .ownership = .stay_in_c,
            .observed_fields = cancel_path_observed_fields[0..],
            .blocked_by = "__cancel_work_sync() may preserve disable depth through disable_work() before falling back to __flush_work(), so cancellation completion stays inside the live C pending-bit and completion rules rather than becoming a Zig wrapper claim.",
        };
    }

    pub fn flushDrainHandoff() FlushDrainHandoff {
        return .{
            .anchor_symbol = "start_flush_work/__flush_workqueue",
            .ownership = .stay_in_c,
            .observed_fields = flush_drain_observed_fields[0..],
            .blocked_by = "insert_wq_barrier(), start_flush_work(), __flush_workqueue(), __cancel_work_sync(), disable_work(), and __flush_work() still coordinate active-color progression, first-flusher handoff, in-flight draining, cancellation disable depth, cancellation wait bits, WORK_OFFQ_DISABLE_BITS preservation, and WORK_OFFQ_CANCELING completion under the live C runtime, so flush and drain ownership stay explicit and in C rather than becoming a Zig wrapper claim.",
            .current_slice_id = currentSliceId(),
            .next_focus = maintenanceHandoff().next_future_target,
        };
    }

    pub fn schedulerVisibleWorkerStateHandoff() SchedulerVisibleWorkerStateHandoff {
        return .{
            .running_anchor_symbol = "wq_worker_running",
            .sleeping_anchor_symbol = "wq_worker_sleeping",
            .ownership = .stay_in_c,
            .observed_fields = scheduler_visible_worker_state_observed_fields[0..],
            .blocked_by = "wq_worker_running() and wq_worker_sleeping() still coordinate WORKER_NOT_RUNNING, runnable-count updates, worker wakeups, and pool flags under pool->lock, so the scheduler-visible worker-state transition remains explicit stay-in-C evidence rather than a live hook wrapper claim.",
            .current_slice_id = currentSliceId(),
            .next_focus = maintenanceHandoff().next_future_target,
        };
    }

    pub fn maxActiveRetuningHandoff() MaxActiveRetuningHandoff {
        return .{
            .anchor_symbol = "workqueue_set_max_active/__queue_work",
            .ownership = .stay_in_c,
            .observed_fields = max_active_retuning_observed_fields[0..],
            .blocked_by = "workqueue_set_max_active() and __queue_work() still coordinate inactive-list promotion, ordered-workqueue sequencing, runtime max_active retuning, and forward-progress visibility under the live pool and pwq lock model, so this remains explicit stay-in-C governance rather than a wrapper claim.",
            .current_slice_id = currentSliceId(),
            .next_focus = maintenanceHandoff().next_future_target,
        };
    }

    pub fn wrapperCandidatePacket() WrapperCandidatePacket {
        return .{
            .posture = descriptor().posture,
            .candidates = wrapper_candidates[0..],
            .current_slice_id = currentSliceId(),
            .next_focus = maintenanceHandoff().next_future_target,
        };
    }

    pub fn stayInCDecisionCount() usize {
        var count: usize = 0;
        for (boundary_areas) |area| {
            if (area.ownership == .stay_in_c) count += 1;
        }
        return count;
    }

    pub fn auditCheckpointCount() usize {
        return audit_checkpoints.len;
    }

    pub fn wrapperCandidateCount() usize {
        return wrapper_candidates.len;
    }

    pub fn currentSliceId() []const u8 {
        return "phase14-workqueue-scheduler-visible-worker-state-refinement";
    }

    pub fn nextAuditFocus() []const u8 {
        return maintenanceHandoff().next_future_target;
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

test "workqueue bridge boundary map records blocked-maintenance stay-in-c areas" {
    const map = WorkqueueBridgeLab.boundaryMap();

    try std.testing.expectEqualStrings("kernel/workqueue.c", map.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", map.posture);
    try std.testing.expectEqual(@as(usize, 8), map.areas.len);
    try std.testing.expectEqual(@as(usize, 6), WorkqueueBridgeLab.stayInCDecisionCount());
    try std.testing.expectEqualStrings("submission-routing", map.areas[0].id);
    try std.testing.expect(map.areas[0].ownership == .boundary_map_only);
    try std.testing.expectEqualStrings("queue_work_on", map.areas[0].anchor_symbols[0]);
    try std.testing.expectEqualStrings("delayed-work-timer-and-requeue", map.areas[2].id);
    try std.testing.expect(map.areas[2].ownership == .stay_in_c);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[2].rationale, "timer-base") != null);
    try std.testing.expectEqualStrings("hotplug-topology-rebinding", map.areas[6].id);
    try std.testing.expect(map.areas[6].ownership == .stay_in_c);
    try std.testing.expectEqualStrings("rescuer-and-scheduler-hooks", map.areas[7].id);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[3].rationale, "insert_wq_barrier()") != null);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[3].rationale, "start_flush_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[3].rationale, "WORK_OFFQ_DISABLE_BITS") != null);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[3].rationale, "disable_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[3].rationale, "__flush_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[3].rationale, "WORK_OFFQ_CANCELING") != null);
    try std.testing.expect(std.mem.indexOf(u8, map.areas[3].rationale, "disable depth") != null);
}

test "workqueue bridge wrapper candidates stay explicit and non-executing" {
    const packet = WorkqueueBridgeLab.wrapperCandidatePacket();

    try std.testing.expectEqualStrings("boundary_map_only", packet.posture);
    try std.testing.expectEqual(@as(usize, 2), packet.candidates.len);
    try std.testing.expectEqual(@as(usize, 2), WorkqueueBridgeLab.wrapperCandidateCount());
    try std.testing.expectEqualStrings(WorkqueueBridgeLab.currentSliceId(), packet.current_slice_id);
    try std.testing.expectEqualStrings("submission-routing", packet.candidates[0].id);
    try std.testing.expect(packet.candidates[0].ownership == .boundary_map_only);
    try std.testing.expectEqualStrings("queue_work_on", packet.candidates[0].anchor_symbols[0]);
    try std.testing.expectEqualStrings("__queue_work", packet.candidates[0].anchor_symbols[1]);
    try std.testing.expect(std.mem.indexOf(u8, packet.candidates[0].blocked_by, "pending-bit claims") != null);
    try std.testing.expect(std.mem.indexOf(u8, packet.candidates[0].blocked_by, "live wrapper") != null);
    try std.testing.expectEqualStrings("allocation-and-attrs", packet.candidates[1].id);
    try std.testing.expect(packet.candidates[1].ownership == .boundary_map_only);
    try std.testing.expectEqualStrings("__alloc_workqueue", packet.candidates[1].anchor_symbols[0]);
    try std.testing.expectEqualStrings("devm_alloc_workqueue", packet.candidates[1].anchor_symbols[1]);
    try std.testing.expect(std.mem.indexOf(u8, packet.candidates[1].blocked_by, "rescuer policy") != null);
    try std.testing.expect(std.mem.indexOf(u8, packet.candidates[1].blocked_by, "ordered-workqueue rules") != null);
    try std.testing.expect(std.mem.indexOf(u8, packet.next_focus, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, packet.next_focus, "shared reminder surface") != null);
}

test "workqueue bridge concurrency audit matches blocked-maintenance packet" {
    const audit = WorkqueueBridgeLab.concurrencyAudit();

    try std.testing.expectEqualStrings("kernel/workqueue.c", audit.anchor);
    try std.testing.expectEqualStrings("boundary_map_only", audit.posture);
    try std.testing.expectEqual(@as(usize, 15), audit.checkpoints.len);
    try std.testing.expectEqual(@as(usize, 7), audit.blocked_live_behaviors.len);
    try std.testing.expectEqual(@as(usize, 15), WorkqueueBridgeLab.auditCheckpointCount());
    try std.testing.expectEqualStrings("phase14-workqueue-scheduler-visible-worker-state-refinement", audit.current_slice_id);
    try std.testing.expect(std.mem.indexOf(u8, audit.next_step, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.next_step, "shared reminder surface") != null);
    try std.testing.expectEqualStrings("pending-bit-claim-window", audit.checkpoints[8].id);
    try std.testing.expect(audit.checkpoints[8].guard == .pending_bit_claim_window);
    try std.testing.expectEqualStrings("delayed-submission-aliases", audit.checkpoints[9].id);
    try std.testing.expectEqualStrings("delayed-timer-expiry-handoff", audit.checkpoints[10].id);
    try std.testing.expectEqualStrings("delayed-requeue-governance", audit.checkpoints[11].id);
    try std.testing.expectEqualStrings("flush-drain-color-governance", audit.checkpoints[12].id);
    try std.testing.expectEqualStrings("hotplug-topology-rebinding", audit.checkpoints[13].id);
    try std.testing.expectEqualStrings("scheduler-visible-worker-state-refinement", audit.checkpoints[14].id);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].anchor_symbol, "start_flush_work") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].summary, "disable-depth fallback") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].observed_fields[2], "nr_pwqs_to_flush") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].observed_fields[3], "first_flusher") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].observed_fields[4], "pwq->nr_in_flight") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].observed_fields[5], "WORK_OFFQ_CANCELING") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].observed_fields[6], "work->data") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].observed_fields[7], "WORK_OFFQ_DISABLE_BITS") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].blocked_by, "insert_wq_barrier()") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].blocked_by, "start_flush_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].blocked_by, "first-flusher") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].blocked_by, "__cancel_work_sync()") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].blocked_by, "disable_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].blocked_by, "__flush_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].blocked_by, "WORK_OFFQ_DISABLE_BITS") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[12].blocked_by, "WORK_OFFQ_CANCELING") != null);
    try std.testing.expect(std.mem.indexOf(u8, audit.checkpoints[13].blocked_by, "POOL_DISASSOCIATED") != null);
}

test "workqueue bridge maintenance handoff keeps blocked-maintenance reread surfaces explicit" {
    const handoff = WorkqueueBridgeLab.maintenanceHandoff();

    try std.testing.expectEqualStrings("blocked_maintenance", handoff.posture);
    try std.testing.expectEqual(@as(usize, 6), handoff.reread_surfaces.len);
    try std.testing.expectEqualStrings("kernel/workqueue_bridge.zig", handoff.reread_surfaces[0]);
    try std.testing.expectEqualStrings("zigux/tests/phase14_workqueue_bridge.zig", handoff.reread_surfaces[1]);
    try std.testing.expectEqualStrings("zigux/tests/phase14_workqueue_reviewability.zig", handoff.reread_surfaces[2]);
    try std.testing.expectEqualStrings("zigux/tests/phase14_workqueue_bridge_manifest.json", handoff.reread_surfaces[3]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase14-workqueue-bridge-slice.md", handoff.reread_surfaces[4]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase14-workqueue-bridge-survey.md", handoff.reread_surfaces[5]);
    try std.testing.expectEqual(@as(usize, 3), handoff.reopen_conditions.len);
    try std.testing.expect(std.mem.indexOf(u8, handoff.reopen_conditions[0], "reviewability test") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff.reopen_conditions[1], "shared smoke or core traceability packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff.reopen_conditions[2], "delayed-work requeue governance") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff.reopen_conditions[2], "scheduler-visible worker-state transitions") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff.next_future_target, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, handoff.next_future_target, "shared reminder surface") != null);
}

test "workqueue bridge cancel-path handoff keeps cancellation completion explicit and in C" {
    const cancel_handoff = WorkqueueBridgeLab.cancelPathHandoff();

    try std.testing.expectEqualStrings("__cancel_work_sync", cancel_handoff.anchor_symbol);
    try std.testing.expect(cancel_handoff.ownership == .stay_in_c);
    try std.testing.expectEqual(@as(usize, 4), cancel_handoff.observed_fields.len);
    try std.testing.expectEqualStrings("WORK_OFFQ_DISABLE_BITS", cancel_handoff.observed_fields[0]);
    try std.testing.expectEqualStrings("work->data", cancel_handoff.observed_fields[1]);
    try std.testing.expectEqualStrings("__flush_work()", cancel_handoff.observed_fields[2]);
    try std.testing.expectEqualStrings("disable_work()", cancel_handoff.observed_fields[3]);
    try std.testing.expect(std.mem.indexOf(u8, cancel_handoff.blocked_by, "disable depth") != null);
    try std.testing.expect(std.mem.indexOf(u8, cancel_handoff.blocked_by, "pending-bit and completion rules") != null);
}

test "workqueue bridge flush-drain handoff keeps flusher and cancellation governance explicit and in C" {
    const flush_handoff = WorkqueueBridgeLab.flushDrainHandoff();

    try std.testing.expectEqualStrings("start_flush_work/__flush_workqueue", flush_handoff.anchor_symbol);
    try std.testing.expect(flush_handoff.ownership == .stay_in_c);
    try std.testing.expectEqual(@as(usize, 8), flush_handoff.observed_fields.len);
    try std.testing.expectEqualStrings("wq->work_color", flush_handoff.observed_fields[0]);
    try std.testing.expectEqualStrings("wq->flush_color", flush_handoff.observed_fields[1]);
    try std.testing.expectEqualStrings("wq->nr_pwqs_to_flush", flush_handoff.observed_fields[2]);
    try std.testing.expectEqualStrings("wq->first_flusher", flush_handoff.observed_fields[3]);
    try std.testing.expectEqualStrings("pwq->nr_in_flight", flush_handoff.observed_fields[4]);
    try std.testing.expectEqualStrings("WORK_OFFQ_CANCELING", flush_handoff.observed_fields[5]);
    try std.testing.expectEqualStrings("work->data", flush_handoff.observed_fields[6]);
    try std.testing.expectEqualStrings("WORK_OFFQ_DISABLE_BITS", flush_handoff.observed_fields[7]);
    try std.testing.expectEqualStrings(WorkqueueBridgeLab.currentSliceId(), flush_handoff.current_slice_id);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "insert_wq_barrier()") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "start_flush_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "first-flusher") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "disable_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "__flush_work()") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "cancellation disable depth") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "WORK_OFFQ_DISABLE_BITS") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "WORK_OFFQ_CANCELING") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.blocked_by, "__cancel_work_sync()") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.next_focus, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, flush_handoff.next_focus, "shared reminder surface") != null);
}

test "workqueue bridge scheduler-visible worker-state handoff stays explicit and in C" {
    const scheduler_handoff = WorkqueueBridgeLab.schedulerVisibleWorkerStateHandoff();

    try std.testing.expectEqualStrings("wq_worker_running", scheduler_handoff.running_anchor_symbol);
    try std.testing.expectEqualStrings("wq_worker_sleeping", scheduler_handoff.sleeping_anchor_symbol);
    try std.testing.expect(scheduler_handoff.ownership == .stay_in_c);
    try std.testing.expectEqual(@as(usize, 3), scheduler_handoff.observed_fields.len);
    try std.testing.expectEqualStrings("WORKER_NOT_RUNNING", scheduler_handoff.observed_fields[0]);
    try std.testing.expectEqualStrings("pool->nr_running", scheduler_handoff.observed_fields[1]);
    try std.testing.expectEqualStrings("pool->flags", scheduler_handoff.observed_fields[2]);
    try std.testing.expectEqualStrings(WorkqueueBridgeLab.currentSliceId(), scheduler_handoff.current_slice_id);
    try std.testing.expect(std.mem.indexOf(u8, scheduler_handoff.blocked_by, "wq_worker_running() and wq_worker_sleeping()") != null);
    try std.testing.expect(std.mem.indexOf(u8, scheduler_handoff.blocked_by, "wakeups") != null);
    try std.testing.expect(std.mem.indexOf(u8, scheduler_handoff.blocked_by, "pool->lock") != null);
    try std.testing.expect(std.mem.indexOf(u8, scheduler_handoff.next_focus, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, scheduler_handoff.next_focus, "shared reminder surface") != null);
}

test "workqueue bridge max-active retuning handoff stays explicit and in C" {
    const retuning_handoff = WorkqueueBridgeLab.maxActiveRetuningHandoff();

    try std.testing.expectEqualStrings("workqueue_set_max_active/__queue_work", retuning_handoff.anchor_symbol);
    try std.testing.expect(retuning_handoff.ownership == .stay_in_c);
    try std.testing.expectEqual(@as(usize, 4), retuning_handoff.observed_fields.len);
    try std.testing.expectEqualStrings("pwq->inactive_works", retuning_handoff.observed_fields[0]);
    try std.testing.expectEqualStrings("pwq->nr_active", retuning_handoff.observed_fields[1]);
    try std.testing.expectEqualStrings("wq->max_active", retuning_handoff.observed_fields[2]);
    try std.testing.expectEqualStrings("pool->last_progress_ts", retuning_handoff.observed_fields[3]);
    try std.testing.expectEqualStrings(WorkqueueBridgeLab.currentSliceId(), retuning_handoff.current_slice_id);
    try std.testing.expect(std.mem.indexOf(u8, retuning_handoff.blocked_by, "inactive-list promotion") != null);
    try std.testing.expect(std.mem.indexOf(u8, retuning_handoff.blocked_by, "ordered-workqueue sequencing") != null);
    try std.testing.expect(std.mem.indexOf(u8, retuning_handoff.blocked_by, "runtime max_active retuning") != null);
    try std.testing.expect(std.mem.indexOf(u8, retuning_handoff.blocked_by, "stay-in-C governance") != null);
    try std.testing.expect(std.mem.indexOf(u8, retuning_handoff.next_focus, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, retuning_handoff.next_focus, "shared reminder surface") != null);
}
