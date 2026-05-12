# Phase 14 Workqueue Bridge Slice

This bounded Phase 14 slice keeps `kernel/workqueue_bridge.zig` as a review-only boundary map anchored to `kernel/workqueue.c`.

The current bridge stays intentionally boundary-first:
- records the caller-facing submission boundary around `queue_work_on()` and `__queue_work()` without claiming live enqueue, wakeup, or execution behavior
- records the allocation and attribute boundary around `__alloc_workqueue()` and `devm_alloc_workqueue()` as future wrapper candidates only
- records the flush and cancel coordination boundary around `__flush_workqueue()` and `cancel_work_sync()` without claiming completion, draining, or active-color parity
- marks `manage_workers()` and the `worker_pool` state machine as explicit stay-in-C decisions
- marks `rescuer_thread()`, `wq_worker_running()`, and `wq_worker_sleeping()` as explicit stay-in-C decisions tied to scheduler-visible concurrency ownership
- keeps the original eight-checkpoint concurrency audit, plus the landed `phase14-workqueue-pending-bit-followup`, delayed-submission alias, delayed timer-expiry, delayed-requeue governance, flush-drain governance, and rescuer-mayday governance follow-ups, as review-only evidence rather than live ownership claims

The bridge now describes a blocked-maintenance packet with eight boundary areas, fifteen review-only audit checkpoints, and seven blocked live behaviors. This slice still does not claim live worker pools, work execution, hotplug transitions, flush semantics, cancellation completion, mayday escalation, rescuer threads, scheduler-visible worker-state transitions, or a direct `kernel/workqueue.c` port.

The next honest bounded step in this same lane is to keep the packet truthful if `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, the survey note, or the manifest drift. Any reopen should stay review-only and keep delayed-work requeue control, flush-drain active-color ownership, runtime `max_active` retuning, hotplug rebinding, and live execution in C.
