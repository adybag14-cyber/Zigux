# Phase 3 chrdev notify ack slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded notification-ack `chrdev_notify_ack` seam on top of `chrdev_notify_budget`.

Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no timeout subsystem beyond the bounded ack window in this seam

It only proves deterministic ack planning over a fixed notification-budget result:
- acked delivery when a matching ack is observed
- deferred ack when a matching event is still inside the ack window
- expired ack when the window is already empty
- skipped ack when the ack mask does not match the budget result
- bounded acked, deferred, expired, and skipped ack summaries
