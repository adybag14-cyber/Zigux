# Phase 7 Helper Lane Sequencing

This note keeps the current Phase 7 helper packet reviewable without letting shared control-surface lanes and helper-local lanes claim the same ownership.

## Lane Map

- shared control-surface packet, lane `P7-Y05`:
  - `Documentation/zigux/phase7-helper-lane-sequencing.md`
  - `Documentation/zigux/phase7-string-helpers-slice.md`
  - `Documentation/zigux/phase7-shared-control-review-checkpoint.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/check-phase7-build-wiring.py`
  - `scripts/zigux/check-phase7-shared-control-gap.py`
  - `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
  - parked shared reminder paths: `scripts/zigux/validate-phase7.py` and `zigux/tests/phase7_build.zig`

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
  - `samples/zigux/README.md`
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
  - scheduled alias note: recurring scheduled lane `kernel-leaf-libraries` may advance into this rbtree packet only after same-lane rereads keep the already-landed string-helpers, argv-split, and cmdline packets explicit on current `master`

## Current Repo Reality

- the shared control packet is only partly recoverable in this slot. `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` remain directly readable on current `master`, but `scripts/zigux/validate-phase7.py` and `zigux/tests/phase7_build.zig` still sit in parked reminder territory, so `P7-Y05` should keep the shared wrapper stack framed as reminder vocabulary instead of route-present proof.

- the readable non-owner shared-control files in this slot are still `.github/workflows/zigux-bootstrap.yml` and `zigux/Makefile`, and fresh reread now shows the workflow carries the current `check-phase7-shared-control-gap.py` and `check-phase7-make-wrapper-selftest-alignment.py` self-test hooks while the readable `zigux/Makefile` still omits `phase7-validate`, `phase7-test`, `phase7`, and the helper-local Phase 7 wrapper routes. Keep shared-control truthfulness anchored to those returned checker hooks and absent-wrapper boundaries instead of claiming the older build routes have returned.

- `argv_split` currently survives through `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, and `scripts/zigux/check-phase7-argv-split-packet.py`. Fresh helper-local reread for this slot confirmed the dedicated fixture vectors have now returned on current `master`, so `P7-L09` should treat the slice-helper-test-fixture-survey-manifest-checker packet as the current same-lane packet instead of carrying the fixture as a missing follow-on.

- `cmdline` currently survives through `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `scripts/zigux/check-phase7-cmdline-packet.py`, and the no-standalone-cmdline-sample boundary in `samples/zigux/README.md`. Fresh helper-local reread for this slot confirmed the dedicated cmdline slice, companion replay, survey, manifest, checker, and no-sample boundary now directly materialize on current `master`, so `P7-L10` should treat that helper-local packet as the current same-lane packet instead of widening into shared validator or Makefile follow-through.

- `rbtree` currently survives through `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`, `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, and `scripts/zigux/check-phase7-rbtree-parity.py`. Fresh same-lane reread for this slot confirmed the direct-anchor note and returned manifest now keep the helper, dedicated test, survey, fixture pair, and parity checker explicit on current `master`, while the shared `scripts/zigux/validate-phase7.py` and `zigux/tests/phase7_build.zig` paths remain parked reminder vocabulary in the shared-control packet rather than direct returned evidence.

## Anti-Overlap Rules

- Treat scheduled lane `P7-Y07` as the argv-split alias for `P7-L09`; if a scheduled run starts under `P7-Y07`, keep the work inside the currently returned `argv_split` slice, helper, dedicated test, dedicated fixture, survey, manifest, and checker surfaces.
- `P7-Y05` owns only shared validator, scripts-root, sample-root, tests-root, make-wrapper, and build-route truthfulness.
- `P7-L09` owns only argv-split helper-local parity, survey, manifest, fixture, checker, or reminder drift; because the current slot could directly reread `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, and `scripts/zigux/check-phase7-argv-split-packet.py`, keep same-lane work inside those returned surfaces.
- `P7-L10` owns only cmdline helper-local parity, survey, manifest, checker, or reminder drift; because the current slot could directly reread `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `scripts/zigux/check-phase7-cmdline-packet.py`, and the cmdline no-sample boundary in `samples/zigux/README.md`, keep same-lane work inside those returned surfaces.
- `P7-L13` owns only rbtree helper-local parity, survey, manifest, fixture, parity-checker, or direct-anchor-note drift; because the current slot could directly reread `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`, `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, and `scripts/zigux/check-phase7-rbtree-parity.py`, keep same-lane work inside that returned helper-local packet and keep the shared `phase7-*` make-wrapper, shared-build, and validator reminders framed as separate shared-control reminder vocabulary.
- Route shared validator, Makefile, workflow, docs-root, tests-root, or sample-root Phase 7 drift to the separate shared-control lanes instead of reassigning it to any helper-local packet.

## Next Bounded Step

- If the drift is a partially returned `argv_split` surface, keep the change inside `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, or `scripts/zigux/check-phase7-argv-split-packet.py` while the helper-local packet stays the lane owner.
- If the drift is a partially returned `cmdline` surface, keep the change inside `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `scripts/zigux/check-phase7-cmdline-packet.py`, or `samples/zigux/README.md` while the helper-local packet stays the lane owner.
- If the drift is a partially returned `rbtree` surface, keep the change inside `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`, `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, or `scripts/zigux/check-phase7-rbtree-parity.py` while the restored helper-local packet stays the lane owner.
- If the drift is the shared docs-root Phase 7 checkpoint, route it to `P7-Y05` and keep the change inside `Documentation/zigux/phase7-shared-control-review-checkpoint.md` only.
- If the drift is the shared tests-root or scripts-root Phase 7 tranche summary, route it to `P7-Y05` and keep the change inside `zigux/tests/README.md` or `scripts/zigux/README.md` only.
