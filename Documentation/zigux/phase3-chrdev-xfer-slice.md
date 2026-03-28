# Phase 3 Chrdev Xfer Slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-xfer-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-xfer.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded kernel-facing `chrdev_xfer` planning helper on top of `chrdev_io_plan`
- convert a request-specific read/write plan into a resumable multi-segment transfer plan
- expose resumed, continuable, and completes states explicitly without claiming live handler dispatch
- keep this slice fixture-driven and reviewable

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/chrdev_xfer_plan.zig`
- `zigux/tests/phase3_chrdev_xfer_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_xfer/phase3_chrdev_xfer_c_harness.c`
- `scripts/zigux/check-phase3-chrdev-xfer.py`

Boundary
- this is not live read/write dispatch
- this does not call real handlers
- this only proves bounded chrdev-xfer planning parity over committed bitmap fixtures
