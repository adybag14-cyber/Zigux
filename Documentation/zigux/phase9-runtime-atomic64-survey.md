# Phase 9 Runtime Atomic64 Survey

This note keeps an owner-facing review surface for the Phase 9 runtime atomic64 packet aligned with current `master`.

## Roadmap anchor

Phase 9 is the runtime pilot tranche.

- Linux anchor: `lib/atomic64_test.c`
- required Zigux features: first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity
- recommended Zigux destinations: `zigux/tests/runtime_*` and `samples/zigux/runtime_*`

This packet is still review-first rather than loadable-runtime-complete. The goal of this note is to record the exact partial atomic64 family-local packet that current `master` exposes without pretending that the broader runtime substrate blocker or the missing direct atomic64 sample-and-test packet are already closed.

## Current review surface

Current `master` keeps the following atomic64 family-local surfaces visible:

- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `zigux/tests/runtime_atomic64_manifest.json`
- `samples/zigux/runtime_atomic64_loader.zig`

Current `master` also still keeps the adjacent shared loader-facing packet visible:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/phase9_build.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`

Direct atomic64 sample-and-test packet files do not currently materialize on `master`:

- `samples/zigux/runtime_atomic64.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`

That means the honest current packet is a partial atomic64 family-local reminder plus the adjacent shared loader-facing handoff packet, not a fully materialized atomic64 sample, module, diff, and survey bundle.

## Bounded truthfulness rules

Keep this atomic64 packet honest in the same way as the shared Phase 9 owner map.

1. Treat the atomic64 family as a bounded runtime-pilot review packet, not as proof that live runtime registration parity or loadable module wiring is complete.
2. Keep the shared loader-facing packet separate from family-local atomic64 wording. If the broader loader facade, contract, allocator/init-flow replay, or build-only checker drift, record that in the shared Phase 9 lane instead of pretending the atomic64 family covers it alone.
3. Do not invent a dedicated `validate-phase9.py` route, a separate atomic64-only validator, or a cleared runtime-substrate handoff on current `master`.
4. Keep the older non-owner boundaries explicit: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.

## Active blocker posture

The immediate same-family blocker on current `master` is not only the broader runtime substrate.

The atomic64 family-local packet is still partial: the loader scaffold, manifest, and module-slice note exist, but the direct atomic64 sample, module gate, diff gate, and dedicated survey gate do not currently materialize on `master`. Until those files exist again, the Phase 9 atomic64 lane should describe its family-local proof as partial repo reality rather than as a fully visible survey-backed starter packet.

The broader Phase 9 runtime substrate also remains blocked. Until that shared substrate lands, the atomic64 packet should stay described as reviewable handoff evidence rather than as completed live runtime module lifecycle parity.

## Recommended next step

The next same-family follow-through should stay small and literal: either restore the missing direct atomic64 sample, module, diff, and survey files, or repair the remaining overstated module-slice and shared reminder wording one file at a time so every Phase 9 atomic64 surface matches current `master` again.
