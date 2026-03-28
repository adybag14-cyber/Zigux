# Phase 3 chrdev notify ack policy slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-ack-policy-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-ack-policy.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded notification-ack-policy `chrdev_notify_ack_policy` seam on top of `chrdev_notify_ack`.

Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no timeout subsystem beyond the bounded ack-policy flags in this seam

It only proves deterministic ack-policy shaping over a fixed notification-ack result:
- force-deferred policy
- suppress-expired policy
- cookie-coalescing policy
- bounded acked, deferred, suppressed, coalesced, expired, and skipped ack-policy summaries
