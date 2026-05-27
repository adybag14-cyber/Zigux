# Phase 13 Landlock Ruleset Survey

This document records the bounded Phase 13 survey lane around `security/landlock/ruleset.c`.

## Status
- `PHASE13_STATUS=active`
- `PHASE13_LANE_KEY=P13-L10`
- `PHASE13_SLICE=landlock-ruleset-helper-packet-cleanup`
- reviewed against live `master` `master-readback-2026-05-27`
- scope: the shipped `security/landlock/ruleset.zig` helper starter, the helper-local ownership note, this survey note, the direct `zigux/tests/phase13_landlock_ruleset.zig` replay, the manifest-backed ruleset packet, and the dedicated packet checker
- product boundary:
  - `security/landlock/ruleset.zig`
  - `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
  - `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  - `zigux/tests/phase13_landlock_ruleset.zig`
  - `zigux/tests/phase13_landlock_ruleset_manifest.json`
  - `scripts/zigux/check-phase13-landlock-ruleset-packet.py`

## Why this slice exists
The Phase 13 roadmap explicitly names `security/landlock/ruleset.c` as one of the shared subsystem-helper anchors.

That matters because the ruleset side of Landlock sits on the boundary between reviewable access-mask and rule-tree planning and the live rb-tree, hierarchy, and ownership mutations that Zigux still must not overclaim. Current `master` ships a bounded ruleset helper starter, a helper-local ownership note, a direct replay, a manifest-backed packet, and a dedicated checker file, but the checker still carries the older ownership-absent packet shape.

The highest-value bounded work in this lane is therefore to keep that shipped packet truthful to current `master` instead of overclaiming companion note files or live ownership surfaces that are not materialized in the live tree.

## Survey findings
- `security/landlock/ruleset.zig` stays planning-only through `RulesetHelperLab.descriptor()`, `planRulesetCreation()`, `planRuleTreeSearch()`, and `planInsertRuleBranch()` without claiming live rb-tree mutation or hierarchy ownership.
- the shipped helper starter now keeps ruleset creation, handled-access capture, no-match tree-link planning, matched level-zero access-extension planning, and matched-rule layer-append planning explicit without pretending to allocate or mutate live rulesets.
- the direct `zigux/tests/phase13_landlock_ruleset.zig` replay now proves both matched-rule branches separately: level-zero updates extend the existing access mask in place, while non-zero incoming layers append a new constraint layer and preserve the rule count.
- `zigux/tests/phase13_landlock_ruleset_manifest.json` now records the current bounded packet truthfully: the helper starter, ownership note, survey note, direct replay, manifest, and dedicated checker are landed, while the older slice-note companion remains absent on current `master`.
- the immediate repo-reality gap versus the roadmap is therefore not an absent ruleset helper packet. It is the still-missing shared-build companion plus the still-missing helper-local slice note, while the existing checker also still needs a same-packet realignment from the older ownership-absent packet shape to the current ownership-present one.

## Exact Live Readback
- live helper readback on current `master` still shows `.provides_ruleset_creation_planning = true`, `.provides_rule_tree_search_planning = true`, `.provides_rule_insertion_planning = true`, `.validates_non_empty_access_masks = true`, `.validates_layer_capacity = true`, `.validates_rule_capacity = true`, and `.validates_matched_layer_order = true` in `RulesetHelperLab.descriptor()`.
- current `master` still exports `pub fn planRulesetCreation(`, `pub fn planRuleTreeSearch(`, and `pub fn planInsertRuleBranch(`, which keeps the helper-local creation, tree-search, and insert-branch planners explicit in the helper surface itself instead of burying them in survey-only prose.
- the shipped direct replay now checks the no-match tree-link path, the matched level-zero access-extension path, the matched-rule layer-append path, and the manifest packet markers while keeping the `rb_replace_node()` signal reviewable as a planner output rather than a live mutation.
- the shipped manifest now records `"current_phase13_build_present": false`, `"current_ruleset_zig_present": true`, `"current_phase13_landlock_ruleset_slice_present": false`, `"current_phase13_landlock_ruleset_ownership_present": true`, `"current_phase13_landlock_ruleset_survey_present": true`, `"current_phase13_landlock_ruleset_test_present": true`, and `"current_landlock_ruleset_packet_checker_present": true`, so the packet stays explicit about the still-missing slice note together with the still-blocked shared-build, live-tree, and hierarchy boundaries.
- the shipped checker file still expects the older ownership-absent packet shape: it looks for `blocked \`phase13-landlock-ruleset-ownership-note\`` in this survey and for `"current_phase13_landlock_ruleset_ownership_present": false` in the manifest even though current `master` now ships the ownership note and records it as present.

## Recorded gaps
The current lane state is:
- landed `phase13-landlock-ruleset-helper-starter`
- landed `phase13-landlock-ruleset-ownership-note`
- landed `phase13-landlock-ruleset-survey-note`
- landed `phase13-landlock-ruleset-direct-test-gate`
- landed `phase13-landlock-ruleset-packet-checker`
- blocked `phase13-build-gate`
- blocked `phase13-landlock-ruleset-slice-note`
- blocked `phase13-landlock-ruleset-packet-checker-realignment`
- blocked `phase13-landlock-live-tree-state`
- blocked `phase13-landlock-live-hierarchy-state`

This keeps the packet honest: Zigux has a reviewable ruleset helper starter plus the ownership note, this survey note, the direct replay, the manifest-backed packet, and the checker file, but the checker still needs ownership-state realignment and the packet still does not claim the missing slice note, a wider shared-build route, live rb-tree mutation, live hierarchy lifetime, or broader Landlock enforcement.

## Non-goals
This slice does not claim:
- live rb-tree mutation or node replacement side effects
- live ruleset object ownership or deferred-free behavior
- live hierarchy allocation, merge semantics, or lifetime control
- full Landlock enforcement or broader security policy parity
- ownership of the adjacent syscall packet or shared Phase 13 reminder surfaces
- closure of the wider Phase 13 shared-helper tranche

## Next bounded step
If this helper-local packet reopens, compare `security/landlock/ruleset.zig`, `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py` together on current `master` before widening into any new shared release-note, syscall, notifier, or live-state work.
