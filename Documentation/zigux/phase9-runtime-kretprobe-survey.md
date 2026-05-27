# Phase 9 Runtime Kretprobe Survey

This note tracks the bounded Phase 9 runtime kretprobe pilot packet.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_LANE_KEY=P9-L13`
- `PHASE9_SURVEYED_COMMIT=2026-05-27-runtime-kretprobe-reinit-reexit-packet-alignment`
- scope: direct sample proof, direct loader proof, direct initialized-snapshot guard proof, direct registration-reentry proof, direct reinit-reexit rollback proof, direct module proof, direct survey proof, shared Phase 9 build rerun handles, and no broader shared runtime-loader parity claim

## Current repo reality
- trusted current-tree reads on 2026-05-27 materialize `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and `zigux/tests/phase9_build.zig`
- this restored packet also materializes `Documentation/zigux/phase9-runtime-kretprobe-survey.md`, `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`, and `zigux/tests/runtime_kretprobe_manifest.json` so the family-local review story matches the direct sample and test surfaces already on `master`
- keep `zigux/tests/phase9_build.zig` explicit only as a bounded rerun shard whose live body reruns the sample, loader, initialized-snapshot guard, registration-reentry guard, reinit-reexit guard, survey, and module tests; that shard still does not prove broader shared runtime-loader parity or shipped publication flow
- keep `zigux/Makefile` explicit as the narrow wrapper rerun handle for the same packet: current `master` exposes `phase9-runtime-kretprobe-test`, and that wrapper still shells into `zig build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig --summary all`
- keep the direct sample `.requires_runtime_substrate = true` and `.provides_selftest_hook = true` markers explicit when this survey summarizes runtime pilot scope
- keep the direct sample initialized, selftest_complete, and exited lifecycle packet explicit when this survey summarizes family-local lifecycle proof
- keep the direct loader shared-request plan packet explicit without promoting it into broader shared runtime-loader completion proof
- keep the initialized-snapshot, registration-reentry, and reinit-reexit companions explicit when this survey summarizes the bounded kretprobe pilot packet

## Boundaries
- keep the visible kretprobe-side reminder packet inside `Documentation/zigux/phase9-runtime-kretprobe-survey.md`, `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`, `zigux/tests/runtime_kretprobe_manifest.json`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig`, the shared `zigux/tests/phase9_build.zig` shard, and the narrow `zigux/Makefile` wrapper
- keep the adjacent `zigux/tests/runtime_first_loadable_parity_behavior.zig` surface explicit as cross-family evidence rather than as family-local loader parity proof
- keep the blocked shared runtime-loader substrate explicit
- do not claim loadable runtime kretprobe module parity
- do not present the visible kretprobe packet as proof that the broader shared runtime-loader packet returned
- keep the focused `phase9-runtime-kretprobe-tests` route name, the dedicated `phase9-runtime-kretprobe-reinit-reexit-guard-tests` route, and the narrower `phase9-runtime-kretprobe-test` Makefile wrapper framed only as bounded rerun handles for the visible sample, loader, initialized-snapshot guard, registration-reentry guard, reinit-reexit guard, survey, and module packet

## Roadmap gap
- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime kretprobe reminder packet is still `direct_sample_loader_guard_and_module_packet_without_broader_shared_runtime_loader_parity`: the survey note, module-slice note, manifest-backed ownership packet, survey gate, bounded build shard, direct sample, direct loader companion, direct initialized-snapshot guard, direct registration-reentry guard, direct reinit-reexit guard, and direct module proof are visible, but the broader shared runtime-loader substrate is still only partially materialized on the trusted path
- the blocked deliverable remains `loadable Phase 9 runtime kretprobe pilot module parity`

## Gates
1. `zig test zigux/tests/runtime_kretprobe_survey.zig`
2. `zig test zigux/tests/runtime_kretprobe_module.zig`
3. `zig test samples/zigux/runtime_kretprobe.zig`
4. `zig test samples/zigux/runtime_kretprobe_loader.zig`
5. `zig test samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`
6. `zig test samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`
7. `zig test samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig`
8. `zig build phase9-runtime-kretprobe-reinit-reexit-guard-tests --build-file zigux/tests/phase9_build.zig --summary all`
9. `zig build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig --summary all`
10. `make -C zigux phase9-runtime-kretprobe-test`

Treat the shared `zigux/tests/phase9_build.zig` kretprobe route names plus the narrow `zigux/Makefile` wrapper as bounded rerun handles for the visible sample, loader, initialized-snapshot guard, registration-reentry guard, reinit-reexit guard, survey, and module packet only while the broader shared runtime-loader family remains partial.

## Next bounded step

Replay `zig build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig` on a fresh full checkout and fix only the next kretprobe-local compile or note drift it exposes, leaving broader shared runtime-loader follow-through to the separate shared-owner packet.