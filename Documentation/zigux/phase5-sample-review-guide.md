# Phase 5 Sample Review Guide

This guide keeps the roadmap-backed Phase 5 sample lane reviewable without pretending that every older sample-root or tests-root path is directly readable on current `master`.

## Purpose

Use this guide when a change touches Phase 5 contributor guidance, one of the approved Linux sample anchors, or one of the current `samples/zigux/` reference-sample ports.

The roadmap-backed goal for Phase 5 is still narrow:

* make approved Zigux idioms reviewable and repeatable
* keep ownership and lifetime cues explicit
* keep exact review surfaces visible
* avoid widening non-runtime samples into runtime-substrate claims

## Roadmap anchors

Phase 5 is still scoped by the four Linux sample anchors named in the roadmap:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Treat those anchors as the approved Phase 5 destination set unless the roadmap changes.

## Current repo reality on `master`

Fresh GitHub-app readback on 2026-05-14 in this run confirmed that current `master` still carries the bounded four-anchor Phase 5 packet together with its shared contributor surfaces, but the directly readable sample-local evidence is mixed rather than fully restored across every anchor.

The shared reminder surfaces presently present on `master` are:

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

The directly readable sample-local evidence recovered in this run is:

* the bytestream packet through `Documentation/zigux/phase5-kfifo-sample-survey.md` plus `samples/zigux/bytestream_fifo.zig`
* the kobject packet through `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json`
* the trace-events packet through `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`
* the kretprobe anchor through `Documentation/zigux/phase5-kretprobe-sample-survey.md` only

Within that shared reminder set, the current aligned surfaces for the kretprobe-gap story are:

* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/phase5-kretprobe-sample-survey.md`
* `Documentation/zigux/review-checklist.md`
* `Documentation/zigux/README.md`
* `samples/zigux/README.md`
* `scripts/zigux/README.md`

Those shared reminder surfaces now keep the missing `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example*`, and `zigux/tests/phase5_build.zig` packet explicit, keep the bytestream anchor narrowed to its survey-note-plus-sample evidence, keep the kobject anchor narrowed to its note-plus-sample-plus-tests evidence, and keep the directly readable trace-events packet distinct from the later Phase 9 runtime family.

Direct readback in this run did not recover these older Phase 5 packet paths:

* `samples/zigux/kretprobe_example.zig`
* `zigux/tests/phase5_build.zig`
* `zigux/tests/phase5_bytestream_fifo.zig`
* `zigux/tests/phase5_bytestream_fifo_manifest.json`
* `zigux/tests/phase5_bytestream_fifo_survey.zig`
* `zigux/tests/phase5_kobject_example_survey.zig`
* `zigux/tests/phase5_kretprobe_example.zig`
* `zigux/tests/phase5_kretprobe_example_manifest.json`
* `zigux/tests/phase5_kretprobe_example_survey.zig`

Keep shared contributor wording aligned with that mixed packet instead of repeating a fully restored sample-root-plus-tests story that current readback does not support.

That same inspection also confirmed that later runtime-facing sample families are still present on `master`. Keep them under the separate Phase 9 lane instead of counting them as extra Phase 5 evidence:

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

Because the four approved Phase 5 anchors are still the intended packet, same-lane follow-through should stay inside one of these bounded categories:

* contributor-guidance truthfulness fixes
* exact-readback repairs in shared review surfaces
* one shared-route or packet-alignment repair at a time
* one sample-local survey-note, manifest, or replay-contract update at a time when the coupled landed sample changes

Treat the current Phase 5 packet as landed but intentionally non-runtime:

* keep the roadmap-backed four-anchor scope explicit even when one or more sample-local files are not directly readable in this run
* shared docs that describe those anchors should distinguish direct-readback evidence from survey-note-only evidence instead of flattening every sample into the same packet shape
* when one reminder surface is already aligned, do not smooth over the remaining stale ones; keep the aligned-versus-drifted split explicit so same-lane follow-through can stay one shared surface at a time
* do not describe `zigux/tests/phase5_build.zig`, `make -C zigux phase5-test`, or `make -C zigux phase5` as current directly readable proof surfaces unless a fresh reread confirms those exact paths again
* do not reopen sample behavior broadly, and do not count runtime-loader or runtime-pilot work as part of the non-runtime Phase 5 packet

## Shared ownership map

When Phase 5 follow-through is doc-only, keep the shared-versus-sample-local split explicit so reminder-surface work does not reopen neighboring sample packets by accident.

* shared Phase 5 packet work belongs in `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` only when the change preserves the same four-sample non-runtime packet and the same direct-readback caveats recorded above
* within that shared set, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now reflect the same survey-note-only kretprobe posture, the narrower bytestream and kobject packets, and the directly readable trace-events packet, so future shared-surface follow-through should start from whichever one-file reminder surface actually drifts next instead of reopening this already-aligned split
* bytestream packet work currently belongs in `Documentation/zigux/phase5-kfifo-sample-survey.md` plus `samples/zigux/bytestream_fifo.zig`; do not restate the older bytestream tests-root or shared-build packet as directly readable evidence until a fresh reread proves those paths returned
* kobject packet work currently belongs in `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json`; do not restate `zigux/tests/phase5_kobject_example_survey.zig` or the broader shared-build packet as directly readable evidence until a fresh reread proves they returned
* trace-events packet work currently belongs in `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`; do not restate the missing shared `phase5_build.zig` route as directly readable evidence until a fresh reread proves it returned
* kretprobe packet work currently belongs in `Documentation/zigux/phase5-kretprobe-sample-survey.md`; do not restate the older sample-root, focused-test, manifest, survey-replay, or shared-build packet as directly readable evidence until a fresh reread proves those paths returned
* if a shared doc needs to remind reviewers about one sample-specific ownership cue, point to the exact currently readable packet for that sample instead of re-describing behavior from memory or borrowing cues from a different sample family
* keep the later `samples/zigux/runtime_*.zig` and `*_loader.zig` families out of shared Phase 5 reminder work unless the only purpose is to restate the already-landed Phase 5-versus-Phase 9 boundary

## Boundary reminders

Phase 5 stays non-runtime.

Do not treat later runtime-oriented loader or pilot work as extra Phase 5 samples. Keep runtime-facing delivery under the later runtime lane instead of using it to imply that the roadmap's non-runtime Phase 5 packet is larger than the four approved anchors.

Keep these no-extra-sample reminders explicit too:

* there is no standalone `samples/zigux/*string*` Phase 5 reference sample on current `master`; keep string-helper reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`; keep cmdline reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`; keep `argv_split` reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`; keep `rbtree` reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`; keep direct bitmap helper reviewability under the earlier helper and rollback packets while runtime bitmap work stays in the later runtime lane
* there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample on current `master`; keep the approved formatting idiom cue bounded to the selected-string plus `iter=%d` reminder carried by the directly readable `trace_events_sample` packet while standalone formatting-helper evidence stays under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet

Respect the freeze map too. Do not widen Phase 5 work toward freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`, and do not pull the study-only `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` families into this lane.

## Contributor checklist

Before landing a Phase 5 change, confirm:

* the roadmap anchor is one of the four approved Linux sample paths listed above
* the change says clearly whether it touches shared contributor guidance or one specific landed sample packet
* if a shared Phase 5 guide, README, checklist, survey note, manifest, test entrypoint, or make wrapper mentions a sample or replay route, that surface is directly readable on current `master`
* if a shared doc claims a sample-local replay route or build route, do not infer it from older wording alone; confirm the exact path is directly readable first
* keep `scripts/zigux/README.md` aligned with the same survey-note-only kretprobe posture, the narrower bytestream and kobject packets, and the directly readable trace-events packet already reflected here; if a future reread changes any of those packet shapes, update the shared scripts reminder in the same bounded pass instead of treating it as preexisting drift
* keep the bytestream packet aligned with `Documentation/zigux/phase5-kfifo-sample-survey.md` plus `samples/zigux/bytestream_fifo.zig` until the older tests-root and shared-build companion paths are directly readable again, and when the sample adds or renames reviewability helpers make the shared bytestream cues here move with surfaces such as `runRemainingCapacityReplay()`, `occupancySummary()`, and `writableSpanSummary()` instead of leaving the guide pinned to an older narrower subset
* keep the kobject packet aligned with `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json`, and do not restate `zigux/tests/phase5_kobject_example_survey.zig` or `zigux/tests/phase5_build.zig` as current direct evidence unless a fresh reread proves they returned
* keep the trace-events packet aligned with `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`, and do not restate `zigux/tests/phase5_build.zig` as current direct evidence unless a fresh reread proves it returned
* keep the kretprobe packet aligned with `Documentation/zigux/phase5-kretprobe-sample-survey.md` until `samples/zigux/kretprobe_example.zig`, its focused tests-root companions, and the shared build route are directly readable again
* if a landed sample contract changes, the directly coupled survey note or manifest-backed contributor prompts move with it instead of lagging behind the sample code
* the lane keeps runtime-substrate claims out of scope unless a later roadmap-backed runtime lane explicitly owns them
* later `runtime_*` sample and loader families remain clearly separated from the non-runtime Phase 5 packet

## Focused sample cues

### `bytestream_fifo`

Review the currently readable bytestream packet through `Documentation/zigux/phase5-kfifo-sample-survey.md` and `samples/zigux/bytestream_fifo.zig`.

Keep `StorageBacking.embedded_fixed_buffer`, `previewInto()`, `snapshotInto()`, `runPreviewBoundaryReplay()`, `runWrappedPreviewReplay()`, `runRemainingCapacityReplay()`, the replay-visible preview markers, `occupancySummary()` plus `writableSpanSummary()` for cold, full, and wrapped-window reviewability, the short-drain `"hel"` plus queued `"lo"` helper boundary, the explicit queue-shape helpers around `available()`, `visibleSpanSummary()`, and `usesWrappedStorageWindow()`, and the `init()` -> `runAnchorReplay()` -> `exit()` ownership path explicit together as one bounded non-runtime packet.

Keep the survey note truthful about direct readback: if the bytestream-focused tests-root, manifest, survey replay, or shared `phase5_build.zig` route are mentioned again here, re-verify those exact paths first instead of borrowing older restored-path wording.

### `kobject_example`

Review the currently readable kobject packet through `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json`.

Keep `runAnchorReplay()` explicit for the init-first, exact-three-attribute registration cue, `runPreRegistrationBoundaryReplay()` explicit for the initialized-but-not-registered zero-active-attributes plus show-or-store rejection boundary, `runRegisteredBoundaryReplay()` explicit for the already-registered duplicate-registration and replay-restart rejection packet plus the still-usable bounded foo roundtrip afterward, `runInputValidationReplay()` explicit for the shared `baz`/`bar` dispatch and parse-failure packet while the sample stays registered, `runTeardownReplay()` explicit for the registered teardown reset plus post-`exit()` rejection packet, `ownershipSummary()` plus sample-owned `runOwnershipReplay()` explicit for the lifecycle packet, the unnamed attribute-group shape, and the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split together as one bounded non-runtime packet.

### `kretprobe_example`

Review the current kretprobe anchor through `Documentation/zigux/phase5-kretprobe-sample-survey.md` only until a fresh reread proves the older sample-root, focused-test, manifest, survey-replay, and shared-build paths returned.

Keep shared guidance aligned with that survey-note-only posture instead of repeating the older restored-path caveat or treating missing sample-local paths as directly readable proof.

### `trace_events_sample`

Review the currently readable trace-events packet through `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`.

Keep `formattedMessage()`, `runPayloadBoundaryReplay()`, `runCallbackBoundaryRecoveryReplay()`, `runStringFormattingCycleReplay()`, and `runLifecycleBoundaryReplay()` explicit together with the selected-string plus `iter=%d` formatting cue, the exact `checked_focus` order, the full modulo-selected string cycle across counts `0` through `4`, the registration-first callback path, the restored zero-depth registration balance, the public lifecycle summary, the underflow plus `OutstandingRegistration` rejection packet, and the post-`exit()` replay rejection boundary as one bounded non-runtime packet.

## Non-goals

This shared Phase 5 guide does not claim:

* procfs parity
* sysfs creation parity
* probe registration parity
* tracepoint macro parity
* user-copy parity
* module registration or loader wiring parity
* scheduler-facing, workqueue-facing, ring-buffer-facing, or other deep-core runtime substrate closure