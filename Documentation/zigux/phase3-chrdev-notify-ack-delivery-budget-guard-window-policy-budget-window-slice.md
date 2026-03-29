# Phase 3 chrdev notify ack delivery budget guard window policy budget window slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded budget-window layer on top of the stable `chrdev_notify_ack_delivery_budget_guard_window_policy_budget` seam.

Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no new timeout subsystem

It only proves deterministic budget-window shaping over the bounded guard-window-policy-budget result:
- pass-through `skipped`, `suppressed`, `dropped`, and `held` outcomes when the parent is already terminal
- window consumption for parent `acked`, `deferred`, and `coalesced` paths
- held transition when the remaining window reaches the configured floor
- window-exhaustion drop when the remaining window is already zero
- committed C-vs-Zig parity fixtures for the guard-window-policy-budget-window summary
