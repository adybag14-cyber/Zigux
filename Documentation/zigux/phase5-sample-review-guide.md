# Phase 5 Sample Review Guide

This guide keeps the roadmap-backed Phase 5 sample lane reviewable without letting a stale shared reminder surface override newer direct packet proof.

## Purpose

Use this guide when a change touches Phase 5 contributor guidance, one of the approved Linux sample anchors, or the shared tracing and probe reviewer surfaces.

The Phase 5 goal stays narrow:

* keep the approved Zigux idioms reviewable
* keep ownership and lifetime cues explicit
* keep exact review surfaces visible
* avoid widening non-runtime samples into runtime-substrate claims

## Roadmap anchors

Phase 5 is still scoped by the same four Linux sample anchors named in the roadmap:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Treat those four anchors as the approved Phase 5 destination set unless the roadmap changes.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-18 confirmed that current `master` now directly serves the core bytestream sample packet again through these paths:

* `samples/zigux/bytestream_fifo.zig`
* `zigux/tests/phase5_bytestream_fifo.zig`
* `zigux/tests/phase5_bytestream_fifo_survey.zig`

That same reread also confirmed that several bytestream companion surfaces still need to stay in the conservative bucket for now:

* `Documentation/zigux/phase5-kfifo-sample-survey.md`
* `zigux/tests/phase5_bytestream_fifo_manifest.json`
* `zigux/tests/phase5_build.zig`

Keep the direct bytestream proof and the still-missing companion surfaces split explicitly instead of flattening them back into one all-missing or all-restored packet.

The same 2026-05-18 repo-first inspection also confirmed that current `master` still keeps the shared non-runtime trace-events reminder packet in the narrower formatting-companion posture already reflected by the sample-root and tests-root reminder surfaces, while the older direct sample-local companions still need fresh reread proof before they can be treated as returned current-`master` evidence:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
* `Documentation/zigux/phase5-sample-lane-sequencing.md`
* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `samples/zigux/trace_events_string_formatting_sample.zig`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`

Treat that narrower shared reminder packet as the current concrete trace-events evidence in this lane.
Keep the bounded formatting companion explicit as a sibling cue inside the approved trace-events anchor rather than as a fourth returned direct sample-root port or a fifth sample.
Keep these older shared or sample-local paths framed as repo-reality gaps or current public-tree-backed companion evidence until a fresh reread proves they returned directly on `master`:

* `Documentation/zigux/phase5-trace-events-sample-survey.md`
* `samples/zigux/trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample_manifest.json`
* `zigux/tests/phase5_trace_events_sample_survey.zig`
* `zigux/tests/phase5_build.zig`

For the shared tracing and probe lane, ground reviewer guidance in the restored direct kretprobe packet plus the narrower trace-events reminder packet above and these shared reminder surfaces:

* `Documentation/zigux/phase5-kretprobe-sample-survey.md`
* `Documentation/zigux/phase5-sample-lane-sequencing.md`
* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`

Keep those shared surfaces honest about the restored direct kretprobe packet, the narrower trace-events formatting companion packet, and the current split between repo-reality gaps and current public-tree-backed companion evidence instead of treating the trace-events anchor as a restored direct packet or turning any companion route into direct authenticated proof.

## Bytestream posture

For `kfifo`, follow the restored direct packet through `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, and `zigux/tests/phase5_bytestream_fifo_survey.zig`.

Keep the current split explicit too:

* `Documentation/zigux/phase5-kfifo-sample-survey.md`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_build.zig` remain current public-tree-backed companion evidence or repo-reality gaps until a fresh reread proves direct authenticated proof again
* same-lane follow-through should repair one reminder surface at a time instead of reclassifying the whole bytestream packet from memory or older wording alone
* the lane still stays non-runtime and should not widen into procfs, user-copy, locking, runtime loader, or module-registration claims

## Tracing and probe posture

For `kretprobe`, follow the restored direct packet recorded in `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`, while keeping `zigux/tests/phase5_build.zig` framed only as current public-tree-backed companion evidence.

For `trace_events`, follow the narrower current reminder packet through `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, `samples/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, while keeping `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and `zigux/tests/phase5_build.zig` framed as repo-reality gaps or current public-tree-backed companion evidence rather than direct authenticated proof or a returned full packet.

Use the shared docs to preserve these bounded cues:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` keeps the selected-string plus `iter=%d` formatting cue bounded to the trace-events packet instead of turning it into a fifth Phase 5 sample
* `samples/zigux/trace_events_string_formatting_sample.zig` keeps the sibling formatting companion explicit through `selectedStringForIteration(...)`, the exact `iter=%d` buffer print, and the non-allocating lifecycle boundary around the bounded replay instead of standing in for the whole trace-events packet
* `Documentation/zigux/phase5-sample-lane-sequencing.md`, `samples/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` keep the shared reminder packet explicit about the narrower trace-events formatting companion packet and the still-bounded companion-evidence posture without widening into runtime claims
* `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig` keep the restored non-runtime kretprobe packet explicit without widening into the Phase 9 runtime family

## Ownership and lifetime posture

The roadmap still includes the `kobject` anchor, and fresh Phase 5 reread in this run kept the split evidence explicit: authenticated current-`master` contents readback still did not return the older sample-root or tests-root packet members that earlier reminder surfaces cited, while public-tree fallback still exposes the bounded packet below:

* `Documentation/zigux/phase5-kobject-sample-survey.md`
* `samples/zigux/kobject_example.zig`
* `zigux/tests/phase5_kobject_example.zig`
* `zigux/tests/phase5_kobject_example_manifest.json`
* `zigux/tests/phase5_kobject_example_survey.zig`
* `zigux/tests/phase5_build.zig`

Keep shared contributor guidance honest about that split instead of restating the older kobject packet as direct authenticated proof or flattening it into a pure missing-packet story.

Use the shared docs to preserve these bounded cues until a fresh reread restores direct authenticated proof for the whole packet:

* Phase 5 still owns the roadmap-backed `samples/kobject/kobject-example.c` anchor
* `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, `zigux/tests/phase5_kobject_example_survey.zig`, and `zigux/tests/phase5_build.zig` remain current public-tree-backed companion evidence rather than direct authenticated proof
* the lane still stays non-runtime and should not widen into sysfs creation, `kernel_kobj` integration, uevents, or module-registration claims
* same-lane follow-through should repair one shared reminder surface at a time instead of recreating missing sample-local ownership checklists from historical wording alone

## Approved idiom gap

Current `master` still ships no standalone `samples/zigux/*printf*` or `*vsprintf*` Phase 5 reference sample, and it still ships no standalone broad `*format*` Phase 5 reference sample outside the bounded trace-events cues carried by `samples/zigux/trace_events_string_formatting_sample.zig` and the shared reminder packet.

Keep the approved formatting idiom bounded to the selected-string plus `iter=%d` reminder carried by the trace-events review packet:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`

Do not describe that formatting cue as a fifth Phase 5 sample, a standalone formatting-helper port, or the whole proof of the trace-events packet.

## Review posture

Because current `master` keeps the restored direct bytestream packet, the restored direct kretprobe packet, the shared trace-events side in the narrower formatting-companion posture, and the `kobject` anchor in the public-tree-backed-companion-plus-authenticated-gap bucket, same-lane follow-through should stay inside these bounded categories:

* one bytestream reminder-surface truthfulness repair at a time
* one trace-events reminder-surface truthfulness repair at a time
* one trace-events approved-idiom-gap repair at a time
* one trace-events sample-root, tests-root, approved-idiom-gap, or shared-build reminder alignment repair at a time
* one kobject split-evidence reminder repair at a time

Avoid:

* treating the restored bytestream direct packet as permission to promote still-missing survey-note, manifest, or shared-build companions into direct authenticated proof
* treating the narrower trace-events reminder packet as a restored direct sample packet when current sample-root and tests-root rereads still keep the direct sample-local companions in the gap bucket
* treating `zigux/tests/phase5_build.zig` as direct authenticated proof while the current lane still only has bounded public-tree-backed confirmation for that shared build route
* treating the `kobject` anchor as a returned direct sample packet while current authenticated rereads still keep its older sample-root and tests-root packet members out of direct-proof status
* broadening the lane into runtime-loader, module-registration, procfs, sysfs, workqueue, or ring-buffer claims
* treating Phase 9 runtime samples as extra Phase 5 evidence
* treating the trace-events packet as permission to reopen unrelated bytestream, kobject, or kretprobe reminder work here

## Boundary reminders

Phase 5 stays non-runtime.

Keep later runtime-facing sample work under the separate Phase 9 lane.

Keep these no-extra-sample reminders explicit too:

* `samples/zigux/trace_events_string_formatting_sample.zig` is a bounded trace-events formatting companion, not a fifth Phase 5 anchor and not a standalone helper packet
* there is no standalone `samples/zigux/*string*` Phase 5 reference sample on current `master` outside the bounded trace-events formatting companion and the shared reminder packet
* there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`

Respect the freeze map too.
Do not widen Phase 5 work toward `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.