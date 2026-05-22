# Phase 14 Compile Shard Matrix Survey

This note records the current Phase 14 compile-shard coverage against the roadmap-backed core-adjacent study packet.

## Roadmap baseline

Phase 14 stays bounded to these four anchors:

- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- `net/core/skbuff.c`
- `kernel/rcu/tree.c`

The roadmap keeps `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in the study-only bucket, and it keeps `net/core/skbuff.c` plus `kernel/rcu/tree.c` frozen in C initially.

## Current matrix

- `PHASE14_COMPILE_SHARD_TOTAL=6`
- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`
- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`
- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`
- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`
- shared gate: `make -C zigux phase14-validate`
- focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`
- broader wrapper gaps: `phase14-smoke`, `phase14-test`, and `phase14` remain absent from the readable current `zigux/Makefile` body
- machine-readable source: `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- checker: `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
- shared survey shard: `phase14-end-to-end-smoke-tests` (`focused_and_full_bundle`)

## Anchor coverage

- `kernel/workqueue.c` -> lane `P14-L04`
  - `phase14-workqueue-bridge-tests`
  - `phase14-workqueue-reviewability-tests`
  - direct workqueue reviewability evidence is readable again, but the lane stays blocked on `phase14-workqueue-live-execution-blocker`
- `kernel/trace/ring_buffer.c` -> lane `P14-L08`
  - `phase14-ring-buffer-survey-tests`
  - the direct ring-buffer survey companion is readable again, but the lane remains study-only and maintenance-scoped
- `net/core/skbuff.c` -> lane `P14-L11`
  - `phase14-skbuff-bridge-tests`
  - the manifest-backed compile row is present, but the focused Zig replay remains partial through this lane's exact contents path and the anchor stays freeze-in-C initially
- `kernel/rcu/tree.c` -> lane `P14-L16`
  - `phase14-rcu-tree-survey-tests`
  - the manifest-backed compile row is present, but the focused Zig replay remains partial through this lane's exact contents path and the anchor stays freeze-in-C initially

## Product reading

The compile-shard story is no longer an unknown-count placeholder.

Current `master` now carries an exact six-row machine-readable matrix for the shared Phase 14 smoke packet. That improves reviewability, and the packet now records the one focused build-file smoke shard explicitly. The returned release-boundary exact-count checker now also rereads this survey and the shared smoke manifest together, so the six-row `6 / 1 / 5` split has a direct truthfulness guard instead of living only in prose.

That still does not reopen the broader Phase 14 Makefile wrapper family and it does not change the roadmap posture for any deep-core anchor.

The honest same-lane conclusion stays narrow:

- keep the single shared gate explicit through `make -C zigux phase14-validate`
- keep the focused raw build-file shard explicit through `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`
- keep the six compile rows explicit as reviewability evidence only
- keep the returned exact-count checker explicit through `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
- keep workqueue and ring-buffer framed as study-only compile-adjacent footholds
- keep skbuff and RCU framed as manifest-backed compile rows that still do not justify a delivery claim or a freeze-map status change

## Next bounded step

If current repo state drifts again, repair the smallest Phase 14 reminder or checker surface that undercounts this six-row matrix, its single focused build-file shard, or the manifest-backed `6 / 1 / 5` split before widening any anchor-local work.
