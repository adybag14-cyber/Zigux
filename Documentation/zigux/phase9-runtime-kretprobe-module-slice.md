# Phase 9 Runtime Kretprobe Module Slice

This note keeps the bounded runtime kretprobe pilot-module slice reviewable without widening it into broader shared runtime-loader claims.

## Scope
- pair this slice note with `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
- keep `zigux/tests/runtime_kretprobe_manifest.json` and `zigux/tests/runtime_kretprobe_survey.zig` aligned with the same family-local packet
- keep `zigux/tests/runtime_kretprobe_module.zig` as the direct module-boundary witness for the visible kretprobe pilot family

## Current packet
- `samples/zigux/runtime_kretprobe.zig` advertises `.requires_runtime_substrate = true` and `.provides_selftest_hook = true`
- the sample keeps initialized, selftest_complete, and exited lifecycle tracking explicit together with the bounded selftest hook and exit replay
- `samples/zigux/runtime_kretprobe_loader.zig` keeps the family-local shared-request plan reviewable without promoting that plan into shipped broader runtime-loader parity
- `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig` keeps captured initialized-state replay explicit across later selftest and exit activity
- `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig` keeps registration reuse and fail-closed post-exit behavior explicit
- `samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig` keeps the paired rejected re-init and rejected re-exit rollback packet explicit after initialized direct activity and after selftest-ready replay
- `zigux/tests/runtime_kretprobe_module.zig` keeps the descriptor, selftest summary, lifecycle snapshot, initialized-stage exit replay, rejected re-init and re-selftest rollback, duplicate-registration rollback, failed-exit rollback, failed-unregister rollback, rejected entry-without-registration rollback, and rejected return-without-entry rollback packet reviewable at the module boundary

## Build boundary
- keep `zigux/tests/phase9_build.zig` explicit as the bounded rerun shard for `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-reinit-reexit-guard-tests`, `phase9-runtime-kretprobe-survey-tests`, and `phase9-runtime-kretprobe-module-tests`
- keep `zigux/Makefile` explicit only as the narrow wrapper rerun handle for `phase9-runtime-kretprobe-test`
- keep `zigux/tests/runtime_first_loadable_parity_behavior.zig` adjacent as cross-family evidence rather than as family-local loader completion proof

## Non-goals
- do not claim broader shared runtime-loader parity
- do not claim shipped publication, install-root, or depmod-visible proof
- do not treat the direct loader companion as proof that the wider shared runtime-loader packet has landed

## Next bounded step

If the kretprobe sample family changes again, refresh only this slice note, the paired survey note, the manifest, and the survey gate needed to keep the direct pilot-module packet truthful while leaving broader shared runtime-loader work parked in its own lane.