# Phase 9 Runtime Pilot Lane Sequencing

This note keeps the roadmap-backed Phase 9 runtime pilot lane honest when current `master` carries one shipped trace-events runtime packet, one narrower returned shared runtime-loader reminder surface with a dedicated command/environment boundary guard, one bounded runtime bitmap reminder packet, and one returned runtime kretprobe pilot packet that shared reminder surfaces still undercount.

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

Trusted mixed rereads on 2026-05-25 confirm four distinct current-master Phase 9 postures.

### 1. Trace-events remains the direct shipped runtime sample family

- surviving review surfaces: `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `scripts/zigux/check-phase9-trace-events-direct-summary.py`, `scripts/zigux/check-phase9-trace-events-summary-preservation.py`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/tests/README.md`
- surviving direct runtime-module sample: `samples/zigux/runtime_trace_events.zig`
- surviving fail-closed runtime companion: `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- surviving exit-rollback runtime companion: `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
- surviving registration-reentry runtime companion: `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
- surviving re-init rollback runtime companion: `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`
- surviving re-init plus re-exit rollback runtime companion: `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`
- surviving family-local survey witness: `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig`
- surviving runtime-module evidence inside that direct sample: `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking
- balanced registration re-entry replay in `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` across both the initialized and selftest_complete stages remains part of the still-shipped narrow packet
- exact registration and re-init evidence inside the shipped trace-events packet now reads cleanly on current `master`: duplicate `registerFunctionThread()` attempts fail closed with `error.FunctionThreadAlreadyRegistered` while preserving the prior summary in both initialized and selftest-complete states, and rejected `init()` attempts preserve the prior summary in initialized, selftest-complete, and exited states inside `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`

### 2. The shared runtime-loader allocator/init-flow and command/environment boundary packet survives as a narrower shared-owner surface

Trusted GitHub rereads on 2026-05-25 directly recover the still-live shared loader packet through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the still-returned `samples/zigux/runtime_bitmap_loader.zig` scaffold, and the bounded `zigux/tests/phase9_build.zig` shard.

- the shared runtime-loader allocator/init-flow packet remains mixed-source shared-owner evidence, and the dedicated command/environment boundary guard travels with that narrower direct-readback shard instead of widening it into family-local proof
- `zigux/kernel/runtime_loader_contract.zig` keeps the initcall and registration boundary literal inside the surviving shared packet: staged entry and exit symbol names remain metadata in `LoadPlan`, readiness still depends on counted `.initialized` or `.selftest_complete` handoff state through `InitFlow.readyForRuntimeLoad()`, and the shared contract explicitly keeps `module_init`, `module_exit`, `initcall`, `exitcall`, `register_api`, `unregister_api`, `summary`, and `registration_snapshot` out of the shared request contract
- the shared-loader reminder packet keeps metadata-only registration posture explicit instead of executable runtime registration: current Phase 9 review surfaces can point at staged registration labels and handoff-state evidence, but they must not claim that runtime registration callbacks or module-loading control paths have landed
- the older `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, and `samples/zigux/runtime_trace_events_loader.zig` references do not materialize on the trusted direct-read path, so keep them as historical wider-family vocabulary instead of current shared-owner proof
- `zigux/tests/phase9_build.zig` still exposes `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, and `phase9-runtime-trace-events-loader-substrate-drift-tests`
- `zigux/tests/runtime_loader_allocator_init_flow.zig` keeps the exact handoff evidence narrow: initialized-stage bitmap and kretprobe plans plus selftest-complete trace-events and atomic64 plans may advance only when the prepared `LoadPlan` keeps allocator handoff, entry and exit symbol metadata, selftest-hook state, and init-flow counters unchanged across `prepareRequest()`, `requestRuntimeLoad()`, and `releaseWithoutSubstrate()`
- the surviving loader route names are bounded rerun vocabulary rather than proof that blocked publication, install-root, or module-metadata surfaces are solved
- `zigux/kernel/runtime_loader_command_env_boundary_guard.zig` keeps the command/environment guard reviewable on current `master` by fail-closing when argv or environment control markers bleed into `zigux/kernel/runtime_loader.zig` or `zigux/kernel/runtime_loader_contract.zig`
- keep the Phase 8 command and environment ownership boundary explicit: deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` cues stay with `tools/lib/subcmd/exec-cmd.zig`, while `LINES` and `COLUMNS` stay with `tools/lib/subcmd/help.zig`
- current Phase 9 material still does not prove shipped runtime command or environment activation control; it proves only that the shared runtime-loader packet keeps those Phase 8 control surfaces out of the loader contract

### 3. The runtime bitmap side returns a broader direct packet without promoting the broader shared runtime-loader boundaries

- the current reminder surfaces keep the bounded runtime bitmap packet visible through `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_direct_init_contract.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and `samples/zigux/runtime_bitmap_cold_stage_guard.zig`
- `samples/zigux/runtime_bitmap_loader.zig` stays a returned companion on the trusted path, but it sits adjacent to the narrower shared loader packet above rather than proving that the older broader loader-gap packet returned
- `zigux/tests/phase9_build.zig` keeps the returned bitmap packet inside the shared rerun bundle through `phase9-runtime-bitmap-tests` plus the dedicated `phase9-runtime-bitmap-cold-stage-guard-tests` route
- that broader bitmap-side visibility still must not be used to imply that the broader shared runtime-loader or blocked publication boundaries returned

### 4. The runtime kretprobe side returns a family-local pilot packet, and shared reminder surfaces still need one-surface-at-a-time follow-through

Trusted GitHub rereads on 2026-05-25 directly recover `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and the live `zigux/tests/phase9_build.zig` routes that now wire them.

- `samples/zigux/runtime_kretprobe.zig` is a returned family-local runtime sample rooted in the Phase 9 `samples/kprobes/kretprobe_example.c` anchor, with selftest-hook and lifecycle-parity proof kept inside that pilot packet
- `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig` is the returned sample-side initialized-snapshot companion for that same pilot family, keeping captured initialized lifecycle state explicit across later selftest and exit without treating that guard as proof of shared runtime-loader closure
- `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig` is the returned sample-side registration-reentry companion for that same pilot family, keeping reusable balanced probe cycles explicit across both initialized and selftest_complete states without treating that guard as proof of shared runtime-loader closure
- exact registration evidence inside `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig` now reads cleanly on current `master`: balanced `registerProbe()` and `unregisterProbe()` cycles stay reusable before selftest and after selftest, while all registration, entry, return, unregister, and exit operations fail closed after the module reaches `.exited`
- `samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig` is the returned sample-side paired re-init and re-exit rollback companion for that same pilot family, keeping rejected `init()` and `exit()` transitions snapshot-stable after both initialized direct activity and selftest-ready replay without treating that guard as proof of shared runtime-loader closure
- `samples/zigux/runtime_kretprobe_loader.zig` is the returned sample-side loader companion for that same pilot family, keeping initialized-stage shared-request planning and later selftest snapshot stability explicit without treating that loader witness as proof of broader shared runtime-loader closure
- `zigux/tests/runtime_kretprobe_survey.zig` is the returned family-local survey witness for that same pilot family
- `zigux/tests/runtime_kretprobe_module.zig` is the returned module-side lifecycle companion for that same pilot family
- `zigux/tests/runtime_first_loadable_parity_behavior.zig` now includes the kretprobe pilot beside the atomic64 and bitmap pilots, so current `master` no longer supports treating kretprobe as absent from the cross-family parity surface
- `zigux/tests/phase9_build.zig` now exposes `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-reinit-reexit-guard-tests`, `phase9-runtime-kretprobe-survey-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests`, so the returned loader companion, paired re-init and re-exit rollback companion, and survey witness are now part of the bounded rerun packet rather than sample-side evidence only
- those returned kretprobe routes and files are still family-local pilot evidence, not proof that broader shared loader, publication, or install-root boundaries returned
- shared reminder surfaces outside this sequencing note still need one-surface-at-a-time follow-through so they do not undercount the returned initialized-snapshot, registration-reentry, reinit-reexit, loader, or survey witnesses, overclaim absent manifest companions, or widen that bounded pilot packet into shared-loader completion claims

## Current shared-owner state

The shared Phase 9 reminder family should now be read as four distinct truths:

1. the trace-events runtime packet is still the shipped direct current-`master` proof for selftest-hook and lifecycle-parity reviewability
2. the returned shared runtime-loader allocator/init-flow kernel-and-test surface plus the dedicated command/environment boundary guard stay neighboring shared-owner evidence, while the older loader-gap survey and manifest paths stay historical vocabulary until trusted rereads return them
3. the bitmap side keeps a broader direct packet on trusted rereads, so current `master` supports a bounded runtime bitmap reminder packet plus the returned shared allocator/init-flow and command/environment boundary packet, not proof that the broader bitmap family returned
4. the kretprobe side now keeps a returned family-local pilot packet on trusted rereads, but shared reminder surfaces beyond this owner note still need one-surface-at-a-time follow-through before later scheduled runs should treat that packet as fully propagated reminder state

The broader shared reminder packet is therefore only partly aligned on current `master`:

- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` still need one-surface-at-a-time follow-through where they undercount the returned initialized-snapshot, registration-reentry, reinit-reexit, loader, or survey witnesses, overclaim absent manifest companions, or otherwise drift from the bounded family-local kretprobe packet confirmed here on current `master`
- `scripts/zigux/README.md` now again carries a dedicated shared Phase 9 reminder section on current `master`, so keep counting it as active same-lane evidence beside the aligned docs-root and tests-root packet
- `Documentation/zigux/README.md` now truthfully counts `scripts/zigux/README.md` inside its shared Phase 9 reminder packet because trusted rereads on 2026-05-26 recover the dedicated scripts-root Phase 9 reminder section again, so keep that docs-root companion mention aligned with the returned scripts-root surface instead of reopening a stale missing-section warning
- `Documentation/zigux/README.md` and `zigux/tests/README.md` still correctly frame the older `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, and `samples/zigux/runtime_trace_events_loader.zig` references as historical wider-family vocabulary rather than current direct evidence
- treat any docs-root, checklist, or tests-root drift that remains after this scripts-root restoration as shared reminder debt to repair one surface at a time instead of widening it into runtime behavior claims or broader checklist churn inside this lane

This means the shared owner packet should keep the narrow trace-events family explicit, keep the returned shared loader packet explicit, keep the direct command/environment boundary guard explicit, keep the bounded runtime bitmap reminder packet explicit, keep the returned kretprobe pilot explicit as returned family-local evidence, and avoid promoting any of them into claims that deeper publication, install-root, or loadable-runtime-complete substrate work is finished.

- `zigux/tests/phase9_build.zig` still records bounded atomic64 diff, bitmap, loader-shared, trace-events loader-substrate-drift, kretprobe, command/environment boundary, parity-survey, and parity-behavior route names, but that surviving build bundle is not proof that blocked publication boundaries or install-root surfaces are complete
- no shared reminder surface should present the bounded runtime bitmap packet or the returned kretprobe packet as equal to the shipped trace-events packet or as proof that every broader runtime boundary returned
- keep the older non-owner boundary anchors explicit too: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence

## Historical boundaries

- the older wider-family loader reminder vocabulary that no longer returns on the trusted direct path includes `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, and `samples/zigux/runtime_trace_events_loader.zig`
- still preserve blocked `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, and depmod-publication vocabulary
- keep `modules.order`, `modules.builtin`, `Module.symvers`, and module install-root wording framed as blocked wider-family vocabulary too
- keep blocked depmod script, depmod manifest, and depmod alias-output wording framed as historical wider-family vocabulary too until trusted direct rereads return a current shared owner surface for that publication packet

## Governance rule for this lane

This lane may:

- refresh this note when trusted repo reality changes
- tighten one stale shared reminder surface at a time when it undercounts or overclaims the trace-events packet, the returned shared loader packet, the direct command/environment boundary guard, the bounded runtime bitmap packet, the returned kretprobe packet, or build-route maturity
- keep the narrow trace-events packet explicit as the current shipped runtime-pilot proof
- keep the returned shared loader packet explicit without overstating blocked publication or install-root completion
- keep the direct command/environment boundary guard explicit without treating it as proof of shipped runtime command or environment activation control
- keep the bounded runtime bitmap reminder packet explicit without overstating what has actually returned
- keep the returned kretprobe pilot explicit as family-local proof without treating it as a shared-owner or publication-complete packet
- keep the bounded `zigux/tests/phase9_build.zig` shard explicit as route vocabulary without treating it as proof that blocked publication boundaries or install-root surfaces are complete

This lane should not reopen:

- new runtime behavior based only on stale reminder wording
- checker growth when the active problem is a stale shared summary
- backlog promotion of the bounded runtime bitmap reminder packet or the returned kretprobe packet into proof that every broader runtime boundary returned
- blocked publication or install-root completion claims that the surviving route names still do not prove
- family-local runtime kretprobe behavior work that belongs in the returned pilot packet itself rather than in this shared sequencing note

Treat stale shared-owner undercount or overclaim as the active blocker before reopening checker-local or runtime-behavior work.

## Freeze boundary

- keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain cautionary non-owner context rather than proof of runtime-substrate or bridge readiness

## Recommended next-step order

1. Start with `Documentation/zigux/README.md` if a fresh reread still undercounts the returned initialized-snapshot, registration-reentry, reinit-reexit, loader, or survey witnesses, overclaims absent manifest companions, or otherwise drifts from the shared-owner split confirmed here on current `master`.
2. Re-read `Documentation/zigux/review-checklist.md` and `zigux/tests/README.md` only if one of those reminder surfaces still treats the returned kretprobe packet as absent, overclaims absent manifest companions, or drifts away from the returned loader core surfaces, the direct command/environment boundary guard, the bounded runtime bitmap packet, or the returned registration-reentry companion confirmed here on current `master`.
3. If the broader shared runtime-loader family changes again, widen this note only after an exact reread proves the specific returned file family or blocked-boundary vocabulary moved.
4. If the runtime bitmap packet changes again, widen the bitmap-side reminder packet only after the trusted direct read path proves the specific returned file set changed.
5. If the kretprobe packet changes again, keep the next follow-through inside one shared reminder surface only unless the live family-local sample or module packet itself drifts first.

## Anti-overlap rule

If a scheduled run is assigned shared Phase 9 backlog or governance work, keep the run inside repo-reality rereads and one-file reminder repair. Do not treat the bounded runtime bitmap reminder packet as full sample-family return, do not treat the returned kretprobe pilot packet as a reason to reopen family-local behavior work from the shared lane, do not treat `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-pilot expansion evidence, and do not treat the surviving loader route names or the direct command/environment boundary guard as proof that blocked publication, install-root, or module-metadata work is complete.