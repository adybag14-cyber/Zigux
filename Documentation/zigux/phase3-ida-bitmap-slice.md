# Phase 3 IDA Bitmap Slice

PHASE3_STATUS=active
PHASE3_SLICE=ida-bitmap-view-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-ida-bitmap.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded `ida`-style bitmap view over raw allocation bits
- summarize scanned capacity, allocated count, first allocated ID, and first free ID
- keep the scan explicitly capped by `max_scan`
- make truncation and exhaustion explicit through exported flags

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/ida_bitmap_view.zig`
- `zigux/tests/phase3_ida_bitmap_dump.zig`
- `zigux/tests/fixtures/phase3_ida_bitmap/phase3_ida_bitmap_c_harness.c`
- `scripts/zigux/check-phase3-ida-bitmap.py`

Boundary
- this is not full `ida`
- this is not a live allocator
- this only proves bounded allocation-state summary parity over committed bitmap fixtures
