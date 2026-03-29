# Phase 3 chrdev notify ack delivery budget guard window policy budget slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-delivery-budget-guard-window-policy-budget-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded budget layer on top of the stable `chrdev_notify_ack_delivery_budget_guard_window_policy` seam.

Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no new timeout subsystem

It only proves deterministic budget shaping over the bounded guard-window-policy result:
- pass-through `skipped`, `suppressed`, `dropped`, and `held` outcomes when no budget applies
- deferred-budget consumption for parent `deferred` paths
- primary-budget consumption for parent `acked` paths
- fallback deferred conversion when primary budget is exhausted and deferred budget remains
- budget-exhaustion drop when neither primary nor deferred budget remains
- committed C-vs-Zig parity fixtures for the guard-window-policy-budget summary
