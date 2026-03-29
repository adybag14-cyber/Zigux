# Phase 3 chrdev notify ack delivery budget guard window slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-delivery-budget-guard-window-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack-delivery-budget-guard-window.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded primary/deferred window layer on top of the current stable `chrdev_notify_ack_delivery_budget_guard` seam.

Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no new timeout subsystem

It only proves deterministic window shaping over the existing bounded guard result:
- pass-through `suppressed`, `dropped`, `skipped`, and already-held outcomes
- primary-window dispatch for `acked` and `coalesced` paths when room exists above the configured floor
- deferred-window fallback for `acked` and parent-deferred paths when the primary window is unavailable
- held delivery when neither window can be consumed without breaching the configured floor
- preserved parent summary as the source of truth for the underlying bounded guard seam
- committed C-vs-Zig parity fixtures for the guard-window summary
