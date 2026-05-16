# Phase 7 Leaf-Helper Lane Sequencing

This note keeps the roadmap-backed Phase 7 runtime leaf-helper packet reviewable without widening into runtime pilots, deep-core freeze anchors, or neighboring subsystem work.

## Scope

Phase 7 stays limited to the first reusable runtime-safe leaf-helper families named by the product roadmap:

- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`

These helpers are allowed to reopen only for bounded helper-local semantics, ownership, or validation repairs.

Do not use this lane to widen into:

- Phase 8 tooling expansion under `tools/lib/*`
- Phase 9 runtime pilot modules or samples
- deep-core freeze-in-C anchors covered by the Phase 15 freeze-map governance packet
- driver, MMIO, DMA, or queue work from later phases

## Current Repo Reality

Fresh repo-first inspection shows the live Phase 7 packet already has its four roadmap-backed runtime helper destinations under `lib/`.

That means the honest current lane split is helper-local rather than shared-batch delivery:

- `lib/string_helpers.zig` owns string copy-and-pad helpers, sysfs and match-string equality rules, counted-search helpers, and C-string-safe duplication or replacement follow-through
- `lib/cmdline.zig` owns `memparse()`, `parseOptionStr()`, `nextArg()`, and option-range parsing follow-through
- `lib/argv_split.zig` owns copied-storage tokenization, exported empty-view reuse, and null-terminated argv contract follow-through
- `lib/rbtree.zig` owns ordered traversal, duplicate-search helpers, cached-root leftmost tracking, and alias-surface follow-through

No helper in this packet should be treated as a generic stand-in for the others. Reopen one helper family at a time.

## Validation Discipline

Use the narrowest honest replay that matches the chosen helper family.

- `lib/string_helpers.zig`: `zig test lib/string_helpers.zig`
- `lib/cmdline.zig`: `zig test lib/cmdline.zig`
- `lib/argv_split.zig`: `zig test lib/argv_split.zig`
- `lib/rbtree.zig`: `zig test lib/rbtree.zig`

If a future change adds shared Phase 7 tests-root wiring, keep that route additive. Do not replace the helper-local Zig replay with a broader route unless the broader route proves the same boundary more clearly.

## Anti-Overlap Rules

When this lane reopens, stay inside one bounded step only.

- Do not batch two helper families into one run.
- Prefer validation and ownership repairs before semantic expansion.
- Keep borrowed-buffer and sentinel-termination contracts explicit for `cmdline` and `argv_split`.
- Keep leftmost-cache, duplicate-search, and iterator ownership explicit for `rbtree`.
- Keep C-string boundary, sysfs newline-equivalence, and counted-search ownership explicit for `string_helpers`.
- If a helper-local test already covers the questioned edge, do not invent a second packet for the same proof.

## Freeze-Map Posture

This Phase 7 packet is outside the deep-core freeze map.

That does not authorize broader runtime work.
It only means these four runtime-safe leaf helpers may continue to evolve inside their bounded helper-owned contracts while deep-core freeze-in-C anchors remain governed by the separate Phase 15 packet.

## Next Bounded Step

Start from one helper family only and pick the smallest truthful follow-up:

- `lib/string_helpers.zig`: helper-local boundary or ownership drift in string, sysfs, or counted-search behavior
- `lib/cmdline.zig`: helper-local drift in `memparse()`, `parseOptionStr()`, or `nextArg()` token-boundary behavior
- `lib/argv_split.zig`: helper-local drift in empty-view reuse, copied-storage tokenization, or null-terminated argv export
- `lib/rbtree.zig`: helper-local drift in cached-root leftmost behavior, duplicate-search traversal, or alias-surface parity

If current helper-local tests and ownership notes already agree, leave the helper parked and do not widen to a second family in the same lane.
