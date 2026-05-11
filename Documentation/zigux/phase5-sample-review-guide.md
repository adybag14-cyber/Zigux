# Phase 5 Sample Review Guide

This guide keeps the roadmap-backed Phase 5 lane reviewable without overstating what current `master` actually exposes through direct file reads.

## Purpose

Use this guide when a change touches Phase 5 contributor guidance, one of the approved Linux sample anchors, or one of the landed `samples/zigux/` reference-sample ports.

The roadmap-backed goal for Phase 5 is still narrow:

* make approved Zigux idioms reviewable and repeatable
* keep ownership and lifetime cues explicit
* keep exact replay routes visible
* avoid widening non-runtime samples into runtime-substrate claims

## Roadmap anchors

Phase 5 is still scoped by the four Linux sample anchors named in the roadmap:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Treat those anchors as the approved Phase 5 destination set unless the roadmap changes.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-11 found the full four-anchor non-runtime Phase 5 packet readable on current `master`.

Directly readable shared contributor surfaces still present on current `master` are:

* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/phase5-kfifo-sample-survey.md`
* `Documentation/zigux/phase5-kobject-sample-survey.md`
* `Documentation/zigux/phase5-kretprobe-sample-survey.md`
* `Documentation/zigux/phase5-trace-events-sample-survey.md`
* `Documentation/zigux/README.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`
* `zigux/Makefile`
* `.github/workflows/zigux-bootstrap.yml`

Directly readable landed non-runtime Phase 5 sample anchors are currently:

* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kobject_example.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/trace_events_sample.zig`

The shared replay route and directly coupled trace-events review surfaces are also readable together on current `master`:

* `zigux/tests/phase5_build.zig`
* `zigux/tests/phase5_trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample_manifest.json`
* `zigux/tests/phase5_trace_events_sample_survey.zig`

That same inspection still confirmed that later runtime-facing sample families are present on `master`. Keep them under the separate Phase 9 lane instead of counting them as extra Phase 5 evidence:

* `samples/zigux/runtime_atomic64.zig`
* `samples/zigux/runtime_atomic64_loader.zig`
* `samples/zigux/runtime_bitmap.zig`
* `samples/zigux/runtime_bitmap_loader.zig`
* `samples/zigux/runtime_bitmap_top_bit_contract.zig`
* `samples/zigux/runtime_kretprobe.zig`
* `samples/zigux/runtime_kretprobe_loader.zig`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_loader.zig`

## Review posture

Because the readable Phase 5 packet now includes all four roadmap-backed non-runtime anchors, same-lane follow-through should stay inside one of these bounded categories:

* contributor-guidance truthfulness fixes
* exact-readback repairs in shared review surfaces
* one shared-route or packet-alignment repair at a time
* one sample-local survey-note, manifest, or replay-contract update at a time when the coupled landed sample changes
* one no-extra-sample boundary repair at a time when a shared Phase 5 surface starts drifting toward helper, runtime, or freeze-map families that do not belong in the Phase 5 packet

Treat the current Phase 5 packet as intentionally non-runtime and fully four-anchor on current `master`:

* the directly readable non-runtime packet on current `master` is the four-anchor `bytestream_fifo`, `kobject_example`, `kretprobe_example`, and `trace_events_sample` set
* the roadmap-backed job in this lane is to keep those sample packets and their shared contributor surfaces truthful and aligned
* local or workflow wording should not fall back to older "trace-events is still missing" claims while the sample-local and shared replay surfaces are readable together again

Do not reopen sample behavior broadly, and do not count runtime-loader or runtime-pilot work as part of the non-runtime Phase 5 packet.

## Boundary reminders

Phase 5 stays non-runtime.

Do not treat later runtime-oriented loader or pilot work as extra Phase 5 samples. Keep runtime-facing delivery under the later runtime lane instead of using it to imply that the roadmap's non-runtime Phase 5 packet is larger than the four directly readable landed anchors.

Keep these no-extra-sample reminders explicit too:

* there is no standalone `samples/zigux/*string*` Phase 5 reference sample on current `master`; keep string-helper reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`; keep cmdline reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`; keep `argv_split` reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`; keep `rbtree` reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`; keep direct bitmap helper reviewability under the earlier helper and rollback packets while runtime bitmap work stays in the later runtime lane
* there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample on current `master`; keep the approved formatting idiom cue tied to the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig`

Respect the freeze map too. Do not widen Phase 5 work toward freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`, and do not pull the study-only `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` families into this lane.

## Contributor checklist

Before landing a Phase 5 change, confirm:

* the roadmap anchor is one of the four approved Linux sample paths listed above
* the change says clearly whether it touches shared contributor guidance or one specific landed sample packet
* if a shared Phase 5 guide, README, checklist, survey note, manifest, test entrypoint, or make wrapper mentions a sample or replay route, that surface is directly readable on current `master`
* if a shared doc claims a sample-local survey note is part of the shipped packet, that exact survey note path is directly readable instead of being inferred from a sibling sample or older wording
* if a shared doc claims a sample-local replay route, the corresponding sample file, paired tests, paired manifest, and build entrypoint can all be read directly from the repo instead of being inferred from stale wording alone
* if the shared packet mentions the non-runtime trace-events anchor, keep `samples/zigux/trace_events_sample.zig`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and `zigux/tests/phase5_build.zig` explicit together, and keep `ownershipSummary()` plus sample-owned `runOwnershipReplay()` explicit across that same shared reviewer packet instead of letting ownership-lifetime cues drift behind the payload, formatting, and callback helpers
* if a landed sample contract changes, the directly coupled survey note or manifest-backed contributor prompts move with it instead of lagging behind the sample code
* if shared guidance touches the landed `kretprobe` packet, keep sample-owned `runRetargetReplay()`, `runLifecycleGuardReplay()`, the fixed `maxactiveBudget()` cue at `20`, `ownershipSummary()` plus `runOwnershipReplay()`, and `runRecoveryReplay()` with timestamp-order rejection, recovery, and post-exit handler rejection explicit across the guide, survey note, checklist, sample root, and any directly readable shared replay route
* the lane keeps runtime-substrate claims out of scope unless a later roadmap-backed runtime lane explicitly owns them
* later `runtime_*` sample and loader families remain clearly separated from the non-runtime Phase 5 packet

## Focused Sample Cues

### `trace_events_sample`

Review the landed trace-events packet through `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and the shared `zigux/tests/phase5_build.zig` replay route.

Keep `formattedMessage()`, the selected-string plus `iter=%d` replay, `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, `runCallbackBoundaryReplay()`, `ownershipSummary()` plus sample-owned `runOwnershipReplay()`, the exact `checked_focus` order, restored registration balance, `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection, post-exit replay and callback-registration rejection, docs-root and sample-root contributor surfaces, and the Phase 5-versus-Phase 9 boundary explicit together as one bounded non-runtime packet.

Keep the no-extra-formatting reminder explicit too: no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample.

### `kretprobe_example`

Review the landed kretprobe packet through `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`.

Keep pre-init retargeting, `runLifecycleGuardReplay()` plus the pre-init and post-init guard boundaries, the fixed `maxactiveBudget()` cue at `20`, `runRecoveryReplay()` plus outstanding-instance rejection, timestamp-order rejection and recovery plus post-exit handler rejection, and the sample-owned lifecycle summary packet explicit.

Current `master` still ships no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, or direct `*bitmap*` Phase 5 reference sample. Keep `tools/lib/bitmap.zig`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/tests/phase9_build.zig` under their existing helper, rollback, and runtime lanes instead of treating bitmap as a shared Phase 5 approved idiom.

## Non-goals

This shared Phase 5 guide does not claim:

* procfs parity
* sysfs creation parity
* probe registration parity
* tracepoint macro parity
* user-copy parity
* module registration or loader wiring parity
* scheduler-facing, workqueue-facing, ring-buffer-facing, or other deep-core runtime substrate closure