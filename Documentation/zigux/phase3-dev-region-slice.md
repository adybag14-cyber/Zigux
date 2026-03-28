# Phase 3 Dev Region Slice

PHASE3_STATUS=active
PHASE3_SLICE=dev-region-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-dev-region.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded kernel-facing device-region planning helper on top of `minor_alloc_plan`
- expose encoded `mkdev`-style region endpoints without pretending to register a live device region
- keep the summary explicit about truncation, discovery, exhaustion, and encoded first/last device numbers
- keep this slice fixture-driven and reviewable

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/dev_region_plan.zig`
- `zigux/tests/phase3_dev_region_dump.zig`
- `zigux/tests/fixtures/phase3_dev_region/phase3_dev_region_c_harness.c`
- `scripts/zigux/check-phase3-dev-region.py`

Boundary
- this is not live `alloc_chrdev_region`
- this is not device registration
- this only proves bounded device-region planning parity over committed bitmap fixtures
