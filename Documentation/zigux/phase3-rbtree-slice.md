# Phase 3 Rbtree Interop Helper Slice

This document records the first bounded Phase 3 helper packet around the roadmap's `lib/rbtree.c` anchor.

## Status

- `PHASE3_STATUS=active`
- `PHASE3_SLICE=rbtree-helper-interop`
- scope: first bounded `zigux/helpers/rbtree_*` helper packet only
- product boundary:
  - `zigux/helpers/rbtree_view.zig`
  - `Documentation/zigux/phase3-rbtree-slice.md`
  - `zigux/tests/phase3_rbtree_survey.zig`
  - `zigux/tests/phase3_rbtree_manifest.json`

## Why this slice exists

The roadmap gap note has been pointing at the missing Phase 3 `rbtree` helper family for a while.

This slice keeps the next move deliberately small:

- one helper-local summary view over the existing runtime `rbtree` packet
- bounded node counting with a truncation signal
- explicit first-node and last-node address reporting
- one machine-checked survey packet that records the narrowed remaining gap

That gives Phase 3 a real `zigux/helpers/rbtree_*` foothold without pretending the curated C header and binding surface is already complete.

## Gates

1. run the helper-local Zig tests
- `zig test zigux/helpers/rbtree_view.zig`

2. keep the survey packet machine-checked
- `zig test zigux/tests/phase3_rbtree_survey.zig`

3. keep the wider roadmap-gap packet aligned
- `python3 scripts/zigux/validate-phase3-roadmap-gap-survey.py`

## Boundary

This slice does not yet claim:

- a new C-facing `include/linux/zigux.h` helper surface
- new `include/zigux/abi.h` structs
- new `zigux/bindings/abi.zig` layout types
- a C-vs-Zig parity fixture for `rbtree` boundary records

The remaining honest Phase 3 `rbtree` gap after this step is the curated header-and-binding surface, not the total absence of a helper packet.

## Next bounded step

The next honest follow-up is a curated `rbtree` boundary contract in the existing ABI packet, with one small header-and-binding shape plus one parity fixture, before any further Phase 3 char-device growth.
