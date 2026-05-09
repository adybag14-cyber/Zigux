# Phase 7 Helper Lane Sequencing

This note keeps the parked Phase 7 helper bundle split into one shared review packet and four helper-owned packets so future follow-up work does not overlap unnecessarily.

## Shared Phase 7 packet

Use the shared Phase 7 lane only when the change is about shared reviewability rather than one helper's behavior.

Shared review surfaces on current `master`:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `samples/zigux/README.md`
- `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`
- `scripts/zigux/validate-phase7.py`
- `scripts/zigux/check-phase7-make-wrapper.py`
- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
- `scripts/zigux/check-phase7-build-wiring.py`
- `zigux/tests/phase7_build.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

Shared-lane work should stay limited to:
- docs-root, scripts-root, tests-root, or samples-root truthfulness updates
- make-wrapper or selftest-alignment wording and checker upkeep
- build-wiring, bundled replay, or no-sample boundary corrections
- other anti-overlap wording that keeps the parked helper bundle readable as one unit

## Helper-owned packets

### `string_helpers`

Helper-owned packet:
- `Documentation/zigux/phase7-string-helpers-slice.md`
- `lib/string_helpers.zig`
- `zigux/tests/phase7_string_helpers.zig`
- `zigux/tests/phase7_string_helpers_survey.zig`
- `zigux/tests/phase7_string_helpers_manifest.json`
- `zigux/tests/phase7_string_helpers_sample_boundary.zig`

Reopen this helper only for a concrete `string_helpers` parity, ownership, or boundary gap inside that packet.

### `cmdline`

Helper-owned packet:
- `Documentation/zigux/phase7-cmdline-slice.md`
- `lib/cmdline.zig`
- `zigux/tests/phase7_cmdline.zig`
- `zigux/tests/phase7_cmdline_survey.zig`
- `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`

Current evidence says a future `cmdline` reopen should stay limited to the likely oversized-integer wrap follow-up in `getOption()` or `getOptions()` plus its directly coupled tests and slice wording.

### `argv_split`

Helper-owned packet:
- `Documentation/zigux/phase7-argv-split-slice.md`
- `lib/argv_split.zig`
- `zigux/tests/phase7_argv_split.zig`
- `zigux/tests/phase7_argv_split_survey.zig`
- `zigux/tests/phase7_argv_split_manifest.json`
- `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
- `scripts/zigux/check-phase7-argv-split-packet.py`

Current evidence says this packet is parked after the dedicated caller-buffer immutability proof. Reopen it only for another direct `argv_split.c` parity, ownership, or pointer-discipline gap.

### `rbtree`

Helper-owned packet:
- `Documentation/zigux/phase7-rbtree-slice.md`
- `lib/rbtree.zig`
- `zigux/tests/phase7_rbtree.zig`
- `zigux/tests/phase7_rbtree_survey.zig`
- `zigux/tests/phase7_rbtree_manifest.json`
- `zigux/tests/fixtures/phase7_rbtree.json`
- `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
- `scripts/zigux/check-phase7-rbtree-parity.py`

Current evidence says this packet is parked after focused helper-local and dedicated parity replays. Reopen it only for a fresh `lib/rbtree.c` parity gap or a directly coupled packet drift.

## Anti-overlap rules

- Do not reopen the shared Phase 7 lane just because one helper needs a local fix.
- Do not treat `scripts/zigux/check-phase7-build-wiring.py` as a helper-owned surface; it is the shared parked bundle gate.
- Do not use a `cmdline`, `argv_split`, or `rbtree` follow-up to widen into `string_helpers`, or vice versa.
- If a follow-up touches only one helper and its directly coupled slice, tests, fixtures, manifest, or dedicated checker, keep that work inside the helper-owned packet.
- If the follow-up only corrects how Phase 7 surfaces are described across docs, shared checkers, make routes, or the no-sample boundary, keep it in the shared packet.

## Current parked state

The current bounded Phase 7 decision is to keep the helper bundle parked unless one of two things happens:
- a future run proves a concrete helper-local parity or ownership gap inside one helper-owned packet
- a future run finds a shared wording or build-wiring drift that affects how the parked helper bundle is reviewed as one unit
