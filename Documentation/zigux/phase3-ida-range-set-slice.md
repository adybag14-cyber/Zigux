# Phase 3 IDA Range-Set Slice

PHASE3_STATUS=active
PHASE3_SLICE=ida-range-set-view-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-ida-range-set.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded non-overlapping `ida` range-set planning view over raw allocation bits
- summarize both discovered candidate ranges and greedily selected range starts for a requested width
- cap candidate enumeration by `max_ranges`
- cap selected ranges by `max_selected`
- make truncation, candidate discovery, exhaustion, and selection explicit through exported flags

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/ida_range_set_view.zig`
- `zigux/tests/phase3_ida_range_set_dump.zig`
- `zigux/tests/fixtures/phase3_ida_range_set/phase3_ida_range_set_c_harness.c`
- `scripts/zigux/check-phase3-ida-range-set.py`

Boundary
- this is not full `ida`
- this is not a live allocator
- this only proves bounded non-overlapping range-set summary parity over committed bitmap fixtures