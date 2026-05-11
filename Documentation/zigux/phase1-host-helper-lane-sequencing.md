# Phase 1 Host-Helper Lane Sequencing

This note keeps the closed Phase 1 host-helper packet reviewable without reopening helper semantics or batching unrelated follow-up work back together.

## Scope

Phase 1 stays limited to the roadmap-backed host-side helper tranche:

- `tools/lib/bitmap.zig`
- `tools/lib/find_bit.zig`
- `tools/lib/string.zig`
- `tools/lib/rbtree.zig`
- tightly coupled parity, closure, benchmark, and review-surface gates that already belong to that helper packet

Do not use this lane to widen into runtime helpers, Phase 3 ABI work, sample work, or later driver phases.

## Current Split

The live Phase 1 packet on `master` is already closed as a bounded helper tranche, but it is intentionally split into two follow-up families.

### Shared-Replay Parked Helpers

These helpers reopen only for shared replay drift, fixture drift, build-route drift, or review-surface truthfulness:

- `tools/lib/argv_split.zig`
- `tools/lib/cmdline.zig`
- `tools/lib/ctype.zig`
- `tools/lib/hweight.zig`
- `tools/lib/list_sort.zig`
- `tools/lib/slab.zig`
- `tools/lib/str_error_r.zig`
- `tools/lib/vsprintf.zig`
- `tools/lib/zalloc.zig`

### Direct-Anchor Follow-Up Helpers

These are the only helpers that still keep bounded direct helper-local follow-up anchors on current `master`:

- `tools/lib/bitmap.zig`
- `tools/lib/find_bit.zig`
- `tools/lib/rbtree.zig`
- `tools/lib/string.zig`

## Current Repo Reality

Fresh repo-first inspection shows that the older saved bitmap closure-validator blocker is already closed on current `master`.

The Phase 1 closure validator already carries the bitmap final-partial-word and Linux-style alias closure markers that older lane memory still described as missing. Future runs should not reopen that already-landed validator sync.

The docs-root Phase 1 summary now also names this owner-map note, so the earlier `Documentation/zigux/README.md` truthfulness gap is closed on current `master` as well.

Fresh validator-local rereads still show that the parked `scripts/zigux/validate-phase1.py` bitmap-manifest-anchor handoff is the next smallest same-lane follow-up, but its saved publication helper is preimage-pinned to an older live validator body. Future runs should refresh that one-file helper against current `master` before trying to land it.

## Anti-Overlap Rules

When this lane reopens, stay inside one bounded step only.

- Do not batch shared-replay parked helpers with the direct-anchor helper family.
- Do not reopen the already-landed bitmap closure-marker repair.
- Do not reopen the already-landed docs-root owner-map sync.
- Prefer the smallest same-family reviewability, parity-gate, fixture, or build-route repair before changing helper semantics.
- If the exact direct-anchor gap is already closed on `master`, advance only to the next unfinished bounded step inside the same helper family.

## Next Bounded Step

The next honest same-lane follow-up is to refresh the parked one-file `scripts/zigux/validate-phase1.py` bitmap-manifest-anchor helper against the current live validator preimage, then tighten the shared Phase 1 closure-validator packet around the same owner-map note so the docs-root and fail-closed review surfaces cannot drift apart.

Until that validator refresh lands, keep Phase 1 follow-up work parked on review-surface truthfulness, closure accuracy, fixture drift, or other already-shipped parity-gate surfaces rather than reopening helper behavior.

## Footer

This note is lane-local coordination only. It does not reopen the closed Phase 1 helper tranche or imply wider product scope.
