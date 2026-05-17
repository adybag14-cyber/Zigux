# Phase 7 Helper Lane Sequencing

This note keeps the current Phase 7 helper packet reviewable without letting shared control-surface lanes and helper-local lanes claim the same ownership.

## Purpose

Phase 7 stays limited to the roadmap-backed in-kernel leaf-helper tranche and the reminder surfaces that belong to that tranche.

- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`
- the shared validator, tests-root, scripts-root, sample-root, Makefile, and build-route reminders that already belong to those helpers when they are directly readable on current `master`

Do not use this lane to widen into Phase 5 samples, Phase 8 tooling, or broader runtime-loader work.

## Lane Map

The roadmap-backed Phase 7 ownership map still uses six non-overlapping buckets even when the current direct-readback surface is narrower than the full intended packet.

- shared control-surface packet, lane `P7-Y05`:
  - shared reminder surfaces and shared validator-or-build follow-through for `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, `zigux/tests/phase7_build.zig`, `scripts/zigux/validate-phase7.py`, and the Phase 7 make-wrapper note family when those routes are directly readable on current `master`
- shared helper-lane owner map, lane `P7-Y06`:
  - `Documentation/zigux/phase7-helper-lane-sequencing.md`
- shared Phase 7 docs-root backlog note, lane `P7-Y08`:
  - `Documentation/zigux/README.md`
- string-helpers starter packet, lane `P7-L04`:
  - `Documentation/zigux/phase7-string-helpers-slice.md`
  - `lib/string_helpers.zig`
  - `zigux/tests/phase7_string_helpers.zig`
  - `zigux/tests/phase7_string_helpers_survey.zig`
  - `zigux/tests/phase7_string_helpers_manifest.json`
  - `zigux/tests/phase7_string_helpers_sample_boundary.zig`
  - scheduled alias note: recurring scheduled lane `P7-Y01` is the older schedule label for this same string-helpers packet and must be treated as the same owner, not as a second helper lane
- cmdline packet, lane `P7-L05`:
  - `Documentation/zigux/phase7-cmdline-slice.md`
  - `lib/cmdline.zig`
  - `zigux/tests/phase7_cmdline.zig`
  - `zigux/tests/phase7_cmdline_survey.zig`
  - `zigux/tests/phase7_cmdline_manifest.json`
  - `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`
- argv-split packet, lane `P7-L09`:
  - `Documentation/zigux/phase7-argv-split-slice.md`
  - `lib/argv_split.zig`
  - `zigux/tests/phase7_argv_split.zig`
  - `zigux/tests/phase7_argv_split_survey.zig`
  - `zigux/tests/phase7_argv_split_manifest.json`
  - `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
  - `scripts/zigux/check-phase7-argv-split-packet.py`
  - scheduled alias note: recurring scheduled lane `P7-Y07` is the older schedule label for this same argv-split packet and must be treated as the same owner, not as a second helper lane
- rbtree packet, lane `P7-L13`:
  - `Documentation/zigux/phase7-rbtree-slice.md`
  - `lib/rbtree.zig`
  - `zigux/tests/phase7_rbtree.zig`
  - `zigux/tests/phase7_rbtree_survey.zig`
  - `zigux/tests/phase7_rbtree_manifest.json`
  - `zigux/tests/fixtures/phase7_rbtree.json`
  - `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
  - `scripts/zigux/check-phase7-rbtree-parity.py`
  - scheduled alias note: recurring scheduled lane `P7-Y04` is the older schedule label for this same rbtree packet and must be treated as the same owner, not as a second helper lane

- `PHASE7_SHARED_CONTROL_LANE=P7-Y05`
- `PHASE7_HELPER_SEQUENCING_LANE=P7-Y06`
- `PHASE7_SHARED_DOCS_ROOT_LANE=P7-Y08`
- `PHASE7_STRING_HELPERS_LANE=P7-L04`
- `PHASE7_STRING_HELPERS_SCHEDULE_ALIAS=P7-Y01 -> P7-L04`
- `PHASE7_CMDLINE_LANE=P7-L05`
- `PHASE7_ARGV_SPLIT_LANE=P7-L09`
- `PHASE7_ARGV_SPLIT_SCHEDULE_ALIAS=P7-Y07 -> P7-L09`
- `PHASE7_RBTREE_LANE=P7-L13`
- `PHASE7_RBTREE_SCHEDULE_ALIAS=P7-Y04 -> P7-L13`
- `PHASE7_ANTI_OVERLAP_RULE=P7-Y06 owns only the shared helper-lane owner map, P7-Y08 owns only the docs-root tranche summary, and helper-local slices keep their own lane keys without reusing either shared note lane.`

## Current Repo Reality

Fresh repo-first inspection in Slot 007 shows a narrower direct-readback surface than several older Phase 7 reminder notes still describe.

- `string_helpers` remains the only fully direct-readback helper-local packet on current `master`: `Documentation/zigux/phase7-string-helpers-slice.md`, `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_manifest.json`, and `zigux/tests/phase7_string_helpers_sample_boundary.zig` all remain directly readable, so `P7-L04` should stay on starter-packet truthfulness or one deeper helper-local expansion step only.
- `cmdline` is not currently direct-readback safe in this environment. Fresh authenticated contents reads in this slot returned missing for `lib/cmdline.zig`, and the corresponding slice, dedicated test, survey, manifest, and fixture packet should stay parked until a same-lane reread proves they returned on current `master`.
- `argv_split` currently has only a helper foothold confirmed in this slot: `lib/argv_split.zig` is directly readable, but fresh authenticated contents reads still returned missing for `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, and `scripts/zigux/check-phase7-argv-split-packet.py`. That means `P7-L09` should treat the helper file as a partial returned surface rather than claim the broader packet has fully returned.
- `rbtree` currently survives only through the direct anchor `zigux/tests/phase7_rbtree_survey.zig`. Fresh authenticated contents reads in this slot still returned missing for `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, and `scripts/zigux/check-phase7-rbtree-parity.py`, so `P7-L13` should stay anchored to the surviving survey or one newly returned companion only.
- the shared control packet is also only partly recoverable in this slot. `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` remain directly readable, but fresh authenticated contents reads still returned missing for `scripts/zigux/validate-phase7.py` and `zigux/tests/phase7_build.zig`, so `P7-Y05` should treat the shared wrapper stack as parked reminder vocabulary until those files rematerialize.

That means the honest lane state is not "all four helper families are landed and fully direct-readback reviewable." The current live split is one fully readable `string_helpers` packet, one helper-only `argv_split` foothold, one survey-only `rbtree` anchor, one still-missing `cmdline` packet, and the separate shared-control reminder surfaces.

## Anti-Overlap Rules

- Do not use `P7-Y06` for helper code, dedicated tests, fixtures, manifests, parity packets, or docs-root tranche summaries.
- Do not let helper-local slice notes reuse `P7-Y06`; helper-local notes must keep their own helper lane keys.
- Treat scheduled lane `P7-Y01` as the string-helpers alias for `P7-L04`; if a scheduled run starts under `P7-Y01`, keep the work inside the string-helpers packet and record the alias instead of creating a second Phase 7 helper owner.
- Treat scheduled lane `P7-Y07` as the argv-split alias for `P7-L09`; if a scheduled run starts under `P7-Y07`, keep the work inside the currently returned `argv_split` surfaces and do not claim the missing dedicated test, survey, manifest, fixture, or checker packet as direct current-`master` evidence before those files reread.
- Treat scheduled lane `P7-Y04` as the rbtree alias for `P7-L13`; if a scheduled run starts under `P7-Y04`, keep the work inside `zigux/tests/phase7_rbtree_survey.zig` or another newly returned rbtree companion instead of reopening the missing broader packet by implication.
- `P7-Y08` owns only `Documentation/zigux/README.md` truthfulness for the current Phase 7 tranche summary; it does not own helper-local slices, validators, Makefile routes, or `zigux/tests/phase7_build.zig`.
- `P7-L04` owns only string-helpers helper-local parity, survey, sample-boundary, manifest, or same-slice reminder drift; the helper and dedicated replay are fully direct-readback on current `master`, so follow-through here should stay inside that restored starter packet or one deeper helper-local expansion step unless a new repo-reality gap appears.
- `P7-L05` owns only cmdline helper-local parity, survey, manifest, fixture, or same-slice reminder drift; because the current slot could not directly reread even `lib/cmdline.zig`, follow-through here should stay parked until a fresh same-lane reread proves the packet returned.
- `P7-L09` owns only argv-split helper-local parity, fixture, survey, manifest, checker, or reminder drift; because only `lib/argv_split.zig` returned in this slot, keep same-lane work narrowed to the smallest returned companion once another direct surface rematerializes.
- `P7-L13` owns only rbtree helper-local parity, traversal, manifest, fixture, checker, or reminder drift; because the current slot could directly reread only `zigux/tests/phase7_rbtree_survey.zig`, keep same-lane work anchored there or in another freshly returned companion instead of assuming the full packet is back.
- `P7-Y05` owns only shared validator, scripts-root, sample-root, tests-root, make-wrapper, and build-route truthfulness.
- If a helper packet is only partially readable, prefer the smallest reminder-surface or direct-anchor truthfulness fix instead of widening helper behavior.

## Next Bounded Step

Start from the helper-local or shared reminder surface that actually drifted.

- If the drift is a helper-local lane key, helper-local next-step claim, or helper-local blocked posture, fix that helper slice only.
- If the drift is the shared owner map itself, fix this note only.
- If the drift is the docs-root Phase 7 tranche summary, route it to `P7-Y08` and keep the change inside `Documentation/zigux/README.md` only.
- If the drift is the shared tests-root or scripts-root Phase 7 tranche summary, route it to `P7-Y05` and keep the change inside `zigux/tests/README.md` or `scripts/zigux/README.md` only.
- If the drift is a fully readable `string_helpers` helper-local surface, route it to `P7-L04`.
- If the drift is a partially returned `argv_split` or `rbtree` surface, keep the change inside the one directly readable companion that triggered the reread instead of widening into the missing packet.
- If the drift is `cmdline`, wait for a fresh same-lane reread that proves the packet has returned before claiming direct current-`master` evidence.

This note is lane-local coordination only. It does not reopen helper implementation work or broaden Phase 7 scope.
