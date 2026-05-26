# Phase 14 Compile Shard Matrix Evidence

This note records the exact current-master Phase 14 compile-shard coverage verified for lane `P14-L09`.

## Current head

- verified on `2026-05-26`
- current `master` head observed during this lane: `9c4f5255d15055642bb440d32b408ffcc1d20f5e`
- current `master` head subject: `test(scripts/zigux): add Phase 10 review-guide packet guard`

## Exact current coverage

- `PHASE14_COMPILE_SHARD_TOTAL=6`
- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`
- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`
- shared gate: `make -C zigux phase14-validate`
- focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`
- current workflow route: `run: make -C zigux phase14-validate`
- current broader wrapper gap: `phase14-smoke`, `phase14-test`, and `phase14` remain absent from the readable `zigux/Makefile` route layer

## Row Evidence

- `phase14-workqueue-bridge-tests` -> `phase14_workqueue_bridge.zig` -> `full_bundle_only`
- `phase14-workqueue-reviewability-tests` -> `phase14_workqueue_reviewability.zig` -> `full_bundle_only`
- `phase14-skbuff-bridge-tests` -> `phase14_skbuff_bridge.zig` -> `full_bundle_only`
- `phase14-ring-buffer-survey-tests` -> `phase14_ring_buffer_survey.zig` -> `full_bundle_only`
- `phase14-rcu-tree-survey-tests` -> `phase14_rcu_tree_survey.zig` -> `full_bundle_only`
- `phase14-end-to-end-smoke-tests` -> `phase14_end_to_end_smoke_survey.zig` -> `focused_and_full_bundle`

## Evidence Surfaces

- machine-readable matrix: `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- focused build shard wiring: `zigux/tests/phase14_build.zig`
- shared route layer: `zigux/Makefile`
- workflow route layer: `.github/workflows/zigux-bootstrap.yml`
- current matrix survey companion: `Documentation/zigux/phase14-compile-shard-matrix-survey.md`

## Bounded Reading

The current repo state supports a narrow, reviewability-only claim.

The compile matrix is exact and machine-readable, but only one shard is exposed as a focused raw build-file route. The shared route that the readable Makefile and workflow currently expose remains `make -C zigux phase14-validate`. That means the six-row matrix is current evidence for bounded Phase 14 coverage, not a claim that the broader wrapper family has returned.

## Next Same-Lane Step

If current `master` changes again, refresh the smallest evidence or checker surface that drifts away from this exact `6 / 1 / 5` matrix, the focused raw build-file shard, or the single shared `phase14-validate` route before widening any anchor-local work.
