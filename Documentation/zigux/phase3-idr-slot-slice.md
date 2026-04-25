# Phase 3 IDR Slot Slice

PHASE3_STATUS=active
PHASE3_SLICE=idr-slot-view-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug idr-slot
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded `idr`-style slot view over raw xarray-style entries
- classify present entries as plain pointer, encoded value, or `ERR_PTR`
- keep the scan explicitly capped by `max_scan`
- expose `base_id`, `first_present_id`, and `next_free_id`

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/idr_slot_view.zig`
- `zigux/tests/phase3_idr_slot_dump.zig`
- `zigux/tests/fixtures/phase3_idr_slot/phase3_idr_slot_c_harness.c`
- `scripts/zigux/check-phase3-idr-slot.py`

Boundary
- this is not full `idr`
- this is not full `ida`
- this only proves bounded ID-space slot classification and summary parity
