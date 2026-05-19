# Phase 7 Helper Lane Sequencing

This note keeps the current Phase 7 helper packet reviewable without letting shared control-surface lanes and helper-local lanes claim the same ownership.

## Lane Map

- argv-split packet, lane `P7-L09`:
  - `Documentation/zigux/phase7-argv-split-slice.md`
  - `lib/argv_split.zig`
  - `zigux/tests/phase7_argv_split.zig`
  - `zigux/tests/phase7_argv_split_survey.zig`
  - `zigux/tests/phase7_argv_split_manifest.json`
  - `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
  - `scripts/zigux/check-phase7-argv-split-packet.py`
  - scheduled alias note: recurring scheduled lane `P7-Y07` is the older schedule label for this same argv-split packet and must be treated as the same owner, not as a second helper lane

- cmdline packet, lane `P7-L10`:
  - `Documentation/zigux/phase7-cmdline-slice.md`
  - `lib/cmdline.zig`
  - `zigux/tests/phase7_cmdline.zig`
  - `zigux/tests/phase7_cmdline_survey.zig`
  - `zigux/tests/phase7_cmdline_manifest.json`
  - `scripts/zigux/check-phase7-cmdline-packet.py`
  - scheduled alias note: recurring scheduled lane `kernel-leaf-libraries` may advance into this cmdline packet once the string-helpers and argv-split helper-local packets are already landed on current `master`

- rbtree packet, lane `P7-L13`:
  - `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`
  - `Documentation/zigux/phase7-rbtree-slice.md`
  - `lib/rbtree.zig`
  - `zigux/tests/phase7_rbtree.zig`
  - `zigux/tests/phase7_rbtree_survey.zig`
  - `zigux/tests/phase7_rbtree_manifest.json`
  - `zigux/tests/fixtures/phase7_rbtree.json`
  - `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
  - `scripts/zigux/check-phase7-rbtree-parity.py`
  - `zigux/tests/phase7_build.zig`
  - `scripts/zigux/validate-phase7.py`
  - scheduled alias note: recurring scheduled lane `kernel-leaf-libraries` may advance into this rbtree packet only after same-lane rereads keep the already-landed string-helpers, argv-split, and cmdline packets explicit on current `master`

## Current Repo Reality

- `argv_split` currently survives through `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, and `scripts/zigux/check-phase7-argv-split-packet.py`. Fresh helper-local reread for this slot confirmed the dedicated fixture vectors have now returned on current `master`, so `P7-L09` should treat the slice-helper-test-fixture-survey-manifest-checker packet as the current same-lane packet instead of carrying the fixture as a missing follow-on.

- `cmdline` currently survives through `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, and `scripts/zigux/check-phase7-cmdline-packet.py`. Fresh helper-local reread for this slot confirmed the dedicated cmdline slice, companion replay, survey, manifest, and checker now directly materialize on current `master`, so `P7-L10` should treat that helper-local packet as the current same-lane packet instead of widening into shared validator or Makefile follow-through.

- `rbtree` currently survives through `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`, `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `scripts/zigux/check-phase7-rbtree-parity.py`, `zigux/tests/phase7_build.zig`, and `scripts/zigux/validate-phase7.py`. Fresh same-lane reread for this slot confirmed the direct-anchor note and returned manifest now keep the helper, dedicated test, survey, fixture pair, parity checker, shared build file, and shared validator explicit on current `master`, so `P7-L13` should treat that restored helper-test-fixture-checker-build-validator packet as the current same-lane packet while still keeping dedicated `phase7-*` make-wrapper and workflow steps outside the returned proof.

## Anti-Overlap Rules

- Treat scheduled lane `P7-Y07` as the argv-split alias for `P7-L09`; if a scheduled run starts under `P7-Y07`, keep the work inside the currently returned `argv_split` slice, helper, dedicated test, dedicated fixture, survey, manifest, and checker surfaces.
- `P7-L09` owns only argv-split helper-local parity, survey, manifest, fixture, checker, or reminder drift; because the current slot could directly reread `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, and `scripts/zigux/check-phase7-argv-split-packet.py`, keep same-lane work inside those returned surfaces.
- `P7-L10` owns only cmdline helper-local parity, survey, manifest, checker, or reminder drift; because the current slot could directly reread `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, and `scripts/zigux/check-phase7-cmdline-packet.py`, keep same-lane work inside those returned surfaces.
- `P7-L13` owns only rbtree helper-local parity, survey, manifest, fixture, parity-checker, direct-anchor-note, shared-build reminder, or shared-validator reminder drift; because the current slot could directly reread `Documentation/zigux/phase7-rbtree-direct-anchor-note.md` and `zigux/tests/phase7_rbtree_manifest.json` while those same surfaces keep `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `scripts/zigux/check-phase7-rbtree-parity.py`, `zigux/tests/phase7_build.zig`, and `scripts/zigux/validate-phase7.py` explicit as the returned packet, keep same-lane work inside that restored packet and keep missing dedicated `phase7-*` make-wrapper and workflow steps framed as separate shared-control gaps.
- Route shared validator, Makefile, workflow, docs-root, tests-root, or sample-root Phase 7 drift to the separate shared-control lanes instead of reassigning it to any helper-local packet.

## Next Bounded Step

- If the drift is a partially returned `argv_split` surface, keep the change inside `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, or `scripts/zigux/check-phase7-argv-split-packet.py` while the helper-local packet stays the lane owner.
- If the drift is a partially returned `cmdline` surface, keep the change inside `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, or `scripts/zigux/check-phase7-cmdline-packet.py` while the helper-local packet stays the lane owner.
- If the drift is a partially returned `rbtree` surface, keep the change inside `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`, `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `scripts/zigux/check-phase7-rbtree-parity.py`, `zigux/tests/phase7_build.zig`, or `scripts/zigux/validate-phase7.py` while the restored helper-local-plus-shared-build packet stays the lane owner.
