# Phase 3 Rbtree Interop Survey

This note records the current state of the roadmap-backed `lib/rbtree.c` anchor inside the live Phase 3 ABI and interop packet.

## Status

- `PHASE3_RBTREE_ROADMAP_ANCHOR=lib/rbtree.c`
- `PHASE3_RBTREE_PHASE1_EVIDENCE=tools/lib/rbtree.zig,Documentation/zigux/phase1-closure.md`
- `PHASE3_RBTREE_PHASE7_EVIDENCE=lib/rbtree.zig,Documentation/zigux/phase7-rbtree-slice.md,zigux/tests/phase7_rbtree.zig,zigux/tests/phase7_rbtree_survey.zig,zigux/tests/phase7_rbtree_manifest.json`
- `PHASE3_RBTREE_PHASE3_SURVEY=Documentation/zigux/phase3-rbtree-interop-survey.md`
- `PHASE3_RBTREE_PHASE3_BOUNDARY=missing-helper-dump-fixture-and-slice`
- `PHASE3_RBTREE_NON_GOALS=no-balancing-port,no-export-shim-growth,no-uapi-growth`
- `PHASE3_RBTREE_NEXT_BOUNDED_STEP=one-curated-phase3-rbtree-view-slice`

## Roadmap Anchor

Phase 3 names `lib/rbtree.c` as one of the four permanent C/Zigux boundary anchors. That means the remaining work here is not general helper growth. The remaining work is one reviewable Phase 3 packet that turns existing `rbtree` evidence into a boundary-facing interop slice.

## Current Evidence

The repo already carries real `rbtree` evidence in two later-adjacent packets:

- `tools/lib/rbtree.zig` plus `Documentation/zigux/phase1-closure.md` record the earlier host-helper parity lane
- `lib/rbtree.zig`, `Documentation/zigux/phase7-rbtree-slice.md`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, and `zigux/tests/phase7_rbtree_manifest.json` record the later runtime-helper lane

That evidence matters because the remaining Phase 3 gap is not “no `rbtree` work exists.” The real gap is that current `master` still has no Phase 3 boundary packet that exposes one curated `rbtree` interop surface through the ABI and bindings layer.

## Missing Boundary Packet

Current `master` still lacks the direct Phase 3 packet that would close this anchor:

- no `zigux/helpers/rbtree*.zig` boundary-facing helper family
- no `zigux/tests/phase3_rbtree*.zig` dump, fixture, or parity packet
- no `Documentation/zigux/phase3-rbtree-slice.md` slice note
- no curated `rbtree` surface in `include/zigux/abi.h` or `zigux/bindings/abi.zig`

So the gap has narrowed from “survey or slice missing” to “survey now exists, but the actual boundary-facing slice is still missing.”

## Non-Goals

This survey does not treat any of the following as the next honest Phase 3 step:

- porting the full balancing or mutation path from `lib/rbtree.c`
- widening `zigux/kernel/export_shim.zig` or `zigux/uapi/version.zig`
- counting the larger `chrdev_*` planning ladder as substitute closure for the roadmap-backed `rbtree` anchor

## Next Bounded Step

The next honest same-lane follow-on is one small Phase 3 `rbtree` interop slice:

- one curated read-mostly node or root view type
- one committed dump or manifest-backed parity fixture
- one explicit replay path that keeps the slice reviewable without widening into a full balancing port
