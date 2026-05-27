# Phase 3 idr-slot Slice

This note records one bounded Phase 3 helper-side `idr_slot` packet on current `master`.

## Current Slice

- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/helpers/xarray_slot_view.zig`
- `zigux/helpers/idr_slot_view.zig`
- `zigux/tests/phase3_idr_slot_starter_packet.zig`
- `zigux/tests/phase3_idr_slot_starter_packet_build.zig`
- `zigux/tests/fixtures/phase3_idr_slot_manifest.json`
- `scripts/zigux/check-phase3-idr-slot-starter-packet.py`

## Bounded Contract

This packet stays intentionally small:

- `zigux/helpers/idr_slot_view.zig` only classifies one raw IDR slot word into four bounded lanes: `empty`, tagged internal `xa_value`, tagged `err_ptr`, and pointer-backed.
- The helper reuses the already-landed `xarray_slot_view`, `xa_value`, and `err_ptr` rules instead of widening into allocation, traversal, ownership, or broader IDR semantics.
- `zigux/tests/phase3_idr_slot_starter_packet.zig` keeps the empty, pointer, tagged-value, tagged-error, and top-of-error-band cases explicit so the tagged encodings do not drift back into the pointer lane.
- The manifest and checker keep this as a helper-local starter packet rather than claiming the wider shared ABI validator, xarray dump parity surface, or the broader IDA follow-through.

## Current Replay Surface

The current helper-local packet has one bounded replay layer:

- `zigux/helpers/idr_slot_view.zig`
- `zigux/tests/phase3_idr_slot_starter_packet.zig`
- `zigux/tests/phase3_idr_slot_starter_packet_build.zig`
- `zigux/tests/fixtures/phase3_idr_slot_manifest.json`
- `scripts/zigux/check-phase3-idr-slot-starter-packet.py`
- `python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-idr-slot-starter-packet.py --repo-root .`
- `zig build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig`

That keeps the current follow-through narrow and reviewable without reopening the broader shared Phase 3 validator packet.

## Current Gap

This is still not the broader shared Phase 3 catalog or validator-support packet. The landed `idr_slot` helper-local packet is real repo evidence, but any same-lane follow-through should stay narrowed to shared-validator alignment only if current `master` later needs this helper absorbed into the wider Phase 3 survey surfaces.

## Scope

This note is limited to the helper-local `idr_slot_view` classifier layered on the already-landed tagged `xarray_slot_view`, `xa_value`, and `err_ptr` helpers, together with one starter packet, one dedicated build file, one helper-local manifest, and one checker. It does not claim broader IDR traversal semantics, export-shim wiring, xarray dump parity, or wider IDA coverage.
