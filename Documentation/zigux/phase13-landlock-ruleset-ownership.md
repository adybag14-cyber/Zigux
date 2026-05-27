# Phase 13 Landlock Ruleset Ownership

This note records the bounded ownership and review split for the shared Phase 13 Landlock ruleset packet so helper-local reminder surfaces do not blur planner-only ruleset work into live rb-tree, hierarchy, or syscall ownership.

## Scope

This note is for the ruleset side of the active Phase 13 Landlock packet only.

Current `master` materializes `security/landlock/ruleset.zig` as a helper-local starter for the roadmap-owned `security/landlock/ruleset.c` anchor. Keep helper-owned wording tightly scoped to descriptor-backed ruleset creation planning, rule-tree search planning, insert-with-link planning, matched-rule replacement planning, matched level-zero access-extension planning, matched-rule layer-append planning, and access-mask, layer-capacity, rule-capacity, and matched-layer-order validation.

Do not present that helper packet as live rb-tree mutation, live ruleset ownership transfer, hierarchy allocation, domain merge semantics, deferred-free lifetime control, or full Landlock enforcement.

## Current Repo Reality

Current `master` now materializes the ruleset helper packet through:
- `security/landlock/ruleset.zig`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`

Current `master` still does not materialize these directly coupled companions:
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `zigux/tests/phase13_build.zig`

Keep these neighboring surfaces distinct:
- `Documentation/zigux/phase13-roadmap-traceability.md` for the broader Phase 13 roadmap-to-repo owner map
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` for the broader Phase 13 owner split and lane routing
- `Documentation/zigux/phase13-landlock-syscalls-governance.md` for syscall-packet ownership and review boundaries

## Owned Review Surface

When contributors touch the ruleset-facing Landlock packet, keep this note aligned first with the shipped helper-local packet:
- `security/landlock/ruleset.zig`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`

Keep contributor guidance anchored to the helper-local packet while the slice note and shared-build companion remain absent.

## Ownership Boundaries

Use this note to keep these boundaries explicit:
- helper-local ownership wording, review prompts, and reminder-surface review boundaries belong here
- the helper surface, survey note, direct replay, manifest, and packet checker belong here today
- slice-note ownership stays recorded as a repo-reality gap until that file returns on `master`
- future work should stay tied to planning-only ruleset behavior instead of treating it as live rb-tree mutation, live hierarchy lifetime, or full Landlock enforcement

## Review Prompts

If a change updates the Phase 13 Landlock ruleset packet, verify that:
- the broad Phase 13 reminder surfaces keep this ownership note explicit beside the survey, checker, direct replay, and manifest
- no wording here promotes the still-missing slice note or shared-build companion into shipped current-`master` evidence
- helper-owned wording stays limited to ruleset creation, rule-tree search, insert-branch planning, and the bounded validation surfaces that keep those planner contracts reviewable
- note-versus-gap ownership stays explicit: this note owns the helper-local policy and ownership packet, while the remaining gaps stay `Documentation/zigux/phase13-landlock-ruleset-slice.md` and `zigux/tests/phase13_build.zig`
