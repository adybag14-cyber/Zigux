# Phase 3 chrdev resume slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-resume-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug chrdev-resume
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded multi-pass `chrdev_resume` planning seam on top of `chrdev_xfer`.

Boundaries:
- no live kernel dispatch
- no blocking behavior
- no retry scheduling
- no file-operations implementation

It only proves deterministic continuation planning across a bounded number of passes.
