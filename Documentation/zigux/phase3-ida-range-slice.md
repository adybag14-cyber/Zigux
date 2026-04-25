# Phase 3 IDA Range Slice

PHASE3_STATUS=active
PHASE3_SLICE=ida-range-view-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug ida-range
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded `ida` range-set planning view over raw allocation bits
- summarize candidate first-fit ranges for a requested width
- keep range enumeration capped by `max_ranges`
- make truncation, candidate discovery, and exhaustion explicit through exported flags

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/ida_range_view.zig`
- `zigux/tests/phase3_ida_range_dump.zig`
- `zigux/tests/fixtures/phase3_ida_range/phase3_ida_range_c_harness.c`
- `scripts/zigux/check-phase3-ida-range.py`

Boundary
- this is not full `ida`
- this is not a live allocator
- this only proves bounded candidate-range summary parity over committed bitmap fixtures
