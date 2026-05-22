# Phase 14 Compile Shard Matrix Evidence

This note records exact bounded evidence for the current Phase 14 compile-shard matrix on `master`.

## Status

- `PHASE14_LANE_KEY=P14-L09`
- `PHASE14_EVIDENCE_DATE=2026-05-22`
- `PHASE14_EVIDENCE_KIND=compile_shard_matrix`
- `PHASE14_MANIFEST_PATH=zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `PHASE14_BUILD_PATH=zigux/tests/phase14_build.zig`
- `PHASE14_MAKEFILE_PATH=zigux/Makefile`
- `PHASE14_COMPILE_SHARD_COUNT=6`
- `PHASE14_FULL_BUNDLE_ONLY_COUNT=5`
- `PHASE14_FOCUSED_AND_FULL_BUNDLE_COUNT=1`
- `PHASE14_SHARED_SMOKE_COMMAND_COUNT=1`
- `PHASE14_SMOKE_SHARD_COMMAND_COUNT=0`

## Exact matrix

- `phase14-workqueue-bridge-tests` -> `phase14_workqueue_bridge.zig` -> `full_bundle_only`
- `phase14-workqueue-reviewability-tests` -> `phase14_workqueue_reviewability.zig` -> `full_bundle_only`
- `phase14-skbuff-bridge-tests` -> `phase14_skbuff_bridge.zig` -> `full_bundle_only`
- `phase14-ring-buffer-survey-tests` -> `phase14_ring_buffer_survey.zig` -> `full_bundle_only`
- `phase14-rcu-tree-survey-tests` -> `phase14_rcu_tree_survey.zig` -> `full_bundle_only`
- `phase14-end-to-end-smoke-tests` -> `phase14_end_to_end_smoke_survey.zig` -> `focused_and_full_bundle`

## Current evidence

- `zigux/tests/phase14_end_to_end_smoke_manifest.json` is directly readable through the contents path and keeps `make -C zigux phase14-validate` as the only shared smoke command while `smoke_shard_commands` stays empty.
- public raw readback on `2026-05-22` recovered `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, and `zigux/tests/phase14_rcu_tree_survey.zig` even though the same files still returned contents-path `404` in this lane's exact read mode.
- `zigux/tests/phase14_build.zig` carries six `b.addTest` shard entries, wires `phase14-smoke` to the focused `phase14-end-to-end-smoke-tests` shard only, and wires the build-file `test` step to all six shards.
- `zigux/Makefile` still narrows the shared rerun route to `phase14-validate`; it does not materialize `phase14-smoke`, `phase14-test`, or `phase14`, so the focused smoke shard remains build-file-local evidence rather than a returned Makefile wrapper.
- the current manifest and build file therefore agree on shard count and labels, but they also preserve the narrower route split: one focused smoke shard exists in `phase14_build.zig` while the shared route surface still exposes only `make -C zigux phase14-validate`.

## Bounded conclusion

- the current Phase 14 compile-shard matrix is present and internally coherent at six rows
- five rows remain `full_bundle_only`
- one row, `phase14-end-to-end-smoke-tests`, remains the only `focused_and_full_bundle` shard
- the next same-lane follow-through should stay on reminder and evidence truthfulness unless `zigux/Makefile` grows a returned wrapper for the focused smoke shard
