# Phase 3 Chrdev Route Slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-route-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug chrdev-route
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded kernel-facing `chrdev_route` planning helper on top of `chrdev_fops_plan`
- split the route into explicit entry, data, and exit op masks
- expose routeable vs blocked routing explicitly without claiming live handler dispatch
- keep this slice fixture-driven and reviewable

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/chrdev_route_plan.zig`
- `zigux/tests/phase3_chrdev_route_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_route/phase3_chrdev_route_c_harness.c`
- `scripts/zigux/check-phase3-chrdev-route.py`

Boundary
- this is not live file-operation dispatch
- this does not call real handlers
- this only proves bounded chrdev-route planning parity over committed bitmap fixtures
