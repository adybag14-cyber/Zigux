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

That roadmap boundary still matters, but repo reality matters more than stale reminder wording. If live `master` only keeps one direct runtime sample plus a small review packet, say that plainly instead of treating the older shared runtime-loader packet as current evidence.

## Live repo reality on current master

Current `master` keeps a narrow Phase 9 runtime-pilot packet.

- surviving review surfaces: `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `zigux/tests/README.md`
- surviving direct runtime-module sample: `samples/zigux/runtime_trace_events.zig`
- surviving runtime-module evidence inside that sample: `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking

Current `master` does not currently expose the broader shared runtime-loader packet that earlier reminder surfaces described. Fresh repo-first rereads did not find `zigux/tests/phase9_build.zig`, the shared `zigux/tests/runtime_*` replay family, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/Makefile`, or the older `samples/zigux/runtime_*_loader.zig` scaffolds on `master`.

## Current shared-owner state

The shared Phase 9 reminder packet is now aligned around the narrow surviving trace-events evidence.

- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `zigux/tests/README.md`, and the surviving `samples/zigux/runtime_trace_events.zig` packet all now center the same narrow trace-events selftest-hook evidence rather than the removed shared runtime-loader family
- no current shared reminder surface should describe `zigux/tests/phase9_build.zig`, the shared `zigux/tests/runtime_*` replay family, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/Makefile`, or the older `samples/zigux/runtime_*_loader.zig` scaffolds as shipped current-`master` evidence unless a fresh repo reread proves they have returned
- the next honest shared Phase 9 move is no longer another speculative reminder rewrite; it is a fresh repo-first reread if one of the surviving shared reminder surfaces or the surviving direct trace-events sample changes again

## Governance rule for this lane

This lane may:

- refresh `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` when current repo reality changes
- tighten one stale reminder surface at a time when it overclaims removed runtime-loader, build, kernel, or sample owners
- keep the surviving trace-events runtime sample explicit as real Phase 9 selftest-hook and lifecycle evidence
- keep the shipped `scripts/zigux/check-phase9-trace-events-runtime-packet.py` guard explicit as part of the narrow current review packet
- keep the roadmap target explicit without pretending the broader shared runtime-loader family is still shipped

This lane should not reopen:

- new runtime behavior or sample semantics based only on stale reminder wording
- checker or validator growth when the real issue is a stale shared summary
- backlog promotion of removed `phase9_build`, shared runtime-loader, or multi-sample runtime packet surfaces without a fresh repo reread that proves they have returned

## Shared reminder packet rules

1. Keep the roadmap-versus-repo relationship explicit: Phase 9 still targets runtime modules, selftest hooks, and lifecycle parity, but current `master` now shows only a narrow surviving trace-events packet rather than the older shared runtime-loader family.
2. Keep the shipped `scripts/zigux/check-phase9-trace-events-runtime-packet.py` guard visible whenever this note names the surviving direct runtime sample packet.
3. Do not describe `zigux/tests/phase9_build.zig`, shared `zigux/tests/runtime_*` replays, shared runtime-loader kernel files, `zigux/Makefile`, or the older `samples/zigux/runtime_*_loader.zig` scaffolds as shipped evidence unless a fresh repo reread proves they have returned.
4. Treat stale reminder overclaim as the active blocker before reopening checker-local or runtime-behavior work.
5. Refresh one shared reminder surface at a time when the tree changes again.
6. If the broader shared runtime-loader packet returns later, reread the exact file family before widening this note back out.

## Recommended next-step order

1. Re-read `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `samples/zigux/runtime_trace_events.zig` before touching the shared reminder packet again.
2. If one of those surviving surfaces drifts, trim only the smallest one-file reminder surface that overclaims removed loader evidence or drops the narrow trace-events checker-backed packet.
3. If those surviving shared reminders stay aligned, leave this shared Phase 9 reminder family parked and do not widen into runtime behavior or absent loader, build, kernel, or sample surfaces.
4. If the broader shared runtime-loader packet returns later, widen this note only after an exact file reread proves it.

## Anti-overlap rule

If a scheduled run is assigned shared Phase 9 backlog or governance work, keep the run inside repo-reality rereads and one-file reminder repair. Do not reopen runtime behavior just because older notes still remember the removed shared runtime-loader packet, and do not treat absent loader, build, kernel, or sample paths as live evidence.