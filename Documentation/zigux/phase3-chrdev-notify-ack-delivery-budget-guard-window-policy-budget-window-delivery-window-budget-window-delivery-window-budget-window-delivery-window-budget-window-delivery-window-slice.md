# Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery window slice
PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig
This slice adds a bounded delivery-window layer on top of the stable chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery seam.
Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no new timeout subsystem
It only proves deterministic delivery-window shaping over the bounded guard-window-policy-budget-window-delivery result:
- pass-through skipped, suppressed, dropped, and held outcomes when the parent is already terminal
- primary delivery-window consumption for parent acked and coalesced paths
- deferred delivery-window preservation for parent deferred paths
- floor-held deferral when the remaining delivery window reaches the configured floor
- delivery-window exhaustion drop when no delivery window remains
- committed C-vs-Zig parity fixtures for the guard-window-policy-budget-window-delivery-window summary
