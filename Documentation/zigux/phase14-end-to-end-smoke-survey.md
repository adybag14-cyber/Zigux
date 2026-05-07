# Phase 14 End-to-End Smoke Survey

This document records the shared Phase 14 smoke lane that keeps the current study-only core-adjacent packet reviewable on `master` without implying a removed validator stack or an active deep-core port.

## Status

- `PHASE14_STATUS=study_only`
- `PHASE14_SLICE=end-to-end-smoke-verification`
- `PHASE14_SHARED_LANE=P14-L07`
- `PHASE14_SHARED_REPLAY_PRESENT=yes`
- `PHASE14_SMOKE_SHARD_PRESENT=yes`
- `PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate`
- `PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py`
- `PHASE14_TEST_ENTRYPOINT=make -C zigux phase14-test`
- `PHASE14_SMOKE_ENTRYPOINT=make -C zigux phase14-smoke`
- `PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all`
- `PHASE14_SMOKE_BUILD_ENTRYPOINT=zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
- `PHASE14_COMBINED_ENTRYPOINT=make -C zigux phase14`
- `PHASE14_ANCHOR_PACKET_COUNT=4`
- `PHASE14_COMPILE_ARTIFACT_COUNT=5`
- `PHASE14_FOCUSED_SHARD_COUNT=1`
- `PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=4`
- `PHASE14_STAY_IN_C_BOUNDARY=explicit`
- `PHASE14_REVIEW_BLOCKER_STATUS=blocked_on_stay_in_c_evidence`
- `PHASE14_STATUS_CHANGE_CLAIM=no`
- `PHASE14_BOUNDARY_MAP=shared-anchor-packet-bundle`
- `PHASE14_CONCURRENCY_AUDIT_SCOPE=anchor-local-packets-only`

Shared smoke boundary:

- `Documentation/zigux/README.md`
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- `Documentation/zigux/phase14-core-boundary-traceability.md`
- `Documentation/zigux/phase14-release-boundary-survey.md`
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase14.py`
- `scripts/zigux/check-phase14-docs-root-smoke-summary.py`
- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
- `zigux/tests/README.md`
- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_workqueue_bridge.zig`
- `zigux/tests/phase14_workqueue_bridge_manifest.json`
- `zigux/tests/phase14_skbuff_bridge.zig`
- `zigux/tests/phase14_skbuff_bridge_manifest.json`
- `zigux/tests/phase14_ring_buffer_survey.zig`
- `zigux/tests/phase14_ring_buffer_manifest.json`
- `zigux/tests/phase14_rcu_tree_survey.zig`
- `zigux/tests/phase14_rcu_tree_manifest.json`
- `zigux/tests/phase14_end_to_end_smoke_survey.zig`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

## Why This Slice Exists

The roadmap keeps `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` inside a bounded Phase 14 study-only tranche between the active Phase 13 helper packet and the parked Phase 15 governance packet.

That means the honest product task here is not a new bridge or validator-first expansion. It is one shared smoke packet that keeps the four anchor-local manifests, the cross-anchor traceability note, the docs-root summary, the release-boundary note, the freeze-map posture, and the shipped replay routes aligned.

Within that packet, `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as the two boundary-study-only anchors, while `kernel/rcu/tree.c` and `net/core/skbuff.c` stay explicit as the two freeze-in-C-governed anchors.

## Exact Evidence Captured

Shared smoke commands:

- `make -C zigux phase14-validate`
- `make -C zigux phase14-smoke`
- `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
- `make -C zigux phase14-test`
- `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
- `make -C zigux phase14`

Attached-toolchain fallback examples:

- `make -C zigux phase14-validate ZIG=/absolute/path/to/attached-zig/zig`
- `make -C zigux phase14-smoke ZIG=/absolute/path/to/attached-zig/zig`
- `make -C zigux phase14-test ZIG=/absolute/path/to/attached-zig/zig`
- `make -C zigux phase14 ZIG=/absolute/path/to/attached-zig/zig`

Compile coverage matrix:

- `phase14-workqueue-bridge-tests`: root `phase14_workqueue_bridge.zig`, coverage `full_bundle_only`
- `phase14-skbuff-bridge-tests`: root `phase14_skbuff_bridge.zig`, coverage `full_bundle_only`
- `phase14-ring-buffer-survey-tests`: root `phase14_ring_buffer_survey.zig`, coverage `full_bundle_only`
- `phase14-rcu-tree-survey-tests`: root `phase14_rcu_tree_survey.zig`, coverage `full_bundle_only`
- `phase14-end-to-end-smoke-tests`: root `phase14_end_to_end_smoke_survey.zig`, coverage `focused_and_full_bundle`

Anchor packets in the current smoke bundle:

- workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, blocked `phase14-workqueue-live-execution-blocker`
- skbuff: `zigux/tests/phase14_skbuff_bridge_manifest.json`, blocked `phase14-skbuff-live-ownership-blocker`
- ring buffer: `zigux/tests/phase14_ring_buffer_manifest.json`, blocked `phase14-ring-buffer-zig-port-blocker`
- RCU tree: `zigux/tests/phase14_rcu_tree_manifest.json`, blocked `phase14-rcu-tree-bridge-blocker`

## Shared Smoke Findings

- `zigux/Makefile`, `scripts/zigux/validate-phase14.py`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, and this smoke note align on the shipped validator, focused smoke shard, shared full-bundle replay, and convenience wrapper for the current study-only packet.
- `scripts/zigux/check-phase14-docs-root-smoke-summary.py` now also keeps this shared smoke note and the manifest-backed packet inventory tied to the shipped `phase14-validate` route instead of leaving the docs-root smoke-summary checker implicit in `zigux/Makefile` alone.
- `Documentation/zigux/phase14-core-boundary-traceability.md` keeps the current ring-buffer, skbuff, and RCU lane keys, surveyed commits, ready-next posture, blocked gaps, and stay-in-C decisions visible in one cross-anchor note instead of leaving that boundary evidence to separate lane notes or run memory alone.
- `zigux/tests/phase14_build.zig` keeps one dedicated smoke shard for `phase14-end-to-end-smoke-tests`, while the four anchor-local artifacts remain `full_bundle_only` under the broader Phase 14 test replay.
- `Documentation/zigux/freeze-map.md` still names the same four anchors, so the packet stays grounded in stay-in-C and blocked-evidence posture instead of drifting toward an implementation claim.
- `Documentation/zigux/phase14-ring-buffer-survey.md` and `zigux/tests/phase14_ring_buffer_manifest.json` agree on lane `P14-L08` at surveyed commit `946d5c73fdb763ba860a20879b05da54e1896e8c`, keeping the ring-buffer anchor study-only while carrying the landed exported-page copy-path audit instead of any `kernel/trace/ring_buffer.zig` claim.
- This note keeps the attached-toolchain fallback scoped to note-local environment guidance only; broader README, manifest, or shared-surface alignment remains outside this lane unless a future shared-smoke pass intentionally widens scope.

## Productization Evidence

- named owner: `Core-Adjacent Pod`
- status bucket: `study_only`
- validation gate: `make -C zigux phase14-validate && make -C zigux phase14-smoke && make -C zigux phase14-test && make -C zigux phase14`
- rollback owner: `keep the freeze-map anchors in C and reopen only with stronger evidence`
- review blocker status: `blocked_on_stay_in_c_evidence`

Roadmap risk bundle:

- `hidden runtime behavior`
- `memory-ordering mistakes`
- `overpromising full parity`
- `deep-core scope creep`

Fallback path:

Keep `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as the source of truth and keep the shared smoke packet limited to survey-backed reviewability evidence.

## Non-Goals

This shared smoke slice does not claim:

- live workqueue execution, draining, or cancellation parity
- skbuff lifetime, destructor, checksum, or segmentation ownership
- `kernel/trace/ring_buffer.zig`
- any live `kernel/rcu/tree_bridge.zig` ownership claim
- any Phase 14 status change beyond the current study-only shared packet

## Gates

1. Run the shared validator.
   `make -C zigux phase14-validate`
2. Run the focused smoke shard.
   `make -C zigux phase14-smoke`
   `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
3. Run the shared full-bundle replay.
   `make -C zigux phase14-test`
   `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
4. Run the convenience wrapper.
   `make -C zigux phase14`
5. Use the attached-toolchain fallback only when `zig` is not already on `PATH`.
   `make -C zigux phase14-validate ZIG=/absolute/path/to/attached-zig/zig`
   `make -C zigux phase14-smoke ZIG=/absolute/path/to/attached-zig/zig`
   `make -C zigux phase14-test ZIG=/absolute/path/to/attached-zig/zig`
   `make -C zigux phase14 ZIG=/absolute/path/to/attached-zig/zig`

## Next Bounded Step

Leave this shared smoke lane parked unless one of the four anchor-local manifests, the cross-anchor traceability note, the shared replay wiring, or the paired Phase 14 docs surfaces drift. If they do, refresh this packet instead of widening into new bridge or deep-core implementation work.
