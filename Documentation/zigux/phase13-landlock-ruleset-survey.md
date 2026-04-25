# Phase 13 Landlock Ruleset Survey

This document records the bounded Phase 13 survey lane around `security/landlock/ruleset.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=landlock-ruleset-helper-starter`
- scope: the landed `security/landlock/ruleset.zig` helper starter, its dedicated Phase 13 test gate and manifest, the shared Phase 13 build wiring, and the lane notes that compare the new foothold against the roadmap
- product boundary:
  - `security/landlock/ruleset.zig`
  - `zigux/tests/phase13_landlock_ruleset.zig`
  - `zigux/tests/phase13_landlock_ruleset_manifest.json`
  - `zigux/tests/phase13_build.zig`
  - `Documentation/zigux/phase13-landlock-ruleset-slice.md`
  - `Documentation/zigux/phase13-landlock-ruleset-survey.md`

## Why this slice exists

The Phase 13 roadmap explicitly names `security/landlock/ruleset.c` as a shared security-helper anchor.

That matters because the live Landlock ruleset anchor is already 719 lines and mixes access-mask bookkeeping with rb-tree storage, rule insertion, merge and inherit behavior, hierarchy lifetime, deferred frees, and domain-facing request evaluation.

The highest-value honest step in this lane is therefore not to pretend Zigux owns Landlock enforcement. It is to start with the small access-mask and layer-accounting helpers that are reviewable in isolation, then keep the remaining object-tree and hierarchy work explicit.

## Survey findings

- `security/landlock/ruleset.c` is present on `master` and is broad enough to cross several security and lifetime boundaries at once: handled-access masks, per-layer request matrices, rb-tree keyed rules, hierarchy ownership, and domain merge semantics.
- the live repo already had the shared Phase 13 build gate and `make -C zigux phase13` target, which made it practical to add a lane-local ruleset helper without widening into kernel build integration.
- the new `security/landlock/ruleset.zig` starter stays intentionally narrow around `landlock_create_ruleset()` planning, handled-access unioning, per-layer mask initialization, `landlock_unmask_layers()` bit clearing, and the matching-rule branch of `insert_rule()` where access rights are extended or a merged layer is appended.
- the starter does not claim object references, locking, rb-tree storage, hierarchy allocation, workqueue-backed deferred frees, or interaction with `security/landlock/syscalls.c`.
- the next honest ruleset-facing step is one small planner around the `insert_rule()` tree walk, especially `get_root()`, `walker_node`, and the no-match insertion-count branch, still in-memory and still outside rb-tree storage and hierarchy lifetime.

## Recorded gaps

The current lane state is:

- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-landlock-ruleset-starter`
- landed `phase13-landlock-ruleset-test-gate`
- landed `phase13-landlock-ruleset-slice-note`
- landed `phase13-landlock-ruleset-survey-note`
- landed `phase13-landlock-rule-layer-merge-followup`
- ready-next `phase13-landlock-tree-search-followup`

This keeps the lane explicit without overstating progress: Zigux now has a real `ruleset.zig` helper foothold for access-mask accounting and matching-rule insertion planning, but it still does not claim live rule storage, hierarchy ownership, or full Landlock policy enforcement.

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

Stay in the Phase 13 landlock ruleset lane and add one tiny `security/landlock/ruleset.zig` tree-search planner next, limited to `insert_rule()` root selection, `walker_node` descent, and the no-match insertion-count branch before any rb-tree storage, hierarchy lifetime, or live LSM state is attempted.
