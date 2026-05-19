# Phase 1 Host-Helper Lane Sequencing

This note keeps the closed Phase 1 host-helper packet reviewable without reopening helper semantics or batching unrelated follow-up work back together.

## Scope

Phase 1 stays limited to the roadmap-backed host-side helper tranche and the already-shipped shared validation surfaces that belong to that helper packet.

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
- current authenticated reads still recover `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `scripts/zigux/check-phase1-route-summary-counts.py`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`, so those are the trustworthy reminder surfaces for this lane on current `master`
- current authenticated reads still do not recover `scripts/zigux/validate-phase1.py` on `master`, while `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1-closure.py`, and `zigux/Makefile` are back on current `master`; the returned Makefile now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate`, `phase3`, `phase8-validate`, `phase8-exec-cmd-test`, `phase8-test`, and `phase8`, `phase10-validate`, `phase10-test`, and `phase10` routes, so this lane should use that restored closure-side packet as live owner-map evidence while still treating the older validator-first and Phase 1 make-route names as historical packet members
- the helper-specific direct-owner marker lines in this note are already exact-checked by `scripts/zigux/check-phase1-direct-owner-markers.py`, so reread them only if the note or its dedicated checker changes
- the dedicated owner-map checker itself is now part of the live Phase 1 reminder packet beside this lane note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`, so future reminder surfaces should keep that checker explicit instead of treating the owner-map note as docs-only context
- broader shared reminder surfaces now split cleanly: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` now all keep `scripts/zigux/check-phase1-bench.py` explicit as the shipped bench-side checker while preserving the older installer-backed, validator-first, bench-route, and replay names as historical packet members, so bench wording is no longer the default same-lane follow-through.
- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS=the shared reminder packet now keeps scripts/zigux/check-phase1-bench.py explicit across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md, while the older installer-backed, validator-first, bench-route, and replay names stay historical packet members until they reread cleanly on current master`
- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/check-phase1-route-summary-counts.py`
- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`
- the bootstrap ledger still records commits 15 through 18 as the bounded Phase 1 closure, closure-gate, workflow-viability, and installer-backed path, but current authenticated reads do not recover several of those older closure-side files, so treat that ledger history as historical tranche context rather than as direct current-`master` evidence
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

- `tools/lib/bitmap.zig` owns its helper-local bitmap anchors and the committed bitmap replay keys in `zigux/tests/fixtures/phase1_helpers.json`. The restored `Documentation/zigux/phase1-closure.md` note plus `scripts/zigux/validate-phase1-closure.py` now remain live closure-side companions on current `master`, but nearby bitmap rereads should still stay on the manifest-backed anchors and that restored closure packet rather than widening back into the older missing validator-first or make-route surfaces by default. The live helper-local bitmap packet already keeps caller-window and multiword-tail `xorBits()` clamp proofs review-visible beside the fill-tail, copy-alias, cross-word `scnprintf()`, empty-buffer, and allocator-reset anchors cataloged in the manifest-backed review surface.
- `tools/lib/find_bit.zig` owns its helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, `getValue8()`, and `findLastBit()` byte-clump and backward-scan coverage, underscore-alias and Linux-style alias coverage including the shipped `find_first_andnot_bit()`, `find_next_andnot_bit()`, `_find_first_andnot_bit()`, and `_find_next_andnot_bit()` entry points, and tail-word skip anchors plus the committed tail-clamped `find_bit` replay fields already preserved in `zigux/tests/fixtures/phase1_helpers.json`. Reopen shared replay only if that committed tail-clamped packet drifts.
- current `master` also keeps the helper-local `clump8`, `getValue8()`, and `findLastBit()` byte-clump and backward-scan proofs explicit in both `tools/lib/find_bit.zig` and the manifest's `helper_test_anchors` list, so nearby Phase 1 follow-through should keep those checks inside the same direct `find_bit` packet instead of splitting byte-clump or last-bit drift into a separate shared replay family
- `tools/lib/rbtree.zig` now keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed coverage helper-local while the committed shared replay owns duplicate-search parity through `matchIterator()` as well as `find()`, `findFirst()`, and `nextMatch()`, and current `master` already consumes `cached_leftmost_return_serials` as shared cached-root leftmost-return evidence. The dedicated `low_level_alias_anchor` in `zigux/tests/fixtures/phase1_helper_manifest.json` also keeps the low-level Linux-style alias proof named explicitly inside that same helper-local packet instead of leaving it implied only by the broader helper test list. Until another committed cached-root replay field lands, leave the remaining cached-root anchors helper-local and do not batch a second widening into the same reopen step.
- `tools/lib/string.zig` keeps `strscpy()` and `strscpyPad()` copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through `sysfsStreq()`, `sysfs_streq()`, `sysfsMatchString()`, and `sysfs_match_string()`, C-string list lookup through `matchString()` and `match_string()`, counted-search `strnchr()`, embedded-NUL trim preservation, and moving-earliest-dirty-byte `memchrInv()` coverage helper-local, while the committed shared replay still owns embedded-NUL `replaceChar` parity bytes and the current string fixture keys. Current `master` still exact-checks the manifest's memparse, matched-prefix and suffix, sysfs, C-string lookup, counted-search anchor groups, string review-summary scalars, and helper-specific `next_safe_step_note` through the shipped string review packet, while the older closure-side validator names are not directly readable in this environment; leave string parked unless those direct anchors drift, the helper-local sysfs review-anchor alignment between the string review packet and this lane note drifts, or committed shared-field drift appears.
- The counted-search owner term here also covers the current `strnchrNul()` and `strnchrnul()` match-or-NUL boundary anchor already cataloged in `zigux/tests/fixtures/phase1_helper_manifest.json`, so future string-only rereads should keep that helper-local boundary proof inside the same counted-search packet instead of treating it as an unowned follow-up beside `strnchr()`.
- the still-open string sysfs follow-through, if it reopens, should stay on one string-only shared review-rule packet across `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `scripts/zigux/check-phase1-string-review-packet.py`; the restored `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` companions are now live broader reminder evidence on current `master`, but string should stay parked on the helper-local sysfs review anchors unless those direct string surfaces drift.

- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys it already owns; the restored phase1-closure note and validate-phase1-closure guard are live companions again, while the older validator-first and make-route names stay historical`
- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), and findLastBit() byte-clump and backward-scan coverage, underscore-alias and Linux-style alias coverage including the shipped find_first_andnot_bit(), find_next_andnot_bit(), _find_first_andnot_bit(), and _find_next_andnot_bit() entry points, and tail-word skip anchors plus the committed tail-clamped find_bit replay fields already preserved in zigux/tests/fixtures/phase1_helpers.json`
- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed shared replay already owns duplicate-search parity through find(), findFirst(), nextMatch(), and matchIterator() plus the parked cached_leftmost_return_serials witness`
- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`

These four helper-specific owner markers are now exact-checked by `scripts/zigux/check-phase1-direct-owner-markers.py` on current `master`, so nearby Phase 1 follow-through should leave this owner-map packet parked unless a fresh reread shows direct-anchor drift or the dedicated checker itself drifts.

## Next Bounded Step

Start from `zigux/tests/fixtures/phase1_helper_manifest.json` and pick one helper family only.

- If the helper sits in the shared-replay parked set, reread only its shared replay, fixture, build-route, and review-surface packet and land one drift repair if needed.
- If the helper sits in the direct-anchor set, reread only that helper's direct anchors plus any already-committed shared fixture keys it owns and land one bounded follow-up if needed.
- For `tools/lib/bitmap.zig`, do not replay older validator-first or Phase 1 make-route cue names by default; current authenticated reads now recover `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1-closure.py`, and `zigux/Makefile`, and the returned Makefile now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate`, `phase3`, `phase8-validate`, `phase8-exec-cmd-test`, `phase8-test`, `phase8`, `phase10-validate`, `phase10-test`, and `phase10` routes, but it still omits `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so bitmap follow-through should stay on the live manifest-backed direct anchors plus the restored closure packet unless those broader historical packet members become directly readable again. That direct bitmap packet now explicitly includes the caller-window and multiword-tail `xorBits()` clamp witnesses alongside the other live bitmap-local review anchors.
- The next smallest same-lane shared-validation step is closed for this owner-map packet: `scripts/zigux/check-phase1-direct-owner-markers.py` exact-checks the four `PHASE1_*_DIRECT_OWNER` lines in this note before any helper-local replay widening.
- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording, route-summary checker, and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, scripts/zigux/check-phase1-route-summary-counts.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`
- Treat the helper-specific next-safe-step markers below as the default tie-breakers whenever multiple older saved helper cues still exist in Memory; for `tools/lib/bitmap.zig`, let the explicit `PHASE1_BITMAP_NEXT_SAFE_STEP` line below reinforce that the older closure-side cue names are no longer the default reopen path on current `master`.
- `zigux/tests/fixtures/phase1_helper_manifest.json` now records helper-local `next_safe_step_note` entries for `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig`; treat those helper-specific manifest notes plus the `PHASE1_*_NEXT_SAFE_STEP` lines below as the authoritative tie-breakers instead of reopening a helper family from older saved cues or missing shared-validator paths.`
- The older one-file string summary-sync cue is no longer the honest default next step: current `master` keeps string parked on helper-local sysfs review-anchor alignment across the live string review packet and this lane note, while the older closure-side validator names remain historical packet members until directly readable again.
- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`
- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped replay drift; do not reopen older saved validator cues or neighboring helper families`
- the existing byte-clump and `findLastBit()` proofs belong to that same `find_bit` direct-anchor packet too, so if one of those helper-local anchors drifts, refresh the current helper-family note before widening shared replay ownership
- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`
- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`
- If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default.
- If those surfaces still agree on current `master`, leave the helper parked and do not widen to a second helper family in the same lane.

## Footer

This note is lane-local coordination only. It does not reopen the closed Phase 1 helper tranche or imply wider product scope.
