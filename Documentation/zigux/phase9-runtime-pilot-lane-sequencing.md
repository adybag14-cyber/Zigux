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

## Current shared-owner state

The newest obvious Phase 9 docs-root drift has already been retired.

- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `zigux/tests/README.md`, and the surviving `samples/zigux/runtime_trace_events.zig` packet already center the narrow trace-events selftest-hook evidence rather than the removed shared runtime-loader family
- `Documentation/zigux/README.md` has now been tightened so the docs-root Phase 9 summary matches that narrow trace-events packet instead of presenting the removed shared runtime-loader inventory as shipped current-`master` evidence
- the next honest shared Phase 9 move is to reread the remaining companion reminder surfaces one at a time and only trim another file if it still overclaims removed loader files

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

1. Re-read any remaining Phase 9 companion reminder surfaces against `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `zigux/tests/README.md`, and `samples/zigux/runtime_trace_events.zig`, then trim a file only if it still overclaims removed loader surfaces.
2. If no stale reminder remains, decide whether the next bounded step is another reminder repair elsewhere or a new direct runtime sample or tests slice.
3. If the broader shared runtime-loader packet returns later, widen this note only after an exact file reread proves it.

## Anti-overlap rule

If a scheduled run is assigned shared Phase 9 backlog or governance work, keep the run inside repo-reality rereads and one-file reminder repair. Do not reopen runtime behavior just because older notes still remember the removed shared runtime-loader packet, and do not treat absent loader, build, kernel, or sample paths as live evidence.