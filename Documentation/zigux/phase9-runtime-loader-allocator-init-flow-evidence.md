# Phase 9 Runtime Loader Allocator/Init-Flow Evidence

This note records the current `master` readback for the shared Phase 9 runtime-loader allocator and init-flow replay packet.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-loader-allocator-init-flow-evidence`
- `PHASE9_EVIDENCE_MODE=github_connector_readback`
- `PHASE9_EXACT_READBACK_REF=master`
- `PHASE9_ALLOCATOR_INIT_FLOW_TEST_BLOB_SHA=75f8d3795cf407366d593a72fd7a0778a196a51e`
- `PHASE9_SHARED_BUILD_BLOB_SHA=3f9c864f8bfe679533b64d6b310154c0629b5cf8`
- `PHASE9_MAKEFILE_BLOB_SHA=5c955d73ed22487f60f4b4d8129e8258acdda818`
- `PHASE9_EXACT_CHECK_TEST_COUNT=14`
- `PHASE9_INVALID_INIT_OR_HANDOFF_CASE_COUNT=6`
- `PHASE9_APPROVED_PILOT_FAMILY_DRIFT_CASE_COUNT=5`
- `PHASE9_SELFTEST_HOOK_DRIFT_CASE_COUNT=3`
- `PHASE9_PREPARED_PLAN_DRIFT_CASE_COUNT=8`
- `PHASE9_STALE_LOADER_STATE_CASE_COUNT=4`
- `PHASE9_SHARED_BUILD_ROUTE_MARKER_COUNT=10`
- `PHASE9_MANIFEST_PACKET_COUNT=4`

## Current Route

- `zigux/tests/runtime_loader_allocator_init_flow.zig` remains the exact allocator and init-flow replay source.
- `zigux/tests/phase9_build.zig` keeps the replay wired into `phase9-runtime-loader-shared-tests` and the broader shared `test` step.
- `make -C zigux phase9-runtime-loader-shared-tests` remains the focused Linux-style replay route for the shared runtime-loader facade, contract, allocator/init-flow, and loader-gap survey packet.
- `zig build test --build-file zigux/tests/phase9_build.zig` remains the broader shared replay route.
- `python3 scripts/zigux/check-phase9-allocator-init-flow-evidence.py` is the dedicated exact-readback checker for this narrower note.

## Exact Check Inventory

1. The replay covers all four shipped pilot families: `runtime_atomic64`, `runtime_bitmap`, `runtime_trace_events`, and `runtime_kretprobe`.
2. The smallest initialized shared request shape stays explicit for the bitmap and kretprobe families.
3. The caller-provided selftest-complete request shape stays explicit across atomic64 and trace-events.
4. The selftest-complete parity between bitmap and kretprobe stays explicit even though their allocator handoffs differ.
5. Initialized prepared snapshots stay pinned even when later live state would look exited.
6. Selftest-complete prepared snapshots stay pinned even when later live state would look exited.
7. The invalid init or handoff rejection packet still covers six cases: missing init, premature selftest, exited state, duplicate init, duplicate selftest, and incomplete selftest-complete handoff.
8. The approved pilot-family drift rejection packet still covers five cases: module-name drift, anchor drift, entry-symbol drift, exit-symbol drift, and an unknown pilot family.
9. Loader-not-required handoffs are still rejected directly.
10. Selftest-hook evidence drift is still rejected for three cases: missing hook after selftest-complete, missing hook on initialized state, and selftest-runs-without-hook.
11. Prepared-plan drift still keeps the request pinned in prepared state across eight mutations: `requires_runtime_substrate`, `module_name`, `anchor`, `entry_symbol`, `exit_symbol`, `allocator_handoff`, `provides_selftest_hook`, and `init_flow.selftest_runs`.
12. Stale loader-state transitions are still rejected across four checks: release before request, duplicate request, duplicate release, and a no-loader-needed literal plan.
13. The shared build route still carries ten exact route markers for the allocator/init-flow test module, its imports, its dedicated test artifact name, and its inclusion in both `phase9-runtime-loader-shared-tests` and the shared `test` step.
14. The current manifest-backed evidence packet still reads four manifest files, confirms the four Phase 9 anchors, keeps the trace-events delivery-evidence catalog and ownership map explicit, keeps the kretprobe lifecycle-boundary summary explicit, and keeps the live enum cardinalities pinned at three allocator handoff states, two handoff stages, and three request states.

## Current Conclusion

- The shared Phase 9 allocator/init-flow packet is already substantive on `master`; the bounded gap was exact-check evidence, not missing request-shape coverage.
- The honest current next step is to keep this note and its checker aligned with the shipped replay source and the shared build route without widening into a larger runtime-substrate claim.
