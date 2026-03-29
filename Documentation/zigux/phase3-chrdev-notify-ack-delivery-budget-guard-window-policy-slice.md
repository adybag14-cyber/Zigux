# Phase 3 chrdev notify ack delivery budget guard window policy slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-delivery-budget-guard-window-policy-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack-delivery-budget-guard-window-policy.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded policy layer on top of the stable `chrdev_notify_ack_delivery_budget_guard_window` seam.

Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no new timeout subsystem

It only proves deterministic policy shaping over the bounded guard-window result:
- pass-through `skipped` outcomes
- pass-through `acked`, `deferred`, `coalesced`, `dropped`, and `held` outcomes when no policy bit applies
- forced defer for `acked` and `coalesced` paths
- held suppression without mutating the parent guard-window summary
- dropped suppression without mutating the parent guard-window summary
- committed C-vs-Zig parity fixtures for the guard-window-policy summary