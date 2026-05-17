const std = @import("std");

pub const lane_key = "P14-L04";
pub const phase = "Phase 14";
pub const anchor = "kernel/workqueue.c";
pub const recommended_destination = "kernel/workqueue_bridge.zig";
pub const ready_next_gap = "phase14-workqueue-flush-color-followup";
pub const blocked_gap = "phase14-workqueue-live-execution-blocker";

pub const AuditKind = enum {
    boundary_map,
    concurrency_audit,
    stay_in_c,
};

pub const Ownership = enum {
    review_only,
    stay_in_c,
    blocked_on_live_concurrency,
};

pub const Audit = struct {
    id: []const u8,
    kind: AuditKind,
    ownership: Ownership,
    summary: []const u8,
    symbols: []const []const u8,
    coupled_state: []const []const u8,
    rationale: []const u8,
};

pub const audits = [_]Audit{
    .{
        .id = "submission-routing-and-pending-claim",
        .kind = .boundary_map,
        .ownership = .review_only,
        .summary = "Record how queue submission claims PENDING and routes work without claiming live enqueue ownership.",
        .symbols = &[_][]const u8{
            "try_to_grab_pending",
            "queue_work_on",
            "__queue_work",
        },
        .coupled_state = &[_][]const u8{
            "work->data",
            "pwq->refcnt",
            "pool->lock",
        },
        .rationale = "The bridge can name the irq-disabled pending-bit claim window and the unbound retry loop, but the live submission handoff still stays in C.",
    },
    .{
        .id = "pending-bit-and-unbound-retry",
        .kind = .concurrency_audit,
        .ownership = .stay_in_c,
        .summary = "Keep the pending-bit claim window and unbound refcount retry path in C while documenting the exact submission governance seam.",
        .symbols = &[_][]const u8{
            "try_to_grab_pending",
            "queue_work_on",
            "__queue_work",
        },
        .coupled_state = &[_][]const u8{
            "WORK_STRUCT_PENDING_BIT",
            "WORK_OFFQ_CANCELING",
            "work->data",
            "pwq->refcnt",
            "last_pool->lock",
        },
        .rationale = "Pending-bit claiming, cancellation exclusion, and unbound pwq reselection still depend on the shipped work->data and pool-lock discipline, so Zigux should record the retry seam without claiming live submission ownership.",
    },
    .{
        .id = "max-active-and-lock-handoff",
        .kind = .concurrency_audit,
        .ownership = .stay_in_c,
        .summary = "Keep max_active gating and cross-pool lock handoff in C while documenting the concurrency seam.",
        .symbols = &[_][]const u8{
            "__queue_work",
            "process_one_work",
            "worker_thread",
        },
        .coupled_state = &[_][]const u8{
            "last_pool->lock",
            "pool->lock",
            "pwq->inactive_works",
            "pool->worklist",
        },
        .rationale = "Ordered-workqueue sequencing, unlock-relock execution windows, and idle transitions remain coupled to worker_pool state rather than a narrow Zig wrapper contract.",
    },
    .{
        .id = "delayed-work-requeue-governance",
        .kind = .concurrency_audit,
        .ownership = .stay_in_c,
        .summary = "Keep delayed-work timer expiry and requeue control in C while making the alias and timer handoff explicit.",
        .symbols = &[_][]const u8{
            "queue_delayed_work_on",
            "mod_delayed_work_on",
            "__queue_delayed_work",
            "delayed_work_timer_fn",
        },
        .coupled_state = &[_][]const u8{
            "timer_base",
            "target_cpu",
            "pwq->wq",
        },
        .rationale = "Timer-base ownership, CPU affinity, and delayed-work requeue policy still belong to the shipped C implementation.",
    },
    .{
        .id = "flush-drain-cancel-boundary",
        .kind = .concurrency_audit,
        .ownership = .stay_in_c,
        .summary = "Keep flush, drain, and cancellation completion in C while documenting the bounded Phase 14 seam.",
        .symbols = &[_][]const u8{
            "__flush_workqueue",
            "drain_workqueue",
            "__flush_work",
            "__cancel_work_sync",
            "pwq_dec_nr_in_flight",
        },
        .coupled_state = &[_][]const u8{
            "wq->work_color",
            "wq->flush_color",
            "wq->first_flusher",
            "wq->flusher_overflow",
            "pwq->nr_in_flight",
            "wq->nr_pwqs_to_flush",
        },
        .rationale = "Reflush looping, single-work barrier waiting, and cancellation completion still share color progression and in-flight accounting that the bridge should describe without claiming parity.",
    },
    .{
        .id = "rescuer-and-scheduler-hooks",
        .kind = .stay_in_c,
        .ownership = .blocked_on_live_concurrency,
        .summary = "Rescuer behavior, scheduler-visible callbacks, and forward-progress control remain blocked behind live concurrency ownership.",
        .symbols = &[_][]const u8{
            "manage_workers",
            "rescuer_thread",
            "wq_worker_running",
            "wq_worker_sleeping",
        },
        .coupled_state = &[_][]const u8{
            "pool->manager",
            "pwq->mayday_cursor",
            "wq->maydays",
            "worker_pool state machine",
        },
        .rationale = "Live worker_pool execution, hotplug rebinding, rescuer wakeups, and scheduler callbacks are still too coupled to claim active Zig ownership.",
    },
};

pub fn findAudit(id: []const u8) ?*const Audit {
    for (&audits) |*audit| {
        if (std.mem.eql(u8, audit.id, id)) return audit;
    }
    return null;
}
