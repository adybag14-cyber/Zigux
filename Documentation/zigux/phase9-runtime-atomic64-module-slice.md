# Phase 9 Runtime Atomic64 Module Slice

This note tracks the bounded Phase 9 runtime atomic64 starter packet on `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-module-starter`
- `PHASE9_LANE_KEY=P9-L04`
- `PHASE9_SURVEYED_COMMIT=2026-05-23-runtime-atomic64-shared-loader-reminder-trim`
- scope: selftest-hook and guarded lifecycle reviewability through the direct atomic64 starter packet, plus the adjacent shared loader-facing reminder surfaces only

## Direct Packet

- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `samples/zigux/runtime_atomic64.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`

## Adjacent Shared Loader-Facing Reminder Packet

- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/phase9-first-loadable-runtime-module-parity.md`
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

These shared-loader reminder surfaces are visible review-only evidence on current `master`, and the direct atomic64 packet is still narrower than full loader-backed parity. That means the honest current atomic64 packet is a direct starter packet beside the returned allocator/init-flow loader packet, the dedicated command/environment boundary guard, and the returned bitmap-loader companion, not the older broader loader-gap survey family and not a completed loadable runtime-module path.

## Why This Slice Exists

The direct packet keeps the selftest hook surface and guarded lifecycle parity evidence visible around `lib/atomic64_test.c` without claiming a real loadable Zigux runtime module. The direct packet also keeps the five-family operation replay explicit through `zigux/tests/runtime_atomic64_diff.zig` and the lifecycle boundary proofs explicit through `zigux/tests/runtime_atomic64_module.zig`.

The adjacent shared loader-facing reminder packet keeps the current cross-family and shared-owner wording reviewable through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `zigux/Makefile`, but it remains visible review-only evidence while the broader runtime substrate stays blocked.

## Gates

1. `zigux/tests/runtime_atomic64_module.zig` remains the dedicated lifecycle gate for the direct packet.
2. `zigux/tests/runtime_atomic64_diff.zig` remains the narrow differential gate against `lib/atomic64_test.c`.
3. `zigux/tests/runtime_atomic64_survey.zig` and `zigux/tests/runtime_atomic64_manifest.json` remain the packet-local survey and manifest gates for the direct starter packet and the visible shared-loader reminder packet.
4. `zigux/tests/phase9_build.zig` keeps `phase9-runtime-atomic64-diff`, `phase9-runtime-atomic64-module-tests`, `phase9-runtime-atomic64-sample-tests`, `phase9-runtime-atomic64-tests`, `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, and `phase9-runtime-loader-shared-tests` explicit beside the shared-loader reminder packet.
5. The visible shared-loader reminder packet keeps the narrower allocator/init-flow replay, command/environment boundary guard, and returned bitmap-loader companion explicit instead of being treated as proof that the missing runtime substrate has already landed.

## Review Surface

- `zigux/tests/runtime_atomic64_module.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/runtime_atomic64_survey.zig`, and `zigux/tests/runtime_atomic64_manifest.json` keep the direct packet machine-checkable.
- The shared-loader reminder packet keeps the allocator/init-flow replay explicit, keeps the command/environment boundary guard explicit, keeps the returned bitmap-loader companion visible, and keeps the loader-facing review packet visible without claiming live runtime binding.

## Freeze-Map Governance Boundary

- `Documentation/zigux/freeze-map.md` still keeps `kernel/workqueue.c` in the study-only bucket, so this slice stays review-only beside that workqueue-facing boundary instead of claiming scheduler or workqueue parity.
- No parity scorecard entry or Architecture Council status-change request is attached to this slice on current `master`.
- Any future freeze-map status change for this family must route through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, and it must keep `Documentation/zigux/phase15-study-only-anchor-accounting.md` explicit while `kernel/workqueue.c` remains a study-only boundary, instead of being inferred from this family-local packet.

## Minimum Freeze-Map Review Record

- owner: the direct atomic64 starter packet named by `PHASE9_LANE_KEY=P9-L04`, with this note carrying the same Phase 9 freeze-boundary review record for `P9-L13`
- phase: `Phase 9`
- status bucket: review-only direct starter packet plus the returned allocator/init-flow loader packet, dedicated command/environment boundary guard, and returned bitmap-loader companion beside the study-only `kernel/workqueue.c` boundary
- validation gate summary: `zigux/tests/runtime_atomic64_module.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/runtime_atomic64_survey.zig`, `zigux/tests/runtime_atomic64_manifest.json`, `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, and `samples/zigux/runtime_bitmap_loader.zig` keep this packet reviewable without claiming live loader parity
- rollback owner: `lib/atomic64_test.c` remains the product source of truth while any future status change still routes through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, with `Documentation/zigux/phase15-study-only-anchor-accounting.md` kept explicit while the `kernel/workqueue.c` boundary stays study-only

## Non-goals

- No claim that the real runtime substrate is available.
- No claim of scheduler-facing or workqueue parity.
- No claim of full loadable module lifecycle parity before the shared runtime substrate lands.
- No claim that the visible shared-loader reminder packet is the same thing as a completed live loader binding.

## Next Bounded Step

Keep future follow-through inside one exact atomic64 packet truthfulness repair. The strongest next candidate remains whichever direct atomic64 note, manifest, survey, or loader-reminder assertion drifts first, because that is the smallest safe way to keep this slice truthful without overstating current repo reality.