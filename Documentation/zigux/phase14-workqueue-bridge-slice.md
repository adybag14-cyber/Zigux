# Phase 14 Workqueue Bridge Slice

This bounded Phase 14 slice starts `kernel/workqueue_bridge.zig` as a pure boundary map anchored to `kernel/workqueue.c`.

The current bridge stays intentionally narrow:

- records the caller-facing submission boundary around `queue_work_on()` and `__queue_work()` without claiming live enqueue, wakeup, or execution behavior
- records the allocation and attribute boundary around `__alloc_workqueue()` and `devm_alloc_workqueue()` as a study checkpoint with wrapper wording explicitly deferred
- records the flush and cancel coordination boundary around `__flush_workqueue()` and `cancel_work_sync()` without claiming completion, draining, or active-color parity
- marks `manage_workers()` and the `worker_pool` state machine as explicit stay-in-C decisions
- marks `rescuer_thread()`, `wq_worker_running()`, and `wq_worker_sleeping()` as explicit stay-in-C decisions tied to scheduler-visible concurrency ownership
- exposes a bounded concurrency audit checklist for `pool->lock` ownership, the mayday-to-rescuer path, and scheduler-hook pairing so the lane does not keep describing that audit work as merely pending

This slice does not claim worker creation, pool wakeup, delayed work timing, CPU hotplug handling, rescuer execution, scheduler hook parity, forward-progress guarantees, or any live workqueue wrapper behavior.

The next honest bounded step in this same lane is to tighten that landed audit with one small field-level follow-up around forward-progress state, `WORKER_NOT_RUNNING`, and the narrowest `pool->lock` wording before any wrapper leaves the current boundary-map-only posture.
