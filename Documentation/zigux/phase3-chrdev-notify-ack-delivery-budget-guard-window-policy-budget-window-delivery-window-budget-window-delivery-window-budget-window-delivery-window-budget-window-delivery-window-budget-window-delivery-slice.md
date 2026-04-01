# Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery window budget slice
PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig
This slice adds a bounded delivery-window-budget layer on top of the stable `chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window` seam.
Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no new timeout subsystem
It only proves deterministic delivery-window-budget shaping over the bounded guarded delivery-window result:
- pass-through suppressed, skipped, dropped, and held outcomes when the parent is already terminal
- primary delivery-window-budget consumption for parent acked and coalesced paths
- deferred delivery-window-budget fallback when the primary delivery-window budget is exhausted
- deferred delivery-window-budget consumption for parent deferred paths
- dropped fallback when both primary and deferred delivery-window budgets are exhausted
- committed C-vs-Zig parity fixtures for the guarded delivery-window-budget summary
