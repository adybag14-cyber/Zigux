# Phase 1 Helper Lane Sequencing

This note turns the current Phase 1 helper evidence into one bounded anti-overlap map for helper lanes only.

## Status

- `PHASE1_STATUS=parked`
- `PHASE1_SLICE=helper-lane-sequencing`
- lane: `P1-Y10`
- scope: use the current bitmap, find_bit, rbtree, and string helper packet to say which Phase 1 helper lane owns which already-landed evidence and which next bounded step still belongs to that lane
- product boundary:
  - `Documentation/zigux/phase1-helper-lane-sequencing.md`

## Why this note exists

The live repo already has several distinct Phase 1 helper follow-up packets inside the closed host-tools tranche:

- bitmap shared-fixture work around `tools/lib/bitmap.zig`
- bitmap in-tree replay alignment around `zigux/tests/phase1_helpers.zig`
- find_bit closure truthfulness notes around `tools/lib/find_bit.zig`
- rbtree manifest and closure-validator alignment around `tools/lib/rbtree.zig`
- string review-surface alignment and direct helper semantics work around `tools/lib/string.zig`

Those packets now share the same closure note, helper manifest, shared Phase 1 replay route, and Linux-style `make -C zigux phase1*` commands. That shared packet is useful, but it also makes it easier for nearby scheduled runs to borrow each other's helper scope or reopen the wrong surface.

This note keeps the closed Phase 1 helper tranche honest by separating shared replay routes from per-lane ownership.

## Shared packet versus lane ownership

Shared Phase 1 replay surface:

- `Documentation/zigux/phase1-closure.md`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/build.zig`
- `zigux/Makefile`
- `make -C zigux phase1-validate`
- `make -C zigux phase1-test`
- `make -C zigux phase1-bench`
- `make -C zigux phase1`

These shared routes prove that the current bounded host-tools packet still replays together. They do not change which lane owns a helper semantics fix, a fixture-only parity packet, a helper-local review note, or a manifest and validator alignment step.

## Lane map

`P1-X01` bitmap shared-fixture lane owns the shared parity packet for `tools/lib/bitmap.zig`:

- `zigux/tests/fixtures/phase1_helpers.json`
- `zigux/tests/fixtures/phase1_helpers_c_harness.c`
- the committed `bitmap_scnprintf()` truncation, terminator-only, and zero-length fixture keys

This lane may cite `zigux/tests/phase1_helpers.zig` as downstream replay evidence, but it does not own in-tree replay-only alignment when the committed fixture packet is already correct.

`P1-L06` bitmap replay-alignment lane owns the in-tree Zig replay follow-through for that same helper family:

- `zigux/tests/phase1_helpers.zig`
- the direct bitmap parity assertions that consume the committed shared fixture packet

This lane may reuse the existing bitmap fixture packet, but it should not reopen bitmap fixture growth, helper-local bitmap semantics, or unrelated Phase 1 helper packets unless the shared replay truly cannot stay honest without a tightly coupled follow-up.

`P1-Y04` find_bit closure-truthfulness lane owns the helper-local versus shared-packet boundary for `tools/lib/find_bit.zig`:

- `Documentation/zigux/phase1-closure.md`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- the explicit audit-only treatment of `inclusive_boundary_*` and `past_nbits_*` fixture fields until `zigux/tests/phase1_helpers.zig` consumes them directly
- the direct helper-local ownership note for zero-window behavior

This lane may cite the shared parity replay, but it does not own new helper logic, unrelated fixture growth, or other helper-family closure wording.

`P1-X08` rbtree manifest and validator-alignment lane owns the bounded review-schema truthfulness for `tools/lib/rbtree.zig`:

- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `scripts/zigux/validate-phase1-closure.py`
- the current rbtree review-anchor schema that keeps helper-test anchors, the shared replay anchor, and the parity fixture keys aligned with what the closure validator actually checks

This lane may talk about duplicate-search and cached-root helper-local anchors when the manifest or closure packet needs them, but it does not own rbtree helper logic, shared replay expansion, or other helper-family manifest drift.

`P1-L16` string review-surface alignment lane owns the helper-local string manifest and closure wording for `tools/lib/string.zig`:

- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `Documentation/zigux/phase1-closure.md`
- the string prefix and suffix review anchors
- the string memparse review summaries

This lane may cite the direct helper tests and the shared string replay, but it does not own closure-validator schema follow-through or same-file C-string semantics repairs once a concrete helper behavior bug is isolated.

`P1-Y09` string closure-validator governance lane owns validator recognition and schema follow-through for the current `tools/lib/string.zig` review packet:

- `scripts/zigux/validate-phase1-closure.py`
- the string section of `zigux/tests/fixtures/phase1_helper_manifest.json` only when a validator-recognized review-anchor or parity-key packet changes
- the current string validator schema for prefix/suffix review metadata, memparse review summaries, and the shared `replaceChar()` C-string parity keys

This lane may cite the closure note and manifest-side wording, but it does not own helper-local string semantics repairs or broader closure-wording-only refreshes when the validator schema itself is unchanged.

`P1-L17` string helper-semantics lane owns direct bounded behavior fixes in `tools/lib/string.zig`:

- `tools/lib/string.zig`
- the directly coupled helper-local string tests that prove C-string boundary behavior such as embedded-NUL stop rules

This lane may refresh an already-coupled direct test when a semantics fix lands, but it should not widen into the broader string manifest, validator schema, or closure packet unless that metadata truly drifts after the helper fix.

## Anti-overlap rules

- If a Phase 1 run changes `zigux/tests/fixtures/phase1_helpers.json` or `zigux/tests/fixtures/phase1_helpers_c_harness.c` for bitmap parity keys, that work belongs to `P1-X01`.
- If a Phase 1 run changes only the bitmap section of `zigux/tests/phase1_helpers.zig` so the live Zig replay matches already-committed fixture behavior, that work belongs to `P1-L06`.
- If a Phase 1 run changes `Documentation/zigux/phase1-closure.md` or `zigux/tests/fixtures/phase1_helper_manifest.json` to keep `find_bit` helper-local ownership versus audit-only shared fields honest, that work belongs to `P1-Y04`.
- If a Phase 1 run changes the rbtree section of `zigux/tests/fixtures/phase1_helper_manifest.json` or the matching closure-validator schema in `scripts/zigux/validate-phase1-closure.py`, that work belongs to `P1-X08`.
- If a Phase 1 run changes string review-anchor naming or string review-summary wording in `zigux/tests/fixtures/phase1_helper_manifest.json` or `Documentation/zigux/phase1-closure.md`, that work belongs to `P1-L16`.
- If a Phase 1 run changes the string section of `scripts/zigux/validate-phase1-closure.py` to recognize already-landed string review anchors or parity keys from `zigux/tests/fixtures/phase1_helper_manifest.json`, that work belongs to `P1-Y09`.
- If a Phase 1 run changes `tools/lib/string.zig` to repair a bounded C-string behavior gap and updates only the directly coupled helper-local proof, that work belongs to `P1-L17`.
- Shared Phase 1 build or make replay drift should reopen only the smallest directly coupled helper packet unless the break truly spans multiple helper families at once.

## Next bounded step

Keep this sequencing note parked unless future repo drift blurs the ownership boundary between the Phase 1 bitmap, find_bit, rbtree, and string helper packets again. Any deeper helper, fixture, replay, manifest, validator, or closure work should return to the owning helper lane instead of expanding this note.
