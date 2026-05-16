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
- the bitmap owner map now also includes the already-landed shared closure-validator bitmap review markers recorded in `Documentation/zigux/phase1-closure.md`, including the fill-tail-clamp and cross-word `bitmap.scnprintf()` markers, so treat that closure packet as parked unless a fresh reread shows note drift or committed shared replay drift
- the earlier bitmap validator-summary wording drift is closed on current `master`: `scripts/zigux/validate-phase1.py` already matches the live bitmap `review_packet_summary` in `zigux/tests/fixtures/phase1_helper_manifest.json`, so bitmap follow-through should stay parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift
- the earlier bitmap closure-validator summary wording drift is also closed on current `master`: `scripts/zigux/validate-phase1-closure.py` already matches the live bitmap `review_packet_summary` in `zigux/tests/fixtures/phase1_helper_manifest.json`, so keep bitmap parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift
- the helper-specific direct-owner marker lines in this note are already exact-checked by `scripts/zigux/check-phase1-direct-owner-markers.py`, so reread them only if the note or its dedicated checker changes
- the dedicated owner-map checker itself is now part of the live Phase 1 closure-maintenance packet beside `Documentation/zigux/phase1-closure.md`, the shared `phase1-validate` route, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, so future reminder surfaces should keep that checker explicit instead of treating the owner-map note as docs-only context
- broader shared reminder surfaces now keep that reviewer-facing route-role split aligned on current `master`: `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md` both say that `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test` replays the bounded checker logic while `python3 scripts/zigux/check-phase1-installer-companion-checks.py` guards the shipped Phase 1 reminder surfaces, so treat `scripts/zigux/check-phase1-installer-companion-checks.py`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md` as a parked shared-reminder packet unless one of those surfaces drifts again
- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS=none`
- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=scripts/zigux/check-phase1-installer-companion-checks.py,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md`
- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md and Documentation/zigux/review-checklist.md now both keep the installer companion split explicit: --self-test replays the bounded checker logic, while the live checker route guards the shipped Phase 1 reminder surfaces without widening the counted docs-root packet line; leave that shared-reminder packet parked unless one of those three surfaces drifts`
- the bootstrap ledger already treats commits 15 through 18 as the bounded Phase 1 closure, closure-gate, workflow-viability, and installer-backed path through `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1-closure.py`, `.github/workflows/zigux-bootstrap.yml`, and `scripts/zigux/install-zig.py`; the later owner-map note plus `scripts/zigux/check-phase1-installer-review-surfaces.py` and `scripts/zigux/check-phase1-installer-companion-checks.py` should still be treated as parked closure-maintenance surfaces rather than as evidence that the helper tranche needs another helper-batch reopen
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

- `tools/lib/bitmap.zig` owns its helper-local bitmap anchors, the committed bitmap replay keys in `zigux/tests/fixtures/phase1_helpers.json`, and the already-landed shared closure-validator bitmap review markers in `Documentation/zigux/phase1-closure.md` plus `scripts/zigux/validate-phase1-closure.py`. The older final-partial-word, Linux-alias, fill-tail-clamp, cross-word `bitmap.scnprintf()`, validator-summary, and closure-validator-summary follow-through cues are closed on current `master`, so a nearby bitmap reopen should stay parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift.
- `tools/lib/find_bit.zig` owns its helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-`nbits`, underscore-alias, Linux-style alias, and tail-word skip anchors plus the committed tail-clamped `find_bit` replay fields already emitted by `zigux/tests/fixtures/phase1_helpers_c_harness.c` and consumed by `zigux/tests/fixtures/phase1_helpers.json`. Reopen shared replay only if that committed tail-clamped packet drifts.
- current `master` also carries the newer direct `test "find or bit returns the next set bit from either bitmap"` proof inside `tools/lib/find_bit.zig`, so notes-only and closure-side rereads should treat the OR-path as part of the existing helper-local `find_bit` anchor family instead of inventing a new shared replay packet for it
- `tools/lib/rbtree.zig` now keeps cached-root coverage helper-local while the committed shared replay owns duplicate-search parity through `matchIterator()` as well as `find()`, `findFirst()`, and `nextMatch()`. The next widening, if any, is the dedicated cached-root leftmost-return fixture key only; do not batch a second widening into the same reopen step.
- `tools/lib/string.zig` keeps `strscpy()` and `strscpyPad()` copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through `sysfsStreq()`, `sysfs_streq()`, `sysfsMatchString()`, and `sysfs_match_string()`, C-string list lookup through `matchString()` and `match_string()`, counted-search `strnchr()`, embedded-NUL trim preservation, and moving-earliest-dirty-byte `memchrInv()` coverage helper-local, while the committed shared replay still owns embedded-NUL `replaceChar` parity bytes and the current string fixture keys. Current `master` already exact-checks the manifest's memparse, matched-prefix and suffix, sysfs, C-string lookup, and counted-search anchors through `scripts/zigux/validate-phase1-closure.py`, so the next same-family string follow-up is no longer another closure-validator tightening pass. Reopen only for drift inside those direct anchors, for helper-local sysfs review-anchor alignment drift between the string review packet and the closure note, or for committed shared-field drift; do not reopen a generic closure-validator pass. The counted-search owner term here also covers the current `strnchrNul()` and `strnchrnul()` match-or-NUL boundary anchor already cataloged in `zigux/tests/fixtures/phase1_helper_manifest.json`, so future string-only rereads should keep that helper-local boundary proof inside the same counted-search packet instead of treating it as an unowned follow-up beside `strnchr()`.
- the still-open string sysfs follow-through, if it reopens, should stay on one string-only shared review-rule packet across `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/check-phase1-string-review-packet.py`, and `scripts/zigux/validate-phase1-closure.py` instead of being split between helper-local string rereads and a generic closure-validator lane

- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys and the already-landed shared closure-validator bitmap review markers it already owns`
- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, underscore-alias, Linux-style alias, and tail-word skip anchors plus the committed tail-clamped find_bit replay fields already emitted by the shared C harness and consumed by the shared fixture`
- `PHASE1_RBTREE_DIRECT_OWNER=rbtree cached-root coverage stays helper-local while the committed shared replay owns duplicate-search parity and matchIterator() through the dedicated iterator fixture key, so the next widening is the cached-root leftmost-return fixture key only`
- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`

These four helper-specific owner markers are now exact-checked by `scripts/zigux/check-phase1-direct-owner-markers.py` on current `master`, so nearby Phase 1 follow-through should leave this owner-map packet parked unless a fresh reread shows direct-anchor drift or the dedicated checker itself drifts.

## Next Bounded Step

Start from `zigux/tests/fixtures/phase1_helper_manifest.json` and pick one helper family only.

- If the helper sits in the shared-replay parked set, reread only its shared replay, fixture, build-route, and review-surface packet and land one drift repair if needed.
- If the helper sits in the direct-anchor set, reread only that helper's direct anchors plus any already-committed shared fixture keys it owns and land one bounded follow-up if needed.
- For `tools/lib/bitmap.zig`, do not replay the older closed exact-marker cue, the already-closed validator-summary cue, or the already-closed closure-validator summary cue; current `master` already exact-requires and self-tests `PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW` and `PHASE1_BITMAP_LINUX_ALIAS_REVIEW`, and both `scripts/zigux/validate-phase1.py` and `scripts/zigux/validate-phase1-closure.py` already match the live bitmap `review_packet_summary`.
- For `tools/lib/bitmap.zig`, the earlier closure-note cross-word `bitmap.scnprintf()` follow-through is also closed on current `master`: `Documentation/zigux/phase1-closure.md` already keeps `PHASE1_BITMAP_SCNPRINTF_CROSS_WORD_REVIEW` explicit, so leave that note parked unless a fresh reread shows new direct-anchor drift or committed shared replay drift.
- Fresh repo-first readback now shows the earlier shared bitmap validation drift is closed rather than pending: `scripts/zigux/validate-phase1-closure.py` already matches the live bitmap `review_packet_summary` in `zigux/tests/fixtures/phase1_helper_manifest.json`, so keep bitmap parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift.
- The next smallest same-lane shared-validation step is closed for this owner-map packet: `scripts/zigux/check-phase1-direct-owner-markers.py` exact-checks the four `PHASE1_*_DIRECT_OWNER` lines in this note before any helper-local replay widening.
- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared reminder packet parked now that Documentation/zigux/review-checklist.md carries the same self-test-versus-live route-role wording as Documentation/zigux/README.md; if a future host-tools-alpha run reopens Phase 1, start from the helper-specific next-safe-step markers below instead of another shared reminder pass`
- Treat the helper-specific next-safe-step markers below as the default tie-breakers whenever multiple older saved helper cues still exist in Memory; for `tools/lib/bitmap.zig`, let the explicit `PHASE1_BITMAP_NEXT_SAFE_STEP` line below reinforce that the older closure-validator and validator-summary cues are already closed on current `master`.
- `zigux/tests/fixtures/phase1_helper_manifest.json` now records helper-local `next_safe_step_note` entries for `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig`; treat those helper-specific manifest notes plus the `PHASE1_*_NEXT_SAFE_STEP` lines below as the authoritative tie-breakers instead of reopening a helper family from older saved cues or shared-validator paths.
- Current `master` already exact-checks the string manifest's memparse, prefix and suffix, sysfs, lookup, and `strnchr()` anchor groups through `scripts/zigux/validate-phase1-closure.py`, so the smallest same-lane string follow-up is no longer another closure-validator tightening pass; leave string parked unless those direct anchors drift, the string review packet and closure note fall out of sync, or committed shared string replay fields drift.
- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen the already-closed closure-validator or validator-summary packets by default`
- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, underscore-alias, Linux-style alias, or tail-word skip anchors, or for committed tail-clamped replay drift; do not reopen older saved validator cues or neighboring helper families`
- the already-landed OR-path proof in `test "find or bit returns the next set bit from either bitmap"` belongs to that same `find_bit` direct-anchor packet, so if it drifts, refresh the existing helper-family notes or closure evidence instead of widening shared replay ownership
- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only for the dedicated cached-root leftmost-return fixture key or for drift inside the already-committed shared iterator replay; do not batch a second widening into the same run`
- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and closure note unless dedicated shared sysfs fixture keys land; do not reopen a generic closure-validator pass`
- If those surfaces still agree on current `master`, leave the helper parked and do not widen to a second helper family in the same lane.

## Footer

This note is lane-local coordination only. It does not reopen the closed Phase 1 helper tranche or imply wider product scope.
