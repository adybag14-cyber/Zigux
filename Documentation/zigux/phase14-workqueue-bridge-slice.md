# Phase 14 Workqueue Bridge Slice

This bounded Phase 14 slice starts `kernel/workqueue_bridge.zig` as a pure boundary map anchored to `kernel/workqueue.c`.

The current bridge stays intentionally narrow:

- records the caller-facing submission boundary around `queue_work_on()` and `__queue_work()` without claiming live enqueue, wakeup, or execution behavior
- records the allocation and attribute boundary around `__alloc_workqueue()` and `devm_alloc_workqueue()` as future wrapper candidates only
- records the flush and cancel coordination boundary around `__flush_workqueue()` and `cancel_work_sync()` without claiming completion, draining, or active-color parity
- marks `manage_workers()` and the `worker_pool` state machine as explicit stay-in-C decisions
- marks `rescuer_thread()`, `wq_worker_running()`, and `wq_worker_sleeping()` as explicit stay-in-C decisions tied to scheduler-visible concurrency ownership
- adds a sixteen-checkpoint concurrency audit outline that names manager-role serialization, `worker_pool` forward-progress fields, the `__queue_work()` `max_active` or ordered inactive-list gate, the irq-disabled `try_to_grab_pending()` or `queue_work_on()` PENDING-bit claim window, the unbound `__queue_work()` `pwq->refcnt` retry loop, the `__queue_work()` `last_pool->lock` reentrancy handoff, the `__flush_workqueue()` flush-color cascade, the `start_flush_work()` barrier insertion path, the `pwq_dec_nr_in_flight()` color-release completion path, the `drain_workqueue()` or `__flush_work()` or `__cancel_work_sync()` reflush-and-cancel boundary, the disable-depth and delayed-cancel sync boundary around `__cancel_work()`, `clear_pending_if_disabled()`, `__cancel_work_sync()`, and `cancel_delayed_work_sync()`, the new delayed-wrapper alias checkpoint around `disable_delayed_work()`, `disable_delayed_work_sync()`, and `enable_delayed_work()`, the `process_one_work()` unlock or relock execution window, the `worker_thread()` idle sleep transition, scheduler hook state transitions, and the rescuer mayday handoff while keeping all live ownership in C

This slice still does not claim live worker pools, work execution, hotplug transitions, flush semantics, cancellation completion, mayday escalation, rescuer threads, or scheduler-visible worker-state transitions.

The next honest bounded step in this same lane is to audit `queue_delayed_work_on()`, `mod_delayed_work_on()`, and `clear_pending_if_disabled()` so the bridge records the delayed submission aliases around pending ownership, disabled-work bypass, and timer handoff before any wrapper claims CPU-affinity, timer, or requeue parity.
