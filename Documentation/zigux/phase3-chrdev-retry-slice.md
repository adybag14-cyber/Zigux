# Phase 3 chrdev retry slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-retry-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-retry.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded retry-policy `chrdev_retry` planning seam on top of `chrdev_resume`.

Boundaries:
- no live kernel dispatch
- no timer wheel or scheduler integration
- no real sleep/backoff execution
- no file-operations implementation

It only proves deterministic retry planning, retry-budget exhaustion, and bounded backoff metadata over a fixed resume result.
