# Phase 3 chrdev notify budget slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-budget-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-budget.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded notification-budget `chrdev_notify_budget` seam on top of `chrdev_notify_policy`.

Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no dynamic budget engine beyond the bounded counters in this seam

It only proves deterministic budget shaping over a fixed notification-policy result:
- delivery-budget issuance
- fallback deferred delivery when the delivery budget is empty
- deferred-budget exhaustion and drop
- suppressed notifications preserving both budgets
- bounded issued, deferred, dropped, and suppressed budget summaries
