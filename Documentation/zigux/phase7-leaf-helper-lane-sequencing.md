# Phase 7 Leaf-Helper Lane Sequencing

This note keeps the roadmap-backed Phase 7 runtime leaf-helper packet reviewable without widening into runtime pilots, deep-core freeze anchors, or neighboring subsystem work.

## Scope

Phase 7 stays limited to the first reusable runtime-safe leaf-helper families named by the product roadmap:

- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`

These helpers are allowed to reopen only for bounded helper-local semantics, ownership, validation, or direct-anchor truthfulness repairs.

Do not use this lane to widen into:

- Phase 8 tooling expansion under `tools/lib/*`
- Phase 9 runtime pilot modules or samples
- deep-core freeze-in-C anchors covered by the Phase 15 freeze-map governance packet
- driver, MMIO, DMA, or queue work from later phases

## Current Repo Reality

Fresh repo-first inspection shows the roadmap-backed Phase 7 family is only partially materialized on current `master`.

That means the honest current lane split is helper-local and direct-readback-aware rather than a four-helper landed batch:

- `lib/string_helpers.zig` plus its helper-local survey, manifest, and no-string-sample boundary packet are directly readable and remain the clearest same-lane reopen surface
- `lib/argv_split.zig` is directly readable, but the older helper-local slice, dedicated tests, manifest, fixture, and checker companions are not directly readable in the same reread, so treat it as a narrower helper-only surface until those companion reminders return; if a shared tests-root or scripts-root reminder still omits that directly readable helper, fix the reminder one file at a time instead of reconstructing the missing companion packet
- `lib/cmdline.zig` is directly readable again on current `master`, but the older helper-local slice, dedicated tests, manifest, fixture, and checker companions are not directly readable in the same reread, so treat it as a narrower helper-only surface until those companion reminders return; if a shared reminder still frames the helper as missing, fix that reminder one file at a time instead of reconstructing the missing companion packet
- `zigux/tests/phase7_rbtree_survey.zig` and `zigux/tests/phase7_rbtree_manifest.json` are directly readable surviving anchors for the `rbtree` family, but `lib/rbtree.zig` and the older broader rbtree helper, fixture, checker, and build-route packet are not directly readable on current `master` during this reread

No helper in this packet should be treated as a generic stand-in for the others.
Reopen one directly readable helper family or surviving direct-anchor packet at a time.

## Validation Discipline

Use the narrowest honest replay that matches the chosen helper family and the files you can directly prove are present on current `master`.

- `lib/string_helpers.zig`: `zig test lib/string_helpers.zig`
- `lib/argv_split.zig`: `zig test lib/argv_split.zig`
- `lib/cmdline.zig`: `zig test lib/cmdline.zig`
- `lib/rbtree.zig`: use `zig test lib/rbtree.zig` only after a fresh reread proves the helper has returned on current `master`
- surviving `rbtree` survey-or-manifest anchor work: validate by rereading `Documentation/zigux/phase7-helper-lane-sequencing.md`, `zigux/tests/phase7_rbtree_survey.zig`, and `zigux/tests/phase7_rbtree_manifest.json` together so the surviving packet does not imply that the missing helper, fixtures, checker, or shared build routes have returned

If a future change adds shared Phase 7 tests-root wiring, keep that route additive. Do not replace the helper-local Zig replay with a broader route unless the broader route proves the same boundary more clearly.

## Anti-Overlap Rules

When this lane reopens, stay inside one bounded step only.

- Do not batch two helper families into one run.
- Prefer validation and ownership repairs before semantic expansion.
- Keep borrowed-buffer and sentinel-termination contracts explicit for `cmdline` and `argv_split`.
- Keep leftmost-cache, duplicate-search, iterator ownership, and surviving-anchor truthfulness explicit for `rbtree`.
- Keep C-string boundary, sysfs newline-equivalence, and counted-search ownership explicit for `string_helpers`.
- If a helper-local test already covers the questioned edge, do not invent a second packet for the same proof.

## Freeze-Map Posture

This Phase 7 packet is outside the deep-core freeze map.

That does not authorize broader runtime work.
It only means these runtime-safe leaf helpers may continue to evolve inside their bounded helper-owned contracts while deep-core freeze-in-C anchors remain governed by the separate Phase 15 packet.

## Next Bounded Step

Start from one directly readable helper family or surviving direct-anchor packet only and pick the smallest truthful follow-up:

- `lib/string_helpers.zig`: helper-local boundary or ownership drift in string, sysfs, or counted-search behavior
- `lib/argv_split.zig`: helper-local drift in empty-view reuse, copied-storage tokenization, or null-terminated argv export, or one shared reminder-surface truthfulness repair that explicitly names the helper-only `lib/argv_split.zig` anchor plus its `zig test lib/argv_split.zig` replay without recreating the missing slice, dedicated tests, manifest, fixture, or checker packet
- `lib/cmdline.zig`: helper-local drift in borrowed-slice parsing, `nextArg()` quoting, or `memparse()` ownership behavior, or one shared reminder-surface truthfulness repair that explicitly names the helper-only `lib/cmdline.zig` anchor plus its `zig test lib/cmdline.zig` replay without recreating the missing slice, dedicated tests, manifest, fixture, or checker packet
- surviving `rbtree` anchors: keep same-lane follow-through inside `zigux/tests/phase7_rbtree_survey.zig` or `zigux/tests/phase7_rbtree_manifest.json` until a fresh reread proves `lib/rbtree.zig` or another current helper-local companion packet has returned

If current helper-local tests, surviving direct anchors, and ownership notes already agree, leave the helper parked and do not widen to a second family in the same lane.