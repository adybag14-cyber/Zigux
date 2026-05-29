# Phase 3 ABI idr-slot Shared Refresh

This P3-L06 note records the bounded shared ABI and bindings evidence that landed after the earlier shared Phase 3 ABI slice refresh. It is intentionally notes-only because the code, helper-local slice note, manifest entries, replay routes, and Makefile wrappers are already present on current `master`.

## Grounding

Roadmap Phase 3 is the permanent C/Zigux boundary: explicit export and UAPI surfaces, curated bindings, layout assertions, approved wrapper policy, and narrow unsafe handling. Ledger entry 26 started the shared ABI substrate, and the later Phase 3 entries extend it only when a bounded interop slice carries real helper, fixture, and replay evidence.

The current `idr_slot` packet qualifies as substantive interop progress rather than wrapper churn because direct GitHub readback reached all of these same-family files on current `master`:

- `Documentation/zigux/phase3-idr-slot-slice.md`
- `zigux/helpers/idr_slot_view.zig`
- `zigux/tests/phase3_idr_slot_starter_packet.zig`
- `zigux/tests/phase3_idr_slot_starter_packet_build.zig`
- `zigux/tests/phase3_idr_slot_build.zig`
- `zigux/tests/phase3_idr_slot_dump.zig`
- `zigux/tests/phase3_idr_slot_dump_build.zig`
- `zigux/tests/fixtures/phase3_idr_slot/phase3_idr_slot_c_harness.c`
- `zigux/tests/fixtures/phase3_idr_slot/expected.json`
- `zigux/tests/fixtures/phase3_idr_slot_manifest.json`
- `scripts/zigux/check-phase3-idr-slot-starter-packet.py`
- `scripts/zigux/check-phase3-idr-slot.py`
- `zigux/Makefile`

## Shared ABI Meaning

The landed packet adds one bounded `idr_slot` classifier layered on the already landed `xarray_slot_view`, `xa_value`, and `err_ptr` helpers. It keeps the raw slot lanes explicit as empty, tagged internal `xa_value`, tagged `err_ptr`, and pointer-backed entries. The starter packet and dump replay make those cases reviewable from both Zig and C-fixture evidence without claiming broader IDR allocation, traversal, ownership, or IDA semantics.

For the shared ABI lane, this means the honest repo-reality statement now includes `idr_slot` alongside the earlier bitmap/cpumask, list/hlist, err_ptr/xarray, and xarray-slot Phase 3 packets. It remains a bounded manifest-backed helper-local interop packet, not full Phase 3 completion and not a license to widen the shared ABI note into unrelated runtime-core delivery.

## Validation Surface

The replay surface exposed by the landed packet is:

- `python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --repo-root .`
- `python3 scripts/zigux/check-phase3-idr-slot.py --self-test`
- `python3 scripts/zigux/check-phase3-idr-slot.py --repo-root . --zig zig --cc gcc`
- `zig build phase3-idr-slot --build-file zigux/tests/phase3_idr_slot_build.zig`
- `zig build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig`
- `zig build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig`

This refresh does not edit those routes. It records that they already exist and should be considered part of the shared ABI/bindings evidence packet on the next P3-L06 reread.

## Next Safe Step

Leave P3-L06 parked unless `Documentation/zigux/phase3-abi-slice.md`, this refresh note, `Documentation/zigux/phase3-idr-slot-slice.md`, `zigux/tests/fixtures/phase3_abi_manifest.json`, the `idr_slot` helper/test/checker files, or the Phase 3 aggregate runner moves again. If the lane reopens, prefer either folding this note into the main shared ABI slice when a patch-capable checkout is available or recording the next genuinely landed ABI/bindings packet with the same interop-only discipline.
