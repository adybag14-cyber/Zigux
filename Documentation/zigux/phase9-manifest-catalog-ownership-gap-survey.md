# Phase 9 Manifest, Catalog, and Ownership Gap Survey

This note records the current `master` delivery-discipline gap between the Phase 9 runtime-pilot roadmap and the shared manifest, catalog, and ownership-map packet.

## Readback date

Current repository state was reread on 2026-05-27 against `master`.

## Roadmap anchor

Phase 9 is still the runtime pilot tranche.

- primary Linux anchors:
  - `lib/atomic64_test.c`
  - `lib/test_bitmap.c`
  - `samples/trace_events/trace-events-sample.c`
  - `samples/kprobes/kretprobe_example.c`
- required Zigux features:
  - first loadable Zigux runtime modules
  - selftest hooks
  - runtime module lifecycle parity
- recommended Zigux destinations:
  - `zigux/tests/runtime_*`
  - `samples/zigux/runtime_*`

The roadmap allows bounded shared reminder packets only when scope, validation, rollback, and ownership stay explicit. If the shared manifest, catalog, and ownership map disagree, the Phase 9 delivery packet stops being trustworthy.

## Current shared packet agreement

Trusted current-`master` rereads on 2026-05-27 confirm that these three files are the shared Phase 9 inventory sources:

- `zigux/tests/runtime_pilot_manifest.json`
- `scripts/zigux/phase9_catalog.py`
- `Documentation/zigux/phase9-runtime-pilot-ownership-map.md`

The current manifest and ownership map agree on two important returned shared-packet members:

- `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`
- `samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig`

Those same two paths are currently explicit in `zigux/tests/runtime_pilot_manifest.json`, and the ownership map also keeps them inside the shared Phase 9 owner packet or the returned runtime-kretprobe family packet.

## Current catalog drift

Current `master` still leaves the catalog narrower than the manifest-backed packet it is meant to inventory.

In `scripts/zigux/phase9_catalog.py`, the `EXPECTED_PACKET_FILES` tuple undercounts the current shared packet by omitting:

- `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`
- `samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig`

That means the catalog no longer reflects the same bounded Phase 9 packet that the manifest and ownership map already describe.

## Current checker gap

Current `master` also leaves the catalog self-check too weak for this exact drift.

`scripts/zigux/check-phase9-catalog-selftest.py` proves that the shared packet files exist and that a few catalog markers stay present, but it does not fail closed on the exact `EXPECTED_PACKET_FILES` membership mismatch above.

That leaves the shared Phase 9 delivery packet in a mixed state:

- the manifest is stricter than the catalog
- the ownership map is stricter than the catalog
- the self-checker still allows the narrower catalog to pass marker-only validation

## Survey conclusion

Against the Phase 9 roadmap, this is a delivery-discipline gap rather than a runtime-behavior gap.

- the current repo does carry a bounded shared Phase 9 manifest-backed packet
- the packet still keeps ownership explicit enough to stay inside roadmap discipline
- the catalog and its checker are not yet strict enough to prove that the shared packet description remains aligned with the manifest and ownership map

The honest current reading is therefore: the Phase 9 shared reminder family is partially aligned on `master`, but the manifest-backed catalog packet is not yet self-policing enough to be treated as fully trustworthy delivery evidence.

## Next bounded step

If a later same-lane follow-through is needed, keep it narrow and in this order:

1. repair `scripts/zigux/phase9_catalog.py` so its `EXPECTED_PACKET_FILES` matches the live manifest-backed packet again
2. tighten `scripts/zigux/check-phase9-catalog-selftest.py` so it fails closed on exact packet-membership drift instead of marker-only drift
3. only then widen to any other shared reminder surface that still undercounts the same two returned packet members
