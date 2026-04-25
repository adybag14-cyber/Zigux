# Phase 3 Chrdev Fops Slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-fops-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug chrdev-fops
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded kernel-facing `chrdev_fops` planning helper on top of `chrdev_open_plan`
- compute the required `file_operations` bitmask for a granted open mode
- expose routeable vs missing-op failure explicitly
- keep this slice fixture-driven and reviewable

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/chrdev_fops_plan.zig`
- `zigux/tests/phase3_chrdev_fops_dump.zig`
- `zigux/tests/fixtures/phase3_chrdev_fops/phase3_chrdev_fops_c_harness.c`
- `scripts/zigux/check-phase3-chrdev-fops.py`

Boundary
- this is not live `file_operations`
- this does not dispatch opens to real handlers
- this only proves bounded chrdev-fops planning parity over committed bitmap fixtures
