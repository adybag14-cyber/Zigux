# Phase 3 chrdev notify ack window policy budget window delivery window budget slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded final budget seam on top of `chrdev_notify_ack_window_policy_budget_window_delivery_window`.

Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no timeout subsystem beyond the bounded counters in this seam

It only proves deterministic final budget shaping over a fixed notification-ack-window-policy-budget-window-delivery-window result:
- primary final-budget consumption for acked and coalesced outcomes
- deferred final-budget fallback when the primary final budget is exhausted
- preserved suppressed, dropped, and skipped outcomes without reclassification
- bounded acked, deferred, suppressed, coalesced, dropped, and skipped final-budget summaries
