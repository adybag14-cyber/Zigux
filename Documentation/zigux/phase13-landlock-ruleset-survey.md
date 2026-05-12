# Phase 13 Landlock Ruleset Survey

This document records the bounded Phase 13 survey lane around `security/landlock/ruleset.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=landlock-ruleset-helper-boundary-survey`
- reviewed against live `master` `master-readback-2026-05-12`
- scope: the shipped `security/landlock/ruleset.zig` helper starter, the direct `zigux/tests/phase13_landlock_ruleset.zig` replay, the manifest-backed ruleset packet, the paired ownership note, the dedicated packet checker, and the still-missing slice and shared-build companions that would be required before this packet could claim a broader replay bundle
- product boundary:
  - `security/landlock/ruleset.zig`
  - `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
  - `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  - `zigux/tests/phase13_landlock_ruleset.zig`
  - `zigux/tests/phase13_landlock_ruleset_manifest.json`
  - `scripts/zigux/check-phase13-landlock-ruleset-packet.py`

## Why this slice exists

The Phase 13 roadmap explicitly names `security/landlock/ruleset.c` as one of the shared subsystem-helper anchors.

That matters because the ruleset side of Landlock sits right on the boundary between reviewable access-mask and rule-tree planning and the live rb-tree, hierarchy, and ownership mutations that Zigux still must not overclaim.

Current `master` already ships a small ruleset helper starter, a direct replay, a manifest-backed packet, and a dedicated packet checker. The highest-value bounded work in this lane is therefore to keep that shipped helper packet rereadable as its own survey note instead of leaving the ruleset boundary implied through the ownership note and broader release-facing reminders alone.

## Survey findings

- `security/landlock/ruleset.zig` stays planning-only through `RulesetHelperLab.descriptor()`, with `.touches_live_object_trees = false` and `.touches_live_hierarchy = false` keeping the helper honest about what it does not claim.
- the shipped helper starter keeps ruleset-creation and access-mask accounting explicit through `planRulesetCreation()`, `unionAccessMasks()`, `initLayerMasks()`, and `unmaskLayers()` without pretending to allocate or mutate live rulesets.
- the shipped helper starter keeps the `insert_rule()` branch split explicit through `planRuleInsertion()`, `planRuleTreeSearch()`, `planRuleTreeLink()`, `planRuleTreeReplacement()`, and `planInsertRuleBranch()`, so the no-match attach path and the matched-rule replacement path stay reviewable as helper planning rather than live tree mutation.
- the direct `zigux/tests/phase13_landlock_ruleset.zig` replay already proves the descriptor contract, the no-match tree-link planner, the matched-rule replacement planner, and the manifest-backed packet markers without widening into live rb-tree ownership.
- `zigux/tests/phase13_landlock_ruleset_manifest.json` already records the same bounded packet truthfully: it keeps the ruleset helper starter, direct replay, and dedicated packet checker marked as landed while the older shared `zigux/tests/phase13_build.zig` surface plus live tree and hierarchy state stay blocked.
- current `master` still does not materialize `Documentation/zigux/phase13-landlock-ruleset-slice.md` or the older shared `zigux/tests/phase13_build.zig` route, so the ruleset lane remains a helper-local replay packet rather than a wider shared-build replay story.
- the immediate repo-reality gap versus the roadmap is therefore not an absent ruleset helper packet. It is the still-missing slice note and shared-build companion around the helper, replay, manifest, checker, and survey surfaces that current `master` already ships.

## Exact Live Readback

- live helper readback on current `master` still shows `.provides_ruleset_creation_planning = true`, `.provides_union_access_masks = true`, `.provides_layer_mask_init = true`, `.provides_rule_unmasking = true`, `.provides_rule_insertion_planning = true`, `.provides_rule_tree_search_planning = true`, `.provides_rule_tree_link_planning = true`, `.provides_rule_tree_replacement_planning = true`, and `.provides_insert_rule_branch_planning = true` in `RulesetHelperLab.descriptor()`.
- current `master` still exports `pub fn planRuleTreeSearch(`, `pub fn planRuleTreeLink(`, `pub fn planRuleTreeReplacement(`, and `pub fn planInsertRuleBranch(`, which keeps the helper-local tree-search, link, and matched-rule replacement planners explicit in the helper surface itself instead of burying them in survey-only prose.
- the shipped direct replay still checks the descriptor contract, the no-match tree-link path, the matched-rule replacement path, and the manifest packet markers while keeping the `rb_replace_node()` signal reviewable as a planner output rather than a live mutation.
- the shipped manifest still records `"current_phase13_build_present": false`, `"current_ruleset_zig_present": true`, `"current_phase13_landlock_ruleset_test_present": true`, `"current_landlock_ruleset_packet_checker_present": true`, `"status": "blocked_on_live_tree_state"`, and `"status": "blocked_on_hierarchy_lifetime"`, so the packet remains explicit about the still-blocked live-tree and hierarchy boundaries.

## Recorded gaps

The current lane state is:

- landed `phase13-landlock-ruleset-helper-starter`
- landed `phase13-landlock-ruleset-ownership-note`
- landed `phase13-landlock-ruleset-survey-note`
- landed `phase13-landlock-ruleset-direct-test-gate`
- landed `phase13-landlock-ruleset-packet-checker`
- blocked `phase13-landlock-ruleset-slice-note`
- blocked `phase13-build-gate`
- blocked `phase13-landlock-live-tree-state`
- blocked `phase13-landlock-live-hierarchy-state`

This keeps the packet honest: Zigux now has a reviewable ruleset helper starter plus the paired ownership note, this survey note, the direct replay, the manifest-backed packet, and the dedicated checker, but it still does not claim a wider shared-build route, live rb-tree mutation, live hierarchy lifetime, or broader Landlock enforcement.

## Non-goals

This slice does not claim:

- live rb-tree mutation or node replacement side effects
- live ruleset object ownership or deferred-free behavior
- live hierarchy allocation, merge semantics, or lifetime control
- full Landlock enforcement or broader security policy parity
- ownership of the adjacent syscall packet or notifier reminder surfaces
- closure of the wider Phase 13 shared-helper tranche

## Next bounded step

If this helper-local packet reopens, compare `security/landlock/ruleset.zig`, `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py` together on current `master` before widening into any new shared release-note, syscall, notifier, or live-state work.