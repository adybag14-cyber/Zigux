# Phase 3 chrdev requeue slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-requeue-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-requeue.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded requeue-policy `chrdev_requeue` planning seam on top of `chrdev_retry`.

Boundaries:
- no live kernel dispatch
- no scheduler or timer-wheel integration
- no queue ownership transfer
- no file-operations implementation

It only proves deterministic projected-remaining calculation, queue-capacity outcomes, and bounded requeue metadata over a fixed retry result.
