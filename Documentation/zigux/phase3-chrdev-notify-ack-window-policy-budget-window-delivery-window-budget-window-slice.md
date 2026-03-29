# Phase 3 chrdev notify ack window policy budget window delivery window budget window slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded final window/floor seam on top of `chrdev_notify_ack_window_policy_budget_window_delivery_window_budget`.

Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no timeout subsystem beyond the bounded counters in this seam

It only proves deterministic final window shaping over a fixed notification-ack-window-policy-budget-window-delivery-window-budget result:
- primary final-window consumption for acked, deferred, and coalesced outcomes
- floor-held deferral when the final window reaches its bounded floor
- dropped reclassification when the final window is exhausted
- preserved suppressed, dropped, and skipped outcomes without budget-window reclassification
- bounded acked, deferred, suppressed, coalesced, dropped, and skipped final-window summaries
