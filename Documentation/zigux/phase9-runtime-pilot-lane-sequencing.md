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

- surviving review surfaces: `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, and `zigux/tests/README.md`
- surviving direct runtime-module sample: `samples/zigux/runtime_trace_events.zig`
- surviving runtime-module evidence inside that sample: `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking

Current `master` does not currently expose the broader shared runtime-loader packet that earlier reminder surfaces described. Fresh repo-first rereads did not find `zigux/tests/phase9_build.zig`, the shared `zigux/tests/runtime_*` replay family, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/Makefile`, or the older `samples/zigux/runtime_*_loader.zig` scaffolds on `master`.

## Current shared-owner drift

The active Phase 9 drift is now reminder-local overclaim, not a missing reread of a still-live shared loader packet.

- this sequencing note currently overstates the live Phase 9 packet by treating removed shared loader, build, kernel, and sample surfaces as present
- `Documentation/zigux/review-checklist.md` still carries the same older shared runtime-loader inventory even though the surviving tree has narrowed
- `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` and `zigux/tests/README.md` are already centered on the surviving trace-events selftest-hook packet rather than the removed shared runtime-loader family

That means the next honest shared Phase 9 move is to narrow stale reminder surfaces until they match the surviving trace-events sample packet, not to invent broader runtime-loader continuity that the live tree no longer exposes.

## Governance rule for this lane

This lane may:

- refresh `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` when current repo reality changes
- tighten one stale reminder surface at a time when it overclaims removed runtime-loader, build, kernel, or sample owners
- keep the surviving trace-events runtime sample explicit as real Phase 9 selftest-hook and lifecycle evidence
- keep the roadmap target explicit without pretending the broader shared runtime-loader family is still shipped

This lane should not reopen:

- new runtime behavior or sample semantics based only on stale reminder wording
- checker or validator growth when the real issue is a stale shared summary
- backlog promotion of removed `phase9_build`, shared runtime-loader, or multi-sample runtime packet surfaces without a fresh repo reread that proves they have returned

## Shared reminder packet rules

1. Keep the roadmap-versus-repo relationship explicit: Phase 9 still targets runtime modules, selftest hooks, and lifecycle parity, but current `master` now shows only a narrow surviving trace-events packet rather than the older shared runtime-loader family.
2. Do not describe `zigux/tests/phase9_build.zig`, shared `zigux/tests/runtime_*` replays, shared runtime-loader kernel files, `zigux/Makefile`, or the older `samples/zigux/runtime_*_loader.zig` scaffolds as shipped evidence unless a fresh repo reread proves they have returned.
3. Treat stale reminder overclaim as the active blocker before reopening checker-local or runtime-behavior work.
4. Refresh one shared reminder surface at a time when the tree changes again.
5. If the broader shared runtime-loader packet returns later, reread the exact file family before widening this note back out.

## Recommended next-step order

1. Re-read `Documentation/zigux/review-checklist.md` against `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `zigux/tests/README.md`, and `samples/zigux/runtime_trace_events.zig`, then trim the stale shared runtime-loader wording so the checklist matches the surviving trace-events packet.
2. After that reminder surface is honest, decide whether the checker should stay trace-events-only or whether another small Phase 9 reminder surface still overclaims removed loader files.
3. Only after the Phase 9 reminder packet is honest again should future runs decide whether the next bounded step is another reminder repair or a new direct runtime sample/tests slice.

## Anti-overlap rule

If a scheduled run is assigned shared Phase 9 backlog or governance work, keep the run inside repo-reality rereads and one-file reminder repair. Do not reopen runtime behavior just because older notes still remember the removed shared runtime-loader packet, and do not treat absent loader, build, kernel, or sample paths as live evidence.