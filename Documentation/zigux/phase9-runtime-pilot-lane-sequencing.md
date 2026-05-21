# Phase 9 Runtime Pilot Lane Sequencing

This note keeps the roadmap-backed Phase 9 runtime pilot lane honest when current `master` carries one shipped trace-events runtime packet, one stale shared runtime-loader reminder packet, and one partial runtime bitmap reminder packet.

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

### 2. The older shared runtime-loader allocator/init-flow packet is now stale reminder vocabulary rather than returned current-master evidence

Fresh direct contents rereads on 2026-05-21 returned missing for `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/tests/runtime_loader_allocator_init_flow.zig`, and the same run's repository file search found no surviving `runtime_loader` paths on current `master`.

- `zigux/tests/phase9_build.zig` still exposes `phase9-runtime-atomic64-diff`, `phase9-runtime-bitmap-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-first-loadable-runtime-module-parity-survey-tests`
- that build-bundle wording is therefore current route vocabulary only; it is not enough to treat the missing loader file family as returned shared-owner evidence
- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still describe the allocator/init-flow packet as current shared-owner evidence, which is the live same-family control-surface drift for this lane
- keep the Phase 8 command and environment ownership boundary explicit: deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` cues stay with `tools/lib/subcmd/exec-cmd.zig`, while `LINES` and `COLUMNS` stay with `tools/lib/subcmd/help.zig`
- current Phase 9 material still does not prove shipped runtime command or environment activation control, even though the older reminder packet continues to talk as if the shared loader file family had returned

### 3. The runtime bitmap side is still only partial

- the current reminder surfaces still keep the partial runtime bitmap packet visible through `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_module.zig` and `zigux/tests/runtime_bitmap_diff.zig` remain the same-family trusted-contents gaps already called out by the shared reminder packet
- current `master` therefore still supports only a partial runtime bitmap reminder packet, and that partial bitmap visibility must not be used to imply that the older loader packet has returned

## Current shared-owner state

The shared Phase 9 reminder family should now be read as three distinct truths:

1. the trace-events runtime packet is still the shipped direct current-`master` proof for selftest-hook and lifecycle-parity reviewability
2. the older shared runtime-loader allocator/init-flow packet currently survives only as stale reminder vocabulary across broader shared surfaces plus the `phase9-runtime-loader-shared-tests` route name in `zigux/tests/phase9_build.zig`, while the exact loader file family itself does not survive on the current trusted contents path
3. the bitmap side is still only partially materialized on trusted rereads, so it cannot be treated as proof that the loader packet returned or that the full bitmap family returned

This means the shared owner packet should keep the narrow trace-events family explicit, keep the current loader-file absence explicit, keep the partial runtime bitmap reminder packet explicit, and avoid promoting any of them into a claim that deeper publication, install-root, or loadable-runtime-complete substrate work is finished.

- `zigux/tests/phase9_build.zig` still records the bounded atomic64, bitmap, loader-shared, and cross-family parity-survey route names, but that surviving build bundle is not proof that the missing loader file family returned
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` remain the current reminder surfaces for the partial bitmap packet
- the missing bitmap module gate and diff gate stay repo-reality gaps on the same trusted path until a later reread restores them
- no shared reminder surface should present the partial bitmap packet as equal to the shipped trace-events packet or as proof that the older shared runtime-loader packet returned

## Historical boundaries

- the older wider-family loader reminder vocabulary still includes `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the `samples/zigux/runtime_*_loader.zig` scaffolds
- the 2026-05-21 direct contents reread and same-run repository file search did not return those loader-family paths, so keep them framed as stale reminder or historical blocked-boundary vocabulary until a future exact reread proves they are back on current `master`
- still preserve blocked `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, and depmod-publication vocabulary
- keep `modules.order`, `modules.builtin`, `Module.symvers`, and module install-root wording framed as blocked wider-family vocabulary too

## Governance rule for this lane

This lane may:

- refresh this note when trusted repo reality changes
- tighten one stale shared reminder surface at a time when it undercounts or overclaims the trace-events packet, the loader-file absence, the partial bitmap packet, or build-route maturity
- keep the narrow trace-events packet explicit as the current shipped runtime-pilot proof
- keep the current loader-file absence explicit without overstating route-name survival into returned shared-owner evidence
- keep the partial runtime bitmap reminder packet explicit without overstating what has actually returned
- keep the bounded `zigux/tests/phase9_build.zig` shard explicit as route vocabulary without treating it as proof that the missing loader files, blocked publication boundaries, or install-root surfaces are complete

This lane should not reopen:

- new runtime behavior based only on stale reminder wording
- checker growth when the active problem is a stale shared summary
- backlog promotion of the partial runtime bitmap reminder packet into proof that the loader packet returned
- blocked publication or install-root completion claims that the surviving route names still do not prove

Treat stale shared-owner overclaim as the active blocker before reopening checker-local or runtime-behavior work.

## Freeze boundary

- keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness

## Recommended next-step order

1. Re-read `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together, because they still overclaim the missing loader file family as returned shared-owner evidence.
2. After that, prefer one shared reminder surface at a time only after a fresh exact reread confirms the same control-surface drift still exists there.
3. If the missing loader files return later, widen this note only after an exact reread proves those paths again on current `master`.
4. If the still-missing bitmap module and diff legs return later, widen the bitmap-side reminder packet only after the trusted direct read path returns those exact files.

## Anti-overlap rule

If a scheduled run is assigned shared Phase 9 backlog or governance work, keep the run inside repo-reality rereads and one-file reminder repair. Do not treat the partial runtime bitmap reminder packet as full sample-family return, do not treat `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-pilot expansion evidence, and do not treat the surviving `phase9-runtime-loader-shared-tests` route name as proof that the older loader packet has returned.
