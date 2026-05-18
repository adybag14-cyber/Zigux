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
  - `samples/zigux/README.md`
  - scheduled alias note: recurring scheduled lane `P7-Y01` is the older schedule label for this same string-helpers packet and must be treated as the same owner, not as a second helper lane
  - packet-label alias note: the surviving string-helpers slice, survey, and manifest surfaces may still use the internal label `helper-local`; treat that label as the same `P7-L04` owner, not as a second string-helpers lane
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
- `PHASE7_STRING_HELPERS_PACKET_LABEL_ALIAS=helper-local -> P7-L04`
- `PHASE7_CMDLINE_LANE=P7-L05`
- `PHASE7_ARGV_SPLIT_LANE=P7-L09`
- `PHASE7_ARGV_SPLIT_SCHEDULE_ALIAS=P7-Y07 -> P7-L09`
- `PHASE7_RBTREE_LANE=P7-L13`
- `PHASE7_RBTREE_SCHEDULE_ALIAS=P7-Y04 -> P7-L13`
- `PHASE7_ANTI_OVERLAP_RULE=P7-Y06 owns only the shared helper-lane owner map, P7-Y08 owns only the docs-root tranche summary, and helper-local slices keep their own helper lane keys without reusing either shared note lane.`

## Current Repo Reality

Fresh repo-first inspection in Slot 067 shows a narrower direct-readback surface than several older Phase 7 reminder notes still describe.

- `string_helpers` remains the only fully direct-readback helper-local packet on current `master`: `Documentation/zigux/phase7-string-helpers-slice.md`, `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_manifest.json`, and `zigux/tests/phase7_string_helpers_sample_boundary.zig` all remain directly readable, so `P7-L04` should stay on starter-packet truthfulness or one deeper helper-local expansion step only. The surviving packet-local `helper-local` label is still the internal alias for this same `P7-L04` owner.
- `cmdline` now survives through `lib/cmdline.zig` plus `zigux/tests/phase7_cmdline_survey.zig`. Fresh authenticated contents reads in this slot did return that helper-plus-survey foothold, but the corresponding slice, dedicated test, manifest, and fixture packet still returned missing on current `master`. That means `P7-L05` should keep same-lane follow-through limited to the returned helper plus survey foothold or to reminder truthfulness that keeps the missing companion packet explicit instead of presenting the broader cmdline packet as fully returned.
- `argv_split` currently survives through `lib/argv_split.zig` plus the helper-local anchors `zigux/tests/phase7_argv_split_survey.zig` and `zigux/tests/phase7_argv_split_manifest.json`. Fresh authenticated contents reads in this slot still returned missing for `zigux/tests/phase7_argv_split.zig`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, and `scripts/zigux/check-phase7-argv-split-packet.py`. That means `P7-L09` should treat those three returned surfaces as the current same-lane anchor rather than claim the broader dedicated test, fixture, checker, or shared build packet has fully returned.
- `rbtree` currently survives through the direct anchors `zigux/tests/phase7_rbtree_survey.zig` and `zigux/tests/phase7_rbtree_manifest.json`. Fresh authenticated contents reads in this slot still returned missing for `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, and `scripts/zigux/check-phase7-rbtree-parity.py`, so `P7-L13` should keep same-lane work anchored to those two surviving files or another freshly returned companion instead of implying the broader packet is back.
- the shared control packet is also only partly recoverable in this slot. `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` remain directly readable, but fresh authenticated contents reads still returned missing for `scripts/zigux/validate-phase7.py` and `zigux/tests/phase7_build.zig`, so `P7-Y05` should treat the shared wrapper stack as parked reminder vocabulary until those files rematerialize.

That means the honest lane state is not "all four helper families are landed and fully direct-readback reviewable." The current live split is one fully readable `string_helpers` packet, one helper-plus-survey `cmdline` foothold, one helper-plus-survey-manifest `argv_split` anchor, one survey-plus-manifest `rbtree` anchor, and the separate shared-control reminder surfaces. Cross-helper truthfulness should keep the landed string-helpers packet explicit instead of repeating the older blocked-by-missing-string-helpers story inside the rbtree lane.

## Anti-Overlap Rules

- Do not use `P7-Y06` for helper code, dedicated tests, fixtures, manifests, parity packets, or docs-root tranche summaries.
- Do not let helper-local slice notes reuse `P7-Y06`; helper-local notes must keep their own helper lane keys.
- Treat scheduled lane `P7-Y01` as the string-helpers alias for `P7-L04`; if a scheduled run starts under `P7-Y01`, keep the work inside the string-helpers packet and record the alias instead of creating a second Phase 7 helper owner.
- Treat the surviving packet-local label `helper-local` as the string-helpers alias for `P7-L04`; if a live slice, survey, or manifest surface uses that label, keep the work inside the same string-helpers packet and do not mint a second helper owner from it.
- Treat scheduled lane `P7-Y07` as the argv-split alias for `P7-L09`; if a scheduled run starts under `P7-Y07`, keep the work inside the currently returned `argv_split` helper, survey, and manifest surfaces and do not claim the missing dedicated test, fixture, checker, or shared build routes as direct current-`master` evidence before those paths reread.
- Treat scheduled lane `P7-Y04` as the rbtree alias for `P7-L13`; if a scheduled run starts under `P7-Y04`, keep the work inside `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, or another freshly returned rbtree companion instead of reopening the missing broader packet by implication.
- `P7-Y08` owns only `Documentation/zigux/README.md` truthfulness for the current Phase 7 tranche summary; it does not own helper-local slices, validators, Makefile routes, or `zigux/tests/phase7_build.zig`.
- `P7-L04` owns only string-helpers helper-local parity, survey, sample-boundary, manifest, or same-slice reminder drift; the helper and dedicated replay are fully direct-readback on current `master`, so follow-through here should stay inside that restored starter packet or one deeper helper-local expansion step unless a new repo-reality gap appears.
- `P7-L05` owns only cmdline helper-local parity, survey, manifest, fixture, or same-slice reminder drift; because the current slot could directly reread `lib/cmdline.zig` plus `zigux/tests/phase7_cmdline_survey.zig` but not the corresponding slice, dedicated test, manifest, or fixture packet, keep same-lane work limited to that returned helper-plus-survey foothold or to reminder truthfulness that keeps those missing companions explicit until a fresh reread proves more of the packet returned.
- `P7-L09` owns only argv-split helper-local parity, survey, manifest, fixture, checker, or reminder drift; because the current slot could directly reread `lib/argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, and `zigux/tests/phase7_argv_split_manifest.json`, keep same-lane work inside those returned surfaces until a fresh reread proves the dedicated external test, fixture, checker, or shared build routes returned.
- `P7-L13` owns only rbtree helper-local parity, traversal, manifest, fixture, checker, or reminder drift; because the current slot could directly reread only `zigux/tests/phase7_rbtree_survey.zig` and `zigux/tests/phase7_rbtree_manifest.json`, keep same-lane work anchored there or in another freshly returned companion instead of assuming the full packet is back.
- `P7-Y05` owns only shared validator, scripts-root, sample-root, tests-root, make-wrapper, and build-route truthfulness.
- If a helper packet is only partially readable, prefer the smallest reminder-surface or direct-anchor truthfulness fix instead of widening helper behavior.

## Next Bounded Step

Start from the helper-local or shared reminder surface that actually drifted.

- If the drift is a helper-local lane key, helper-local next-step claim, or helper-local blocked posture, fix that helper slice only.
- If the drift is the shared owner map itself, fix this note only.
- If the drift is the docs-root Phase 7 tranche summary, route it to `P7-Y08` and keep the change inside `Documentation/zigux/README.md` only.
- If the drift is the shared tests-root or scripts-root Phase 7 tranche summary, route it to `P7-Y05` and keep the change inside `zigux/tests/README.md` or `scripts/zigux/README.md` only.
- If the drift is a fully readable `string_helpers` helper-local surface, route it to `P7-L04`.
- If the drift is a partially returned `argv_split` surface, keep the change inside `lib/argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, or `zigux/tests/phase7_argv_split_manifest.json` until a fresh reread proves the dedicated external test, fixture, checker, or shared build routes returned.
- If the drift is a partially returned `rbtree` surface, keep the change inside the surviving survey-or-manifest anchor instead of implying helper, fixture, checker, or build-route recovery before a fresh same-lane reread proves it.
- If the drift is `cmdline`, first confirm whether the helper-plus-survey foothold in `lib/cmdline.zig` and `zigux/tests/phase7_cmdline_survey.zig` has changed; otherwise keep same-lane claims limited to those returned surfaces and the still-missing companion packet until a fresh reread proves the slice, dedicated test, manifest, or fixture surfaces returned.

This note is lane-local coordination only. It does not reopen helper implementation work or broaden Phase 7 scope.