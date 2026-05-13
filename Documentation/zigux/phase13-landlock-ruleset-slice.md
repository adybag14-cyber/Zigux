# Phase 13 Landlock Ruleset Slice

This document tracks the bounded Phase 13 shared-security-helper slice for Zigux around `security/landlock/ruleset.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=landlock-ruleset-helper-planning-packet`
- roadmap posture: keep the Phase 13 shared-security-helper foothold reviewable without overstating live Landlock mutation
- scope: ruleset-creation planning, access-mask unioning, per-layer mask initialization, rule unmasking, insert-rule planning, tree search, tree link, matched-rule replacement planning, and direct replay plus manifest review only

## Product Boundary

- `security/landlock/ruleset.zig`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`

## Why This Slice Exists

The Phase 13 roadmap explicitly names `security/landlock/ruleset.c` as a shared subsystem-helper anchor.

The current Zigux ruleset helper already covers the reviewable planner side of Landlock ruleset handling, but the lane still needed a helper-local slice note so contributors could see that packet boundary directly instead of reconstructing it from the ownership note and survey alone.

This slice therefore keeps the packet focused on helper planning and direct replay while the missing shared `zigux/tests/phase13_build.zig` route and the blocked live rb-tree and hierarchy work remain outside scope.

## Current Parity Surface

The current packet covers:

- `RulesetHelperLab.descriptor()` with explicit no-live-tree and no-live-hierarchy flags
- `planRulesetCreation()`, `unionAccessMasks()`, `initLayerMasks()`, and `unmaskLayers()` for helper-only access-mask shaping
- `planRuleInsertion()` for fresh-rule and merged-layer follow-up planning
- `planRuleTreeSearch()`, `planRuleTreeLink()`, `planRuleTreeReplacement()`, and `planInsertRuleBranch()` for no-match attach and matched-rule replacement planning
- the direct `zigux/tests/phase13_landlock_ruleset.zig` replay for descriptor, no-match link, matched replacement, and manifest-backed packet markers
- `zigux/tests/phase13_landlock_ruleset_manifest.json` for the packet's landed-versus-blocked state
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py` for the shared companion surface around the ruleset lane

The current packet does not cover:

- live `rb_link_node()`, `rb_insert_color()`, or `rb_replace_node()` mutation side effects beyond planner outputs
- live ruleset object ownership, deferred free, or hierarchy allocation
- the older shared `zigux/tests/phase13_build.zig` route

## Gates

1. run the dedicated ruleset packet checker:
- `python3 scripts/zigux/check-phase13-landlock-ruleset-packet.py`

2. run the shared Phase 13 validator route:
- `make -C zigux phase13-validate`

## Non-Goals

This slice does not claim:

- live rb-tree mutation or storage ownership
- live hierarchy allocation or merge semantics
- broader policy enforcement or syscall-lane ownership
- shared Phase 13 reminder cleanup outside the directly coupled ruleset packet

## Next Bounded Step

If this lane reopens, compare `security/landlock/ruleset.zig`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py` together before claiming any live tree, hierarchy, shared-build, or syscall-surface follow-through.
