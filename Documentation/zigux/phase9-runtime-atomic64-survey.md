# Phase 9 Runtime Atomic64 Survey

This note tracks the bounded Phase 9 runtime atomic64 packet on current `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-survey`
- `PHASE9_LANE_KEY=P9-L16`
- `PHASE9_SURVEYED_COMMIT=2026-05-27-runtime-atomic64-loader-and-parity-reread`
- scope: direct atomic64 starter truthfulness together with the visible direct loader companion, the visible cross-family parity witness, and the visible shared-loader reminder surfaces only

## Current Packet

Current `master` keeps these direct atomic64-facing packet files visible:

- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`
- `zigux/tests/runtime_first_loadable_parity_behavior.zig`

Current `master` also keeps these shared-loader reminder surfaces visible:

- `Documentation/zigux/phase9-first-loadable-runtime-module-parity.md`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/README.md`
- `samples/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `zigux/Makefile`

That means the honest current packet is the direct atomic64 starter packet together with a visible direct loader companion, a visible cross-family parity witness, and a visible shared-loader reminder packet. The shared-loader reminder surfaces visible here keep the broader runtime-substrate blocker explicit, so this packet is still not a completed loadable runtime-module path.

## Routes

1. `zigux/tests/runtime_atomic64_module.zig` keeps the direct lifecycle packet reviewable.
2. `samples/zigux/runtime_atomic64_loader.zig` keeps the loader-facing seed handoff, selftest replay, direct exit, and rejected re-init, re-selftest, and re-exit paths reviewable without widening into publication or install-root claims.
3. `zigux/tests/runtime_atomic64_diff.zig` keeps the `lib/atomic64_test.c` operation families machine-checkable.
4. `zigux/tests/runtime_atomic64_survey.zig` and `zigux/tests/runtime_atomic64_manifest.json` keep the direct sample leg, direct loader companion, note packet, and exact bounded blocker wording fail-closed.
5. `zigux/tests/runtime_first_loadable_parity_behavior.zig` keeps the bounded cross-family atomic64, bitmap, and kretprobe lifecycle parity witness explicit without promoting the atomic64 packet into proof that the broader shared runtime-loader substrate is complete.
6. `zigux/tests/phase9_build.zig` keeps `phase9-runtime-atomic64-diff`, `phase9-runtime-atomic64-loader-tests`, `phase9-runtime-atomic64-module-tests`, `phase9-runtime-atomic64-sample-tests`, `phase9-runtime-atomic64-tests`, `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests` explicit, including `zig build phase9-runtime-atomic64-sample-tests --build-file zigux/tests/phase9_build.zig`.
7. The shared Phase 9 reminder packet keeps the broader runtime-substrate blocker explicit instead of being treated as proof that the missing runtime substrate has already landed.

## Loader Reminder Evidence

The direct loader companion at `samples/zigux/runtime_atomic64_loader.zig` keeps loader-facing seed replay, initialized-stage exit stability, post-selftest mutation before exit, and rejected re-init, re-selftest, and re-exit checkpoints reviewable on current `master`.

The visible shared-loader reminder packet keeps the broader loader-facing boundary explicit without claiming live loader binding. That packet keeps the allocator/init-flow replay explicit, keeps the command/environment boundary guard explicit, keeps the returned bitmap-loader companion visible, and keeps the shared runtime-load transition guard that synchronizes loader stage and shared release state even if the shared request advances before the loader-owned release path runs.

## Boundaries

1. Keep this packet inside the direct atomic64 starter packet, the visible direct loader companion, the visible cross-family parity witness, and the visible shared-loader reminder surfaces only.
2. Keep the visible shared-loader reminder packet explicit as review-only evidence instead of treating it as completed live loader binding or proof that the broader runtime substrate already exists.
3. Keep lifecycle, selftest, direct counter replay, and loader-facing seed or exit evidence visible without widening into scheduler-facing or workqueue-facing ownership.
4. Do not describe the visible loader reminder packet as shipped end-to-end runtime-module parity while the broader runtime substrate remains the blocker recorded in the manifest.

## Freeze-Map Governance Evidence

- `Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in the study-only bucket, so this packet stays review-only beside that workqueue-facing boundary instead of claiming scheduler or workqueue delivery.
- No parity scorecard entry or Architecture Council status-change request is attached to this packet on current `master`.
- Any future freeze-map status change for this family must route through `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-freeze-map-governance.md` instead of being inferred from the landed atomic64 notes, starter packet, direct loader companion, or visible shared-loader reminder packet.

## Minimum Freeze-Map Review Record

- owner: the direct atomic64 starter packet owned by `P9-L16`, with this survey carrying the same Phase 9 freeze-boundary review record for `P9-L16`
- phase: `Phase 9`
- status bucket: review-only direct starter packet plus the visible direct loader companion, visible cross-family parity witness, and visible shared-loader reminder packet beside the study-only `kernel/workqueue.c` boundary
- validation gate summary: `zigux/tests/runtime_atomic64_survey.zig`, `zigux/tests/runtime_atomic64_manifest.json`, `zigux/tests/runtime_atomic64_module.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `samples/zigux/runtime_atomic64_loader.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, and `samples/zigux/runtime_bitmap_loader.zig` keep this packet reviewable without claiming live loader parity
- rollback owner: `lib/atomic64_test.c` remains the product source of truth while any future status change still routes through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- reopen rule: any attempt to treat this packet as runtime-substrate delivery or to move `kernel/workqueue.c` out of study-only posture must reopen through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` with fresh reviewable evidence

## Recommended Next Step

Keep the next same-lane move inside one exact atomic64 packet truthfulness repair while the visible shared-loader reminder packet remains review-only evidence and the broader runtime-substrate blocker is still explicit. The best next same-lane target is whichever direct atomic64 note, manifest, survey, shared parity assertion, or loader-reminder assertion drifts first against the current direct sample leg, direct loader companion, and visible shared-loader reminder packet.