# Phase 3 chrdev notify ack budget slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-budget-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack-budget.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded notification-ack-budget `chrdev_notify_ack_budget` seam on top of `chrdev_notify_ack_policy`.

Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no dynamic budget engine beyond the bounded counters in this seam

It only proves deterministic ack-budget shaping over a fixed notification-ack-policy result:
- ack-budget issuance for acked and coalesced policy results
- fallback deferred ack delivery when the ack budget is empty
- deferred-ack-budget exhaustion and drop for deferred or expired policy results
- suppressed and skipped ack-policy outcomes preserving both budgets
- bounded acked, deferred, dropped, suppressed, and skipped ack-budget summaries
