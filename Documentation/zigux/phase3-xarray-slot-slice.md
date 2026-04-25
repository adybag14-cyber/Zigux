# Phase 3 XArray Slot Slice

PHASE3_STATUS=active
PHASE3_SLICE=xarray-slot-view-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug xarray-slot
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded slot-array view over raw xarray-style entries
- classify entries as `null`, plain pointer, encoded value, or `ERR_PTR`
- keep the scan explicitly capped by `max_scan`

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/xarray_slot_view.zig`
- `zigux/tests/phase3_xarray_slot_dump.zig`
- `zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c`
- `scripts/zigux/check-phase3-xarray-slot.py`

Boundary
- this is not a full `xarray` implementation
- this is not `idr` or `ida`
- this only proves bounded slot classification and summary parity
