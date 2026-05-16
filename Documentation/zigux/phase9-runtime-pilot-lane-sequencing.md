# Phase 9 Runtime Pilot Lane Sequencing

This note keeps the roadmap-backed Phase 9 runtime pilot lane honest when current `master` carries a real shared runtime-loader packet that must stay aligned across reminder, route, build, test, kernel, and sample surfaces.

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

That roadmap boundary matters more than stale reminder wording. If live `master` still exposes the shared loader-facing packet and the bounded runtime-pilot test families, keep this note aligned with those shipped surfaces instead of downgrading the lane to backlog-only posture.

## Live repo reality on current master

Current `master` still exposes a broader shared Phase 9 runtime-loader packet.

- shared reminder and route owners: `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-build-only-surface.py`, and `zigux/Makefile`
- shared build and test packet: `zigux/tests/README.md`, `zigux/tests/phase9_build.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`, `zigux/tests/runtime_loader_lifecycle_boundary_guard.zig`, and `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`
- shared runtime-loader substrate: `zigux/kernel/runtime_loader.zig` and `zigux/kernel/runtime_loader_contract.zig`
- shared runtime-module sample packet: `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_trace_events.zig`, and `samples/zigux/runtime_kretprobe_loader.zig`

Current `master` therefore does not justify a backlog-only Phase 9 posture. The broader shared packet is still live, even if some reminder surfaces have drifted out of sync with it.

## Current shared-owner drift

The active shared-owner drift is now reminder-local, not packet-absence reality.

- this sequencing note currently undercounts the live shared Phase 9 packet by describing only a narrow reminder surface
- `zigux/tests/README.md` also still tells reviewers to treat the broader shared loader packet, the `phase9_build` bundle, and the `make -C zigux phase9*` family as absent even though the shared checklist and Makefile still ship them
- `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` and `zigux/Makefile` still assume the broader Phase 9 packet is present, which makes the backlog-only reminder posture misleading

That means the next honest shared Phase 9 move is reminder-surface truthfulness repair, not invented backlog-only framing and not fresh runtime-loader feature growth.

## Governance rule for this lane

This lane may:

- refresh `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` when current repo reality changes
- tighten one shared reminder surface at a time when it drifts away from the live tree
- keep the shared route, build, test, kernel, and sample owners explicit when they are still present on current `master`
- keep the roadmap target explicit without pretending blocked publication surfaces are already shipped

This lane should not reopen:

- new runtime behavior or sample semantics based only on reminder drift
- checker or validator growth when the real issue is a stale shared summary
- family-local survey or manifest claims that have not been reread on current `master`

## Shared reminder packet rules

1. Keep the roadmap-versus-repo relationship explicit: Phase 9 still targets runtime modules, selftest hooks, and lifecycle parity, and current `master` still exposes a meaningful shared packet toward that target through reminder, route, build, test, kernel, and sample surfaces.
2. Do not describe the still-live `phase9_build`, `phase9-test`, or shared runtime-loader packet as absent while `Documentation/zigux/review-checklist.md`, `zigux/Makefile`, and the reread Phase 9 file family still ship them.
3. Treat reminder-surface undercounts as the active blocker before reopening checker-local or runtime-behavior work.
4. Refresh one shared reminder surface at a time when the tree changes again.
5. If the broader shared packet shrinks later, reread the Makefile, tests-root guide, and shared checker before downgrading this note to backlog-only posture.

## Recommended next-step order

1. Re-read `zigux/tests/README.md` against the live Phase 9 route, build, runtime-loader, and sample surfaces and trim its backlog-only wording so it matches current `master`.
2. Re-read `samples/zigux/README.md` for the same Phase 9 undercount and keep the runtime-loader sample family explicit if the sample-root guide still drifts.
3. Only after the shared reminder packet is honest again should future Phase 9 work decide whether the next bounded step is checker hardening, one reminder surface, or one pilot runtime slice.

## Anti-overlap rule

If a scheduled run is assigned shared Phase 9 backlog or governance work, keep the run inside repo-reality rereads and one-file reminder repair. Do not reopen runtime behavior just because one shared summary has drifted, and do not replay a parked checker handoff once live `master` no longer supports its premise.
