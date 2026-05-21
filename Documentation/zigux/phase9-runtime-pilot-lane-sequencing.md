# Phase 9 Runtime Pilot Lane Sequencing

This note keeps the roadmap-backed Phase 9 runtime pilot lane honest when current `master` carries one shipped trace-events runtime packet, one returned shared runtime-loader reminder packet with a dedicated command/environment boundary guard, and one partial runtime bitmap reminder packet.

## Roadmap anchor

Phase 9 is still the runtime pilot tranche.

- primary Linux anchors:
  - `lib/atomic64_test.c`
  - `lib/test_bitmap.c`
  - `samples/trace_events/trace-events-sample.c`
  - `samples/kprobes/kretprobe_example.c`
- required Zigux features:
  - first loadable Zigux runtime modules
  - selftest hooks
  - runtime module lifecycle parity
- recommended Zigux destinations:
  - `zigux/tests/runtime_*`
  - `samples/zigux/runtime_*`

That roadmap boundary still matters, but repo reality matters more than stale reminder wording.

## Live repo reality on current master

Trusted mixed rereads on 2026-05-21 confirm three distinct current-master Phase 9 postures.

### 1. Trace-events remains the direct shipped runtime sample family

- surviving review surfaces: `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/tests/README.md`
- surviving direct runtime-module sample: `samples/zigux/runtime_trace_events.zig`
- surviving fail-closed runtime companion: `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- surviving exit-rollback runtime companion: `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
- surviving registration-reentry runtime companion: `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
- surviving family-local survey witness: `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig`
- surviving runtime-module evidence inside that direct sample: `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking
- balanced registration re-entry replay in `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` across both the initialized and selftest_complete stages remains part of the still-shipped narrow packet

### 2. The shared runtime-loader allocator/init-flow and command/environment boundary packet remains mixed-source shared-owner evidence

Trusted GitHub rereads on 2026-05-21 still return the broader shared loader packet through `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, the `samples/zigux/runtime_*_loader.zig` scaffolds, and the bounded `zigux/tests/phase9_build.zig` shard.

- `zigux/tests/phase9_build.zig` still exposes `phase9-runtime-atomic64-diff`, `phase9-runtime-bitmap-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-first-loadable-runtime-module-parity-survey-tests`
- that build bundle is still bounded rerun vocabulary rather than proof that blocked publication, install-root, or module-metadata surfaces are solved
- `zigux/tests/phase9_build.zig` now also names `phase9-runtime-loader-command-env-boundary-guard-tests`, which keeps the shared request-contract boundary tied to the same loader shard instead of drifting into the trace-events family-local packet
- `zigux/kernel/runtime_loader_command_env_boundary_guard.zig` keeps the command/environment guard reviewable on current `master` by fail-closing when argv or environment control markers bleed into `zigux/kernel/runtime_loader.zig` or `zigux/kernel/runtime_loader_contract.zig`
- the review-first shared packet still stays neighboring shared-owner evidence through the aligned docs-root, scripts-root, and tests-root reminders, the bounded loader shard, and the direct command/environment boundary guard
- keep the Phase 8 command and environment ownership boundary explicit: deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` cues stay with `tools/lib/subcmd/exec-cmd.zig`, while `LINES` and `COLUMNS` stay with `tools/lib/subcmd/help.zig`
- current Phase 9 material still does not prove shipped runtime command or environment activation control; it proves only that the shared runtime-loader packet keeps those Phase 8 control surfaces out of the loader contract

### 3. The runtime bitmap side is still only partial

- the current reminder surfaces still keep the partial runtime bitmap packet visible through `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_module.zig` and `zigux/tests/runtime_bitmap_diff.zig` remain the same-family trusted-contents gaps already called out by the shared reminder packet
- current `master` therefore still supports only a partial runtime bitmap reminder packet, and that partial bitmap visibility must not be used to imply that the broader bitmap family or blocked publication boundaries returned

## Current shared-owner state

The shared Phase 9 reminder family should now be read as three distinct truths:

1. the trace-events runtime packet is still the shipped direct current-`master` proof for selftest-hook and lifecycle-parity reviewability
2. the older shared runtime-loader allocator/init-flow packet has returned and now keeps a dedicated command/environment boundary guard explicit, but that broader shared packet still stays neighboring shared-owner evidence instead of family-local trace-events proof
3. the bitmap side is still only partially materialized on trusted rereads, so current `master` therefore supports a partial runtime bitmap reminder packet plus the returned shared allocator/init-flow and command/environment boundary packet, not proof that the broader bitmap family returned

This means the shared owner packet should keep the narrow trace-events family explicit, keep the returned shared loader packet explicit, keep the direct command/environment boundary guard explicit, keep the partial runtime bitmap reminder packet explicit, and avoid promoting any of them into a claim that deeper publication, install-root, or loadable-runtime-complete substrate work is finished.

- `zigux/tests/phase9_build.zig` still records the bounded atomic64, bitmap, loader-shared, command/environment boundary, and cross-family parity-survey route names, but that surviving build bundle is not proof that blocked publication boundaries or install-root surfaces are complete
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` remain the current reminder surfaces for the partial bitmap packet
- the missing bitmap module gate and diff gate stay repo-reality gaps on the same trusted path until a later reread restores them
- no shared reminder surface should present the partial bitmap packet as equal to the shipped trace-events packet or as proof that every broader runtime-pilot boundary returned

## Historical boundaries

- the older wider-family loader reminder vocabulary still includes `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, and the `samples/zigux/runtime_*_loader.zig` scaffolds
- still preserve blocked `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, and depmod-publication vocabulary
- keep `modules.order`, `modules.builtin`, `Module.symvers`, and module install-root wording framed as blocked wider-family vocabulary too

## Governance rule for this lane

This lane may:

- refresh this note when trusted repo reality changes
- tighten one stale shared reminder surface at a time when it undercounts or overclaims the trace-events packet, the returned shared loader packet, the direct command/environment boundary guard, the partial bitmap packet, or build-route maturity
- keep the narrow trace-events packet explicit as the current shipped runtime-pilot proof
- keep the returned shared loader packet explicit without overstating blocked publication or install-root completion
- keep the direct command/environment boundary guard explicit without treating it as proof of shipped runtime command or environment activation control
- keep the partial runtime bitmap reminder packet explicit without overstating what has actually returned
- keep the bounded `zigux/tests/phase9_build.zig` shard explicit as route vocabulary without treating it as proof that blocked publication boundaries or install-root surfaces are complete

This lane should not reopen:

- new runtime behavior based only on stale reminder wording
- checker growth when the active problem is a stale shared summary
- backlog promotion of the partial runtime bitmap reminder packet into proof that every broader runtime boundary returned
- blocked publication or install-root completion claims that the surviving route names still do not prove

Treat stale shared-owner undercount or overclaim as the active blocker before reopening checker-local or runtime-behavior work.

## Freeze boundary

- keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness

## Recommended next-step order

1. Re-read `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together only if one of those broader shared reminders drifts away from the returned loader packet, the direct command/environment boundary guard, or the partial bitmap split.
2. After that, prefer one shared reminder surface at a time only after a fresh exact reread confirms the same control-surface drift still exists there.
3. If the broader shared runtime-loader family changes again, widen this note only after an exact reread proves the specific returned file family or blocked-boundary vocabulary moved.
4. If the still-missing bitmap module and diff legs return later, widen the bitmap-side reminder packet only after the trusted direct read path returns those exact files.

## Anti-overlap rule

If a scheduled run is assigned shared Phase 9 backlog or governance work, keep the run inside repo-reality rereads and one-file reminder repair. Do not treat the partial runtime bitmap reminder packet as full sample-family return, do not treat `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-pilot expansion evidence, and do not treat the surviving loader route names or the direct command/environment boundary guard as proof that blocked publication, install-root, or module-metadata work is complete.
