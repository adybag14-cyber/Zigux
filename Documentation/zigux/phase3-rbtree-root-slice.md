# Phase 3 rbtree root Slice

This note records one bounded shared-helper starter packet for the existing Phase 3 rbtree root helper on current `master`.

## Current Slice

- `zigux/bindings/rbtree_root.zig`
- `zigux/helpers/rbtree_root_view.zig`
- `zigux/tests/phase3_rbtree_root_starter_packet.zig`
- `zigux/tests/phase3_rbtree_root_starter_packet_build.zig`
- `zigux/tests/fixtures/phase3_rbtree_root_manifest.json`
- `scripts/zigux/check-phase3-rbtree-root-starter-packet.py`

## Bounded Contract

- `zigux/bindings/rbtree_root.zig` keeps the published root-view layout, cached-leftmost flags, and canonicalization surface explicit on top of the already-landed shared ABI root-view definition.
- `zigux/helpers/rbtree_root_view.zig` stays a narrow helper relay over that binding so empty, uncached, cached, and malformed root-view shapes remain directly reviewable.
- `zigux/tests/phase3_rbtree_root_starter_packet.zig` keeps the empty lane, uncached canonical lane, cached leftmost lane, cached-flag normalization, and rejection of unknown flags or rootless payloads explicit without widening into tree traversal or mutation semantics.
- `zigux/tests/fixtures/phase3_rbtree_root_manifest.json` keeps this helper-local starter packet machine-readable through its packet files, replay routes, and bounded next safe step.
- `scripts/zigux/check-phase3-rbtree-root-starter-packet.py` fail-closes the docs note, binding, helper, starter replay, build shard, and manifest so the packet does not drift back into an untracked helper.

## Replay Route

- `python3 scripts/zigux/check-phase3-rbtree-root-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-rbtree-root-starter-packet.py`
- `zig build phase3-rbtree-root-starter-packet --build-file zigux/tests/phase3_rbtree_root_starter_packet_build.zig`

## Scope

This slice stays intentionally helper-local. It does not yet claim C parity fixtures, exported ABI manifest expansion, subtree traversal, rotations, mutation helpers, or broader rbtree ownership behavior. If this lane needs parity follow-through later, keep it narrowed to one tiny C harness plus one expected fixture without widening beyond helper-local root-view layout and cached-leftmost semantics.
