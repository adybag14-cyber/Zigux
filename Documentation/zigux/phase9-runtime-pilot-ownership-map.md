# Phase 9 Runtime Pilot Ownership Map

This note keeps the shared Phase 9 delivery packet explicit without widening current `master` evidence into blocked publication, depmod bridge, install-root, or module-metadata closure claims.

## Status

- `PHASE9_RUNTIME_PILOT_MANIFEST=zigux/tests/runtime_pilot_manifest.json`
- `PHASE9_RUNTIME_PILOT_CATALOG=scripts/zigux/phase9_catalog.py`
- `PHASE9_RUNTIME_PILOT_CATALOG_SELFTEST=scripts/zigux/check-phase9-catalog-selftest.py`
- `PHASE9_RUNTIME_PILOT_VALIDATOR=scripts/zigux/validate-phase9.py`
- `PHASE9_RUNTIME_PILOT_SCRIPTS_ROOT=scripts/zigux/README.md`
- `PHASE9_RUNTIME_PILOT_SHARED_NOTE=Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `PHASE9_RUNTIME_PILOT_SHARED_BUILD=zigux/tests/phase9_build.zig`
- `PHASE9_RUNTIME_PILOT_BLOCKED_PUBLICATION_OWNER=Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`
- `PHASE9_RUNTIME_PILOT_BLOCKED_DEPMOD_BRIDGE_SURVEY=Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`

## Shared Owner Packet

These files describe the shared reminder, review, rerun, and validation surfaces for the whole Phase 9 runtime pilot lane:

- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/phase9-runtime-pilot-ownership-map.md`
- `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/phase9_catalog.py`
- `scripts/zigux/check-phase9-catalog-selftest.py`
- `scripts/zigux/validate-phase9.py`
- `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`
- `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`
- `zigux/tests/runtime_pilot_manifest.json`
- `zigux/tests/README.md`
- `zigux/tests/phase9_build.zig`

## Blocked Publication Boundary Owner

These reminder surfaces own the blocked module-metadata, depmod bridge, and install-root boundary only:

- `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`
- blocked `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, depmod, install-root, `modules.order`, `modules.builtin`, and `Module.symvers` publication claims

Keep this packet reminder-only. It does not promote blocked publication, depmod bridge, or install-root vocabulary into shared runtime-loader closure or family-local runtime completion claims.

## Shared Runtime Loader Owner

These files remain shared-owner evidence for allocator/init-flow and command/environment boundary work only:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- bounded `phase9-runtime-loader-allocator-init-flow-tests`
- bounded `phase9-runtime-loader-shared-tests`
- bounded `phase9-runtime-loader-command-env-boundary-guard-tests`
- bounded `phase9-runtime-trace-events-loader-substrate-drift-tests`

Keep this packet shared-owner and metadata-only. It does not prove live runtime registration, blocked publication, depmod bridge, or install-root closure.

## Runtime Atomic64 Family Owner

These files are the direct atomic64 runtime pilot packet and should stay atomic64-local:

- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_manifest.json`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- bounded `phase9-runtime-atomic64-tests`

Keep this packet framed as the first-loadable atomic64 pilot rooted in `lib/atomic64_test.c`. It does not prove broader shared runtime-loader closure, blocked publication, depmod bridge, or install-root completion.

## Trace Events Family Owner

These files are the shipped direct runtime pilot packet for the trace-events family:

- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
- `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
- `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`
- `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`
- `zigux/tests/runtime_trace_events_manifest.json`
- `zigux/tests/runtime_trace_events_survey.zig`
- `zigux/tests/runtime_trace_events_module.zig`
- `scripts/zigux/check-phase9-trace-events-runtime-packet.py`
- `scripts/zigux/check-phase9-trace-events-direct-summary.py`
- `scripts/zigux/check-phase9-trace-events-summary-preservation.py`

## Runtime Bitmap Family Owner

These files are the bounded bitmap-side reminder packet and should stay bitmap-local:

- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_direct_init_contract.zig`
- `samples/zigux/runtime_bitmap_cold_stage_guard.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_manifest.json`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`

## Runtime Kretprobe Family Owner

These files are the returned family-local kretprobe packet and should not be promoted into shared-loader closure:

- `samples/zigux/runtime_kretprobe.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`
- `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`
- `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`
- `samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig`
- `zigux/tests/runtime_kretprobe_survey.zig`
- `zigux/tests/runtime_kretprobe_module.zig`
- `zigux/tests/runtime_first_loadable_parity_behavior.zig`
- `scripts/zigux/check-phase9-kretprobe-runtime-packet.py`
- bounded `phase9-runtime-kretprobe-sample-tests`
- bounded `phase9-runtime-kretprobe-loader-tests`
- bounded `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`
- bounded `phase9-runtime-kretprobe-registration-reentry-gate-tests`
- bounded `phase9-runtime-kretprobe-reinit-reexit-guard-tests`
- bounded `phase9-runtime-kretprobe-survey-tests`
- bounded `phase9-runtime-kretprobe-module-tests`
- bounded `phase9-runtime-kretprobe-tests`
- bounded `phase9-first-loadable-runtime-module-parity-behavior-tests`

Keep these rerun handles family-local too: they make the returned kretprobe packet reviewable on current `master`, but they still do not prove broader shared runtime-loader closure, blocked publication, depmod bridge, or install-root completion.

## Historical Wider-Family Vocabulary

Keep these names historical until trusted rereads return them:

- `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
- `zigux/tests/runtime_loader_gap_manifest.json`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- blocked `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, depmod, install-root, `modules.order`, `modules.builtin`, and `Module.symvers` publication claims

Use `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md` as the current reminder surface for that blocked publication and depmod bridge boundary instead of treating the historical names above as active owner paths.

## Governance Rule

When this ownership map and the shared manifest disagree with a family-local reminder surface, tighten the summary surface first. Do not widen runtime behavior or blocked publication, depmod bridge, or install-root claims just because a bounded family packet is directly readable on current `master`.
