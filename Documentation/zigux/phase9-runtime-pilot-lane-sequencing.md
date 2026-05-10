# Phase 9 Runtime Pilot Lane Sequencing

This note keeps the roadmap-backed Phase 9 runtime pilot lane honest when the repo is between survey refreshes, shared-loader repairs, and pilot-family follow-up.

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

That roadmap boundary matters more than older reminder wording. If live `master` no longer exposes a claimed shared loader surface or pilot-family packet, treat the missing file family as a release-discipline blocker instead of assuming the older reminder packet is still authoritative.

## Live repo reality on current master

This survey could still read these shared reminder surfaces:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

This survey could not read the shared loader-facing file family through the live contents tree:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `scripts/zigux/check-phase9-build-only-surface.py`
- `zigux/tests/phase9_build.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`

This survey also could not read the broad Phase 9 pilot-family survey packet that older reminder text still describes:

- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-trace-events-survey.md`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `samples/zigux/runtime_trace_events.zig`

This survey could still read `Documentation/zigux/phase9-runtime-kretprobe-survey.md`, but that remaining note still talks about the missing shared loader packet as if it were shipped current-`master` evidence. Treat that note as one pilot-family reminder that now also needs a future truthfulness pass; do not use it as substitute proof that the shared loader lane is present.

## Governance rule for this lane

Lane `P9-L01` owns shared reminder truthfulness for the broad Phase 9 review packet.

That means this lane may:

- tighten shared reminder wording in `Documentation/zigux/README.md`
- tighten shared reminder wording in `Documentation/zigux/review-checklist.md`
- tighten shared reminder wording in `scripts/zigux/README.md`
- tighten shared reminder wording in `zigux/tests/README.md`
- refresh this sequencing note when repo reality changes

That does not mean this lane should reopen:

- pilot-family sample or module behavior
- pilot-family manifest or diff logic
- family-local survey wording that belongs to a separate owner lane, except to record that the file is currently missing or stale as shared reminder evidence
- new checker or validator growth just to compensate for missing shared Phase 9 files

## Shared reminder packet rules

When a shared Phase 9 review surface is touched, it must follow these rules.

1. Do not describe the shared runtime-loader lane as shipped evidence unless the shared loader-facing files are readable on current `master`.
2. Do not borrow a surviving pilot-family note as proof that the shared loader lane is healthy.
3. Keep the roadmap boundary explicit: Phase 9 still aims at `zigux/tests/runtime_*` and `samples/zigux/runtime_*`, but current `master` can fall short of that target and the reminder packet must say so plainly.
4. Keep the no-dedicated-`validate-phase9.py` posture explicit without replacing it with invented shared gates.
5. Keep earlier-phase references in their own buckets:
   - `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 references
   - `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 references
   - `tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig` remain earlier-phase command and environment cue owners
6. If the shared loader-facing family is missing, shared reminder surfaces should record a blocker or narrow their claims. They should not continue to talk about build steps, loader scaffolds, allocator/init-flow replay, or checker-backed routes as though those files are live.

## Adjacent lane boundaries

Use this split to avoid overlap.

- `P9-L01`: shared reminder and release-discipline truthfulness for the broad Phase 9 packet
- adjacent pilot-family lanes: family-local sample, module, survey, manifest, or diff upkeep when those files actually exist on `master`
- shared loader implementation or checker work: only after the missing shared loader-facing family is restored and can be inspected directly again

If a nearby lane is working inside a surviving family-local packet, this lane should stay on reminder truthfulness and blocker recording only.

## Recommended next-step order

1. Decide whether the missing shared loader-facing file family is meant to be restored on `master` or whether the broad reminder packet should be narrowed permanently.
2. Until that decision is made, treat `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and the surviving `Documentation/zigux/phase9-runtime-kretprobe-survey.md` reminder as overclaim-prone surfaces rather than as proof of a shipped shared Phase 9 route.
3. If the missing shared loader-facing file family is intentionally gone, narrow the shared reminder surfaces one file at a time so they stop naming those missing files and routes as shipped evidence.
4. If the missing shared loader-facing file family is being restored, re-establish the smallest honest shared file first, then reopen the reminder surfaces after live current-`master` readback confirms the route.
5. Only after the shared reminder packet is truthful again should any family-local survey note be refreshed to describe shared loader adjacency.

## Anti-overlap rule

If a scheduled run is assigned Phase 9 shared-governance work, keep the run inside shared reminder truthfulness, repo-reality recording, and next-step narrowing. Do not consume pilot-family backlog just because those local files used to exist in older reminder text.