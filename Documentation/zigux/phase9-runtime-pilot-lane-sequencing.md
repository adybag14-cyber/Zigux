# Phase 9 Runtime Pilot Lane Sequencing

This note keeps the roadmap-backed Phase 9 runtime pilot lane honest when the repo is between shared loader reminder work and pilot-family follow-through.

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

That roadmap boundary matters more than older reminder wording. If live `master` no longer exposes a claimed shared loader surface or pilot-family packet, treat the missing file family as a release-discipline blocker instead of assuming an older reminder packet is still authoritative.

## Live repo reality on current master

Current `master` still exposes the shared loader-facing reminder packet:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `scripts/zigux/check-phase9-build-only-surface.py`
- `zigux/tests/phase9_build.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`

Current `master` also keeps the shared convenience-target names literal for that same packet:

- `make -C zigux phase9-runtime-loader-shared-tests` remains the focused shared-loader replay for the runtime-loader facade, runtime-loader contract, allocator/init-flow proof bundle, and loader-gap survey
- `make -C zigux phase9-test` remains the shared build-only checker plus Phase 9 build replay route
- `make -C zigux phase9` remains the broader runtime-pilot bundle replay route

Current `master` also keeps the four pilot-family review packets visible:

- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-trace-events-survey.md`
- `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
- the dedicated `zigux/tests/runtime_*_manifest.json` packets
- the paired `phase9-runtime-*-module-slice.md` notes
- the dedicated `zigux/tests/runtime_*_survey.zig` gates
- the bitmap-only `samples/zigux/runtime_bitmap_top_bit_contract.zig` companion replay
- the focused `make -C zigux phase9-runtime-atomic64-test`, bitmap-local `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`, `make -C zigux phase9-runtime-bitmap-top-bit-test`, `make -C zigux phase9-runtime-trace-events-test`, and `make -C zigux phase9-runtime-kretprobe-test` pilot-family replay routes

That means the shared Phase 9 packet should keep the loader-facing family explicit as live review evidence while still keeping the loadable-runtime-substrate blocker explicit and keeping pilot-family follow-through inside the family lanes that now own it.

## Current backlog evidence

Current `master` no longer needs the older docs-root follow-through that earlier shared Phase 9 passes were tracking.

- direct readback now shows `Documentation/zigux/review-checklist.md` and `scripts/zigux/README.md` already defer the exact shared owner map back to this sequencing note, while `Documentation/zigux/README.md` remains the first broader reminder surface to narrow one file at a time and `zigux/tests/README.md` should stay parked unless a later reread shows it reclaiming owner-map or blocked-boundary detail again
- the shared `python3 scripts/zigux/check-phase9-build-only-surface.py --self-test` hook when the work is about checker-local reviewability drift before the broader `make -C zigux phase9` replay
- direct readback now also shows `zigux/tests/runtime_loader_allocator_init_flow.zig` already keeps the prepared-plan drift replay explicit across rejected `requestRuntimeLoad()` calls for `requires_runtime_substrate`, `module_name`, `anchor`, `entry_symbol`, `exit_symbol`, selftest-hook, and init-flow drift, while allocator-handoff drift stays covered by dedicated prepared-plan-versus-live-plan equality checks, so the older shared-lane publication handoff for the seven direct explicitness assertions is now stale and future shared follow-through should move to reminder or checker alignment instead of reopening the same replay body
- direct readback now also shows `zigux/tests/phase9_build.zig` routes `zigux/tests/runtime_loader_gap_survey.zig` through the same `phase9-runtime-loader-shared-tests` bundle, so shared owner-map wording needs to keep that loader-gap survey explicit beside `zigux/tests/runtime_loader_allocator_init_flow.zig` instead of undercounting the current shared loader packet
- direct readback now also shows `zigux/tests/phase9_build.zig` resolves the shared loader facade and contract through the support-root `kernel/` subtree via `../kernel/runtime_loader.zig` and `../kernel/runtime_loader_contract.zig`, so the remaining shared wording drift is narrower than the older repo-root inventory suggests
- direct readback now also shows `samples/zigux/runtime_kretprobe_loader.zig` plus `zigux/tests/runtime_loader_allocator_init_flow.zig` already keep the initialized shared-request stability replay and the selftest-complete exit-after-prepare replay explicit for the kretprobe family, so future shared-lane follow-through should not reopen that earlier loader lifecycle proof unless those shipped replays drift
- direct readback now also shows the exact current init-or-registration split: `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_trace_events_loader.zig`, and `samples/zigux/runtime_kretprobe_loader.zig` keep staged `entry_symbol` and `exit_symbol` handoff data, while only the trace-events and kretprobe loaders keep `register_api` and `unregister_api` inside family-local plans or registration snapshots before `toSharedLoadPlan(...)` narrows the shared `runtime_loader.LoadPlan` back to the shared handoff fields, so reminder surfaces should describe staged init-or-exit evidence and metadata-only registration evidence literally instead of implying an executable shared registration path
- the remaining same-lane overlap risk is now the owner-map handoff between this note and the shipped shared reminder packet: older pilot-family labels can still point future runs at stale owners even though the active packet-local follow-through has already moved
- direct readback now also shows `Documentation/zigux/review-checklist.md` already makes the blocked `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root publication, and `depmod` script or manifest state boundary explicit, so the next broader shared reminder pass should begin with `Documentation/zigux/README.md` while leaving `zigux/tests/README.md` parked unless a later reread shows it drifting around that blocked boundary again
- direct readback now also shows `scripts/zigux/README.md` and `zigux/tests/README.md` both keep `zigux/tests/runtime_loader_gap_survey.zig` explicit beside the shared loader-facing packet, so the remaining shared reminder follow-through has narrowed back to reviewer-facing truthfulness around the still-blocked module-metadata and depmod-publication boundary instead of loader-gap inventory sync
- the shipped `scripts/zigux/check-phase9-build-only-surface.py` guard should still fail closed if this note regresses around either the shared owner split or the blocked module-metadata and depmod-publication boundary markers
- the current atomic64 follow-through is the manifest-backed survey-versus-module-slice packet tracked in `P9-L04`, with the shared loader-facing owner map staying adjacent through `P9-L11`
- the current bitmap follow-through stays bitmap-local in `P9-L08`: the manifest, survey note, module-slice note, top-bit companion replay, dedicated `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig` family replay, and survey gate remain family-local, while `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` and the shared loader packet stay adjacent through `P9-L11`
- the current trace-events follow-through stays trace-events-local in `P9-L10`: the manifest, survey note, module-slice note, and survey gate stay family-local while the shared loader packet remains adjacent only
- the current kretprobe follow-through is the manifest-backed loader-plan, survey-gate lifecycle, and tracing proof sync tracked in `P9-L13`, and the older family-local `P9-L10` label should not be reused unless repo evidence explicitly moves ownership back
- the shared module-metadata and depmod-publication boundary is still blocked in the live loader packet: `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root, and `depmod` script or manifest state remain review-only boundary references rather than shipped publication surfaces
- `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references
- `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references

Because the reviewer-facing shared reminder packet is only partly narrowed so far, the next safe shared follow-through is to keep this note aligned with the current pilot-family owner split and then reopen `Documentation/zigux/README.md` one file at a time before considering `zigux/tests/README.md`, and only if either surface still reclaims family-local survey, manifest, module-slice, or survey-gate work, undercounts the current shared loader packet, or fails to defer the exact owner map and blocked publication boundary back here.

## Governance rule for this lane

Shared Phase 9 reminder truthfulness is split across the active shared reminder packet instead of being parked on one broad pilot-family lane.

This lane may:

- refresh `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` when the repo-level owner map changes
- tighten one shared reminder surface at a time when it drifts away from the live shared loader-facing packet
- record a shared loader-facing blocker only when current-`master` readback stops confirming the live packet
- keep the shared convenience-target names, blocker posture, and owner map literal

This lane should not reopen:

- pilot-family sample or module behavior
- pilot-family manifest or diff logic
- family-local survey wording that already belongs to a current packet-local lane
- new checker or validator growth just to compensate for reminder wording drift

## Shared reminder packet rules

1. Do not describe the shared runtime-loader lane as loadable-runtime evidence; keep it explicit that the shared loader family is a review-only handoff packet until the runtime substrate exists.
2. Do not borrow a pilot-family note as substitute proof that the shared loader lane is healthy when the shared loader-facing files themselves drift or disappear; use direct loader-family readback first.
3. Keep the roadmap boundary explicit: Phase 9 still aims at `zigux/tests/runtime_*` and `samples/zigux/runtime_*`, but current `master` can still fall short of loadable-module parity and the reminder packet must say so plainly.
4. Keep the no-dedicated-`validate-phase9.py` posture explicit without replacing it with invented shared gates.
5. Keep earlier-phase references in their own buckets:
   - `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 references
   - `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 references
   - `tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig` remain earlier-phase command and environment cue owners
6. If shared reminder surfaces drift behind the live loader-facing or pilot-family packet, narrow the wording or record the blocker directly. Do not keep stale missing-file claims, stale build-route claims, or invented validation surfaces in place once current-`master` readback contradicts them.
7. `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` should defer the exact shared loader-facing path inventory, convenience-target names, and blocker posture to this sequencing note.
8. If a shared reminder surface or a family-local note cites the `kernel/trace/ring_buffer.c` study-only boundary through the trace-events packet, keep the survey-gate proof manifest-backed and literal: `zigux/tests/runtime_trace_events_manifest.json` remains the source of `surveyed_commit`, and `zigux/tests/runtime_trace_events_survey.zig` must still fail if the survey note drops that commit, the blocked loader scaffold, or the no-status-change posture.

## Adjacent lane boundaries

Use this split to avoid overlap.

- checker-local shared reminder work stays with the dedicated build-only checker lane
- broad shared-owner-map refreshes stay here only when a shared reminder surface or this sequencing note itself drifts
- family-local sample, module, survey, manifest, or diff upkeep stays in the owning pilot-family lanes listed below
- shared loader implementation or checker work belongs to the shared loader packet, not to any one pilot family

If a nearby lane is already working inside a surviving family-local packet, this lane should stay on reminder truthfulness and owner-map clarity only.

## Current Pilot-Family Owner Map

Current `master` already exposes the pilot-family notes plus the shared loader packet, so scheduled follow-through should use the current packet-local owners instead of older labels that no longer match the active lane split. The family-local manifests under `zigux/tests/runtime_*_manifest.json` are the source of truth for these lane labels, and their shared-owner-map references should point back to `P9-L11` when the broader loader-facing packet stays healthy.

- `P9-L04`: owns the current runtime atomic64 manifest-backed survey-versus-module-slice packet. Keep family-local manifest, survey, and directly coupled module-slice wording there while the shared loader-facing reminder packet stays on `P9-L11`.
- `P9-L08`: owns the current runtime bitmap manifest, survey note, module-slice note, focused top-bit companion replay, and survey gate packet. Keep bitmap-local proof there while `P9-L11` owns the shared loader-facing reminder packet.
- `P9-L10`: owns the current runtime trace-events manifest, survey note, module-slice note, and survey-gate packet. Keep trace-events-local proof there while the shared loader-facing reminder packet remains adjacent only.
- `P9-L13`: owns the current runtime kretprobe manifest-backed loader-plan, survey-gate lifecycle, and tracing proof follow-through. Keep kretprobe-local proof there while the older family-local `P9-L10` label remains historical only unless repo evidence explicitly moves ownership back.

## Pilot-Family Anti-overlap Rule

If a follow-through only changes one pilot family's survey note, module-slice note, manifest, dedicated survey gate, or direct build-route wording, keep that repair inside the owning pilot-family lane even when the note mentions shared loader adjacency. Use this shared sequencing lane only when the shared reminder surfaces themselves drift or when the repo-level owner map for those four pilot families needs to be refreshed.

## Recommended next-step order

1. Re-read the shared reminder surfaces against the live shared loader-facing family plus the four pilot-family packets whenever the Phase 9 owner map is in doubt.
2. If the shared reminder packet already defers correctly to this note, refresh the smallest shipped shared summary that still drifts around the blocked module-metadata and depmod-publication boundary and the stale repo-root loader inventory, starting with `Documentation/zigux/README.md` and only then reopening `zigux/tests/README.md` if a later reread still finds drift there, while keeping `scripts/zigux/README.md` parked unless a later reread shows it reclaiming family-local owner-map detail again.
3. If a different shared reminder surface starts reclaiming family-local survey, manifest, module-slice, or survey-gate work, repair that one file at a time instead of widening into pilot behavior or checker growth.
4. If the shared loader-facing family changes or a direct shared-loader proof lands, refresh this sequencing note before later shared reminder passes inherit stale owner labels.
5. Only after the shared reminder packet is truthful again should any family-local survey note be refreshed to describe shared loader adjacency.
- `Documentation/zigux/review-checklist.md` now keeps the shared-loader split visible by naming the shipped `phase9-runtime-bitmap-top-bit-tests` step beside `samples/zigux/runtime_bitmap_top_bit_contract.zig`, while the bitmap-local `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig` replay stays with the family packet instead of being flattened into shared loader evidence, and it remains the reviewer-facing surface that also restates the older command and environment ownership boundaries, while the shared `python3 scripts/zigux/check-phase9-build-only-surface.py --self-test` hook stays part of the same loader-owned validation packet

## Anti-overlap rule

If a scheduled run is assigned Phase 9 shared-governance work, keep the run inside shared reminder truthfulness, repo-reality recording, and next-step narrowing. Do not consume pilot-family backlog just because those local files are easy to read from the same packet.
