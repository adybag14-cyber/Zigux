# Phase 9 Runtime Pilot Lane Sequencing

This note keeps the roadmap-backed Phase 9 runtime pilot lane honest when current `master` carries one shipped trace-events runtime packet, a mixed-source shared runtime-loader allocator/init-flow packet, and a partial runtime bitmap reminder packet.

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

Trusted mixed rereads on 2026-05-20 confirm three distinct current-master Phase 9 packets.

### 1. Trace-events remains the direct shipped runtime sample family

- surviving review surfaces: `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/tests/README.md`
- surviving direct runtime-module sample: `samples/zigux/runtime_trace_events.zig`
- surviving fail-closed runtime companion: `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- surviving exit-rollback runtime companion: `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
- surviving registration-reentry runtime companion: `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
- surviving family-local survey witness: `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig`
- surviving runtime-module evidence inside that direct sample: `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking
- balanced registration re-entry replay in `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` across both the initialized and selftest_complete stages remains part of the still-shipped narrow packet

### 2. The shared runtime-loader allocator/init-flow packet has returned

Fresh mixed reread now shows the allocator/init-flow packet is back on current `master`, even though the exact authenticated contents-read path still flakes on some of the deeper loader files in this runtime.

- direct build-bundle proof: `zigux/tests/phase9_build.zig` now names `runtime_loader_allocator_init_flow.zig` through the dedicated `phase9-runtime-loader-allocator-init-flow-tests` test and keeps that replay inside the shared `phase9-runtime-bitmap-tests` bundle
- direct shared-reminder proof: `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` all keep the allocator/init-flow packet explicit again instead of leaving it as purely historical vocabulary
- direct sample-root proof is still mixed: authenticated reads keep the current sample-root roster narrower, but public-tree fallback rereads do return the four loader scaffolds `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_trace_events_loader.zig`, and `samples/zigux/runtime_kretprobe_loader.zig`
- public-tree fallback also returns the deeper shared loader surfaces `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/runtime_loader_gap_survey.zig`, and `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
- `scripts/zigux/check-phase9-build-only-surface.py` is part of the current shared packet and already guards the review-first allocator/init-flow bundle rather than a removed wider-family reminder

That means the truthful shared-owner posture is no longer “the broader runtime-loader packet is absent.” The truthful posture is narrower and more useful: the review-first allocator/init-flow packet has returned, but deeper loadable-runtime publication and module-install-root completion still remain blocked.

### 3. The runtime bitmap side is still only partial

- direct authenticated reads do materialize `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- the same trusted read path still returns missing for `samples/zigux/runtime_bitmap_loader.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json`
- current `master` therefore supports a partial runtime bitmap reminder packet plus the returned shared allocator/init-flow packet; the bitmap-side gaps should not be used to deny the allocator/init-flow packet that has already returned through the shared loader surfaces

## Current shared-owner state

The shared Phase 9 reminder family should now be read as three distinct truths:

1. the trace-events runtime packet is still the shipped direct current-`master` proof for selftest-hook and lifecycle-parity reviewability
2. the shared runtime-loader allocator/init-flow packet has returned through a mixed direct-read plus public-tree-fallback packet and should be treated as current shared-owner evidence again
3. the bitmap side is still only partially materialized on trusted direct rereads, so it cannot be treated as proof that the full bitmap family returned

This means the shared owner packet should keep the narrow trace-events family explicit, keep the returned allocator/init-flow packet explicit, keep the partial runtime bitmap reminder packet explicit, and avoid promoting any of them into a claim that deeper publication, install-root, or loadable-runtime-complete substrate work is finished.

- `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/phase9_build.zig`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds are the current allocator/init-flow packet evidence surfaces
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` remain the current trusted bitmap-side evidence surfaces
- the missing bitmap loader, module gate, diff gate, and manifest stay repo-reality gaps on the same trusted path until a later reread restores them
- no shared reminder surface should present the partial bitmap packet as equal to the shipped trace-events packet or as proof that all runtime publication boundaries are now complete

## Historical boundaries

- the older wider-family reminder-survey trio `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, and `zigux/tests/runtime_loader_gap_survey.zig`
- still preserve blocked `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, and depmod-publication vocabulary
- keep `modules.order`, `modules.builtin`, and module install-root wording framed as blocked wider-family vocabulary too even though the review-first allocator/init-flow packet itself has returned
- they now count again as current shared-owner evidence for the returned allocator/init-flow packet, but not as proof that those deeper blocked publication surfaces are solved

## Governance rule for this lane

This lane may:

- refresh this note when trusted repo reality changes
- tighten one stale shared reminder surface at a time when it undercounts or overclaims the allocator/init-flow packet, bitmap-family return, or build-route maturity
- keep the narrow trace-events packet explicit as the current shipped runtime-pilot proof
- keep the returned allocator/init-flow packet explicit without overstating blocked publication or substrate completion
- keep the partial runtime bitmap reminder packet explicit without overstating what has actually returned
- keep the bounded `zigux/tests/phase9_build.zig` bundle explicit without treating it as proof that every deeper runtime-publication surface is complete

This lane should not reopen:

- new runtime behavior based only on stale reminder wording
- checker growth when the active problem is a stale shared summary
- backlog promotion of the partial bitmap reminder packet into proof that the deeper bitmap family returned
- blocked publication or install-root completion claims that the returned allocator/init-flow packet still does not prove

Treat stale shared-owner undercount or overclaim as the active blocker before reopening checker-local or runtime-behavior work.

## Freeze boundary

- keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness

## Recommended next-step order

1. Re-read the smallest shared reminder surfaces that still deny the returned allocator/init-flow packet and trim one stale undercount at a time.
2. Prefer `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, or another single shared reminder surface only after a fresh exact reread confirms the same mixed-source packet shape.
3. If the still-missing bitmap loader, module, diff, and manifest legs return later, widen the bitmap-side reminder packet only after the trusted direct read path returns those exact files.
4. If the blocked publication or install-root surfaces return later, widen this note only after an exact reread proves those deeper loader-family files too.

## Anti-overlap rule

If a scheduled run is assigned shared Phase 9 backlog or governance work, keep the run inside repo-reality rereads and one-file reminder repair. Do not treat the partial runtime bitmap reminder packet as full sample-family return, do not treat `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-pilot expansion evidence, and do not treat the returned allocator/init-flow packet as proof that the blocked publication surfaces are solved.