# Phase 9 Runtime Pilot Lane Sequencing

This note keeps the roadmap-backed Phase 9 runtime pilot lane honest when current `master` carries backlog evidence instead of a broad shared runtime-loader packet.

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

That roadmap boundary matters more than older reminder wording. If live `master` does not expose the claimed shared loader-facing packet or the bounded runtime-pilot test families, treat that as repo-reality drift instead of assuming older reminder text is still authoritative.

## Live repo reality on current master

Current `master` exposes only a narrow shared Phase 9 reminder surface:

- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`
- `zigux/tests/README.md`
- `samples/zigux/runtime_trace_events.zig`

Current `master` does not currently expose the older shared Phase 9 loader-facing inventory that earlier shared notes referenced, including the broader docs-root and scripts-root reminder stack, the shared runtime-loader implementation files, the `phase9_build` bundle, the dedicated `runtime_*` manifest or survey packet, the `runtime_*_loader.zig` scaffolds, or the broader `make -C zigux phase9*` route family.

The surviving `samples/zigux/runtime_trace_events.zig` sample is not enough to treat the older shared-loader packet as still landed. Until the shared runtime-loader and `zigux/tests/runtime_*` family resurfaces on current `master`, the honest shared Phase 9 posture is backlog reality, not shipped loader-packet reviewability.

## Current backlog evidence

The active shared-owner drift is now narrower than older Phase 9 notes claimed.

- this sequencing note itself had drifted by naming a large shared loader-facing packet that current `master` no longer exposes
- `zigux/tests/README.md` still needs its own bounded Phase 9 reread so its review-packet wording matches the current tree and defers shared owner-map truth back to this note
- `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` now survives mainly as a boundary reminder and self-test surface; its repo-root validation path still expects `Documentation/zigux/review-checklist.md` and `zigux/Makefile`, so treat that checker as backlog evidence rather than proof that the broader shared reminder packet is still present

That means the next honest shared Phase 9 move is reminder repair, not new family-local pilot claims and not invented shared validation routes.

## Governance rule for this lane

This lane may:

- refresh `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` when current repo reality changes
- tighten one shared reminder surface at a time when it drifts away from the live tree
- record the missing shared Phase 9 loader-facing packet as a blocker when the tree no longer confirms the older inventory
- keep the roadmap target explicit without overstating what current `master` actually ships

This lane should not reopen:

- pilot-family implementation or sample behavior based only on old reminder text
- family-local survey, manifest, module-slice, or diff claims that current `master` does not expose
- new checker or validator growth just to compensate for missing shared reminder files

## Shared reminder packet rules

1. Keep the roadmap-versus-repo gap explicit: Phase 9 still targets `zigux/tests/runtime_*` and `samples/zigux/runtime_*`, but current `master` does not yet expose that broader packet.
2. Do not describe missing shared-loader files, missing replay routes, or missing pilot-family packet files as live evidence.
3. Treat the surviving boundary checker as a backlog signal, not as proof that the broader review-checklist and Makefile-backed packet is still landed.
4. Refresh one shared reminder surface at a time when the tree changes again.
5. If the shared runtime-loader packet resurfaces later, refresh this sequencing note before re-expanding any other shared summary.

## Recommended next-step order

1. Re-read `zigux/tests/README.md` against the current tree and trim its Phase 9 review packet back to what current `master` actually exposes, while deferring shared owner-map truth to this note.
2. If a docs-root or scripts-root Phase 9 reminder surface returns later, refresh this sequencing note first so later shared summaries inherit a truthful inventory.
3. Only after the shared reminder packet is honest again should future Phase 9 work decide whether the next bounded step is restoring one runtime-pilot sample companion, one shared reminder file, or one checker target.

## Anti-overlap rule

If a scheduled run is assigned shared Phase 9 backlog or governance work, keep the run inside repo-reality recording and one-file reminder repair. Do not consume pilot-family backlog just because older notes still name removed files or routes.
