# Phase 9 Runtime Pilot Lane Sequencing

This note keeps the roadmap-backed Phase 9 runtime pilot lane honest when current `master` carries only a narrow surviving runtime-pilot packet rather than the older shared runtime-loader family.

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

That roadmap boundary still matters, but repo reality matters more than stale reminder wording. If live `master` only keeps a narrow direct runtime packet plus a small review packet, say that plainly instead of treating the older shared runtime-loader packet as current evidence.

## Live repo reality on current master

Current `master` keeps a narrow Phase 9 runtime-pilot packet.

- surviving review surfaces: `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `zigux/tests/README.md`
- surviving direct runtime-module sample: `samples/zigux/runtime_trace_events.zig`
- surviving fail-closed runtime companion: `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- surviving exit-rollback runtime companion: `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
- surviving registration-reentry runtime companion: `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
- surviving runtime-module evidence inside that direct sample: `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking
- surviving companion boundaries inside the same narrow packet: the unregistered function-thread fail-closed replay in `samples/zigux/runtime_trace_events_unregistered_gate.zig` plus its initialized-before/after and selftest_complete-before/after summary-stability checks around those rejected function-thread calls, the failed-exit rollback replay in `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` that keeps `error.OutstandingRegistration` and later post-exit invalid-lifecycle rejections fail-closed without changing the surviving summary, and the balanced registration re-entry replay in `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` across both the initialized and selftest_complete stages, including the later selftest_complete duplicate-registration fail-closed proof that leaves the summary unchanged before the reusable replay continues

Current `master` does not currently expose the broader shared runtime-loader packet that earlier reminder surfaces described. Fresh repo-first rereads did not find `zigux/tests/phase9_build.zig`, the shared `zigux/tests/runtime_*` replay family, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, or the older `samples/zigux/runtime_*_loader.zig` scaffolds on `master`. Current `master` does materialize `zigux/Makefile` again, but its live body only exposes the rematerialized Phase 2 toolchain routes, the bounded `phase3-validate` and `phase3` routes, and the Phase 10 wrappers; it still does not provide dedicated `phase9-*` runtime-pilot handles.

## Current shared-owner state

The shared Phase 9 reminder packet is now aligned around the narrow surviving trace-events runtime packet.

- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and the surviving `samples/zigux/runtime_trace_events.zig` packet plus `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` now center the same narrow trace-events selftest-hook evidence rather than the removed shared runtime-loader family
- the same narrow packet also now keeps `samples/zigux/runtime_trace_events_unregistered_gate.zig` explicit as the fail-closed companion for the direct runtime trace-events sample, including the initialized-before/after and selftest_complete-before/after summary-stability proof around rejected function-thread calls, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` explicit as the failed-exit rollback and post-exit invalid-lifecycle companion that leaves the selftest_complete summary unchanged until the function thread unregisters and exit can complete cleanly, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` explicit as the balanced registration re-entry companion across the initialized and selftest_complete stages, including the later selftest_complete duplicate-registration fail-closed proof that leaves the summary unchanged before the reusable replay continues, instead of pretending the broader loader family returned
- no current shared reminder surface should describe `zigux/tests/phase9_build.zig`, the shared `zigux/tests/runtime_*` replay family, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, or the older `samples/zigux/runtime_*_loader.zig` scaffolds as shipped current-`master` evidence unless a fresh repo reread proves they have returned, and `zigux/Makefile` should stay framed only as a readable non-owner surface whose live body still lacks dedicated `phase9-*` runtime-pilot routes
- fresh repo-first rereads still do not directly return the older runtime bitmap packet `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, `zigux/tests/runtime_bitmap_survey.zig`, and `zigux/tests/runtime_bitmap_manifest.json`, so keep that bitmap family framed as backlog-only Phase 9 support material rather than present runtime proof or extra Phase 5 evidence until the exact file family returns on current `master`
- fresh repo-first rereads now return missing for `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, and `zigux/tests/runtime_loader_gap_survey.zig`, so the older wider-family loader-gap trio no longer survives on current `master` as a parked metadata-or-depmod vocabulary packet either; keep `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root, and depmod-publication wording framed as retired wider-family vocabulary unless those exact reminder paths return later
- the next honest shared Phase 9 move is no longer another speculative reminder rewrite; it is a fresh repo-first reread if one of the surviving shared reminder surfaces or the surviving direct trace-events sample family changes again

## Governance rule for this lane

This lane may:

- refresh `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` when current repo reality changes
- tighten one stale reminder surface at a time when it overclaims removed runtime-loader, build, kernel, or sample owners
- keep the surviving trace-events runtime sample explicit as real Phase 9 selftest-hook and lifecycle evidence
- keep `samples/zigux/runtime_trace_events_unregistered_gate.zig` explicit as the same packet's fail-closed companion, including the initialized-before/after and selftest_complete-before/after summary-stability proof around rejected function-thread calls
- keep `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` explicit as the same packet's failed-exit rollback and post-exit invalid-lifecycle companion while exit still has to preserve the selftest_complete summary before the registration depth returns to zero
- keep `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` explicit as the same packet's balanced registration re-entry companion across the initialized and selftest_complete stages, including the later selftest_complete duplicate-registration fail-closed proof that leaves the summary unchanged before the reusable replay continues
- keep the shipped `scripts/zigux/check-phase9-trace-events-runtime-packet.py` guard explicit as part of the narrow current review packet
- keep the roadmap target explicit without pretending the broader shared runtime-loader family is still shipped
- keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness

This lane should not reopen:

- new runtime behavior or sample semantics based only on stale reminder wording
- checker or validator growth when the real issue is a stale shared summary
- backlog promotion of removed `phase9_build`, shared runtime-loader, or multi-sample runtime packet surfaces without a fresh repo reread that proves they have returned
- `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-pilot follow-up targets, implied bridge candidates, or evidence that the surviving trace-events packet has crossed the freeze-map study boundary

## Shared reminder packet rules

1. Keep the roadmap-versus-repo relationship explicit: Phase 9 still targets runtime modules, selftest hooks, and lifecycle parity, but current `master` now shows only a narrow surviving trace-events packet rather than the older shared runtime-loader family.
2. Keep the shipped `scripts/zigux/check-phase9-trace-events-runtime-packet.py` guard visible whenever this note names the surviving direct runtime sample packet.
3. Keep `samples/zigux/runtime_trace_events_unregistered_gate.zig` visible as the same narrow packet's fail-closed companion whenever this note summarizes the currently shipped runtime sample family, and keep its initialized-before/after and selftest_complete-before/after summary-stability proof explicit too.
4. Keep `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` visible as the same narrow packet's failed-exit rollback and post-exit invalid-lifecycle companion whenever this note summarizes the currently shipped runtime sample family, and keep the unchanged selftest_complete summary before clean exit explicit too.
5. Keep `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` visible as the same narrow packet's balanced registration re-entry companion whenever this note summarizes the currently shipped runtime sample family, and keep its initialized-stage reuse plus the selftest_complete duplicate-registration fail-closed proof explicit too.
6. Do not describe `zigux/tests/phase9_build.zig`, shared `zigux/tests/runtime_*` replays, shared runtime-loader kernel files, or the older `samples/zigux/runtime_*_loader.zig` scaffolds as shipped evidence unless a fresh repo reread proves they have returned; keep `zigux/Makefile` explicit only as a readable non-owner surface whose live body still lacks dedicated `phase9-*` routes.
7. Treat the older runtime bitmap packet as backlog-only support material until a fresh repo reread proves the exact file family returned; do not let those historical bitmap names become present runtime proof or extra Phase 5 evidence by implication.
8. Treat the removed `phase9-runtime-loader-gap-survey` note plus the missing `runtime_loader_gap_*` survey companions as retired wider-family metadata and depmod vocabulary, not as current shared-owner proof for the surviving narrow packet; only restore those references after a fresh repo reread proves the exact paths returned.
9. Treat stale reminder overclaim as the active blocker before reopening checker-local or runtime-behavior work.
10. Keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` framed as freeze-map study-only anchors, and route that shared anchor inventory back through `Documentation/zigux/phase15-study-only-anchor-accounting.md`, instead of letting the surviving runtime-pilot packet imply deeper runtime-substrate or bridge readiness across those boundaries.
11. Refresh one shared reminder surface at a time when the tree changes again.
12. If the broader shared runtime-loader packet returns later, reread the exact file family before widening this note back out.

## Recommended next-step order

1. Re-read `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, and `zigux/Makefile` before touching the shared reminder packet again.
2. If one of those surviving surfaces drifts, trim only the smallest one-file reminder surface that overclaims removed loader evidence or drops the narrow trace-events checker-backed packet.
3. If those surviving shared reminders stay aligned, leave this shared Phase 9 reminder family parked and do not widen into runtime behavior or absent loader, build, kernel, or sample surfaces.
4. If the broader shared runtime-loader packet returns later, widen this note only after an exact file reread proves it.

## Anti-overlap rule

If a scheduled run is assigned shared Phase 9 backlog or governance work, keep the run inside repo-reality rereads and one-file reminder repair. Do not reopen runtime behavior just because older notes still remember the removed shared runtime-loader packet, do not treat `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-pilot expansion evidence, and do not treat absent loader, build, kernel, or sample paths as live evidence.