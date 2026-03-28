# Phase 3 chrdev notify ack window slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-window-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack-window.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded notification-ack-window `chrdev_notify_ack_window` seam on top of `chrdev_notify_ack_budget`.

Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no dynamic window engine beyond the bounded counters in this seam

It only proves deterministic ack-window shaping over a fixed notification-ack-budget result:
- window consumption for acked and deferred ack-budget results
- window exhaustion dropping the routed ack
- floor-held deferral when the remaining window would cross the configured floor
- suppressed and skipped ack-budget outcomes preserving the window counters
- bounded acked, deferred, dropped, suppressed, and skipped ack-window summaries
