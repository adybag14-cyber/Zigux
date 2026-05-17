# Phase 3 list/hlist Slice

This note records one bounded Phase 3 interop slice on current `master`.

## Current Slice

- `include/zigux/list_hlist.h`
- `zigux/uapi/list_hlist.zig`
- `zigux/bindings/list_hlist.zig`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/tests/phase3_list_hlist_starter_packet.zig`
- `zigux/tests/phase3_list_hlist_starter_packet_build.zig`
- `zigux/tests/phase3_list_hlist_starter_packet_manifest.json`
- `zigux/tests/phase3_list_hlist_dump.zig`
- `zigux/tests/fixtures/phase3_list_hlist/expected.json`
- `zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c`
- `scripts/zigux/check-phase3-list-hlist.py`

## Bounded Contract

The slice stays intentionally small:

- `include/zigux/list_hlist.h` and `zigux/uapi/list_hlist.zig` define only pointer-width list and hlist node layouts
- `zigux/bindings/list_hlist.zig` keeps the layout offsets and sizes explicit for review
- `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` only expose read-only traversal, length, and link-consistency checks
- `zigux/tests/phase3_list_hlist_starter_packet.zig` proves the helpers against small in-memory examples
- `scripts/zigux/check-phase3-list-hlist.py` compares one bounded C harness and one Zig dump against the committed fixture

## Current Gap

This is not the broader shared Phase 3 ABI substrate from the older snapshot-only packet. It does not claim export-shim wiring, shared `phase3` catalog coverage, mutation helpers, callback support, container-of helpers, or subsystem ownership.

It is one current-master-safe starter packet layered beside the existing `dev_t` and helper-local Phase 3 slices.

## Replay Routes

- `python3 scripts/zigux/check-phase3-list-hlist.py --self-test`
- `python3 scripts/zigux/check-phase3-list-hlist.py`

## Scope

This note is limited to the bounded list and hlist layout bridge plus the read-only traversal helpers and parity fixture. It does not claim the older broader ABI header family or shared Phase 3 replay surface is fully restored.
