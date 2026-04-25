# Phase 3 Cdev Lookup Slice

PHASE3_STATUS=active
PHASE3_SLICE=cdev-lookup-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug cdev-lookup
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded kernel-facing `dev_t` to cdev lookup-planning helper on top of `cdev_add_plan`
- expose whether a target minor resolves into the selected cdev range without pretending to do live registration or open-path dispatch
- keep the summary explicit about truncation, discovery, exhaustion, hit/miss state, and resolved index
- keep this slice fixture-driven and reviewable

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/cdev_lookup_plan.zig`
- `zigux/tests/phase3_cdev_lookup_dump.zig`
- `zigux/tests/fixtures/phase3_cdev_lookup/phase3_cdev_lookup_c_harness.c`
- `scripts/zigux/check-phase3-cdev-lookup.py`

Boundary
- this is not live `kobj_lookup`
- this is not an open-path implementation
- this only proves bounded cdev lookup planning parity over committed bitmap fixtures
