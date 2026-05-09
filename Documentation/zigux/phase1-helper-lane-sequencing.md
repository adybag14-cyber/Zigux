# Phase 1 Helper Lane Sequencing

This note turns the current Phase 1 helper evidence into one bounded anti-overlap map for helper lanes only.

## Status

- `PHASE1_STATUS=parked`
- `PHASE1_SLICE=helper-lane-sequencing`
- lane: `P1-Y10`
- scope: keep the current Phase 1 helper ownership map aligned with the live direct-anchor follow-up packet on `master`
- product boundary:
  - `Documentation/zigux/phase1-helper-lane-sequencing.md`

## Why this note exists

The current Phase 1 manifest and closure packet already keep one hard split explicit:

- shared-replay parked helpers stay limited to `tools/lib/argv_split.zig`, `tools/lib/cmdline.zig`, `tools/lib/ctype.zig`, `tools/lib/hweight.zig`, `tools/lib/list_sort.zig`, `tools/lib/slab.zig`, `tools/lib/str_error_r.zig`, `tools/lib/vsprintf.zig`, and `tools/lib/zalloc.zig`
- direct helper-local follow-up anchors stay limited to `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig`

That split is still correct on current `master`, but the older helper-lane names that used to describe the direct-anchor packet are no longer the live ownership map. Nearby scheduled runs should follow the current owners below instead of reviving superseded helper lanes.

## Shared packet versus direct-anchor packet

Shared Phase 1 replay surfaces stay here:

- `Documentation/zigux/phase1-closure.md`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/build.zig`
- `zigux/Makefile`
- `make -C zigux phase1-validate`
- `make -C zigux phase1-test`
- `make -C zigux phase1-bench`
- `make -C zigux phase1`

Those shared routes prove the bounded host-tools packet still replays together. They do not erase per-helper ownership for manifest, validator, closure, or helper-local review-anchor follow-up.

## Current direct-anchor owner map

`P1-L04` owns bitmap manifest-anchor truthfulness for `tools/lib/bitmap.zig`:

- `zigux/tests/fixtures/phase1_helper_manifest.json`
- bitmap-only review anchors such as the empty-bitmap buffer-preservation, size-alias rounding, and Linux-style alias markers

`P1-Y02` owns bitmap closure parking and next-safe-step evidence:

- bitmap-only closure notes derived from `tools/lib/bitmap.zig`
- direct-anchor follow-up classification checks for the bitmap packet

This lane should stay note-only unless bitmap-local drift reappears.

`P1-L11` owns `find_bit` validator and perf-gate truthfulness:

- `scripts/zigux/validate-phase1.py`
- any shipped `find_bit` replay markers that the Phase 1 validator or perf-oriented packet must recognize without reopening helper-local closure wording

`P1-X04` owns `find_bit` helper-local closure, manifest, and ownership follow-through:

- `Documentation/zigux/phase1-closure.md`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- the directly coupled `find_bit` section of `scripts/zigux/validate-phase1-closure.py` when closure ownership and helper-local review markers move together

This is the current owner for the tail-clamp review packet and the helper-local inclusive-boundary and tail-word skip ownership wording.

`P1-X07` owns the live rbtree review-packet validator follow-through:

- `scripts/zigux/validate-phase1.py`
- `scripts/zigux/validate-phase1-closure.py`
- the directly coupled rbtree review packet when validator recognition must stay aligned with the already-landed manifest and closure wording

This is the current owner for duplicate-search and cached-root validator truthfulness on `master`.

`P1-X05` owns the current string direct-anchor recognition sync:

- the string section of `zigux/tests/fixtures/phase1_helper_manifest.json`
- the directly coupled string section of `scripts/zigux/validate-phase1-closure.py`
- already-landed helper-local `memchrInv` zero-value review anchors and other string direct-anchor inventory that still needs validator recognition

`P1-Y10` owns only this sequencing note:

- `Documentation/zigux/phase1-helper-lane-sequencing.md`
- bounded helper-lane anti-overlap corrections when the current owner map drifts from live `master`

## Superseded overlap guard

The saved `P1-Y12` rbtree backlog handoff is no longer the live owner for current rbtree validator work. Current `master` already uses `P1-X07` as the active rbtree direct-anchor validator packet. Treat `P1-Y12` as historical backlog context only unless a future run is doing memory-side backlog cleanup rather than fresh rbtree validator follow-through.

## Anti-overlap rules

- Do not batch the nine shared-replay parked helpers with the four direct-anchor helpers in one follow-up lane.
- If a run changes only bitmap manifest anchors, it belongs to `P1-L04`.
- If a run only records bitmap closure evidence or a park-or-reopen decision, it belongs to `P1-Y02`.
- If a run changes only `find_bit` validator or perf-gate recognition in `scripts/zigux/validate-phase1.py`, it belongs to `P1-L11`.
- If a run changes `find_bit` closure wording, helper-local ownership wording, or the directly coupled `validate-phase1-closure.py` marker packet, it belongs to `P1-X04`.
- If a run changes rbtree validator recognition for already-landed duplicate-search or cached-root anchors, it belongs to `P1-X07`, not `P1-Y12`.
- If a run changes string direct-anchor inventory or string closure-validator recognition for already-landed helper-local anchors, it belongs to `P1-X05`.
- If a run only refreshes helper-lane ownership boundaries, it belongs to `P1-Y10` and should not reopen helper logic, shared replay fixtures, or unrelated Phase 1 validators.

## Next bounded step

Keep this sequencing note parked unless future repo drift blurs the ownership boundary between the current bitmap, find_bit, rbtree, and string helper packets again. Any deeper helper, fixture, replay, manifest, validator, or closure work should return to the owning helper lane instead of expanding this note.
