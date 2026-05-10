# Phase 9 Runtime Pilot Lane Sequencing

This note turns the roadmap-backed Phase 9 reminder packet on current `master` into one bounded anti-overlap map for scheduled pilot lanes.

Current repo-reality warning:

- this survey could still read the shared Phase 9 reminder surfaces under `Documentation/zigux/`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and `Documentation/zigux/review-checklist.md`
- live contents reads for `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, and the `samples/zigux/runtime_*_loader.zig` scaffolds returned not found during this pass
- treat those missing shared loader and replay paths as planned Phase 9 anchors, not shipped current-`master` evidence, until a future shared-lane run confirms they are back or narrows the reminder packet away from them

## Why this note exists

Phase 9 still carries both:

- a planned shared runtime-loader handoff packet around `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `scripts/zigux/check-phase9-build-only-surface.py`, and `zigux/tests/phase9_build.zig`
- four pilot-family packets rooted in `lib/atomic64_test.c`, `lib/test_bitmap.c`, `samples/trace_events/trace-events-sample.c`, and `samples/kprobes/kretprobe_example.c`

That split remains the roadmap-backed product shape, but without a dedicated sequencing note nearby runs can still reopen the same Phase 9 surfaces from different directions or overstate reminder-only anchors as already shipped replay evidence.

## Shared loader lane

Treat the shared loader lane as the planned owner of these shared Phase 9 anchors whenever they are present on `master`:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `scripts/zigux/check-phase9-build-only-surface.py`
- the shared `python3 scripts/zigux/check-phase9-build-only-surface.py --self-test` hook when the work is about checker-local reviewability drift before the broader `make -C zigux phase9` replay
- the `phase9-runtime-loader-shared-tests` step in `zigux/tests/phase9_build.zig`
- the shared `make -C zigux phase9` route when the work is about loader-facade, allocator-handoff, request-contract, or bundled runtime-pilot reviewability

If one or more of those shared files are absent on live `master`, treat that as a shared repo-reality blocker first. Do not quietly borrow pilot-family survey notes or contributor reminders as substitute proof that the shared loader packet is shipped.

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
- `samples/zigux/runtime_trace_events_loader.zig` now owns the selftest-ready outstanding-registration drain replay plus duplicate-registration rejection and the initialized-stage failed-exit recovery replay; those checks prove when the trace-events pilot may prepare a shared request, but they do not change shared `runtime_loader` ownership
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
- the shared request contract also keeps blocked module-metadata and depmod publication surfaces explicit: `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root, and `depmod` script or manifest state stay outside both `LoadPlan` and `PreparedRequest`, so current `master` still does not claim a shipped module-metadata or depmod bridge

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

- this survey could still read `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, so the broad reminder packet is still visible on current `master`
- this survey could not read `zigux/tests/phase9_build.zig`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, or the `samples/zigux/runtime_*_loader.zig` scaffolds from the live contents tree, so the shared runtime-loader packet is currently a repo-reality blocker rather than a parked shipped replay surface
- because that shared file family is missing, do not treat the broad docs-root, scripts-root, tests-root, or checklist reminders as proof that the shared loader lane is already aligned; the next shared follow-through should either re-establish those concrete files on `master` or narrow the reminder packet so it stops overstating them
- the four pilot-family docs packets remain the safest place to record family-local blocked-state evidence while the shared file family is missing; do not widen those pilot-local blocked notes into substitute shared-loader closure claims
- keep `Documentation/zigux/freeze-map.md` follow-through as a governance cue only; with the shared loader file family missing, any future freeze-map or scorecard mention should reopen the shared lane as a repo-reality and governance blocker first
- leave `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` available as reminder surfaces, but treat them as the next repair targets only after the shared lane decides whether the missing shared file family is being restored or whether those reminders should be narrowed

## Recommended next-step order

1. shared repo-reality repair: first confirm whether the missing shared file family under `zigux/tests/phase9_build.zig`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/kernel/runtime_loader*.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, and `samples/zigux/runtime_*_loader.zig` is meant to be restored on `master` or removed from the shared reminder packet
2. shared reminder refresh: if the missing shared file family is intentionally gone, narrow `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` one surface at a time so they stop describing those paths as shipped replay evidence
3. shared loader lane: if the missing shared file family is being restored instead, re-establish the smallest honest build or checker surface first and only then reopen broader request-contract, allocator/init-flow, or build-only reviewability work
4. bitmap lane: only if the goal is to refine the already-landed top-bit companion or the survey-local `phase9_build.zig` marker alignment inside `zigux/tests/runtime_bitmap_survey.zig`
5. trace-events, atomic64, or kretprobe lanes: only when the change stays inside that family’s sample, loader, module, diff, survey, or blocked-state evidence packet

## Anti-overlap rule

If a scheduled Phase 9 run is assigned a pilot-family lane, keep the work inside that family’s packet plus the smallest unavoidable shared-loader touch. If the shared-loader lane is assigned, do not consume pilot-local backlog just because the shared lane has spare room.