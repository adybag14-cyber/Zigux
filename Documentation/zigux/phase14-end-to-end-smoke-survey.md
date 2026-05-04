# Phase 14 End-to-End Smoke Survey

This document records the shared Phase 14 smoke lane that verifies the current bounded-internals evidence bundle as it exists on `master`.

## Status

- `PHASE14_STATUS=active`
- `PHASE14_SLICE=end-to-end-smoke-verification`
- `PHASE14_SHARED_LANE=P14-L01`
- `PHASE14_SMOKE_VALIDATOR=present`
- `PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py`
- `PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate`
- `PHASE14_TEST_ENTRYPOINT=make -C zigux phase14-test`
- `PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all`
- `PHASE14_COMBINED_ENTRYPOINT=make -C zigux phase14`
- `PHASE14_ANCHOR_PACKET_COUNT=4`
- `PHASE14_COMPILE_ARTIFACT_COUNT=5`
- `PHASE14_FOCUSED_SHARD_COUNT=1`
- `PHASE14_ANCHOR_LOCAL_STEP_COUNT=0`
- `PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=4`
- `PHASE14_STAY_IN_C_BOUNDARY=explicit`
- `PHASE14_REVIEW_BLOCKER_STATUS=blocked_on_stay_in_c_evidence`
- `PHASE14_STATUS_CHANGE_CLAIM=no`
- `PHASE14_FULL_BUNDLE_DEPENDENCY_COUNT=5`
- `PHASE14_FOCUSED_SHARD_DEPENDENCY_COUNT=1`
- `PHASE14_FOCUSED_SHARD_ONLY_ARTIFACT=phase14-end-to-end-smoke-tests`
- `PHASE14_WORKFLOW_SMOKE_PATH=make-wrapper`
- `PHASE14_BOUNDARY_MAP=shared-anchor-packet-bundle`
- `PHASE14_CONCURRENCY_AUDIT_SCOPE=anchor-local-packets-only`
- `PHASE14_ATTACHED_TOOLCHAIN_FALLBACK=ZIG=<attached-zig-path>`
- survey provenance captured against verified `master` head `672d03034b090ab859f4088396160ea13120e1d6`
- shared smoke boundary:
  - `scripts/zigux/validate-phase14.py`
  - `scripts/zigux/check-phase14-docs-root-smoke-summary.py`
  - `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
  - `scripts/zigux/README.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/phase14-release-boundary-survey.md`
  - `zigux/tests/phase14_end_to_end_smoke_manifest.json`
  - `zigux/tests/phase14_end_to_end_smoke_survey.zig`
  - `zigux/tests/phase14_rcu_tree_survey.zig`
  - `zigux/tests/phase14_build.zig`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
  - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 14 roadmap treats `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as boundary-study or freeze-in-C anchors. That means Phase 14 needs a small shared smoke packet that proves the repo still carries those four anchors as one reviewable bundle, with exact commands and explicit ready-next versus blocked posture, instead of letting each lane drift in isolation.

This lane stays narrow on purpose. It does not add a new bridge. It verifies that the current shared replay covers the four anchor-local packets, that the convenience target and workflow still exercise the same shared entrypoint, and that the checklist plus freeze map still describe the same stay-in-C posture. It also records the exact current coverage boundary: only the shared smoke survey has a dedicated shard today, and all four anchor-local artifacts replay only through the broader `test` bundle.

## Exact evidence captured

- verified `master` head: `672d03034b090ab859f4088396160ea13120e1d6`
- shared smoke manifest lane key: `P14-L01`
- shared smoke manifest surveyed commit: `672d03034b090ab859f4088396160ea13120e1d6`
- validator-backed smoke commands:
  - `make -C zigux phase14-validate`
  - `make -C zigux phase14-test`
  - `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
  - `make -C zigux phase14`
- focused smoke-shard commands:
  - `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
  - `make -C zigux phase14-smoke`
- attached-toolchain fallback commands:
  - `make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`
  - `make -C zigux phase14-smoke ZIG=<attached-zig-path>`
  - `make -C zigux phase14-test ZIG=<attached-zig-path>`
  - `make -C zigux phase14 ZIG=<attached-zig-path>`
- compile coverage matrix:
  - `phase14-workqueue-bridge-tests`: root `phase14_workqueue_bridge.zig`, import `workqueue_bridge` from `../../kernel/workqueue_bridge.zig`, coverage `full_bundle_only` through `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
  - `phase14-skbuff-bridge-tests`: root `phase14_skbuff_bridge.zig`, import `skbuff_bridge` from `../../net/core/skbuff_bridge.zig`, coverage `full_bundle_only` through `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
  - `phase14-ring-buffer-survey-tests`: root `phase14_ring_buffer_survey.zig`, coverage `full_bundle_only` through `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
  - `phase14-rcu-tree-survey-tests`: root `phase14_rcu_tree_survey.zig`, coverage `full_bundle_only` through `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
  - `phase14-end-to-end-smoke-tests`: root `phase14_end_to_end_smoke_survey.zig`, coverage `focused_and_full_bundle` through dedicated shard `phase14-smoke` plus the shared `zig build test --build-file zigux/tests/phase14_build.zig --summary all` replay
- anchor packets in the current smoke bundle:
  - workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-Y05`, surveyed commit `542acd7b12c52211ef9a8bd790fa2e2b3367cbf0`, blocked `phase14-workqueue-live-execution-blocker`
  - skbuff: `zigux/tests/phase14_skbuff_bridge_manifest.json`, lane `P14-L12`, surveyed commit `6689715b1930c419e49a44b1c2dd317548a08c1d`, blocked `phase14-skbuff-live-ownership-blocker`
  - ring buffer: `zigux/tests/phase14_ring_buffer_manifest.json`, lane `P14-L08`, surveyed commit `f9a7a6e93c8e6a1b6550fd7b2aa5571729aab05b`, blocked `phase14-ring-buffer-zig-port-blocker`
  - RCU tree: `zigux/tests/phase14_rcu_tree_manifest.json`, lane `P14-Y04`, surveyed commit `355b71d89807a217a6b7c405c996cbd623c48ca0`, blocked `phase14-rcu-tree-bridge-blocker`

## Shared smoke findings

- `zigux/tests/phase14_build.zig` is the shared Phase 14 replay entrypoint and now includes the dedicated smoke survey alongside the four anchor-local packets.
- `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `Documentation/zigux/README.md`, `scripts/zigux/validate-phase14.py`, and `scripts/zigux/README.md` now keep the fast shared-smoke contract explicit, so the docs-root summary, release-boundary exact-count helper, shared note, manifest, make targets, workflow path, and smoke-shard entrypoint are checked before the slower replay claims stay current.
- `Documentation/zigux/phase14-release-boundary-survey.md` is now counted inside the same shared smoke packet, so the release-facing sequencing note cannot drift away from the validator-backed four-anchor boundary packet while this lane stays in maintenance mode.
- `zigux/tests/phase14_build.zig` now exposes one dedicated shared `phase14-smoke` shard, and all four anchor-local artifacts still replay only through the heavier `test` bundle.
- `zigux/tests/phase14_build.zig` now also keeps the routing boundary explicit: the full `test` bundle depends on all five compile artifacts exactly once, while the focused `phase14-smoke` shard depends only on the shared smoke survey artifact.
- `zigux/Makefile` now exposes `make -C zigux phase14-test` as the direct wrapper-backed full replay alongside `make -C zigux phase14-validate` and `make -C zigux phase14-smoke`, so the shared smoke packet names the smallest full-bundle wrapper route explicitly instead of leaving it implied behind `make -C zigux phase14` or the raw `zig build test --build-file zigux/tests/phase14_build.zig --summary all` command.
- `zigux/Makefile` now exposes `make -C zigux phase14-validate` before the full `make -C zigux phase14` replay and also keeps `make -C zigux phase14-smoke` available as the focused shared smoke shard.
- `.github/workflows/zigux-bootstrap.yml` now runs the validator-backed shared smoke packet, the focused `make -C zigux phase14-smoke` wrapper path, and the full Phase 14 build command, so the shared packet gets both a fast contract check and the exact wrapper-backed smoke replay path a reviewer would use locally.
- `Documentation/zigux/freeze-map.md` still names the four Phase 14 anchors, which keeps the smoke packet grounded in the roadmap's study-only and freeze posture rather than implying a bridge-first expansion.
- `Documentation/zigux/review-checklist.md` now carries a dedicated prompt for the shared Phase 14 smoke packet so later edits have to keep the four anchor-local manifests, survey notes, and shared replay contract aligned.
- `zigux/tests/phase14_end_to_end_smoke_survey.zig` now treats the shared note's quoted shared-lane marker plus per-anchor surveyed commits as machine-checked evidence, so future shared or anchor-manifest refreshes cannot silently leave the shared smoke note behind.
- `zigux/tests/phase14_end_to_end_smoke_manifest.json` now also records which compile artifacts are `full_bundle_only` or `focused_and_full_bundle`, so later build-file churn cannot silently undercount dedicated Phase 14 leaf-step coverage.
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md` now keeps the direct attached-toolchain `phase14-test` wrapper explicit beside the shared smoke fallback commands, so reviewers in mounted-toolchain environments can rerun the internal bridge replay without rediscovering the `ZIG=` override from `zigux/Makefile` alone.
- this survey now also keeps the non-fallback `make -C zigux phase14-test` wrapper explicit beside the raw `zig build test --build-file zigux/tests/phase14_build.zig --summary all` command, so the shared smoke packet names the smallest full-bundle wrapper replay that matches the existing Makefile route instead of treating it as attached-toolchain-only knowledge.
- the shared smoke manifest and note now also keep the exact `blocked_on_stay_in_c_evidence` review-blocker status explicit alongside the rollback threshold, fallback path, and return-to-blocked trigger catalog, so the packet fails closed before any shared smoke maintenance can overstate a Phase 14 status change.
- `zigux/tests/phase14_end_to_end_smoke_manifest.json` now is the current four-anchor boundary map for the shared packet, because it keeps the workqueue, skbuff, ring-buffer, and RCU anchor manifests pinned together under one reviewable lane.
- those same four anchor-local packets are the current bounded concurrency-audit scope for this slice: they keep queue, ownership, buffer, and grace-period audit evidence reviewable without claiming live parity or a status change.

## Productization evidence

- named owner: `Core-Adjacent Pod`
- status bucket: `study_only`
- validation gate: `zig build test --build-file zigux/tests/phase14_build.zig --summary all && make -C zigux phase14`
- rollback owner: `Repo Tooling Pod`
- review blocker status: `blocked_on_stay_in_c_evidence`
- roadmap risk bundle:
  - `hidden runtime behavior`
  - `memory-ordering mistakes`
  - `overpromising full parity`
  - `deep-core scope creep`
- ZAR-to-product transfer rationale: absorb ZAR runtime research as product discipline only by keeping exported evidence packets, machine-checked surveyed commits, and explicit blocker posture, without importing ZAR runtime-core behavior into Zigux.
- rollback threshold: keep the shared smoke packet in `study_only` posture and return it to blocked shared-packet maintenance if the validation gate, rollback owner, stay-in-C boundary, fallback path, or quoted anchor posture stops being explicit.
- fallback path: Keep `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as the source of truth, keep the shared smoke packet limited to validator-backed survey evidence, and fall back to blocked shared-packet maintenance if the rollback contract stops being explicit.
- required evidence:
  - named owner, validation gate, and rollback owner recorded together in the shared smoke manifest and survey note
  - shared smoke validator, dedicated docs-root smoke checker, focused `phase14-smoke` shard, full `phase14` replay commands, and the docs-root summary recorded together beside the same stay-in-C boundary
  - anchor packet surveyed commits plus ready-next versus blocked posture refreshed in the shared smoke packet whenever any Phase 14 anchor-local manifest moves
- automatic return-to-blocked triggers:
  - any shared smoke packet edit that drops the named validation gate or rollback owner
  - missing fallback path or study-only stay-in-C wording in the shared manifest, survey note, review checklist, `Documentation/zigux/README.md`, or `scripts/zigux/README.md`
  - any anchor-local manifest refresh that changes a quoted surveyed commit or lane key without refreshing the shared smoke packet
  - loss of the dedicated docs-root smoke checker, the docs-root summary, the focused `phase14-smoke` replay contract, or the validator-backed `make -C zigux phase14-validate` entrypoint from the shared packet

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
- `make -C zigux phase14-test`
- `zig build test --build-file zigux/tests/phase14_build.zig --summary all`

2. run the focused Phase 14 smoke shard
- `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
- `make -C zigux phase14-smoke`

3. run the convenience targets
- `make -C zigux phase14`
- `make -C zigux phase14-smoke`

4. run the attached-toolchain fallback path when `zig` is not on `PATH`
- `make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`
- `make -C zigux phase14-smoke ZIG=<attached-zig-path>`
- `make -C zigux phase14-test ZIG=<attached-zig-path>`
- `make -C zigux phase14 ZIG=<attached-zig-path>`

## Next bounded step

Leave this shared smoke lane closed unless one of the four anchor-local Phase 14 manifests, survey notes, or the shared replay wiring drifts. If it does, refresh this packet instead of widening into new deep-core or bridge implementation work.
