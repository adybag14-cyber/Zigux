# Phase 9 Runtime Pilot Lane Sequencing

This note turns the current `master` evidence for the Phase 9 runtime pilot packet into one bounded anti-overlap map for scheduled pilot lanes.

## Why this note exists

Phase 9 is now carrying both:

- a shared runtime-loader handoff packet under `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `scripts/zigux/check-phase9-build-only-surface.py`, and `zigux/tests/phase9_build.zig`
- four pilot-family packets rooted in `lib/atomic64_test.c`, `lib/test_bitmap.c`, `samples/trace_events/trace-events-sample.c`, and `samples/kprobes/kretprobe_example.c`

That split is real product progress, but without a dedicated sequencing note nearby runs can still reopen the same Phase 9 surfaces from different directions.

## Shared loader lane

Treat the shared loader lane as the only owner of:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `scripts/zigux/check-phase9-build-only-surface.py`
- the shared `python3 scripts/zigux/check-phase9-build-only-surface.py --self-test` hook when the work is about checker-local reviewability drift before the broader `make -C zigux phase9` replay
- the `phase9-runtime-loader-shared-tests` step in `zigux/tests/phase9_build.zig`
- the shared `make -C zigux phase9` route when the work is about loader-facade, allocator-handoff, request-contract, or bundled runtime-pilot reviewability

This lane may tighten loader-facing reviewability, checker-local selftest-hook wording, contract wording, or shared build-only validation, but it should not reopen pilot-local sample, module, diff, or survey logic unless a shared loader contract change forces a synchronized follow-up.

## Pilot-family lanes

Treat each runtime family as a separate pilot lane with its own bounded evidence packet.

### Atomic64 pilot lane

Own:

- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- the `phase9-runtime-atomic64-tests` step in `zigux/tests/phase9_build.zig`

### Bitmap pilot lane

Own:

- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_manifest.json`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`
- `zigux/tests/runtime_bitmap_survey.zig`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- the focused `phase9-runtime-bitmap-top-bit-tests` step and the shared bitmap survey leg in `zigux/tests/phase9_build.zig`

The top-bit companion replay belongs to the bitmap pilot lane only. Do not recast it as shared loader evidence.

### Trace-events pilot lane

Own:

- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- `zigux/tests/runtime_trace_events_module.zig`
- `zigux/tests/runtime_trace_events_diff.zig`
- `zigux/tests/runtime_trace_events_survey.zig`
- `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`
- `Documentation/zigux/phase9-runtime-trace-events-survey.md`
- the `phase9-runtime-trace-events-tests` step in `zigux/tests/phase9_build.zig`

### Kretprobe pilot lane

Own:

- `samples/zigux/runtime_kretprobe.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`
- `zigux/tests/runtime_kretprobe_manifest.json`
- `zigux/tests/runtime_kretprobe_module.zig`
- `zigux/tests/runtime_kretprobe_diff.zig`
- `zigux/tests/runtime_kretprobe_survey.zig`
- `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`
- `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
- the `phase9-runtime-kretprobe-tests` step in `zigux/tests/phase9_build.zig`

## Current pilot-local proof edges

Keep these newer proof surfaces inside their owning pilot family even when they call shared loader helpers:

- `zigux/tests/runtime_bitmap_survey.zig` now owns the fail-closed check that the bitmap survey packet still names the shared `phase9-runtime-bitmap-module-tests`, `phase9-runtime-bitmap-diff-tests`, `phase9-runtime-bitmap-loader-tests`, and `phase9-runtime-bitmap-survey-tests` markers in `zigux/tests/phase9_build.zig`; that guard belongs to the bitmap survey packet together with `samples/zigux/runtime_bitmap_top_bit_contract.zig`, not to the shared loader lane
- `samples/zigux/runtime_trace_events_loader.zig` now owns the selftest-ready outstanding-registration drain replay, duplicate-registration rejection, initialized-stage failed-exit recovery replay, the selftest-complete shared-request snapshot pinned across later exit activity, and the prepared shared selftest-hook plus approved-family anchor and symbol drift guards before any local runtime handoff; those checks prove when the trace-events pilot may prepare and preserve a shared request, but they do not change shared `runtime_loader` ownership
- `zigux/tests/runtime_kretprobe_diff.zig` now owns the overlapping-entry-stamp replay that proves `samples/zigux/runtime_kretprobe.zig` keeps per-instance return timing distinct under concurrent load; that proof edge belongs to the kretprobe pilot family and should not be recast as shared loader evidence
- `Documentation/zigux/phase9-runtime-kretprobe-survey.md`, `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`, `zigux/tests/runtime_kretprobe_manifest.json`, and `zigux/tests/runtime_kretprobe_survey.zig` keep the blocked `starter_landed_without_loadable_runtime_substrate` state in the kretprobe family; do not treat that blocked-state wording as a request to widen the shared loader lane unless the shared substrate packet itself changes

## Older boundaries that stay out of Phase 9 ownership

Keep these boundaries explicit so Phase 9 pilot work does not drift sideways:

- `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` remain the separate Phase 9 runtime bitmap family rooted in `lib/test_bitmap.c`; current `master` still ships no direct `samples/zigux/*bitmap*` Phase 5 reference sample, so keep approved-idiom reviewability under `samples/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `tools/lib/bitmap.zig`, `Documentation/zigux/phase1-closure.md`, and `Documentation/zigux/phase4-validation-matrix.md` instead of flattening bitmap into the four approved Phase 5 sample anchors
- `samples/zigux/trace_events_sample.zig` and `samples/zigux/kretprobe_example.zig` remain the bounded non-runtime Phase 5 anchors for those families
- `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references
- `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references
- `tools/lib/subcmd/exec-cmd.zig` remains the Phase 8 owner of deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` tooling cues
- `tools/lib/subcmd/help.zig` remains the Phase 8 owner of `LINES` and `COLUMNS` terminal-formatting cues
- the shared Phase 9 loader packet remains a metadata-only handoff and should not be read as shipped runtime command or environment activation control

## Shared summary follow-through

When the shared Phase 9 reminders in the docs root, scripts root, tests root, sample-root boundary note, or reviewer-facing checklist are refreshed, they should point back to this sequencing note rather than trying to restate the owner split from scratch.

Keep that follow-through bounded to one shared summary at a time:

- `Documentation/zigux/README.md` for the docs-root packet summary
- `scripts/zigux/README.md` for the scripts-root validator and replay summary
- `zigux/tests/README.md` for the shared tests-root replay reminder
- `samples/zigux/README.md` only when the Phase 9 boundary wording there is being touched already
- `Documentation/zigux/review-checklist.md` for the reviewer-facing Phase 9 prompt

Only `samples/zigux/README.md` and `Documentation/zigux/review-checklist.md` should restate the bitmap-only top-bit companion or the older command and environment control boundaries; the docs root, scripts root, and tests root should keep pointing back here instead of duplicating those pilot-local reminders.

This keeps later closure-note work small while preserving the explicit split between the shared loader lane, the bitmap-only top-bit replay, the samples-root and checklist-facing command and environment boundaries, the shipped checker self-test hook, and the four pilot-family packets.

## Focused convenience targets

When a shared Phase 9 closure note or reminder surface names the exact replay routes, keep the current `zigux/Makefile` convenience targets explicit instead of paraphrasing them:

- shared loader lane: `make -C zigux phase9-runtime-loader-shared-tests`
- atomic64 pilot lane: `make -C zigux phase9-runtime-atomic64-test`
- bitmap pilot lane: `make -C zigux phase9-runtime-bitmap-top-bit-test`
- trace-events pilot lane: `make -C zigux phase9-runtime-trace-events-test`
- kretprobe pilot lane: `make -C zigux phase9-runtime-kretprobe-test`
- bundled Phase 9 replay: `make -C zigux phase9`

This shared note owns those exact convenience-target names for closure work; later docs-root, scripts-root, tests-root, samples-root, and checklist refreshes should point back here instead of inventing shorter aliases or flattening the focused lane routes into the bundled `phase9` replay.

## Current live follow-through state

- `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` already keep this owner map or its shared-loader-versus-pilot split explicit on `master`; treat those three shared reminder surfaces as parked unless the shared loader packet itself changes
- `scripts/zigux/README.md` now keeps the focused shared-loader replay explicit beside the bundled `make -C zigux phase9` route, so the shared loader lane no longer has a parked scripts-root reminder follow-through on current `master`
- the broad docs-root Phase 9 summary in `Documentation/zigux/README.md` should now be treated as parked shared-packet context, not as a request to reopen checker-local or pilot-family follow-through, because this sequencing note plus `scripts/zigux/check-phase9-build-only-surface.py` already record the shared loader packet as aligned on current `master`
- that parked docs-root summary intentionally stays broad: the direct starter samples `samples/zigux/runtime_atomic64.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_trace_events.zig`, and `samples/zigux/runtime_kretprobe.zig` remain pilot-family evidence owned by their dedicated module-slice and survey notes, so future docs-root reminder refreshes should point back here instead of flattening those starters into shared loader ownership
- `samples/zigux/README.md` already carries the bitmap-only top-bit companion reminder plus the older command and environment control boundaries, so later shared-loader follow-through should leave those pilot-local cues there instead of flattening them back into the loader packet
- `Documentation/zigux/freeze-map.md` already keeps the shared Phase 9 runtime-loader packet explicit as a review-only boundary beside `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`, so the shared loader lane should treat freeze-map wording there as a review-surface cue rather than runtime-substrate closure or a status-change request
- the same freeze-map follow-through still carries no linked `Documentation/zigux/phase15-parity-scorecard.md` entry and no Architecture Council status-change request for the shared Phase 9 loader packet on current `master`; if either artifact appears, reopen the shared loader lane as a governance change first instead of treating it as routine pilot-family evidence drift
- if a future `Documentation/zigux/review-checklist.md` refresh is triggered by one of those shared-loader freeze-map governance artifacts, keep that checklist work coupled to the same shared governance reopen instead of landing it as a standalone Phase 9 reminder cleanup
- `Documentation/zigux/review-checklist.md` now keeps the shared-loader split visible without the stale non-existent bitmap build path by naming the shipped `phase9-runtime-bitmap-top-bit-tests` step beside `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and it remains the reviewer-facing surface that also restates the older command and environment ownership boundaries, while the shared `python3 scripts/zigux/check-phase9-build-only-surface.py --self-test` hook stays part of the same loader-owned validation packet
- treat that review-checklist prompt and `scripts/zigux/check-phase9-build-only-surface.py` as one coupled release-discipline packet: a checklist-side Phase 9 reminder refresh is incomplete unless the shared checker keeps this sequencing note, the shipped self-test-hook ownership bullet, and the older freeze-map follow-through coupled instead of only trusting the surrounding reminder surfaces
- `scripts/zigux/check-phase9-build-only-surface.py` now exact-counts the older freeze-map prompt follow-through and also fails closed on both the sequencing note's shared-loader self-test-hook ownership bullet and the coupled checklist-side validation-packet marker, so the shared loader lane no longer has a parked checker-local selftest-hook follow-through on current `master`
- `zigux/tests/README.md` now keeps the shared Phase 9 runtime-loader packet broad while also naming the focused `phase9-runtime-loader-shared-tests` step, so the shared loader lane no longer has a parked tests-root reminder follow-through on current `master`
- `zigux/tests/runtime_loader_allocator_init_flow.zig` now keeps prepared requests pinned across loader-not-required, module-name drift, anchor drift, entry-symbol drift, exit-symbol drift, selftest-hook drift, and init-flow drift, while `zigux/kernel/runtime_loader.zig` now also proves allocator-handoff prepared-plan drift directly in the shared loader packet; the next same-lane follow-through should stay inside `zigux/kernel/runtime_loader.zig` or `zigux/kernel/runtime_loader_contract.zig` and look for the next smallest lifecycle-state or invalid-transition proof instead of reopening broader summaries or replaying the allocator-handoff step
- `Documentation/zigux/phase9-runtime-trace-events-survey.md` and `zigux/tests/runtime_trace_events_survey.zig` now both treat the trace-events loader packet as aligned on current `master`, so the trace-events lane no longer has a parked follow-through around registration-drain wording, failed-exit recovery wording, selftest-complete exit-after-prepare wording, or prepared shared-request drift wording
- with the broad docs-root, scripts-root, and tests-root reminders all parked on current `master`, the next same-lane follow-through should stay inside `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, or `zigux/tests/runtime_loader_allocator_init_flow.zig` and begin with the next smallest shared-loader lifecycle-state or invalid-transition proof instead of reopening a broader summary surface
- reopen this shared lane only if one of the shared reminder surfaces drifts again or if the shared loader lane picks up a new bounded validation surface that needs to be named across the packet

## Recommended next-step order

1. shared reminder refresh: only if another docs-root, scripts-root, tests-root, samples-root, or checklist surface drifts after this alignment; the broad docs-root, scripts-root, and tests-root Phase 9 summaries are currently parked on live `master`, so if a reminder-only follow-through is still justified without changing the shared loader packet, prefer the smallest stale checklist or samples-root cue before reopening those broader summaries
2. shared loader lane: allocator-handoff prepared-plan drift is already covered directly on current `master`, so start with the next smallest lifecycle-state or invalid-transition proof inside `zigux/kernel/runtime_loader.zig` or `zigux/kernel/runtime_loader_contract.zig`; once that lands, prefer the next smallest request-shape or release-without-substrate edge in the other shared loader file, and if a new bounded validation surface lands, wire it through `scripts/zigux/check-phase9-build-only-surface.py` before reopening broader request-contract, allocator/init-flow, or build-only reviewability work
3. bitmap lane: only if the goal is to refine the already-landed top-bit companion or the survey-local `phase9_build.zig` marker alignment inside `zigux/tests/runtime_bitmap_survey.zig`
4. trace-events lane: currently parked on live `master` after landing the registration-drain, failed-exit recovery, selftest-complete exit-after-prepare, prepared shared selftest-hook drift, approved-family anchor and symbol drift, and non-prepared shared-request guards inside `samples/zigux/runtime_trace_events_loader.zig`; reopen only if a new direct pilot-local lifecycle-state or request-shape gap appears there
5. atomic64 or kretprobe lanes: only when the change stays inside that family’s sample, loader, module, diff, survey, or blocked-state evidence packet

## Anti-overlap rule

If a scheduled Phase 9 run is assigned a pilot-family lane, keep the work inside that family’s packet plus the smallest unavoidable shared-loader touch. If the shared-loader lane is assigned, do not consume pilot-local backlog just because the shared lane has spare room.
