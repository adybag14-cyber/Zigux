# Phase 14 End-to-End Smoke Survey

This document records the shared Phase 14 smoke lane that verifies the current bounded-internals evidence bundle as it exists on `master`.

## Status

- `PHASE14_STATUS=active`
- `PHASE14_SLICE=end-to-end-smoke-verification`
- `PHASE14_SMOKE_VALIDATOR=present`
- `PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py`
- `PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate`
- `PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all`
- `PHASE14_COMBINED_ENTRYPOINT=make -C zigux phase14`
- `PHASE14_ANCHOR_PACKET_COUNT=4`
- `PHASE14_COMPILE_ARTIFACT_COUNT=5`
- `PHASE14_FOCUSED_SHARD_COUNT=1`
- `PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=4`
- `PHASE14_STAY_IN_C_BOUNDARY=explicit`
- `PHASE14_STATUS_CHANGE_CLAIM=no`
- survey provenance captured against verified `master` head `1b6cbbcac6e0144ec6ca0a1e954b38f5de748c95`
- shared smoke boundary:
  - `scripts/zigux/validate-phase14.py`
  - `scripts/zigux/README.md`
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

This lane stays narrow on purpose. It does not add a new bridge. It verifies that the current shared replay covers the four anchor-local packets, that the convenience target and workflow still exercise the same shared entrypoint, and that the checklist plus freeze map still describe the same stay-in-C posture. It also records the exact current coverage boundary: only the shared smoke survey has a dedicated shard today, while the four anchor-local artifacts still replay only through the broader `test` bundle.

## Exact evidence captured

- verified `master` head: `1b6cbbcac6e0144ec6ca0a1e954b38f5de748c95`
- shared smoke manifest surveyed commit: `1b6cbbcac6e0144ec6ca0a1e954b38f5de748c95`
- validator-backed smoke commands:
  - `make -C zigux phase14-validate`
  - `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
  - `make -C zigux phase14`
- focused smoke-shard commands:
  - `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
  - `make -C zigux phase14-smoke`
- compile coverage matrix:
  - `phase14-workqueue-bridge-tests`: root `phase14_workqueue_bridge.zig`, import `workqueue_bridge` from `../../kernel/workqueue_bridge.zig`, coverage `full_bundle_only` through `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
  - `phase14-skbuff-bridge-tests`: root `phase14_skbuff_bridge.zig`, import `skbuff_bridge` from `../../net/core/skbuff_bridge.zig`, coverage `full_bundle_only` through `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
  - `phase14-ring-buffer-survey-tests`: root `phase14_ring_buffer_survey.zig`, coverage `full_bundle_only` through `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
  - `phase14-rcu-tree-survey-tests`: root `phase14_rcu_tree_survey.zig`, coverage `full_bundle_only` through `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
  - `phase14-end-to-end-smoke-tests`: root `phase14_end_to_end_smoke_survey.zig`, coverage `focused_and_full_bundle` through dedicated shard `phase14-smoke` plus the shared `zig build test --build-file zigux/tests/phase14_build.zig --summary all` replay
- anchor packets in the current smoke bundle:
  - workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-L01`, surveyed commit `1b346dbd77659625fedfdc2a45f5016e391043f8`, ready-next `phase14-workqueue-drain-cancel-followup`, blocked `phase14-workqueue-live-execution-blocker`
  - skbuff: `zigux/tests/phase14_skbuff_bridge_manifest.json`, lane `P14-L11`, surveyed commit `f65e3d897847bf205198e5c47a41782085620579`, ready-next `phase14-skbuff-validate-xmit-republish-followup`, blocked `phase14-skbuff-live-ownership-blocker`
  - ring buffer: `zigux/tests/phase14_ring_buffer_manifest.json`, lane `P14-L06`, surveyed commit `d78223d3f1a386521769795b1cff384d83cb6a3a`, blocked `phase14-ring-buffer-zig-port-blocker`
  - RCU tree: `zigux/tests/phase14_rcu_tree_manifest.json`, lane `P14-L16`, surveyed commit `4e45e5a392cca82429228d42d89c480fd413042b`, blocked `phase14-rcu-tree-bridge-blocker`

## Shared smoke findings

- `zigux/tests/phase14_build.zig` is the shared Phase 14 replay entrypoint and now includes the dedicated smoke survey alongside the four anchor-local packets.
- `scripts/zigux/validate-phase14.py` and `scripts/zigux/README.md` keep the fast shared-smoke contract explicit, so the note, manifest, make targets, workflow path, and smoke-shard entrypoint are checked before the slower replay claims stay current.
- `zigux/tests/phase14_build.zig` now exposes exactly one dedicated `phase14-smoke` shard for the shared smoke survey, while the four anchor-local artifacts still replay only through the heavier `test` bundle.
- `zigux/Makefile` now exposes `make -C zigux phase14-validate` before the full `make -C zigux phase14` replay and also keeps `make -C zigux phase14-smoke` available as the focused shared smoke shard.
- `.github/workflows/zigux-bootstrap.yml` now runs the validator-backed shared smoke packet, the focused smoke shard, and the full Phase 14 build command, so the shared packet gets both a fast contract check and the existing end-to-end replay.
- `Documentation/zigux/freeze-map.md` still names the four Phase 14 anchors, which keeps the smoke packet grounded in the roadmap's study-only and freeze posture rather than implying a bridge-first expansion.
- `Documentation/zigux/review-checklist.md` now carries a dedicated prompt for the shared Phase 14 smoke packet so later edits have to keep the four anchor-local manifests, survey notes, and shared replay contract aligned.
- `zigux/tests/phase14_end_to_end_smoke_survey.zig` now treats the shared note's quoted per-anchor surveyed commits as machine-checked evidence, so future anchor-manifest refreshes cannot silently leave the shared smoke note behind.
- `zigux/tests/phase14_end_to_end_smoke_manifest.json` now also records which compile artifacts are `full_bundle_only` versus `focused_and_full_bundle`, so later build-file churn cannot silently overstate the number of dedicated Phase 14 shards.

## Productization evidence

- named owner: `Core-Adjacent Pod`
- status bucket: `study_only`
- validation gate: `zig build test --build-file zigux/tests/phase14_build.zig --summary all && make -C zigux phase14`
- rollback owner: `Repo Tooling Pod`
- ZAR-to-product transfer rationale: absorb ZAR runtime research as product discipline only by keeping exported evidence packets, machine-checked surveyed commits, and explicit blocker posture, without importing ZAR runtime-core behavior into Zigux.

## Non-goals

This shared smoke slice does not claim:

- live workqueue execution, draining, or cancellation parity
- skbuff lifetime, destructor, checksum, or segmentation ownership
- `kernel/trace/ring_buffer.zig`
- `kernel/rcu/tree_bridge.zig`
- any Phase 14 status change beyond verifying and recording the current evidence bundle

## Gates

1. run the shared Phase 14 build
- `make -C zigux phase14-validate`
- `zig build test --build-file zigux/tests/phase14_build.zig --summary all`

2. run the focused Phase 14 smoke shard
- `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
- `make -C zigux phase14-smoke`

3. run the convenience targets
- `make -C zigux phase14`
- `make -C zigux phase14-smoke`

## Next bounded step

Leave this shared smoke lane closed unless one of the four anchor-local Phase 14 manifests, survey notes, or the shared replay wiring drifts. If it does, refresh this packet instead of widening into new deep-core or bridge implementation work.
