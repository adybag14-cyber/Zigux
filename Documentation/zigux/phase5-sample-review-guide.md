# Phase 5 Sample Review Guide

This guide keeps the roadmap-backed Phase 5 lane reviewable without overstating what current `master` directly proves.

## Purpose

Use this guide when a change touches Phase 5 contributor guidance, one of the approved Linux sample anchors, or a directly coupled sample-backed Phase 5 review surface.

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

Fresh repo-first inspection on 2026-05-11 confirmed that the shared Phase 5 contributor packet on current `master` still maps to one bounded non-runtime four-sample lane.

Directly re-read shared Phase 5 review surfaces in this inspection were:

  * `Documentation/zigux/phase5-sample-review-guide.md`
  * `Documentation/zigux/phase5-trace-events-sample-survey.md`
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/review-checklist.md`
  * `samples/zigux/README.md`
  * `scripts/zigux/README.md`
  * `zigux/tests/README.md`
  * `zigux/Makefile`
  * `zigux/tests/phase5_kobject_example.zig`

The same inspection also confirmed, through live current-`master` repo filename inventory, that the bounded Phase 5 packet still includes these sample-local anchors and their directly coupled replay surfaces:

  * `samples/zigux/bytestream_fifo.zig`
  * `samples/zigux/kobject_example.zig`
  * `samples/zigux/kretprobe_example.zig`
  * `samples/zigux/trace_events_sample.zig`
  * `zigux/tests/phase5_build.zig`
  * `zigux/tests/phase5_bytestream_fifo.zig`
  * `zigux/tests/phase5_bytestream_fifo_manifest.json`
  * `zigux/tests/phase5_bytestream_fifo_survey.zig`
  * `zigux/tests/phase5_kobject_example.zig`
  * `zigux/tests/phase5_kobject_example_manifest.json`
  * `zigux/tests/phase5_kobject_example_survey.zig`
  * `zigux/tests/phase5_kretprobe_example.zig`
  * `zigux/tests/phase5_kretprobe_example_manifest.json`
  * `zigux/tests/phase5_kretprobe_example_survey.zig`
  * `zigux/tests/phase5_trace_events_sample.zig`
  * `zigux/tests/phase5_trace_events_sample_manifest.json`
  * `zigux/tests/phase5_trace_events_sample_survey.zig`

That filename-backed confirmation is enough to keep the shared contributor map truthful for the full four-sample packet even when one specific content-read route is flaky for a sample-local file during inspection.

That same inspection also confirmed that later runtime-facing sample families are still present on `master`. Keep them under the separate Phase 9 lane instead of counting them as extra Phase 5 evidence:

  * `samples/zigux/runtime_atomic64_loader.zig`
  * `samples/zigux/runtime_kretprobe_loader.zig`
  * `samples/zigux/runtime_trace_events.zig`

## Review posture

Because the roadmap-backed Phase 5 lane is about reviewable idioms rather than runtime-substrate closure, same-lane follow-through should stay inside one of these bounded categories:

  * contributor-guidance truthfulness fixes
  * exact-readback repairs in shared review surfaces
  * one shared-route or packet-alignment repair at a time
  * one sample-local survey note, manifest, or replay-contract repair at a time when that exact landed surface can be read directly

For this shared guide specifically, prefer the strongest directly available evidence:

  * cite a Phase 5 sample-local path here as freshly re-read evidence only when that exact path content was re-read from current `master` during the inspection that motivates the wording
  * if a sample-local content-read route is flaky but live repo inventory confirms the exact path and the paired shared docs still point at the same bounded packet, it is still honest to describe that path as a current Phase 5 packet member rather than as missing evidence
  * keep local `make -C zigux phase5-test` and `make -C zigux phase5` routes described only as shipped wrapper claims when the shared `zigux/tests/phase5_build.zig` route is itself directly readable or is already anchored by the paired tests-root, scripts-root, sample-root, and docs-root packet surfaces in the same inspection
  * keep later `runtime_*` families separate from the non-runtime Phase 5 packet even when they are easier to read back than some sibling Phase 5 sample-local paths

## Boundary reminders

Phase 5 stays non-runtime.

Do not treat later runtime-oriented loader or pilot work as extra Phase 5 samples. Keep runtime-facing delivery under the later runtime lane instead of using it to imply that the roadmap's non-runtime Phase 5 packet is larger than the four approved anchors.

Keep these no-extra-sample reminders explicit too:

  * there is no standalone `samples/zigux/*string*` Phase 5 reference sample on current `master`; keep string-helper reviewability under the Phase 7 helper packet
  * there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`; keep cmdline reviewability under the Phase 7 helper packet
  * there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`; keep `argv_split` reviewability under the Phase 7 helper packet
  * there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`; keep `rbtree` reviewability under the Phase 7 helper packet
  * there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`; keep direct bitmap helper reviewability under the earlier helper and rollback packets while runtime bitmap work stays in the later runtime lane
  * there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample on current `master`; keep the approved formatting idiom cue bounded to the selected-string plus `iter=%d` replay documented for the trace-events packet instead of implying a fifth formatting anchor

Respect the freeze map too. Do not widen Phase 5 work toward freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`, and do not pull the study-only `kernel/workqueue.c` plus `kernel/trace/ring_buffer.c` families into this lane.

## Contributor checklist

Before landing a Phase 5 shared-guidance change, confirm:

  * the roadmap anchor is one of the four approved Linux sample paths listed above
  * the change says clearly whether it touches shared contributor guidance or one specific directly readable sample-backed surface
  * if a shared Phase 5 guide, README, checklist, survey note, manifest, test entrypoint, or make wrapper mentions a sample or replay route, that exact surface is directly readable on current `master` or confirmed as a current packet member by live repo inventory plus aligned shared packet surfaces
  * if a landed sample contract changes, the directly coupled survey note or manifest-backed contributor prompts move with it instead of lagging behind the sample code
  * the lane keeps runtime-substrate claims out of scope unless a later roadmap-backed runtime lane explicitly owns them
  * later `runtime_*` sample and loader families remain clearly separated from the non-runtime Phase 5 packet

## Focused cue from directly re-read evidence

The most concrete directly re-read sample-backed surface in this inspection was `zigux/tests/phase5_kobject_example.zig`.

That focused test surface still keeps the roadmap `samples/kobject/kobject-example.c` anchor explicit together with:

  * the initialized-but-not-registered boundary via `runPreRegistrationBoundaryReplay()`
  * the already-registered duplicate-registration and replay-restart rejection packet via `runRegisteredBoundaryReplay()`
  * the shared `baz` or `bar` dispatch plus parse-failure visibility via `runInputValidationReplay()`
  * the lifecycle packet via `runOwnershipReplay()`
  * the teardown reset and post-exit rejection packet via `runTeardownReplay()`

Use that directly re-read kobject surface as the strongest concrete reminder in this guide until a future run re-verifies more of the sibling Phase 5 sample-local packet directly.

## Non-goals

This shared Phase 5 guide does not claim:

  * procfs parity
  * sysfs creation parity
  * probe registration parity
  * tracepoint macro parity
  * user-copy parity
  * module registration or loader wiring parity
  * scheduler-facing, workqueue-facing, ring-buffer-facing, or other deep-core runtime substrate closure

## Footer
