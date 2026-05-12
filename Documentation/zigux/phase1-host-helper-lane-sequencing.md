# Phase 1 Host-Helper Lane Sequencing

This note keeps the closed Phase 1 host-helper packet reviewable without reopening helper semantics or batching unrelated follow-up work back together.

## Scope

Phase 1 stays limited to the roadmap-backed host-side helper tranche and the already-shipped shared validation surfaces that belong to that tranche.

- all thirteen closed `tools/lib/*.zig` helpers named in `zigux/tests/fixtures/phase1_helper_manifest.json`
- tightly coupled parity, closure, benchmark, and review-surface gates that already belong to that helper packet

Do not use this lane to widen into runtime helpers, Phase 3 ABI work, sample work, or later driver phases.

## Current Split

Current `master` keeps the closed Phase 1 helper packet split into two non-overlapping follow-up families.

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

- `PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`
- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`
- `PHASE1_LANE_RULE_SUMMARY=Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.`
- `PHASE1_LANE_ANTI_OVERLAP_RULE=Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.`

## Current Repo Reality

Fresh repo-first inspection shows that the honest current owner map is the shared Phase 1 helper manifest plus the live helper-local anchors, not an older bitmap-only reopen guide.

That means:

- `zigux/tests/fixtures/phase1_helper_manifest.json` is the authoritative owner-map split for all thirteen closed Phase 1 helpers
- the nine shared-replay parked helpers stay parked unless their shared replay, fixture, build-route, or review-surface packet drifts
- bitmap, find_bit, rbtree, and string are the only helpers eligible for bounded direct-anchor follow-up, and even those should reopen only inside their existing helper-local anchors or already-committed shared fixture keys
- the bitmap owner map now also includes the already-landed shared closure-validator review markers recorded in `Documentation/zigux/phase1-closure.md` and enforced by `scripts/zigux/validate-phase1-closure.py`, so nearby runs should not keep treating that validator packet as a separate generic Phase 1 reopen cue
- the direct-anchor manifest exactness surface in `scripts/zigux/validate-phase1.py` is closed for the shared helper split, manifest packet, helper anchors, and committed replay keys, but the helper-specific direct-owner marker lines in this note still need direct reread until that validator exact-checks them too
- older helper-local reopen cues that are already closed on `master` should not be replayed as the generic next Phase 1 step or used to justify reopening a different helper family

## Anti-Overlap Rules

When this lane reopens, stay inside one bounded step only.

- Do not batch helpers across the shared-replay parked and direct-anchor follow-up families in one run.
- Shared-replay parked helpers reopen only for packet drift, fixture drift, build-route drift, or review-surface truthfulness.
- Direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.
- If a helper-local gap is already closed on `master`, do not keep replaying the older saved cue; advance only to the next unfinished bounded step inside that same helper family.
- Do not treat bitmap-only validator or closure-note follow-through as the default Phase 1 reopen path now that the live owner map spans all thirteen helpers.
- Prefer the smallest same-family reviewability, parity-gate, fixture, benchmark, or build-route repair before changing helper semantics.

## Direct-Anchor Owner Map

Current `master` also needs one helper-specific owner map for the four direct-anchor helpers so nearby lanes do not keep reaching for the same shared follow-up surface from different helper families.

- `tools/lib/bitmap.zig` owns its helper-local bitmap anchors, the committed bitmap replay keys in `zigux/tests/fixtures/phase1_helpers.json`, and the already-landed shared closure-validator bitmap review markers in `Documentation/zigux/phase1-closure.md` plus `scripts/zigux/validate-phase1-closure.py`. The shared helper-split and manifest exactness surface in `scripts/zigux/validate-phase1.py` is already closed, but these helper-specific direct-owner markers still need direct reread until that validator exact-checks them too, so a nearby bitmap reopen should start from fresh direct-anchor or committed shared replay drift instead of replaying an older validator cue.
- `tools/lib/find_bit.zig` owns only its helper-local start-mask, boundary, zero-window, past-`nbits`, alias, and tail-word anchors plus the committed `find_bit` replay fields already emitted by `zigux/tests/fixtures/phase1_helpers_c_harness.c` and consumed by `zigux/tests/fixtures/phase1_helpers.json`. Reopen shared replay only if that committed `find_bit` packet drifts.
- `tools/lib/rbtree.zig` keeps iterator and cached-root coverage helper-local until `master` ships exactly one dedicated shared iterator or cached-root leftmost-return fixture key. Do not batch both widenings into one reopen step.
- `tools/lib/string.zig` already keeps the shared string helper-manifest anchor lists aligned through `scripts/zigux/validate-phase1-closure.py`, so the next honest string reopen is direct helper-local anchor drift or committed shared replay drift, not a generic closure-validator tightening pass.

- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys and the already-landed shared closure-validator bitmap review markers it already owns`
- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local anchors plus the committed find_bit replay fields already emitted by the shared C harness and consumed by the shared fixture`
- `PHASE1_RBTREE_DIRECT_OWNER=rbtree iterator and cached-root coverage stay helper-local until exactly one dedicated shared iterator or cached-root leftmost-return fixture key lands`
- `PHASE1_STRING_DIRECT_OWNER=string already has shared helper-manifest anchor validation in validate-phase1-closure.py, so reopen only for direct anchor drift or committed shared replay drift`

These four helper-specific owner markers are still lane-local reread surfaces on current `master`: `scripts/zigux/validate-phase1.py` exact-checks the shared helper split, manifest packet, helper anchors, and committed replay keys, but it does not exact-check these four direct-owner lines yet.

## Next Bounded Step

Start from `zigux/tests/fixtures/phase1_helper_manifest.json` and pick one helper family only.

- If the helper sits in the shared-replay parked set, reread only its shared replay, fixture, build-route, and review-surface packet and land one drift repair if needed.
- If the helper sits in the direct-anchor set, reread only that helper's direct anchors plus any already-committed shared fixture keys it owns and land one bounded follow-up if needed.
- For `tools/lib/bitmap.zig`, do not replay the closed `scripts/zigux/validate-phase1.py` or `scripts/zigux/validate-phase1-closure.py` validator cue; only reopen if a fresh reread shows new direct-anchor drift or committed shared replay drift.
- If a same-lane follow-up stays inside shared validation instead of helper-local drift, the smallest honest parity-gate step is to teach `scripts/zigux/validate-phase1.py` to exact-check the four `PHASE1_BITMAP_DIRECT_OWNER`, `PHASE1_FIND_BIT_DIRECT_OWNER`, `PHASE1_RBTREE_DIRECT_OWNER`, and `PHASE1_STRING_DIRECT_OWNER` lines in this note before widening into any helper-local replay change.
- If those surfaces still agree on current `master`, leave the helper parked and do not widen to a second helper family in the same lane.

## Footer

This note is lane-local coordination only. It does not reopen the closed Phase 1 helper tranche or imply wider product scope.
