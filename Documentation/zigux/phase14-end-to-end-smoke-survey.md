# Phase 14 End-to-End Smoke Survey

This document records the shared Phase 14 smoke lane that verifies the current bounded-internals evidence bundle as it exists on `master`.

## Status

- `PHASE14_STATUS=active`
- `PHASE14_SLICE=end-to-end-smoke-verification`
- survey provenance captured against verified `master` head `8dcddb52137c4cfbb2f81cdc621c2ba11010db1e`
- shared smoke boundary:
  - `zigux/tests/phase14_end_to_end_smoke_manifest.json`
  - `zigux/tests/phase14_end_to_end_smoke_survey.zig`
  - `zigux/tests/phase14_build.zig`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
  - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 14 roadmap treats `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as boundary-study or freeze-in-C anchors. That means Phase 14 needs a small shared smoke packet that proves the repo still carries those four anchors as one reviewable bundle, with exact commands and explicit ready-next versus blocked posture, instead of letting each lane drift in isolation.

This lane stays narrow on purpose. It does not add a new bridge. It verifies that the current shared replay covers the four anchor-local packets, that the convenience target and workflow still exercise the same shared entrypoint, and that the checklist plus freeze map still describe the same stay-in-C posture.

## Exact evidence captured

- verified `master` head: `8dcddb52137c4cfbb2f81cdc621c2ba11010db1e`
- shared replay commands:
  - `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
  - `make -C zigux phase14`
- focused smoke-shard commands:
  - `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
  - `make -C zigux phase14-smoke`
- anchor packets in the current smoke bundle:
  - workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-L01`, surveyed commit `007f00d0c6b6b430bfbb2110555544cc5faefe8b`, ready-next `phase14-workqueue-drain-cancel-followup`, blocked `phase14-workqueue-live-execution-blocker`
  - skbuff: `zigux/tests/phase14_skbuff_bridge_manifest.json`, lane `P14-L11`, surveyed commit `f65e3d897847bf205198e5c47a41782085620579`, ready-next `phase14-skbuff-validate-xmit-list-reset-followup`, blocked `phase14-skbuff-live-ownership-blocker`
  - ring buffer: `zigux/tests/phase14_ring_buffer_manifest.json`, lane `P14-L06`, surveyed commit `99cd3249c4bab05b74227ed7ca3869284e818588`, ready-next `phase14-ring-buffer-read-page-extraction-followup`, blocked `phase14-ring-buffer-zig-port-blocker`
  - RCU tree: `zigux/tests/phase14_rcu_tree_manifest.json`, lane `P14-L14`, surveyed commit `d839457a2f2dbdc7b53711401741b5e88541c818`, blocked `phase14-rcu-tree-bridge-blocker`

## Shared smoke findings

- `zigux/tests/phase14_build.zig` is the shared Phase 14 replay entrypoint and now includes the dedicated smoke survey alongside the four anchor-local packets.
- `zigux/tests/phase14_build.zig` now also exposes a dedicated `phase14-smoke` shard so the shared smoke packet can be replayed without compiling the heavier anchor-local bundle.
- `zigux/Makefile` keeps the full convenience replay on the same entrypoint through `make -C zigux phase14` and now adds `make -C zigux phase14-smoke` for the focused shared smoke shard.
- `.github/workflows/zigux-bootstrap.yml` now runs both the focused smoke shard and the full Phase 14 build command, so the shared packet gets a direct compile shard without weakening the existing end-to-end replay.
- `Documentation/zigux/freeze-map.md` still names the four Phase 14 anchors, which keeps the smoke packet grounded in the roadmap's study-only and freeze posture rather than implying a bridge-first expansion.
- `Documentation/zigux/review-checklist.md` now carries a dedicated prompt for the shared Phase 14 smoke packet so later edits have to keep the four anchor-local manifests, survey notes, and shared replay contract aligned.
- `zigux/tests/phase14_end_to_end_smoke_survey.zig` now treats the shared note's quoted per-anchor surveyed commits as machine-checked evidence, so future anchor-manifest refreshes cannot silently leave the shared smoke note behind.

## Non-goals

This shared smoke slice does not claim:

- live workqueue execution, draining, or cancellation parity
- skbuff lifetime, destructor, checksum, or segmentation ownership
- `kernel/trace/ring_buffer.zig`
- `kernel/rcu/tree_bridge.zig`
- any Phase 14 status change beyond verifying and recording the current evidence bundle

## Gates

1. run the shared Phase 14 build
- `zig build test --build-file zigux/tests/phase14_build.zig --summary all`

2. run the focused Phase 14 smoke shard
- `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`

3. run the convenience targets
- `make -C zigux phase14`
- `make -C zigux phase14-smoke`

## Next bounded step

Leave this shared smoke lane closed unless one of the four anchor-local Phase 14 manifests, survey notes, or the shared replay wiring drifts. If it does, refresh this packet instead of widening into new deep-core or bridge implementation work.
