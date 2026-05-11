# Phase 1 Host-Helper Lane Sequencing

This note keeps the closed Phase 1 host-helper packet reviewable without reopening helper semantics or batching unrelated follow-up work back together.

## Scope

Phase 1 stays limited to the roadmap-backed host-side helper tranche:

- `tools/lib/bitmap.zig`
- `tools/lib/find_bit.zig`
- `tools/lib/string.zig`
- `tools/lib/rbtree.zig`
- tightly coupled parity, closure, benchmark, and review-surface gates that already belong to that helper packet

Do not use this lane to widen into runtime helpers, Phase 3 ABI work, sample work, or later driver phases.

## Current Split

The live Phase 1 packet on `master` is already closed as a bounded helper tranche, but it is intentionally split into two follow-up families.

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

## Current Repo Reality

Fresh repo-first inspection shows several older saved Phase 1 reopen cues are already closed on current `master`.

The Phase 1 closure validator already carries the bitmap final-partial-word and Linux-style alias closure markers that older lane memory once described as missing. Future runs should not reopen that already-landed validator sync.

The older saved `scripts/zigux/validate-phase1.py` write-text handoff is already closed on current `master` as well. The built-in Phase 1 validator self-test now uses `Path.write_text()`, so future runs should not replay that typo-only repair or keep treating it as the next same-lane deliverable.

The docs-root Phase 1 summary still names this owner-map note, so the earlier `Documentation/zigux/README.md` truthfulness gap remains closed on current `master`.

The earlier `find_bit` edge bench gap is now closed on current `master` too. `zigux/tests/phase1_bench.zig` now carries the underscore-alias and backward-edge `findLastBit()` replay calls inside `findBitEdgeBench()`, and `zigux/tests/fixtures/phase1_bench_expectations.json` already keeps the widened exact edge checksum at `23340000`.

The earlier shared reminder gap is now fully closed on current `master`. `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` all keep `Documentation/zigux/phase1-host-helper-lane-sequencing.md` inside the shared review packet.

The earlier shared Phase 1 validator packet gap is now closed on current `master` too. `scripts/zigux/validate-phase1.py` now exact-checks both the reviewer-facing `review_checklist_phase1_packet` reminder and the broader `tests_root_phase1_packet` marker with this lane note included.

The queued Phase 1 closure-validator expected-manifest drift is already closed on current `master` too. `scripts/zigux/validate-phase1-closure.py` now carries the `tools/lib/find_bit.zig` tail-word inclusive-boundary anchor, its paired contract text, and the widened review-summary wording already present in `zigux/tests/fixtures/phase1_helper_manifest.json`.

Fresh repo-first reread also shows one smaller closure-packet drift still open on current `master`. The direct string helper anchors and `zigux/tests/fixtures/phase1_helper_manifest.json` already keep the signed trailing-rest `memparse()` split explicit, but the compact `PHASE1_STRING_MEMPARSE_REVIEW=` summary in `Documentation/zigux/phase1-closure.md` still shortens that contract, and the paired exact-count marker in `scripts/zigux/validate-phase1-closure.py` still enforces the shorter wording.

That means the older shared-reminder follow-up and the queued closure-validator expected-manifest sync are no longer the next bounded steps. Fresh repo-first inspection closes the earlier tests-root, validator, and closure-validator omissions, and narrows the next honest host-tools follow-up to that newly observed string memparse closure-summary drift instead of replaying any of those already-landed repairs.

Future host-tools follow-up should come only from another freshly observed exact-check drift across the shipped Phase 1 closure, manifest, validator, benchmark, or helper-local anchor surfaces.

## Anti-Overlap Rules

When this lane reopens, stay inside one bounded step only.

- Do not batch shared-replay parked helpers with the direct-anchor helper family.
- Do not reopen the already-landed bitmap closure-marker repair.
- Do not reopen the already-landed `validate-phase1.py` write-text typo repair.
- Do not reopen the already-landed docs-root owner-map sync.
- Do not reopen the already-landed `find_bit` edge bench sync.
- Do not reopen the already-landed portion of the shared closure-note owner-map sync in `Documentation/zigux/phase1-closure.md`.
- Do not reopen the already-landed reviewer-facing owner-map sync in `Documentation/zigux/review-checklist.md`.
- Do not reopen the already-landed tests-root owner-map sync in `zigux/tests/README.md`.
- Do not reopen the already-landed `tests_root_phase1_packet` validator sync in `scripts/zigux/validate-phase1.py`.
- Do not reopen the already-landed shared Phase 1 validator sync for the `find_bit` edge bench packet.
- Do not reopen the already-landed `validate-phase1-closure.py` expected-manifest sync for the `find_bit` tail-word inclusive-boundary packet.
- Do not widen the next slot past the one remaining `PHASE1_STRING_MEMPARSE_REVIEW=` closure-summary sync until that exact closure note and checker wording is aligned with the shipped manifest and direct helper anchors.
- Prefer the smallest same-family reviewability, parity-gate, fixture, benchmark, or build-route repair before changing helper semantics.
- If the exact direct-anchor gap is already closed on `master`, advance only to the next unfinished bounded step inside the same helper family.

## Next Bounded Step

Keep the next host-tools-alpha slot inside the one remaining shared Phase 1 closure-summary drift before reopening any helper-local work.

Start with these already-shipped shared Phase 1 packet surfaces:

- `Documentation/zigux/phase1-closure.md`
- `scripts/zigux/validate-phase1-closure.py`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `tools/lib/string.zig`

The next run should sync the compact `PHASE1_STRING_MEMPARSE_REVIEW=` closure summary and the paired exact-count marker in `scripts/zigux/validate-phase1-closure.py` so they explicitly keep the signed trailing-rest `memparse()` split aligned with the already-shipped direct helper anchors and manifest wording, without reopening any broader Phase 1 reminder packet.

If that exact wording drift is already closed on a future reread, advance only to the next newly observed same-lane checker-local or review-surface mismatch that current `master` still leaves open.

Until a fresh same-lane gap is observed, keep Phase 1 follow-up work on review-surface truthfulness, closure accuracy, fixture drift, benchmark exactness, or other already-shipped parity-gate surfaces rather than reopening helper behavior.

## Footer

This note is lane-local coordination only. It does not reopen the closed Phase 1 helper tranche or imply wider product scope.
