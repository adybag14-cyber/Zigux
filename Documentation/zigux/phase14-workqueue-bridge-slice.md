# Phase 14 Workqueue Bridge Slice

This bounded Phase 14 slice starts `kernel/workqueue_bridge.zig` as a pure boundary map anchored to `kernel/workqueue.c`.

The current bridge stays intentionally narrow:
- records the caller-facing submission boundary around `queue_work_on()` and `__queue_work()` without claiming live enqueue, wakeup, or execution behavior
- records the allocation and attribute boundary around `__alloc_workqueue()` and `devm_alloc_workqueue()` as future wrapper candidates only
- records the flush and cancel coordination boundary around `__flush_workqueue()` and `cancel_work_sync()` without claiming completion, draining, or active-color parity
- marks `manage_workers()` and the `worker_pool` state machine as explicit stay-in-C decisions
- marks `rescuer_thread()`, `wq_worker_running()`, and `wq_worker_sleeping()` as explicit stay-in-C decisions tied to scheduler-visible concurrency ownership
- adds a twelve-checkpoint concurrency audit outline that names manager-role serialization, `worker_pool` forward-progress fields, the `__queue_work()` `max_active` or ordered inactive-list gate, the `try_to_grab_pending()` plus `queue_work_on()` pending-bit claim handoff, the unbound `__queue_work()` `pwq->refcnt` retry contract, the delayed-submission alias fan-in through `queue_delayed_work_on()`, `mod_delayed_work_on()`, and `__queue_delayed_work()`, the `delayed_work_timer_fn()` timer-expiry handoff back into `__queue_work()`, the `__queue_work()` `last_pool->lock` reentrancy handoff, the `process_one_work()` unlock or relock execution window, the `worker_thread()` idle sleep transition, scheduler hook state transitions, and the rescuer mayday handoff while keeping all live ownership in C

This slice still does not claim live worker pools, work execution, hotplug transitions, flush semantics, cancellation completion, mayday escalation, rescuer threads, or scheduler-visible worker-state transitions.

The current lane now also records the delayed timer-expiry handoff through `delayed_work_timer_fn()` and back into `__queue_work()` while keeping timer-base, CPU-affinity, and delayed-work requeue ownership explicitly in C.

The next honest bounded step is to leave this packet in blocked maintenance unless a future run can tighten one equally small stay-in-C note around timer-base, CPU-affinity, or requeue ownership without claiming live delayed-work execution.
