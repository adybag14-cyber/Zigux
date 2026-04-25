# Phase 3 Cdev Add Slice

PHASE3_STATUS=active
PHASE3_SLICE=cdev-add-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug cdev-add
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded kernel-facing `cdev_add(cdev, dev, count)` planning helper on top of `dev_region_plan`
- expose selected device range and count without pretending to register a live cdev
- keep the summary explicit about truncation, discovery, exhaustion, and selected device count
- keep this slice fixture-driven and reviewable

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/cdev_add_plan.zig`
- `zigux/tests/phase3_cdev_add_dump.zig`
- `zigux/tests/fixtures/phase3_cdev_add/phase3_cdev_add_c_harness.c`
- `scripts/zigux/check-phase3-cdev-add.py`

Boundary
- this is not live `cdev_add`
- this is not device registration
- this only proves bounded cdev-add planning parity over committed bitmap fixtures
