# Phase 14 End-to-End Smoke Survey

This document records the shared Phase 14 smoke lane that verifies the current bounded-internals evidence bundle as it exists on `master`.

## Status

- `PHASE14_STATUS=active`
- `PHASE14_SLICE=end-to-end-smoke-verification`
- `PHASE14_SMOKE_VALIDATOR=present`
- `PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py`
- `PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate`
- `PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all`
- `PHASE14_TEST_ENTRYPOINT=make -C zigux phase14-test`
- `PHASE14_COMBINED_ENTRYPOINT=make -C zigux phase14`
- `PHASE14_ANCHOR_PACKET_COUNT=4`
- `PHASE14_STAY_IN_C_BOUNDARY=explicit`
- `PHASE14_STATUS_CHANGE_CLAIM=no`
- survey provenance captured against verified `master` head `ee8d45fb744501e853665e889278d74e9e447f0f`
- shared smoke boundary:
  - `scripts/zigux/validate-phase14.py`
  - `scripts/zigux/check-phase14-docs-root-smoke-summary.py`
  - `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`
  - `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`
  - `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
  - `scripts/zigux/README.md`
  - `zigux/tests/phase14_end_to_end_smoke_manifest.json`
  - `zigux/tests/phase14_end_to_end_smoke_survey.zig`
  - `zigux/tests/phase14_build.zig`
  - `zigux/tests/phase14_workqueue_reviewability.zig`
  - `zigux/tests/README.md`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/phase14-release-boundary-survey.md`
  - `Documentation/zigux/phase14-core-boundary-traceability.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 14 roadmap treats `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as boundary-study or freeze-in-C anchors. That means Phase 14 needs a small shared smoke packet that proves the repo still carries those four anchors as one reviewable bundle, with exact commands and explicit ready-next versus blocked posture, instead of letting each lane drift in isolation.

This lane stays narrow on purpose. It does not add a new bridge. It verifies that the current shared replay covers the four anchor-local packets, that the convenience target and workflow still exercise the same shared entrypoint, and that the checklist plus freeze map still describe the same stay-in-C posture.

## Exact evidence captured

- verified `master` head: `ee8d45fb744501e853665e889278d74e9e447f0f`
- validator-backed smoke commands:
  - `make -C zigux phase14-validate`
  - `make -C zigux phase14-test`
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
  - workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-L04`, surveyed commit `9b98d3b9c812840bf279508030be0b8de093736c`, ready-next `none currently recorded`, blocked `phase14-workqueue-live-execution-blocker`
  - skbuff: `zigux/tests/phase14_skbuff_bridge_manifest.json`, lane `P14-L11`, surveyed commit `f05e02445443e7743c3675a6f8ca4f70f6e736fb`, ready-next `none currently recorded`, blocked `phase14-skbuff-live-ownership-blocker`
  - ring buffer: `zigux/tests/phase14_ring_buffer_manifest.json`, lane `P14-L08`, surveyed commit `99cd3249c4bab05b74227ed7ca3869284e818588`, ready-next `none currently recorded`, blocked `phase14-ring-buffer-zig-port-blocker`
  - RCU tree: `zigux/tests/phase14_rcu_tree_manifest.json`, lane `P14-L14`, surveyed commit `4c889233d157960514b241bcd5aff7cac5fda312`, ready-next `none currently recorded`, blocked `phase14-rcu-tree-bridge-blocker`

## Shared smoke findings

- `zigux/tests/phase14_build.zig` is the shared Phase 14 replay entrypoint and now includes the dedicated smoke survey, the four anchor-local packets, and the focused workqueue reviewability replay.
- `scripts/zigux/validate-phase14.py`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, and `scripts/zigux/check-phase14-release-boundary-exact-counts.py` keep the fast shared-smoke contract explicit, so the note, manifest, make targets, workflow path, docs-root summary, tests-root summary, and smoke-shard entrypoint are checked before the slower replay claims stay current.
- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` now fail-closes the tests-root packet order and exact line counts around the shared Phase 14 smoke anchor, so the shared inventory no longer relies on manual readback alone to keep `zigux/tests/README.md` aligned with the manifest-backed packet.
- `zigux/Makefile` now replays `scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test`, and `scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test` before the three live checker invocations inside `make -C zigux phase14-validate`, while `scripts/zigux/validate-phase14.py` continues to rerun `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` inside that same validator-first route. That keeps all four dedicated Phase 14 drift guards on the shared contract path without implying a separate tests-readme make target that current `master` does not ship.
- the shared compile shard matrix now records that the workqueue reviewability replay plus the four anchor-local replays remain `full_bundle_only`, while `phase14-end-to-end-smoke-tests` is the only `focused_and_full_bundle` shard. That keeps the roadmap's validation-before-expansion discipline explicit without inventing new focused bridge claims.
- `zigux/tests/phase14_build.zig` still exposes a dedicated `phase14-smoke` shard so the shared smoke packet can be replayed without compiling the heavier anchor-local bundle.
- `zigux/Makefile` still exposes `make -C zigux phase14-test` as the wrapper-backed full-bundle replay, still exposes `make -C zigux phase14-smoke` as the focused shared smoke shard, and still honors the standard `ZIG` environment override so the attached archive can be injected with the literal `ZIG=/absolute/path/to/attached-zig/zig` examples above when neither the repo-local `.zig-toolchain` fallback nor the shell's default `zig` binary is available in the local environment.
- `.github/workflows/zigux-bootstrap.yml` still runs the validator-backed shared smoke packet, the focused smoke shard, and the full Phase 14 build command, so the shared packet gets both a fast contract check and the existing end-to-end replay.
- `Documentation/zigux/README.md` and `zigux/tests/README.md` now remain part of the explicit shared smoke surface inventory, so the docs root and tests root keep the same study-only packet visible without depending on phase-local notes alone.
- `Documentation/zigux/freeze-map.md` still names the four Phase 14 anchors, which keeps the smoke packet grounded in the roadmap's study-only and freeze posture rather than implying a bridge-first expansion.
- `Documentation/zigux/review-checklist.md` still carries a dedicated prompt for the shared Phase 14 smoke packet so later edits have to keep the four anchor-local manifests, survey notes, and shared replay contract aligned.
- all four anchor packets are now parked on blocked or governance-only posture inside the shared smoke packet; the workqueue packet no longer records the older `phase14-workqueue-pending-bit-audit` ready-next gap, the ring-buffer packet still has no smaller review-only ready-next step after the tracefs reader-serialization audit, and skbuff plus RCU stay parked under freeze-oriented governance.

## Productization evidence

- named owner: `Core-Adjacent Pod`
- status bucket: `study_only`
- validation gate: `zig build test --build-file zigux/tests/phase14_build.zig --summary all && make -C zigux phase14`
- rollback owner: `Repo Tooling Pod`
- rollback threshold: `0` tolerated same-packet drifts across anchor-local manifests, anchor-local survey notes, the compile shard matrix, and shared replay wiring
- fallback path: keep this shared smoke lane parked and rerun `make -C zigux phase14-validate` before reopening any anchor-local or shared follow-up
- automatic return-to-blocked triggers:
  - anchor-local manifest drift
  - anchor-local survey note drift
  - compile shard matrix drift
  - shared replay wiring drift
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
- `make -C zigux phase14-test`
- `zig build test --build-file zigux/tests/phase14_build.zig --summary all`

2. run the focused Phase 14 smoke shard
- `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`

3. run the convenience targets
- `make -C zigux phase14`
- `make -C zigux phase14-smoke`

4. rerun the same note with the attached toolchain when neither the repo-local `.zig-toolchain` fallback nor the shell's default `zig` binary is available
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-smoke`
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-test`
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14`

## Next bounded step

Keep this shared smoke lane parked unless one of the four anchor-local manifests, survey notes, the compile shard matrix, or the shared replay wiring drifts. Current `master` already closed both older cross-anchor reminder gaps: `Documentation/zigux/phase14-core-boundary-traceability.md` stays aligned, and `Documentation/zigux/review-checklist.md` now explicitly names `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` alongside the rest of the shared smoke packet. Any follow-up should therefore stay limited to a fresh packet-truthfulness or fail-closed drift repair rather than reopening anchor-local study surfaces. All four anchor packets remain parked on blocked or governance-only posture with no smaller ready-next gap recorded in the shared packet, so no anchor-local reopen is justified from this lane unless a new shared-packet mismatch appears.
