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

This survey can read these shared reminder surfaces:

- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

Current `master` readback now confirms the shared loader-facing family through direct file readback plus the adjacent shared reminder inventory:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `scripts/zigux/check-phase9-build-only-surface.py`
- `zigux/tests/phase9_build.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`

This survey can also read the broad Phase 9 pilot-family review packet on current `master`:

- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-trace-events-survey.md`
- `Documentation/zigux/phase9-runtime-kretprobe-survey.md`

That means the shared Phase 9 reviewability packet should keep the loader-facing family explicit as live current-`master` review evidence, while still keeping the loadable-runtime-substrate blocker explicit and keeping pilot-family notes separate from shared-loader proof.

## Current backlog evidence

Current `master` now exposes one concrete shared-governance result for this sequencing lane.

- direct current-`master` file readback confirms the shared loader-facing family instead of the older missing-family blocker wording
- this sequencing note should therefore stay the owner of the exact shared-loader inventory, convenience-target names, and blocker posture for the surrounding shared reminder packet
- future same-lane follow-through should narrow only a shared reminder surface that drifts away from that confirmed packet, one file at a time

Because this note is the shared owner map rather than a pilot-family packet, the next safe Phase 9 follow-through remains a one-file reminder-surface truthfulness repair only if later current-`master` readback shows that surface falling behind the confirmed loader-facing packet.

## Governance rule for this lane

Shared Phase 9 reminder truthfulness is split across the active shared reminder lanes instead of being parked on one broad pilot-family lane.

That means this lane may:

- tighten shared reminder wording in `Documentation/zigux/review-checklist.md`
- tighten shared reminder wording in `scripts/zigux/README.md`
- tighten shared reminder wording in `zigux/tests/README.md`
- refresh this sequencing note when repo reality changes
- record a shared loader-facing blocker only when current-`master` readback stops confirming the live packet
- narrow one shared reminder overclaim or stale missing-file claim at a time when the sequencing note is already the strongest current-`master` source of truth

That does not mean this lane should reopen:

- pilot-family sample or module behavior
- pilot-family manifest or diff logic
- family-local survey wording that belongs to a separate owner lane, except to record that shared reminder wording has drifted from live current-`master` evidence
- new checker or validator growth just to compensate for reminder wording drift

## Shared reminder packet rules

When a shared Phase 9 review surface is touched, it must follow these rules.

1. Do not describe the shared runtime-loader lane as loadable-runtime evidence; keep it explicit that the shared loader family is a review-only handoff packet until the runtime substrate exists.
2. Do not borrow a pilot-family note as substitute proof that the shared loader lane is healthy when the shared loader-facing files themselves drift or disappear; use direct loader-family readback first.
3. Keep the roadmap boundary explicit: Phase 9 still aims at `zigux/tests/runtime_*` and `samples/zigux/runtime_*`, but current `master` can still fall short of loadable-module parity and the reminder packet must say so plainly.
4. Keep the no-dedicated-`validate-phase9.py` posture explicit without replacing it with invented shared gates.
5. Keep earlier-phase references in their own buckets:
   - `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 references
   - `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 references
   - `tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig` remain earlier-phase command and environment cue owners
6. If shared reminder surfaces drift behind the live loader-facing or pilot-family packet, narrow the wording or record the blocker directly. Do not keep stale missing-file claims, stale build-route claims, or invented validation surfaces in place once current-`master` readback contradicts them.
7. `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` must defer the exact shared loader-facing path inventory, convenience-target names, and blocker posture to this sequencing note. If this note no longer confirms those shared loader-facing paths on current `master`, the other shared reminder surfaces must record a blocker or defer back here instead of relisting those paths as live shipped evidence.

## Adjacent lane boundaries

Use this split to avoid overlap.

- `P9-L14`: checker-local reminder wording around `check-phase9-build-only-surface.py` and the nearby shared reminder packet
- `P9-L16`: this sequencing note plus one-file follow-through in docs-root, scripts-root, tests-root, or the shared review checklist when the live loader packet shape changes
- `P9-L01`: only broad cross-family reminder truthfulness that cannot be narrowed into the checker-local or sequencing lanes
- adjacent pilot-family lanes: family-local sample, module, survey, manifest, or diff upkeep when those files actually exist on `master`
- shared loader implementation or checker work: only after a separate bounded lane proves those shared surfaces themselves have a real same-packet gap

If a nearby lane is working inside a surviving family-local packet, this lane should stay on reminder truthfulness and owner-map clarity only.

## Current Pilot-Family Owner Map

Current `master` already exposes four active pilot-family packets through the family-local survey notes, and those lane labels should stay authoritative for pilot-local follow-through.

- `P9-L04`: `Documentation/zigux/phase9-runtime-atomic64-survey.md` owns the runtime atomic64 family-local survey packet. Pilot-local survey, manifest, module, diff, loader-scaffold, and adjacent module-slice linkage repairs stay in that family instead of reopening shared reminder wording.
- `P9-L08`: `Documentation/zigux/phase9-runtime-bitmap-survey.md` owns the runtime bitmap survey packet. Family-local sample, top-bit companion, survey, manifest, diff, and loader-scaffold upkeep stays bitmap-local unless a shared reminder surface itself drifts.
- `P9-L10`: `Documentation/zigux/phase9-runtime-trace-events-survey.md` and `Documentation/zigux/phase9-runtime-trace-events-module-slice.md` own the trace-events packet. Packet-local survey, manifest, module-slice, survey-gate, and adjacent sequencing or `zigux/Makefile` reminder references stay trace-events-local when the shared reminder files themselves remain truthful.
- `P9-L13`: `Documentation/zigux/phase9-runtime-kretprobe-survey.md` owns the runtime kretprobe family-local packet. Sample, loader-plan, survey, manifest, diff, and direct review-note upkeep stays in that family unless the shared reminder packet itself changes.

## Pilot-Family Anti-overlap Rule

If a follow-through only changes one pilot family's survey note, module-slice note, manifest, dedicated survey gate, or direct build-route wording, keep that repair inside the owning pilot-family lane even when the note mentions shared loader adjacency. Use this shared sequencing lane only when the shared reminder surfaces themselves drift or when the repo-level owner map for those four pilot families needs to be refreshed.

## Recommended next-step order

1. Re-read shared reminder surfaces against the live shared loader-facing family plus the four pilot-family survey packets whenever the Phase 9 owner map is in doubt.
2. If one shared reminder surface falls behind the confirmed loader-facing packet or relists blocker posture that this sequencing note no longer supports, repair that surface one file at a time instead of widening into pilot behavior or checker growth.
3. If both shared reminder surfaces drift at once, fix `scripts/zigux/README.md` first and `zigux/tests/README.md` second before touching pilot-local notes.
4. If the shared loader-facing family changes or a direct shared-loader proof lands, refresh this sequencing note first so later shared reminder passes inherit the right owner map.
5. Only after the shared reminder packet is truthful again should any family-local survey note be refreshed to describe shared loader adjacency.

## Anti-overlap rule

If a scheduled run is assigned Phase 9 shared-governance work, keep the run inside shared reminder truthfulness, repo-reality recording, and next-step narrowing. Do not consume pilot-family backlog just because those local files are easy to read from the same packet.
