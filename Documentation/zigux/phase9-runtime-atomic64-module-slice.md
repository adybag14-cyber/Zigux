# Phase 9 Runtime Atomic64 Module Slice

This note tracks the bounded Phase 9 runtime atomic64 starter packet on `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-module-starter`
- `PHASE9_LANE_KEY=P9-L04`
- `PHASE9_SURVEYED_COMMIT=ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- scope: selftest hook surface, guarded lifecycle parity evidence, direct atomic64 starter packet truthfulness, bounded loader-scaffold review only, and dedicated survey-note plus manifest closure only

## Direct Packet

- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`
- `Documentation/zigux/phase9-runtime-atomic64-survey.md`

## Adjacent Shared Loader-Facing Reminder Packet

- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/Makefile`

These shared loader-facing files are visible review-only evidence on current `master`. They keep the shared handoff packet readable beside the atomic64 loader scaffold without turning this family-local slice into a completed loadable runtime-module path.

## Why This Slice Exists

The direct starter keeps the selftest hook surface and guarded lifecycle parity evidence visible around `lib/atomic64_test.c` without claiming a real loadable runtime module.

The bounded loader scaffold under `samples/zigux/runtime_atomic64_loader.zig` still keeps the intended entry symbol, exit symbol, and handoff-plan shape reviewable. It also keeps the prepared `RuntimeAtomic64LoadSummary` snapshot reviewable: once `prepare()` captures the anchor, checked operation families, counter snapshot, and selftest-run count, later counter mutation, later selftest activity, or later exit activity do not rewrite the shared request that this pilot hands toward the still-blocked runtime substrate. The adjacent shared loader-facing reminder packet is now visible on current `master`, but it remains review-only evidence while the broader runtime substrate stays blocked.

That means the honest current atomic64 packet is a direct starter plus a visible shared-loader reminder packet, not a completed loadable runtime-module path.

## Gates

1. `zigux/tests/runtime_atomic64_module.zig` remains the dedicated lifecycle gate for the direct starter packet.
2. `zigux/tests/runtime_atomic64_diff.zig` remains the narrow differential gate against `lib/atomic64_test.c`.
3. `zigux/tests/runtime_atomic64_survey.zig` remains the truthfulness gate for the direct packet and the visible shared-loader reminder packet.
4. `zigux/tests/phase9_build.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/Makefile` stay adjacent shared review surfaces only until the broader runtime substrate actually lands.

## Review Surface

- `samples/zigux/runtime_atomic64.zig` keeps the direct starter and selftest hook surface explicit.
- `zigux/tests/runtime_atomic64_module.zig`, `zigux/tests/runtime_atomic64_diff.zig`, and `zigux/tests/runtime_atomic64_survey.zig` keep the direct packet machine-checkable.
- `Documentation/zigux/phase9-runtime-atomic64-survey.md` and `zigux/tests/runtime_atomic64_manifest.json` keep the packet truthfulness explicit, including the visible shared-loader reminder packet and the still-blocked broader runtime substrate.
- `samples/zigux/runtime_atomic64_loader.zig` remains a bounded loader scaffold only; it owns the prepared `RuntimeAtomic64LoadSummary` snapshot replay across later counter mutation and later lifecycle changes, but it does not currently prove completed runtime-substrate parity.

## Non-goals

- No claim that the real runtime substrate is available.
- No claim of scheduler-facing or workqueue parity.
- No claim of full loadable module lifecycle parity before the shared runtime substrate lands.
- No claim that the visible shared-loader reminder packet is the same thing as a completed live loader binding.

## Next Bounded Step

Keep future follow-through inside the landed direct atomic64 packet until the broader runtime substrate changes or another packet-local truthfulness drift appears.
