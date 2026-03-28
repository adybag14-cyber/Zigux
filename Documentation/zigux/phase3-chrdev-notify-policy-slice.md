# Phase 3 chrdev notify policy slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-policy-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify-policy.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded notification-policy `chrdev_notify_policy` seam on top of `chrdev_notify`.

Boundaries:
- no live kernel dispatch
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration
- no dynamic policy engine beyond the bounded flags in this seam

It only proves deterministic policy shaping over a fixed notification result:
- force-deferred policy
- suppress-failure policy
- cookie-coalescing policy
- bounded delivered, deferred, suppressed, and coalesced policy summaries
