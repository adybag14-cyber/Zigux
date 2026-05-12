# Phase 7 Helper Lane Sequencing

This note keeps the current Phase 7 helper packet reviewable without letting shared control-surface lanes and helper-local lanes claim the same ownership.

## Purpose

Phase 7 stays limited to the roadmap-backed in-kernel leaf-helper tranche and the already-landed shared validation surfaces that belong to that tranche.

- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`
- the shared validator, make-wrapper, build-wiring, docs-root, and no-sample reminder packet that already belongs to those helpers

Do not use this lane to widen into Phase 5 samples, Phase 8 tooling, or broader runtime-loader work.

## Current Lane Map

Current `master` keeps the active Phase 7 helper packet split into six non-overlapping owners.

- shared control-surface packet, lane `P7-Y05`:
  - `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/README.md`
  - `scripts/zigux/validate-phase7.py`
  - `scripts/zigux/check-phase7-make-wrapper.py`
  - `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  - `scripts/zigux/check-phase7-build-wiring.py`
  - `zigux/Makefile`
  - `zigux/tests/phase7_build.zig`
- shared helper-lane owner map, lane `P7-Y06`:
  - `Documentation/zigux/phase7-helper-lane-sequencing.md`
- string-helpers packet, lane `P7-L04`:
  - `Documentation/zigux/phase7-string-helpers-slice.md`
  - `lib/string_helpers.zig`
  - `zigux/tests/phase7_string_helpers.zig`
  - `zigux/tests/phase7_string_helpers_survey.zig`
  - `zigux/tests/phase7_string_helpers_manifest.json`
  - `zigux/tests/phase7_string_helpers_sample_boundary.zig`
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
- rbtree packet, lane `P7-L13`:
  - `Documentation/zigux/phase7-rbtree-slice.md`
  - `lib/rbtree.zig`
  - `zigux/tests/phase7_rbtree.zig`
  - `zigux/tests/phase7_rbtree_survey.zig`
  - `zigux/tests/phase7_rbtree_manifest.json`
  - `zigux/tests/fixtures/phase7_rbtree.json`
  - `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
  - `scripts/zigux/check-phase7-rbtree-parity.py`

- `PHASE7_SHARED_CONTROL_LANE=P7-Y05`
- `PHASE7_HELPER_SEQUENCING_LANE=P7-Y06`
- `PHASE7_STRING_HELPERS_LANE=P7-L04`
- `PHASE7_CMDLINE_LANE=P7-L05`
- `PHASE7_ARGV_SPLIT_LANE=P7-L09`
- `PHASE7_RBTREE_LANE=P7-L13`
- `PHASE7_ANTI_OVERLAP_RULE=P7-Y06 owns only the shared helper-lane owner map; helper-local slices keep their own lane keys and do not reuse the shared sequencing lane.`

## Current Repo Reality

Fresh repo-first inspection shows four different helper states on current `master`.

- `string_helpers` is parked in a blocker posture because `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig` are missing from the live tree even though the survey, manifest, and no-sample boundary packet remain visible.
- `cmdline` is parked as a partial review packet because the slice note, dedicated test, dedicated survey, and manifest remain visible while direct current-path reads still do not prove `lib/cmdline.zig` or `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`.
- `argv_split` is parked as a landed helper-local packet with its helper, survey, manifest, and fixture module still visible.
- `rbtree` is parked as a landed helper-local packet with its helper, survey, manifest, parity packet, and parity checker still visible.

That means the honest shared owner map is not "all helper follow-up stays inside one Phase 7 reminder lane." The helper families have different reopen conditions, and the shared sequencing lane exists only to keep those conditions from overlapping.

This lane is needed because current Phase 7 docs drifted far enough for the cmdline slice to claim the shared sequencing lane key even though cmdline follow-up is helper-local. Correcting that owner-map drift belongs here; restoring or rewriting the cmdline packet itself still belongs to `P7-L05`.

## Anti-Overlap Rules

- Do not use `P7-Y06` for helper code, dedicated tests, fixtures, manifests, or parity packets.
- Do not let helper-local slice notes reuse `P7-Y06`; helper-local notes must keep their own helper lane keys.
- `P7-L04` owns only the bounded string-helpers truthfulness packet until the missing helper-plus-test pair is restored.
- `P7-L05` owns only the cmdline helper packet: restore the helper-plus-fixture pair or rewrite the remaining cmdline-local review packet into an explicit blocked posture.
- `P7-L09` owns only argv-split helper-local parity, fixture, survey, manifest, or reminder drift.
- `P7-L13` owns only rbtree helper-local parity, traversal, manifest, fixture, checker, or reminder drift.
- `P7-Y05` owns only shared validator, make-wrapper, build-route, and shared reminder truthfulness.
- If a helper packet is already parked and truthful on current `master`, leave it parked and do not batch it with another helper family in the same run.

## Next Bounded Step

Start from the slice note or shared reminder surface that drifted.

- If the drift is a helper-local lane key, helper-local next-step claim, or helper-local blocked posture, fix that helper slice only.
- If the drift is the shared owner map itself, fix this note only.
- If the drift is shared validator, make-wrapper, build-route, or docs-root packet truthfulness across more than one helper family, route it to `P7-Y05` instead of this lane.

This note is lane-local coordination only. It does not reopen helper implementation work or broaden Phase 7 scope.