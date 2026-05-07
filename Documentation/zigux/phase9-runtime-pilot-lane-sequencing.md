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
- the `phase9-runtime-loader-shared-tests` step in `zigux/tests/phase9_build.zig`
- the shared `make -C zigux phase9` route when the work is about loader-facade, allocator-handoff, or request-contract reviewability

This lane may tighten loader-facing reviewability, contract wording, or shared build-only validation, but it should not reopen pilot-local sample, module, diff, or survey logic unless a shared loader contract change forces a synchronized follow-up.

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
- `zigux/tests/runtime_kretprobe_module.zig`
- `zigux/tests/runtime_kretprobe_diff.zig`
- `zigux/tests/runtime_kretprobe_survey.zig`
- `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`
- `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
- the `phase9-runtime-kretprobe-tests` step in `zigux/tests/phase9_build.zig`

## Older boundaries that stay out of Phase 9 ownership

Keep these boundaries explicit so Phase 9 pilot work does not drift sideways:

- `samples/zigux/trace_events_sample.zig` and `samples/zigux/kretprobe_example.zig` remain the bounded non-runtime Phase 5 anchors for those families
- `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface bridge references
- `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references
- `tools/lib/subcmd/exec-cmd.zig` still owns deferred command-path and environment-control cues
- `tools/lib/subcmd/help.zig` still owns `LINES` and `COLUMNS` formatting cues

## Shared summary follow-through

When the shared Phase 9 reminders in the docs root, scripts root, tests root, sample-root boundary note, or reviewer-facing checklist are refreshed, they should point back to this sequencing note rather than trying to restate the owner split from scratch.

Keep that follow-through bounded to one shared summary at a time:

- `Documentation/zigux/README.md` for the docs-root packet summary
- `scripts/zigux/README.md` for the scripts-root validator and replay summary
- `zigux/tests/README.md` for the shared tests-root replay reminder
- `samples/zigux/README.md` only when the Phase 9 boundary wording there is being touched already
- `Documentation/zigux/review-checklist.md` for the reviewer-facing Phase 9 prompt

Only `samples/zigux/README.md` and `Documentation/zigux/review-checklist.md` should restate the bitmap-only top-bit companion or the older command and environment control boundaries; the docs root, scripts root, and tests root should keep pointing back here instead of duplicating those pilot-local reminders.

This keeps later closure-note work small while preserving the explicit split between the shared loader lane, the bitmap-only top-bit replay, the samples-root and checklist-facing command and environment boundaries, and the four pilot-family packets.

## Current live follow-through state

- `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` already keep this owner map or its shared-loader-versus-pilot split explicit on `master`
- `samples/zigux/README.md` already carries the bitmap-only top-bit companion reminder plus the older command and environment control boundaries, so later shared-loader follow-through should leave those pilot-local cues there instead of flattening them back into the loader packet
- `Documentation/zigux/review-checklist.md` now keeps the shared-loader split visible without the stale non-existent bitmap build path by naming the shipped `phase9-runtime-bitmap-top-bit-tests` step beside `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and it remains the reviewer-facing surface that also restates the older command and environment ownership boundaries
- the next same-lane follow-through should reopen only if one of the shared reminder surfaces drifts, or if the shared loader lane picks up a new bounded validation surface that needs to be named across the packet

## Recommended next-step order

1. shared loader lane: only when the change is about request-contract, allocator/init-flow, or build-only reviewability
2. shared reminder refresh: only if one of the docs-root, scripts-root, tests-root, samples-root, or checklist surfaces drifts again
3. bitmap lane: after that, only if the goal is to refine the already-landed top-bit or bitmap-specific replay packet
4. atomic64, trace-events, or kretprobe lanes: only when the change stays inside that family’s sample, loader, module, diff, or survey evidence

## Anti-overlap rule

If a scheduled Phase 9 run is assigned a pilot-family lane, keep the work inside that family’s packet plus the smallest unavoidable shared-loader touch. If the shared-loader lane is assigned, do not consume pilot-local backlog just because the shared lane has spare room.
