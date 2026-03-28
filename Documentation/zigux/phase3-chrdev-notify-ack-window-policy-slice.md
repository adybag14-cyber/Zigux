# Phase 3 chrdev notify ack window policy slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-window-policy-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack-window-policy.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded notification-ack-window-policy `chrdev_notify_ack_window_policy` seam on top of `chrdev_notify_ack_window`.

Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no timeout subsystem beyond the bounded ack-window-policy flags in this seam

It only proves deterministic ack-window-policy shaping over a fixed notification-ack-window result:
- force-deferred policy
- suppress-dropped policy
- cookie-coalescing policy
- bounded acked, deferred, suppressed, coalesced, dropped, and skipped window-policy summaries
