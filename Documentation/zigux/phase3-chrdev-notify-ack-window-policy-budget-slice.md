# Phase 3 chrdev notify ack window policy budget slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-window-policy-budget-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack-window-policy-budget.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded notification-ack-window-policy-budget `chrdev_notify_ack_window_policy_budget` seam on top of `chrdev_notify_ack_window_policy`.

Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no timeout subsystem beyond the bounded window-policy-budget counters in this seam

It only proves deterministic window-policy-budget shaping over a fixed notification-ack-window-policy result:
- normal window-policy-budget consumption for acked and coalesced outcomes
- fallback deferred window-policy delivery when the primary window-policy budget is empty
- deferred-window-policy-budget consumption for already-deferred policy outcomes
- bounded acked, deferred, suppressed, coalesced, dropped, and skipped window-policy-budget summaries
