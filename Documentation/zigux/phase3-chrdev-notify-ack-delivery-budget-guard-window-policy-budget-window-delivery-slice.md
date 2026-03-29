# Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery slice
PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig
This slice adds a bounded delivery-budget layer on top of the stable chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window seam.
Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no new timeout subsystem
It only proves deterministic delivery-budget shaping over the bounded guard-window-policy-budget-window result:
- pass-through skipped, suppressed, dropped, and held outcomes when the parent is already terminal
- primary delivery-budget consumption for parent cked and coalesced paths
- deferred-delivery-budget consumption for parent deferred paths
- deferred fallback when the primary delivery budget is already exhausted on parent cked and coalesced paths
- delivery-budget exhaustion drop when neither primary nor deferred delivery budget remains
- committed C-vs-Zig parity fixtures for the guard-window-policy-budget-window-delivery summary
