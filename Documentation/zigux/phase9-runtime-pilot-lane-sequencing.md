# Phase 9 Runtime Pilot Lane Sequencing

This note keeps the roadmap-backed Phase 9 runtime pilot lane honest when current `master` carries one shipped trace-events runtime packet, a partial runtime bitmap reminder packet with restored direct sample proof, and a bounded shared build bundle instead of the older shared runtime-loader family.

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

Trusted current-tree rereads on 2026-05-20 confirm the narrow trace-events packet is still the direct shipped Phase 9 runtime sample family.

- surviving review surfaces: `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/tests/README.md`
- surviving direct runtime-module sample: `samples/zigux/runtime_trace_events.zig`
- surviving fail-closed runtime companion: `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- surviving exit-rollback runtime companion: `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
- surviving registration-reentry runtime companion: `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
- surviving family-local survey witness: `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig`
- surviving runtime-module evidence inside that direct sample: `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking
- balanced registration re-entry replay in `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` across both the initialized and selftest_complete stages remains part of the still-shipped narrow packet

The runtime bitmap side is narrower than older shared reminders claimed.

- direct authenticated reads do materialize `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- the same trusted read path still returns missing for `samples/zigux/runtime_bitmap_loader.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json`
- current `master` therefore supports a partial runtime bitmap reminder packet plus a bounded build bundle, not a fully returned bitmap sample family; the direct sample and top-bit companion have returned, but the loader, module, diff, and manifest legs are still absent on the same trusted path

Current `master` does not currently expose the broader shared runtime-loader packet. Keep `zigux/tests/phase9_build.zig` explicit only as a bounded shared Phase 9 build bundle. Its live body still names adjacent bitmap paths plus `zigux/tests/runtime_atomic64_diff.zig`, while `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the older `samples/zigux/runtime_*_loader.zig` scaffolds remain backlog references unless a fresh trusted reread proves they returned.

## Current shared-owner state

The shared Phase 9 reminder family should now be read as two distinct truths:

1. the trace-events runtime packet is still the shipped direct current-`master` proof for selftest-hook and lifecycle-parity reviewability
2. the bitmap side is only partially materialized on trusted direct rereads, so it cannot be treated as proof that the broader shared runtime-loader family returned

This means the shared owner packet should keep the narrow trace-events family explicit, keep the partial runtime bitmap reminder packet explicit, and avoid promoting either one into a claim that the deeper loader substrate returned.

- `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` are the current trusted bitmap-side evidence surfaces
- the missing bitmap loader, module gate, diff gate, and manifest stay repo-reality gaps on the same trusted path until a later reread restores them
- no shared reminder surface should present the partial bitmap packet as equal to the shipped trace-events packet or as proof that a loadable runtime substrate is present

## Historical boundaries

- the older wider-family reminder-survey trio `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, and `zigux/tests/runtime_loader_gap_survey.zig`
- may still preserve blocked `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, and depmod-publication vocabulary
- keep `modules.order`, `modules.builtin`, and module install-root wording framed as retired wider-family vocabulary too unless those exact reminder paths return later
- they no longer count as current shared-owner evidence for this narrow packet unless a fresh repo reread proves the broader loader family returned

## Governance rule for this lane

This lane may:

- refresh this note when trusted repo reality changes
- tighten one stale shared reminder surface at a time when it overclaims bitmap-family return, loader-substrate return, or build-route maturity
- keep the narrow trace-events packet explicit as the current shipped runtime-pilot proof
- keep the partial runtime bitmap reminder packet explicit without overstating what has actually returned
- keep the bounded `zigux/tests/phase9_build.zig` bundle explicit without treating it as proof that the broader shared runtime-loader family returned

This lane should not reopen:

- new runtime behavior based only on stale reminder wording
- checker growth when the active problem is a stale shared summary
- backlog promotion of the partial bitmap reminder packet into proof that the broader shared runtime-loader family returned

Treat stale reminder overclaim as the active blocker before reopening checker-local or runtime-behavior work.

## Freeze boundary

- keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness

## Recommended next-step order

1. Re-read the shared reminder surfaces that still mention the runtime bitmap family and trim the smallest one-file overclaim next.
2. Prefer `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, or another single shared reminder surface only after a fresh exact reread confirms the same partial return shape.
3. If the still-missing bitmap loader, module, diff, and manifest legs return later, widen the reminder packet only after the trusted direct read path returns those exact files.
4. If the broader shared runtime-loader packet returns later, widen this note only after an exact file reread proves it.

## Anti-overlap rule

If a scheduled run is assigned shared Phase 9 backlog or governance work, keep the run inside repo-reality rereads and one-file reminder repair. Do not treat the partial runtime bitmap reminder packet as full sample-family return, do not treat `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-pilot expansion evidence, and do not treat absent loader, kernel, or sample paths as live evidence.