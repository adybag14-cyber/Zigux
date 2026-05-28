# Phase 1 Rbtree Shared Replay Evidence

This note records the current-master shared replay evidence for the Phase 1 `tools/lib/rbtree.zig` helper so nearby lanes do not reopen the cached-root packet from stale or incomplete assumptions.

## Roadmap and Ledger Context

Phase 1 in the roadmap closes host-side helper work through bounded helper ports plus honest closure evidence. The bootstrap ledger already places `tools/lib/rbtree.zig` inside the Phase 1 helper tranche and the later Phase 1 closure train, so the useful follow-up here is evidence alignment rather than another semantic widening.

## Current Master Evidence

Current `master` already carries the helper-local direct anchors in `tools/lib/rbtree.zig`, including ordered Linux-style alias coverage, low-level Linux-style alias coverage, duplicate-range traversal helpers, and the cached-root insert, leftmost, replacement, detach, singleton-erase, and reseed paths.

The committed Phase 1 fixture at `zigux/tests/fixtures/phase1_helpers.json` already records both of the bounded cached-root shared witnesses:

- `cached_leftmost_return_serials`
- `cached_root_transition_serials`

The focused Phase 1 replay at `zigux/tests/phase1_helpers.zig` already rechecks both witness packets against the live helper.

The shared tests-root smoke route at `zigux/tests/phase1_host_tools_smoke.zig` also already rechecks both witness families on current `master`:

- duplicate-range iteration through `find()`, `findFirst()`, `nextMatch()`, and `matchIterator()`
- exact `cached_leftmost_return_serials` return values `[0, -1, 2, -1]`
- exact `cached_root_transition_serials` transition values `[0, 0, 4, 2]`

That means the cached-root transition witness is already landed shared closure evidence, not helper-local-only context.

## Safe Reopen Rule

Future Phase 1 rbtree rereads should treat `cached_leftmost_return_serials` and `cached_root_transition_serials` as the shared replay packet that is already committed and smoke-checked on current `master`.

Keep the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local until another broader replay field lands. Reopen the helper only for drift in those helper-local anchors, drift in the committed duplicate-search fields, or drift in the two shared cached-root witness packets named above.
