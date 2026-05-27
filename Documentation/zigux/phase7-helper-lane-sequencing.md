# Phase 7 Helper Lane Sequencing

This note keeps the current Phase 7 helper packet reviewable without letting shared control-surface lanes and helper-local lanes claim the same ownership.

## Lane Map

- shared control-surface packet, lane `P7-Y05`:
  - `Documentation/zigux/phase7-helper-lane-sequencing.md`
  - `Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md`
  - `Documentation/zigux/phase7-shared-control-review-checkpoint.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/check-phase7-build-wiring.py`
  - `scripts/zigux/check-phase7-shared-control-gap.py`
  - `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  - `scripts/zigux/validate-phase7.py`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
  - readable non-owner shared build evidence: `zigux/tests/phase7_build.zig`
  - parked shared reminder path: `scripts/zigux/check-phase7-make-wrapper.py`

- string_helpers packet, helper-local lane family:
  - `Documentation/zigux/phase7-string-helpers-slice.md`
  - `lib/string_helpers.zig`
  - `zigux/tests/phase7_string_helpers.zig`
  - `zigux/tests/phase7_string_helpers_survey.zig`
  - `zigux/tests/phase7_string_helpers_manifest.json`
  - `zigux/tests/phase7_string_helpers_sample_boundary.zig`
  - `scripts/zigux/check-phase7-string-helpers-packet.py`
  - scheduled lane-family note: keep helper-local `string_helpers` slice, helper, dedicated replay, survey, manifest, sample-boundary, and checker drift out of `P7-Y05`; only route shared validator, Makefile, workflow, docs-root, tests-root, sample-root, or shared-build reminders back to the shared-control packet
  - scheduled anti-overlap note: recurring helper-local lane `P7-Y01` is same-family `string_helpers` follow-through, not a separate Phase 7 helper packet; keep it narrowed to `lib/string_helpers.zig` and its directly coupled slice, replay, survey, manifest, sample-boundary, or checker surfaces while shared validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminders stay with `P7-Y05`
  - scheduled historical-lane note: older helper-local readbacks for this family stay narrowed to the string_helpers slice, helper, dedicated replay, survey, manifest, sample-boundary, or checker surfaces while shared validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminders stay with `P7-Y05`

- argv-split packet, lane `P7-L09`:
  - `Documentation/zigux/phase7-argv-split-slice.md`
  - `lib/argv_split.zig`
  - `zigux/tests/phase7_argv_split.zig`
  - `zigux/tests/phase7_argv_split_survey.zig`
  - `zigux/tests/phase7_argv_split_manifest.json`
  - `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
  - `scripts/zigux/check-phase7-argv-split-packet.py`
  - scheduled alias note: recurring scheduled lane `P7-Y07` is the older schedule label for this same argv-split packet and must be treated as the same owner, not as a second helper lane

- cmdline packet, lane `P7-L08`:
  - `Documentation/zigux/phase7-cmdline-slice.md`
  - `lib/cmdline.zig`
  - `zigux/tests/phase7_cmdline.zig`
  - `zigux/tests/phase7_cmdline_survey.zig`
  - `zigux/tests/phase7_cmdline_manifest.json`
  - `zigux/tests/phase7_cmdline_survey_build.zig`
  - `scripts/zigux/check-phase7-cmdline-packet.py`
  - `samples/zigux/README.md`
  - scheduled alias note: recurring scheduled lane `kernel-leaf-libraries` may advance into this cmdline packet once the string-helpers and argv-split helper-local packets are already landed on current `master`
  - scheduled maintenance note: recurring scheduled lane `P7-L10` is same-family cmdline cleanup follow-through; keep cmdline-local review-noise, survey-build-checker-manifest drift, and the no-sample boundary narrowed to the cmdline-focused section of this sequencing note, `Documentation/zigux/phase7-cmdline-slice.md`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/phase7_cmdline_survey_build.zig`, `scripts/zigux/check-phase7-cmdline-packet.py`, or `samples/zigux/README.md` instead of treating that lane as a second helper owner or shared-control drift

- rbtree helper-local packet, lane `P7-L13`:
  - `Documentation/zigux/phase7-rbtree-slice.md`
  - `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`
  - `scripts/zigux/check-phase7-rbtree-parity.py`
  - `lib/rbtree.zig`
  - `zigux/tests/phase7_rbtree.zig`
  - `zigux/tests/phase7_rbtree_survey.zig`
  - `zigux/tests/phase7_rbtree_manifest.json`
  - `zigux/tests/fixtures/phase7_rbtree.json`
  - `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
  - readable legacy runtime-family companion: `tools/lib/rbtree.zig`
  - scheduled alias note: recurring scheduled lane `kernel-leaf-libraries` may advance inside this returned rbtree helper-local packet while `tools/lib/rbtree.zig` stays readable as legacy non-owner companion evidence and shared validator, Makefile, workflow, and build-route reminders stay with `P7-Y05`

## Current Repo Reality

- the shared control packet now directly rereads `zigux/tests/phase7_build.zig` on current `master`, but that returned build shard still lives here only as readable non-owner evidence. `zigux/Makefile` still omits `phase7-test`, `phase7`, and the helper-local wrapper routes, so `P7-Y05` should keep the broader shared build-and-test surface framed as reminder vocabulary instead of route-present proof.

- the readable non-owner shared-control files in this slot are still `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase7_build.zig`, and fresh reread now shows the workflow carries the current `check-phase7-shared-control-gap.py` and `check-phase7-make-wrapper-selftest-alignment.py` self-test hooks while the readable `zigux/Makefile` still exposes only the narrow `phase7-validate` foothold and still omits `phase7-test`, `phase7`, and the helper-local Phase 7 wrapper routes. Keep shared-control truthfulness anchored to that returned validator foothold, those returned checker hooks, the readable non-owner build shard, and the still-absent broader wrapper boundaries instead of claiming the older workflow-backed test routes have returned.

- `string_helpers` currently survives through `Documentation/zigux/phase7-string-helpers-slice.md`, `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_manifest.json`, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, and `scripts/zigux/check-phase7-string-helpers-packet.py`. Fresh helper-local reread for this slot confirmed those helper-local surfaces now directly materialize on current `master`, so keep `Documentation/zigux/phase7-string-helpers-slice.md` with the string_helpers helper-local lane family instead of the shared-control packet while shared validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminders stay routed to `P7-Y05`. Current lane evidence also keeps `P7-Y01` inside this same helper-local family, while `P7-L04` remains the shared-control workspace-bootstrap follow-through for validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminder drift rather than a second helper-local string_helpers packet.

- `argv_split` currently survives through `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, and `scripts/zigux/check-phase7-argv-split-packet.py`. Fresh helper-local reread for this slot confirmed the dedicated fixture vectors have now returned on current `master`, so `P7-L09` should treat the slice-helper-test-fixture-survey-manifest-checker packet as the current same-lane packet instead of carrying the fixture as a missing follow-on.

- `cmdline` currently survives through `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/phase7_cmdline_survey_build.zig`, `scripts/zigux/check-phase7-cmdline-packet.py`, and the no-standalone-cmdline-sample boundary in `samples/zigux/README.md`. Fresh helper-local reread for this slot confirmed the dedicated cmdline slice, companion replay, survey, manifest, checker, and no-sample boundary now directly materialize on current `master`, so `P7-L08` should treat that helper-local packet as the current same-lane packet instead of widening into shared validator or Makefile follow-through. Current lane evidence also keeps `P7-L10` inside that same helper-local cleanup family, so cmdline-local review-noise, survey-build-checker-manifest drift, and no-sample-boundary upkeep should stay inside the returned cmdline packet instead of being rerouted as a second helper owner or shared-control drift.

- `rbtree` now survives through `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`, `scripts/zigux/check-phase7-rbtree-parity.py`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, and `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`. Fresh same-lane reread for this slot confirmed the runtime-root helper plus the dedicated JSON and C-harness parity companions now directly materialize on current `master`, while `tools/lib/rbtree.zig` stays readable as legacy runtime-family companion evidence only. `P7-L13` should therefore keep its same-lane truthfulness packet tied to the returned runtime-root helper, the returned notes, the returned replay, the returned survey, the returned manifest, the returned parity checker, the returned JSON fixture, and the returned C harness while leaving `tools/lib/rbtree.zig` plus the broader shared validator, Makefile, workflow, and build-route reminders framed as non-owner evidence.

## Anti-Overlap Rules

- Treat scheduled lane `P7-Y07` as the argv-split alias for `P7-L09`; if a scheduled run starts under `P7-Y07`, keep the work inside the currently returned `argv_split` slice, helper, dedicated test, dedicated fixture, survey, manifest, and checker surfaces.
- `P7-Y05` owns only shared validator, scripts-root, sample-root, tests-root, make-wrapper, and shared build-route truthfulness.
- The helper-local string_helpers family owns `Documentation/zigux/phase7-string-helpers-slice.md`; do not route string_helpers helper, dedicated replay, survey, manifest, sample-boundary, or checker drift through `P7-Y05` just because the shared-control packet still rereads docs-root, tests-root, sample-root, validator, Makefile, workflow, or shared-build reminder files.
- Treat recurring helper-local lane `P7-Y01` as same-family string_helpers follow-through inside that one helper packet, not as a separate Phase 7 helper lane; keep it narrowed to `lib/string_helpers.zig` ownership or directly coupled helper-local truthfulness while shared validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build drift still route back to `P7-Y05`.
- Treat recurring lane `P7-L04` as the shared-control workspace-bootstrap follow-through; keep it narrowed to `Documentation/zigux/phase7-helper-lane-sequencing.md`, `Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md`, `Documentation/zigux/phase7-shared-control-review-checkpoint.md`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/check-phase7-shared-control-gap.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `samples/zigux/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, or the readable non-owner `zigux/tests/phase7_build.zig` instead of reassigning that lane to helper-local string_helpers ownership.
- `P7-L09` owns only argv-split helper-local parity, survey, manifest, fixture, checker, or reminder drift; because the current slot could directly reread `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, and `scripts/zigux/check-phase7-argv-split-packet.py`, keep same-lane work inside those returned surfaces.
- `P7-L08` owns only cmdline helper-local parity, survey, manifest, checker, or reminder drift; because the current slot could directly reread `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/phase7_cmdline_survey_build.zig`, `scripts/zigux/check-phase7-cmdline-packet.py`, and the cmdline no-sample boundary in `samples/zigux/README.md`, keep same-lane work inside those returned surfaces.
- Treat recurring lane `P7-L10` as same-family cmdline cleanup follow-through, not as a second helper owner; keep it narrowed to the cmdline-focused section of `Documentation/zigux/phase7-helper-lane-sequencing.md`, `Documentation/zigux/phase7-cmdline-slice.md`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/phase7_cmdline_survey_build.zig`, `scripts/zigux/check-phase7-cmdline-packet.py`, or the no-sample boundary in `samples/zigux/README.md` when helper-local review-noise or truthfulness drift reopens.
- `P7-L13` owns only rbtree slice-note, direct-anchor-note, runtime-root helper, dedicated replay, survey, manifest, parity-checker, JSON fixture, C-harness, or missing-wrapper reminder drift; because the current slot could directly reread `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`, `scripts/zigux/check-phase7-rbtree-parity.py`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, and `zigux/tests/fixtures/phase7_rbtree_c_harness.c` while `tools/lib/rbtree.zig` remains readable only as legacy non-owner companion evidence, keep same-lane work inside that returned helper-local packet and keep the legacy companion plus broader shared-control routes framed as non-owner vocabulary.
- Route shared validator, Makefile, workflow, docs-root, tests-root, or sample-root Phase 7 drift to the separate shared-control lanes instead of reassigning it to any helper-local packet.

## Next Bounded Step

- If the drift is a string_helpers helper-local surface, keep the change inside `Documentation/zigux/phase7-string-helpers-slice.md`, `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_manifest.json`, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, or `scripts/zigux/check-phase7-string-helpers-packet.py`; treat recurring helper-local lane `P7-Y01` as same-family follow-through inside that one packet rather than as a separate helper family, and route shared validator, Makefile, workflow, docs-root, tests-root, sample-root, and shared-build reminders back to `P7-Y05`.
- If the drift is a partially returned `argv_split` surface, keep the change inside `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, or `scripts/zigux/check-phase7-argv-split-packet.py` while the helper-local packet stays the lane owner.
- If the drift is a partially returned `cmdline` surface, keep the change inside the cmdline-focused section of `Documentation/zigux/phase7-helper-lane-sequencing.md`, `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/phase7_cmdline_survey_build.zig`, `scripts/zigux/check-phase7-cmdline-packet.py`, or `samples/zigux/README.md` while the helper-local packet stays the lane owner.
- If the drift is the current `rbtree` helper-local packet, keep the change inside `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`, `scripts/zigux/check-phase7-rbtree-parity.py`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, or `zigux/tests/fixtures/phase7_rbtree_c_harness.c` while `tools/lib/rbtree.zig` stays the readable legacy non-owner companion; route broader shared validator, Makefile, workflow, or build-route drift back to `P7-Y05`.
- If the drift is the shared docs-root Phase 7 checkpoint, route it to `P7-Y05` and keep the change inside `Documentation/zigux/phase7-shared-control-review-checkpoint.md` only.
- If the drift is the shared tests-root or scripts-root Phase 7 tranche summary, route it to `P7-Y05` and keep the change inside `zigux/tests/README.md` or `scripts/zigux/README.md` only.
