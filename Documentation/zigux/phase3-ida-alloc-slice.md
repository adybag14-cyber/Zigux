# Phase 3 IDA Allocation Slice

PHASE3_STATUS=active
PHASE3_SLICE=ida-alloc-view-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-ida-alloc.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded `ida` allocation-planning view over raw allocation bits
- summarize first-fit placement for a requested allocation width
- expose longest free run in the scanned window
- keep truncation, first-fit success, and exhaustion explicit through flags

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/ida_alloc_view.zig`
- `zigux/tests/phase3_ida_alloc_dump.zig`
- `zigux/tests/fixtures/phase3_ida_alloc/phase3_ida_alloc_c_harness.c`
- `scripts/zigux/check-phase3-ida-alloc.py`

Boundary
- this is not full `ida`
- this is not a live allocator
- this only proves bounded first-fit allocation planning parity over committed bitmap fixtures
