# Phase 3 Minor Alloc Slice

PHASE3_STATUS=active
PHASE3_SLICE=minor-alloc-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-minor-alloc.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded kernel-facing device-minor allocation planning helper on top of the `ida-policy` substrate
- expose `major`, `first_minor`, requested width, chosen minor range, and alternate candidate without pretending to allocate
- keep the summary explicit about truncation, discovery, exhaustion, and longest-free-run state
- keep this slice reviewable and fixture-driven

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/minor_alloc_plan.zig`
- `zigux/tests/phase3_minor_alloc_dump.zig`
- `zigux/tests/fixtures/phase3_minor_alloc/phase3_minor_alloc_c_harness.c`
- `scripts/zigux/check-phase3-minor-alloc.py`

Boundary
- this is not a live allocator
- this is not `ida` replacement
- this only proves bounded device-minor planning parity over committed bitmap fixtures
