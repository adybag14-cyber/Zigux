# Phase 5 Sample Review Guide

This guide keeps the roadmap-backed Phase 5 lane reviewable without overstating what current `master` actually ships.

## Purpose

Use this guide when a change touches Phase 5 contributor guidance, one of the approved Linux sample anchors, or one of the shipped `samples/zigux/` reference-sample ports.

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

## Current repo reality on master

Fresh repo-first inspection for this guide shows that current `master` now ships the full four-sample non-runtime Phase 5 packet together with the shared contributor and replay surfaces that keep it reviewable.

Verified current shared Phase 5 review surfaces on `master` are:

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
* `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
* `make -C zigux phase5-test`
* `make -C zigux phase5`
* `.github/workflows/zigux-bootstrap.yml`

The same inspection also confirmed later runtime-facing sample surfaces are present on `master`, including the `runtime_atomic64`, `runtime_bitmap`, `runtime_kretprobe`, and `runtime_trace_events` families under `samples/zigux/`.

Do not count those later runtime-facing sample and loader surfaces as extra Phase 5 evidence. They belong to the separate Phase 9 runtime pilot lane.

## Review posture

Because the four approved Phase 5 samples are already landed on current `master`, same-lane follow-through should stay inside one of these bounded categories:

* contributor-guidance truthfulness fixes
* exact-readback repairs in shared review surfaces
* one sample-local replay, manifest, or survey-note repair at a time
* one shared README, checklist, or build-route sync at a time

Do not reopen sample behavior broadly unless a fresh repo-first inspection shows a concrete sample-backed drift in the shipped packet.

## Boundary reminders

Phase 5 stays non-runtime.

Do not treat later runtime-oriented loader or pilot work as extra Phase 5 samples. Keep runtime-facing delivery under the later runtime lane instead of using it to imply that the roadmap's non-runtime Phase 5 packet is larger than the four approved anchors.

Keep these no-extra-sample reminders explicit too:

* there is no standalone `samples/zigux/*string*` Phase 5 reference sample on current `master`; keep string-helper reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`; keep cmdline reviewability under `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/Makefile`, and `zigux/tests/phase7_build.zig` instead of counting cmdline as a fifth Phase 5 sample
* there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`; keep `argv_split` reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`; keep `rbtree` reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`; keep direct bitmap helper reviewability under the earlier helper and rollback packets while runtime bitmap work stays in the later runtime lane
* there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample on current `master`; keep the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` as the bounded formatting idiom cue while standalone formatting-helper evidence stays under the closed Phase 1 and bounded Phase 7 helper packets

Respect the freeze map too. Do not widen Phase 5 work toward freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`, and do not pull the study-only `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` families into this lane.

## Contributor checklist

Before landing a Phase 5 change, confirm:

* the roadmap anchor is one of the four approved Linux sample paths listed above
* the change says clearly whether it touches shared contributor guidance or one specific landed sample packet
* if a shared Phase 5 guide, README, checklist, survey note, manifest, test entrypoint, or make wrapper mentions a sample or replay route, that surface is actually present on current `master`
* the four-sample shared replay packet stays aligned around `zigux/tests/phase5_build.zig`, `zig build test --build-file zigux/tests/phase5_build.zig --summary all`, `make -C zigux phase5-test`, and `make -C zigux phase5`
* the change keeps runtime-substrate claims out of scope unless a later roadmap-backed runtime lane explicitly owns them
* later `runtime_*` sample and loader families remain clearly separated from the non-runtime Phase 5 packet

## Non-goals

This shared Phase 5 guide does not claim:

* procfs parity
* sysfs creation parity
* probe registration parity
* tracepoint macro parity
* user-copy parity
* module registration or loader wiring parity
* scheduler-facing, workqueue-facing, ring-buffer-facing, or other deep-core runtime substrate closure
