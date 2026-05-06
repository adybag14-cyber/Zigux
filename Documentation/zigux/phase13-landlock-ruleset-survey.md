# Phase 13 Landlock Ruleset Survey

This document records the bounded Phase 13 survey lane around `security/landlock/ruleset.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_LANE_KEY=P13-L12`
- `PHASE13_SLICE=landlock-ruleset-helper-lab`
- scope: the landed `security/landlock/ruleset.zig` helper lab, its dedicated Phase 13 test gate and manifest, the shared Phase 13 build wiring, the dedicated packet checker at `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, and the lane notes that compare the current helper boundary against the roadmap
- product boundary:
  - `security/landlock/ruleset.zig`
  - `zigux/tests/phase13_landlock_ruleset.zig`
  - `zigux/tests/phase13_landlock_ruleset_manifest.json`
  - `zigux/tests/phase13_build.zig`
  - `Documentation/zigux/phase13-landlock-ruleset-slice.md`
  - `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  - `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
  - `scripts/zigux/check-phase13-landlock-ruleset-packet.py`

## Why this slice exists

The Phase 13 roadmap explicitly names `security/landlock/ruleset.c` as a shared security-helper anchor.

That matters because the live Landlock ruleset anchor is already 719 lines and mixes access-mask bookkeeping with rb-tree storage, rule insertion, merge and inherit behavior, hierarchy lifetime, deferred frees, and domain-facing request evaluation.

The highest-value honest step in this lane is therefore not to pretend Zigux owns Landlock enforcement. It is to keep the access-mask and insertion-accounting helpers reviewable in isolation, then keep the remaining object-tree and hierarchy work explicit.

## Survey findings

- `security/landlock/ruleset.c` is present on `master` and is broad enough to cross several security and lifetime boundaries at once: handled-access masks, per-layer request matrices, rb-tree keyed rules, hierarchy ownership, and domain merge semantics.
- the live repo already had the shared Phase 13 build gate and `make -C zigux phase13` target, which made it practical to add a lane-local ruleset helper without widening into kernel build integration.
- the current `security/landlock/ruleset.zig` helper lab stays intentionally narrow around `landlock_create_ruleset()` planning, handled-access unioning, per-layer mask initialization, `landlock_unmask_layers()` bit clearing, the matching-rule branch of `insert_rule()`, the tree-search outcome planning for `get_root()`, `walker_node`, and no-match insertion-count changes, and the explicit root or left or right tree-link mode for the `rb_link_node()` and `rb_insert_color()` branch.
- the helper-only ownership note now makes the review boundary explicit: `ruleset.zig` owns only the in-memory helper planners above, while `security/landlock/syscalls.zig` keeps file-descriptor, path, and `landlock_restrict_self()` branches, and the live-tree blocker still owns `rb_replace_node()`, object ownership, and hierarchy lifetime.
- the fixture-governance rule for this helper packet is now explicit as well: the ownership note, slice note, survey note, manifest, dedicated test gate, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py` must move together whenever the helper-owned surface or blocked live-tree claim changes.
- the Phase 13 validate path can now run `scripts/zigux/check-phase13-landlock-ruleset-packet.py` to catch drift between the helper-owned ruleset surface, its manifest-backed review packet, and the shared build wiring without widening into live rb-tree state.
- the helper lab does not claim object references, locking, rb-tree storage, hierarchy allocation, workqueue-backed deferred frees, or interaction with `security/landlock/syscalls.c`.
- the remaining ruleset gap now starts where pure in-memory planning stops being honest: `rb_replace_node()`, object ownership, hierarchy lifetime, and other live ruleset state are still outside this helper lab.

## Recorded gaps

The current lane state is:

- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-landlock-ruleset-starter`
- landed `phase13-landlock-ruleset-test-gate`
- landed `phase13-landlock-ruleset-slice-note`
- landed `phase13-landlock-ruleset-survey-note`
- landed `phase13-landlock-ruleset-ownership-note`
- landed `phase13-landlock-rule-layer-merge-followup`
- landed `phase13-landlock-tree-search-followup`
- landed `phase13-landlock-tree-link-followup`
- blocked `phase13-landlock-live-tree-state-blocker`

This keeps the lane explicit without overstating progress: Zigux now has a real `ruleset.zig` helper foothold for access-mask accounting, matching-rule insertion planning, tree-search outcome planning, and no-match tree-link planning, plus one dedicated ownership note that fences the helper packet off from adjacent syscall work and from live-tree claims, but it still does not claim live rule storage, hierarchy ownership, or full Landlock policy enforcement.

## Non-goals

This survey slice does not claim:

- rb-tree mutation or lookup parity
- object reference counting
- hierarchy allocation or parent linkage
- deferred free workqueue behavior
- live ruleset file-descriptor plumbing
- Landlock syscall integration
- LSM hook enforcement

## Gates

1. run the dedicated Phase 13 build
- `zig build test --build-file zigux/tests/phase13_build.zig`

2. run the convenience target
- `make -C zigux phase13`

## Next bounded step

Stay in the Phase 13 landlock ruleset lane only if there is a narrowly reviewable way to study `rb_replace_node()`, object ownership, or hierarchy lifetime without overstating live Landlock behavior; otherwise keep this slice in its current helper-only state.