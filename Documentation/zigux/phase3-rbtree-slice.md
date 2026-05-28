# Phase 3 rbtree Slice

This note records one bounded Phase 3 helper-local `rbtree` starter packet on current work for the `abi-runtime` lane.

## Current Slice

- `zigux/helpers/rbtree_view.zig`
- `zigux/tests/phase3_rbtree_starter_packet.zig`
- `zigux/tests/phase3_rbtree_starter_packet_build.zig`
- `zigux/tests/fixtures/phase3_rbtree_manifest.json`
- `scripts/zigux/check-phase3-rbtree-starter-packet.py`

## Bounded Contract

This packet stays intentionally small:

- `zigux/helpers/rbtree_view.zig` only decodes one `rb_root` pointer plus one `rb_node` parent-and-color word into a reviewable helper-local surface.
- The helper keeps color, parent, child, inorder successor, inorder predecessor, and empty-root decoding explicit without widening into insert, erase, rebalance, or tree mutation logic.
- `zigux/tests/phase3_rbtree_starter_packet.zig` keeps the empty-root case, parent/color decoding, leftmost/rightmost traversal, and inorder successor/predecessor traversal visible.
- `zigux/tests/phase3_rbtree_starter_packet_build.zig` gives the packet one focused replay route instead of wiring it into the broader shared ABI aggregate.
- `zigux/tests/fixtures/phase3_rbtree_manifest.json` plus `scripts/zigux/check-phase3-rbtree-starter-packet.py` keep the packet fail-closed and reviewable.

## Current Gap

This is still not a full shared ABI catalog addition or a broader runtime-tree port. The landed packet only closes the roadmap-shaped `lib/rbtree.c` helper-local interop gap with a starter decoder and focused replay route.

## Scope

This note is limited to one helper-local `rbtree_view` decoder, one starter packet, one focused build file, one helper-local manifest, and one checker. It does not claim rotation semantics, mutation safety, or broader shared validator coverage.
