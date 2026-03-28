# Phase 3 Chrdev Io Slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-io-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-io.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded kernel-facing `chrdev_io` planning helper on top of `chrdev_route_plan`
- convert the route summary into a request-specific read/write plan
- expose dispatchable vs blocked IO explicitly without claiming live handler calls
- keep this slice fixture-driven and reviewable

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/chrdev_io_plan.zig`
- `zigux/tests/phase3_chrdev_io_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_io/phase3_chrdev_io_c_harness.c`
- `scripts/zigux/check-phase3-chrdev-io.py`

Boundary
- this is not live read/write dispatch
- this does not call real handlers
- this only proves bounded chrdev-io planning parity over committed bitmap fixtures
