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
- `PHASE14_STAY_IN_C_BOUNDARY=explicit`
- `PHASE14_STATUS_CHANGE_CLAIM=no`
- survey provenance captured against verified `master` head `c1ca884d084f000475bcb79019227d50a873896a`
- shared smoke boundary:
  - `scripts/zigux/validate-phase14.py`
  - `scripts/zigux/check-phase14-docs-root-smoke-summary.py`
  - `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`
  - `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
  - `scripts/zigux/README.md`
  - `zigux/tests/phase14_end_to_end_smoke_manifest.json`
  - `zigux/tests/phase14_end_to_end_smoke_survey.zig`
  - `zigux/tests/phase14_build.zig`
  - `zigux/tests/phase14_workqueue_reviewability.zig`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
  - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 14 roadmap treats `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as boundary-study or freeze-in-C anchors. That means Phase 14 needs a small shared smoke packet that proves the repo still carries those four anchors as one reviewable bundle, with exact commands and explicit ready-next versus blocked posture, instead of letting each lane drift in isolation.

This lane stays narrow on purpose. It does not add a new bridge. It verifies that the current shared replay covers the four anchor-local packets, that the convenience target and workflow still exercise the same shared entrypoint, and that the checklist plus freeze map still describe the same stay-in-C posture.

## Exact evidence captured

- verified `master` head: `c1ca884d084f000475bcb79019227d50a873896a`
- validator-backed smoke commands:
  - `make -C zigux phase14-validate`
  - `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
  - `make -C zigux phase14`
- focused smoke-shard commands:
  - `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
  - `make -C zigux phase14-smoke`
- attached-toolchain fallback examples for this note's shared replay routes only:
  - `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-smoke`
  - `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-test`
  - `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14`
- compile shard matrix captured in the current shared packet:
  - `phase14-workqueue-bridge-tests` -> `phase14_workqueue_bridge.zig` -> `full_bundle_only`
  - `phase14-workqueue-reviewability-tests` -> `phase14_workqueue_reviewability.zig` -> `full_bundle_only`
  - `phase14-skbuff-bridge-tests` -> `phase14_skbuff_bridge.zig` -> `full_bundle_only`
  - `phase14-ring-buffer-survey-tests` -> `phase14_ring_buffer_survey.zig` -> `full_bundle_only`
  - `phase14-rcu-tree-survey-tests` -> `phase14_rcu_tree_survey.zig` -> `full_bundle_only`
  - `phase14-end-to-end-smoke-tests` -> `phase14_end_to_end_smoke_survey.zig` -> `focused_and_full_bundle`
- anchor packets in the current smoke bundle:
  - workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-L01`, surveyed commit `007f00d0c6b6b430bfbb2110555544cc5faefe8b`, ready-next `phase14-workqueue-drain-cancel-followup`, blocked `phase14-workqueue-live-execution-blocker`
  - skbuff: `zigux/tests/phase14_skbuff_bridge_manifest.json`, lane `P14-Y03`, surveyed commit `f05e02445443e7743c3675a6f8ca4f70f6e736fb`, ready-next none currently recorded, blocked `phase14-skbuff-live-ownership-blocker`
  - ring buffer: `zigux/tests/phase14_ring_buffer_manifest.json`, lane `P14-L08`, surveyed commit `946d5c73fdb763ba860a20879b05da54e1896e8c`, ready-next `phase14-ring-buffer-read-page-copy-followup`, blocked `phase14-ring-buffer-zig-port-blocker`
  - RCU tree: `zigux/tests/phase14_rcu_tree_manifest.json`, lane `P14-L16`, surveyed commit `4c889233d157960514b241bcd5aff7cac5fda312`, ready-next none currently recorded, blocked `phase14-rcu-tree-bridge-blocker`

## Shared smoke findings

- `zigux/tests/phase14_build.zig` is the shared Phase 14 replay entrypoint and now includes the dedicated smoke survey, the four anchor-local packets, and the focused workqueue reviewability replay.
- `scripts/zigux/validate-phase14.py`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, and `scripts/zigux/check-phase14-release-boundary-exact-counts.py` keep the fast shared-smoke contract explicit, so the note, manifest, make targets, workflow path, and smoke-shard entrypoint are checked before the slower replay claims stay current.
- the shared compile shard matrix now records that the workqueue reviewability replay plus the four anchor-local replays remain `full_bundle_only`, while `phase14-end-to-end-smoke-tests` is the only `focused_and_full_bundle` shard. That keeps the roadmap's validation-before-expansion discipline explicit without inventing new focused bridge claims.
- `zigux/tests/phase14_build.zig` still exposes a dedicated `phase14-smoke` shard so the shared smoke packet can be replayed without compiling the heavier anchor-local bundle.
- `zigux/Makefile` still exposes `make -C zigux phase14-validate` before the full `make -C zigux phase14` replay, keeps `make -C zigux phase14-smoke` available as the focused shared smoke shard, and still honors the standard `ZIG` environment override so the attached archive can be injected with the literal `ZIG=/absolute/path/to/attached-zig/zig` examples above when the default toolchain path is unavailable in the local shell.
- `.github/workflows/zigux-bootstrap.yml` still runs the validator-backed shared smoke packet, the focused smoke shard, and the full Phase 14 build command, so the shared packet gets both a fast contract check and the existing end-to-end replay.
- `Documentation/zigux/freeze-map.md` still names the four Phase 14 anchors, which keeps the smoke packet grounded in the roadmap's study-only and freeze posture rather than implying a bridge-first expansion.
- `Documentation/zigux/review-checklist.md` still carries a dedicated prompt for the shared Phase 14 smoke packet so later edits have to keep the four anchor-local manifests, survey notes, and shared replay contract aligned.

## Productization evidence

- named owner: `Core-Adjacent Pod`
- status bucket: `study_only`
- validation gate: `zig build test --build-file zigux/tests/phase14_build.zig --summary all && make -C zigux phase14`
- rollback owner: `Repo Tooling Pod`
- ZAR-to-product transfer rationale: absorb ZAR runtime research as product discipline only by keeping exported evidence packets, machine-checked surveyed commits, compile-shard coverage, and explicit blocker posture, without importing ZAR runtime-core behavior into Zigux.

## Non-goals

This shared smoke slice does not claim:

- live workqueue execution, draining, or cancellation parity
- skbuff lifetime, destructor, checksum, or segmentation ownership
- `kernel/trace/ring_buffer.zig`
- `kernel/rcu/tree_bridge.zig`
- any new focused replay route for the four anchor-local packets
- any Phase 14 status change beyond verifying and recording the current evidence bundle

## Gates

1. run the shared Phase 14 build
- `make -C zigux phase14-validate`
- `zig build test --build-file zigux/tests/phase14_build.zig --summary all`

2. run the focused Phase 14 smoke shard
- `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`

3. run the convenience targets
- `make -C zigux phase14`
- `make -C zigux phase14-smoke`

4. rerun the same note with the attached toolchain when the shell cannot find the default Zig binary
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-smoke`
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-test`
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14`

## Next bounded step

Keep this shared smoke lane open for one remaining review-surface truthfulness repair: `Documentation/zigux/review-checklist.md` still omits `scripts/zigux/check-phase14-docs-root-smoke-summary.py` from the shared Phase 14 prompt even though the docs root, scripts root, manifest, validator packet, and this survey all treat that checker as shipped packet evidence. Once that checklist reminder is made explicit and the paired validator marker is tightened to fail closed on the same four-checker packet, park this lane again unless one of the four anchor-local manifests, survey notes, the compile shard matrix, or the shared replay wiring drifts.
