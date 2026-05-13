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
- the bitmap owner map now also includes the already-landed shared closure-validator bitmap review markers recorded in `Documentation/zigux/phase1-closure.md`, and current `master` now exact-requires and self-tests those markers in `scripts/zigux/validate-phase1-closure.py`, so leave that closure-validator packet parked unless a fresh reread shows new direct-anchor drift or committed shared replay drift
- the earlier bitmap validator-summary wording drift is closed on current `master`: `scripts/zigux/validate-phase1.py` already matches the live bitmap `review_packet_summary` in `zigux/tests/fixtures/phase1_helper_manifest.json`, so bitmap follow-through should stay parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift
- the helper-specific direct-owner marker lines in this note are already exact-checked by `scripts/zigux/check-phase1-direct-owner-markers.py`, so reread them only if the note or its dedicated checker changes
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

- `tools/lib/bitmap.zig` owns its helper-local bitmap anchors, the committed bitmap replay keys in `zigux/tests/fixtures/phase1_helpers.json`, and the already-landed shared closure-validator bitmap review markers in `Documentation/zigux/phase1-closure.md` plus `scripts/zigux/validate-phase1-closure.py`. The closure-validator packet is parked again, and the earlier bitmap validator-summary wording drift is closed too: `scripts/zigux/validate-phase1.py` now matches the live bitmap `review_packet_summary` in `zigux/tests/fixtures/phase1_helper_manifest.json`. A nearby bitmap reopen should therefore start only if a fresh reread finds new direct-anchor drift or committed shared replay drift.
- `tools/lib/find_bit.zig` owns its helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, past-`nbits`, underscore-alias, Linux-style alias, and tail-word skip anchors plus the committed tail-clamped `find_bit` replay fields already emitted by `zigux/tests/fixtures/phase1_helpers_c_harness.c` and consumed by `zigux/tests/fixtures/phase1_helpers.json`. Reopen shared replay only if that committed tail-clamped packet drifts.
- `tools/lib/rbtree.zig` keeps iterator and cached-root coverage helper-local until `master` ships exactly one dedicated shared iterator or cached-root leftmost-return fixture key. Do not batch both widenings into one reopen step.
- `tools/lib/string.zig` keeps memparse safety, prefix and suffix boundary, C-string list lookup, counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte `memchrInv()` coverage helper-local, while the committed shared replay still owns the embedded-NUL `replaceChar` parity bytes and the current string fixture keys. Reopen only for drift inside those direct anchors or committed shared fields, not for a generic closure-validator tightening pass.

- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys and the already-landed shared closure-validator bitmap review markers it already owns`
- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, past-nbits, underscore-alias, Linux-style alias, and tail-word skip anchors plus the committed tail-clamped find_bit replay fields already emitted by the shared C harness and consumed by the shared fixture`
- `PHASE1_RBTREE_DIRECT_OWNER=rbtree iterator and cached-root coverage stay helper-local until exactly one dedicated shared iterator or cached-root leftmost-return fixture key lands`
- `PHASE1_STRING_DIRECT_OWNER=string keeps memparse safety, prefix and suffix boundary, C-string list lookup, counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`

These four helper-specific owner markers are now exact-checked by `scripts/zigux/check-phase1-direct-owner-markers.py` on current `master`, so nearby Phase 1 follow-through should leave this owner-map packet parked unless a fresh reread shows direct-anchor drift or the dedicated checker itself drifts.

## Next Bounded Step

Start from `zigux/tests/fixtures/phase1_helper_manifest.json` and pick one helper family only.

- If the helper sits in the shared-replay parked set, reread only its shared replay, fixture, build-route, and review-surface packet and land one drift repair if needed.
- If the helper sits in the direct-anchor set, reread only that helper's direct anchors plus any already-committed shared fixture keys it owns and land one bounded follow-up if needed.
- For `tools/lib/bitmap.zig`, do not replay the older closed exact-marker validator cue; current `master` already exact-requires and self-tests `PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW` and `PHASE1_BITMAP_LINUX_ALIAS_REVIEW`, so leave the bitmap closure-validator packet parked unless a fresh reread shows direct-anchor drift or committed shared replay drift.
- For `tools/lib/bitmap.zig`, the earlier validator-summary wording follow-through is also closed on current `master`: `scripts/zigux/validate-phase1.py` already matches the live bitmap `review_packet_summary` in `zigux/tests/fixtures/phase1_helper_manifest.json`, so leave that validator packet parked unless a fresh reread shows new direct-anchor drift or committed shared replay drift.
- The next smallest same-lane shared-validation step is closed for this owner-map packet: `scripts/zigux/check-phase1-direct-owner-markers.py` exact-checks the four `PHASE1_*_DIRECT_OWNER` lines in this note before any helper-local replay widening.
- Treat the helper-specific next-safe-step markers below as the tie-breaker whenever multiple older saved helper cues still exist in Memory; choose the helper's own next-safe-step marker instead of widening into a neighboring helper family.
- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen the already-closed closure-validator or validator-summary packets by default`
- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, past-nbits, underscore-alias, Linux-style alias, or tail-word skip anchors, or for committed tail-clamped replay drift`
- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens for exactly one next widening only: a dedicated shared iterator fixture key or a dedicated cached-root leftmost-return fixture key, never both in the same run`
- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside memparse, prefix or suffix, C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; do not reopen a generic closure-validator pass`
- If those surfaces still agree on current `master`, leave the helper parked and do not widen to a second helper family in the same lane.

## Footer

This note is lane-local coordination only. It does not reopen the closed Phase 1 helper tranche or imply wider product scope.
