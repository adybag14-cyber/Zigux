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
- anchor packets in the current smoke bundle:
  - workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-L01`, surveyed commit `007f00d0c6b6b430bfbb2110555544cc5faefe8b`, ready-next `phase14-workqueue-drain-cancel-followup`, blocked `phase14-workqueue-live-execution-blocker`
  - skbuff: `zigux/tests/phase14_skbuff_bridge_manifest.json`, lane `P14-L11`, surveyed commit `f05e02445443e7743c3675a6f8ca4f70f6e736fb`, ready-next `phase14-skbuff-segs-prev-tail-publication-followup`, blocked `phase14-skbuff-live-ownership-blocker`
  - ring buffer: `zigux/tests/phase14_ring_buffer_manifest.json`, lane `P14-L06`, surveyed commit `946d5c73fdb763ba860a20879b05da54e1896e8c`, ready-next `phase14-ring-buffer-reader-page-consume-followup`, blocked `phase14-ring-buffer-zig-port-blocker`
  - RCU tree: `zigux/tests/phase14_rcu_tree_manifest.json`, lane `P14-L14`, surveyed commit `d839457a2f2dbdc7b53711401741b5e88541c818`, blocked `phase14-rcu-tree-bridge-blocker`

## Shared smoke findings

- `zigux/tests/phase14_build.zig` is the shared Phase 14 replay entrypoint and now includes the dedicated smoke survey alongside the four anchor-local packets.
- `zigux/Makefile` keeps the convenience replay on the same entrypoint through `make -C zigux phase14`.
- `.github/workflows/zigux-bootstrap.yml` already runs that same Phase 14 build command, so the smoke packet is naturally covered by the existing workflow once it stays wired into `phase14_build.zig`.
- `Documentation/zigux/freeze-map.md` still names the four Phase 14 anchors, which keeps the smoke packet grounded in the roadmap's study-only and freeze posture rather than implying a bridge-first expansion.
- `Documentation/zigux/review-checklist.md` now carries a dedicated prompt for the shared Phase 14 smoke packet so later edits have to keep the four anchor-local manifests, survey notes, and shared replay contract aligned.

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

2. run the convenience target
- `make -C zigux phase14`

## Next bounded step

Leave this shared smoke lane closed unless one of the four anchor-local Phase 14 manifests, survey notes, or the shared replay wiring drifts. If it does, refresh this packet instead of widening into new deep-core or bridge implementation work.
