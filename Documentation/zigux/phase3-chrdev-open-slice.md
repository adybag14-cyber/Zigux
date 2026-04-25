# Phase 3 Chrdev Open Slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-open-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug chrdev-open
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded kernel-facing `chrdev_open` planning helper on top of `cdev_lookup_plan`
- expose whether a target minor resolves and whether the requested open mode is fully permitted or explicitly denied
- keep the summary explicit about truncation, discovery, exhaustion, hit state, granted mode, and denied mode
- keep this slice fixture-driven and reviewable

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/chrdev_open_plan.zig`
- `zigux/tests/phase3_chrdev_open_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_open/phase3_chrdev_open_c_harness.c`
- `scripts/zigux/check-phase3-chrdev-open.py`

Boundary
- this is not a live `open` path
- this does not execute `file_operations`
- this only proves bounded chrdev-open planning parity over committed bitmap fixtures
