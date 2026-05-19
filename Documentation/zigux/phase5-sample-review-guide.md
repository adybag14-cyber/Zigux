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

Fresh repo-first inspection on 2026-05-19 confirmed that current `master` now directly serves the bounded bytestream sample-plus-tests packet through these paths:

* `Documentation/zigux/phase5-kfifo-sample-survey.md`
* `samples/zigux/bytestream_fifo.zig`
* `zigux/tests/phase5_bytestream_fifo.zig`
* `zigux/tests/phase5_bytestream_fifo_manifest.json`
* `zigux/tests/phase5_bytestream_fifo_survey.zig`

That same reread also confirmed that the shared build companion still needs to stay in the split-readback bucket for now:

* `zigux/tests/phase5_build.zig`

Keep the direct bytestream sample-plus-tests packet explicit while the shared build companion stays framed as current public-tree-backed evidence instead of flattening the packet back into a sample-only story or treating the shared build route as returned authenticated proof.
Fresh 2026-05-19 reread also keeps the current direct packet shape explicit: `samples/zigux/bytestream_fifo.zig` now carries three in-file self-checks, `zigux/tests/phase5_bytestream_fifo.zig` keeps four focused replay tests, and `zigux/tests/phase5_bytestream_fifo_survey.zig` keeps five survey-packet checks aligned with the survey note and manifest.

The same 2026-05-19 repo-first inspection also confirmed a narrower current non-runtime trace-events packet: authenticated contents reread still directly proves the bounded formatting companion, and the shared reminder surfaces below still keep that smaller packet explicit:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
* `Documentation/zigux/phase5-sample-lane-sequencing.md`
* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `scripts/zigux/check-phase5-review-guide-surface.py`
* `samples/zigux/trace_events_string_formatting_sample.zig`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`

Keep that narrower packet as the current concrete trace-events evidence in this lane.
Keep the bounded formatting companion explicit as a sibling cue inside the approved trace-events anchor rather than as a fourth returned direct sample-root port or a fifth sample.
Keep the missing-companion boundary explicit too:

* `Documentation/zigux/phase5-trace-events-sample-survey.md`
* `samples/zigux/trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample_manifest.json`
* `zigux/tests/phase5_trace_events_sample_survey.zig`
* `zigux/tests/phase5_build.zig`

Those paths remain public-tree-backed companion, repo-reality-gap, or historical support references on `master` until a fresh authenticated reread proves they returned directly.
Fresh public current-`master` fallback on 2026-05-19 also keeps the broader non-runtime trace-events sample packet visible through `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`, so same-lane guidance should treat authenticated-contents `404` results there as connector-local readback flakiness instead of repo absence while keeping `zigux/tests/phase5_build.zig` framed as companion evidence only.

For the shared tracing and probe lane, ground reviewer guidance in the restored direct kretprobe packet plus the narrower trace-events packet above and these shared reminder surfaces:

* `Documentation/zigux/phase5-kretprobe-sample-survey.md`
* `Documentation/zigux/phase5-sample-lane-sequencing.md`
* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `scripts/zigux/check-phase5-review-guide-surface.py`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`

Keep those shared surfaces honest about the restored direct kretprobe packet, the bounded trace-events formatting companion, the still-missing broader trace-events companion paths, and the shared-build gap instead of treating the trace-events anchor as either fully absent or fully restored authenticated proof.
Keep the dedicated scripts-side review-guide guard explicit too: `scripts/zigux/check-phase5-review-guide-surface.py` should stay aligned with those same shared surfaces instead of being treated as an optional companion.

## Bytestream posture

For `kfifo`, follow the restored direct sample-plus-tests packet through `Documentation/zigux/phase5-kfifo-sample-survey.md`, `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig`.
Current `master` keeps that packet sharper than the older sample-only story: `samples/zigux/bytestream_fifo.zig` now carries three in-file self-checks, `zigux/tests/phase5_bytestream_fifo.zig` keeps four focused replay tests, and `zigux/tests/phase5_bytestream_fifo_survey.zig` keeps five survey-packet checks aligned with the note and manifest.

Keep the current ten-cue review contract explicit in shared contributor guidance when a bytestream reminder surface is refreshed:

* `bounded_fifo_order`
* `wraparound_requeue`
* `peek_and_skip`
* `non_destructive_snapshot`
* `preview_truncation`
* `remaining_capacity`
* `queue_shape_boundaries`
* `helper_boundaries`
* `reset_and_replay`
* `ownership_and_lifetime`

Use the direct sample-plus-tests packet to keep the primary review surfaces visible too: `previewInto()`, `snapshotInto()`, `occupancySummary()`, `writableSpanSummary()`, `visibleSpanSummary()`, `usesWrappedStorageWindow()`, and the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle should stay easy to find from shared guidance instead of being left implicit in sample-local code only.

Keep the current split explicit too:

* `zigux/tests/phase5_build.zig` remains current public-tree-backed companion evidence until a fresh reread proves broader direct authenticated proof again
* same-lane follow-through should repair one reminder surface at a time instead of reclassifying the whole bytestream packet from memory or older wording alone
* the lane still stays non-runtime and should not widen into procfs, user-copy, locking, runtime loader, or module-registration claims

## Tracing and probe posture

For `kretprobe`, follow the restored direct packet recorded in `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`, while keeping `zigux/tests/phase5_build.zig` framed only as current public-tree-backed companion evidence.

Keep the current kretprobe contributor cues explicit in shared guidance too:

* `samples/zigux/kretprobe_example.zig` keeps `kernel_clone` as the default symbol name while allowing pre-init `retargetSymbol("do_sys_openat2")`
* `zig test samples/zigux/kretprobe_example.zig` and `zig test zigux/tests/phase5_kretprobe_example_survey.zig` stay explicit as the sample-owned self-check plus focused replay route, while the shared `zigux/tests/phase5_build.zig` line stays only current public-tree-backed companion evidence
* the direct packet keeps the pre-init-only `retargetMaxactive(3)` path, replay `maxactive = 20`, the single `my_data`-style entry timestamp word, the one-missed-instance summary, recovered duration `60`, and post-exit `recordMissedInstance()` rejection visible without implying runtime registration parity

For `trace_events`, follow the current bounded packet through `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, `samples/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and `zigux/tests/phase5_build.zig` framed as public-tree-backed companion, repo-reality-gap, or historical support references until a fresh authenticated reread proves they returned directly on current `master`.

Use the shared docs to preserve these bounded cues:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` keeps the selected-string plus `iter=%d` formatting cue bounded to the trace-events packet instead of turning it into a fifth Phase 5 sample
* `samples/zigux/trace_events_string_formatting_sample.zig` keeps the sibling formatting companion explicit through `selectedStringForIteration(...)`, the exact `iter=%d` buffer print, and the non-allocating lifecycle boundary around the bounded replay instead of standing in for the whole trace-events packet
* `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` stay in repo-reality-gap or historical-support wording until authenticated contents reread stops returning 404 for those paths
* `Documentation/zigux/phase5-sample-lane-sequencing.md`, `samples/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` keep the shared reminder packet explicit about that narrower trace-events posture without widening into runtime claims
* `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig` keep the restored non-runtime kretprobe packet explicit without widening into the Phase 9 runtime family

## Ownership and lifetime posture

The roadmap still includes the `kobject` anchor, and fresh Phase 5 reread in this run kept the split evidence explicit: authenticated current-`master` contents readback directly returned the survey note, sample root, focused test, and manifest-backed contract again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` still need public-tree fallback in this runtime.

Authenticated contents readback now directly returns these kobject packet members:

* `Documentation/zigux/phase5-kobject-sample-survey.md`
* `samples/zigux/kobject_example.zig`
* `zigux/tests/phase5_kobject_example.zig`
* `zigux/tests/phase5_kobject_example_manifest.json`

Fresh public current-`master` fallback still carries these companion paths:

* `zigux/tests/phase5_kobject_example_survey.zig`
* `zigux/tests/phase5_build.zig`

Keep shared contributor guidance honest about that split instead of flattening the whole kobject packet into public-tree-only support material, treating the sample-local direct proof as gone, or promoting the survey replay plus shared build route into returned authenticated proof.

Use the shared docs to preserve these bounded cues while that mixed packet remains in place:

* Phase 5 still owns the roadmap-backed `samples/kobject/kobject-example.c` anchor
* `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` remain current public-tree-backed companion evidence
* the lane still stays non-runtime and should not widen into sysfs creation, `kernel_kobj` integration, uevents, or module-registration claims
* same-lane follow-through should repair one shared reminder surface at a time instead of recreating missing sample-local ownership checklists from historical wording alone

### `kobject_example`

When shared contributor guidance needs the current kobject packet, keep this mixed direct-plus-public-tree-backed packet explicit.

The directly readable packet members are:

* `Documentation/zigux/phase5-kobject-sample-survey.md`
* `samples/zigux/kobject_example.zig`
* `zigux/tests/phase5_kobject_example.zig`
* `zigux/tests/phase5_kobject_example_manifest.json`

The current public-tree-backed companions are:

* `zigux/tests/phase5_kobject_example_survey.zig`
* `zigux/tests/phase5_build.zig`

Keep the approved Phase 5 in-memory ownership-and-lifetime idiom reviewable from the shared guide too:

* the initialized-but-not-registered zero-active-attributes boundary stays explicit through `runPreRegistrationBoundaryReplay()` instead of dissolving into broader lifecycle prose
* `ownershipSummary()` plus sample-owned `runOwnershipReplay()` keep the cold, initialized, registered, and exited snapshots plus the active-attribute-count progression visible from contributor-facing guidance
* the unnamed attribute-group shape, shared `baz` or `bar` dispatch, and the registered replay packet stay reviewable without reopening runtime-substrate claims
* keep the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit alongside the registered teardown, post-`exit()` rejection, and anchor-replay rejection packet

Keep the non-goal boundary equally explicit here:

* sysfs file creation parity
* `kernel_kobj` integration
* uevents
* loadable module registration

## Approved idiom gap

Current `master` still ships no standalone `samples/zigux/*printf*` or `*vsprintf*` Phase 5 reference sample, and it still ships no standalone broad `*format*` Phase 5 reference sample outside the bounded trace-events cues carried by `samples/zigux/trace_events_string_formatting_sample.zig` and the shared reminder packet.

Keep the approved formatting idiom bounded to the selected-string plus `iter=%d` reminder carried by the trace-events review packet:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`

Do not describe that formatting cue as a fifth Phase 5 sample, a standalone formatting-helper port, or the whole proof of the trace-events packet.

## Review posture

Because current `master` keeps the restored direct bytestream sample-plus-tests packet, the restored direct kretprobe packet, the shared trace-events side in a narrower posture with a direct formatting companion and older broader companion paths still in the repo-reality-gap bucket, and the `kobject` anchor in a mixed direct-plus-public-tree-backed split packet, same-lane follow-through should stay inside these bounded categories:

* one bytestream reminder-surface truthfulness repair at a time
* one trace-events reminder-surface truthfulness repair at a time
* one trace-events approved-idiom-gap repair at a time
* one trace-events survey-note, sample-root, tests-root, manifest, survey-replay, approved-idiom-gap, or shared-build reminder alignment repair at a time
* one kobject split-evidence reminder repair at a time

Avoid:

* treating the restored direct bytestream sample-plus-tests packet as permission to promote the shared `zigux/tests/phase5_build.zig` route into direct authenticated proof
* treating the narrower trace-events packet as either fully absent or fully direct authenticated sample proof when current `master` still keeps the bounded formatting companion direct, the older broader sample-local companion paths missing from authenticated contents reread, and the shared `zigux/tests/phase5_build.zig` route in support-material posture
* treating `zigux/tests/phase5_build.zig` as direct authenticated proof while the current lane still only has repo-reality-gap or historical-support wording for that shared build route
* treating the whole `kobject` packet as fully direct authenticated proof when current rereads still leave `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` in the public-tree-backed companion bucket
* broadening the lane into runtime-loader, module-registration, procfs, sysfs, workqueue, ring-buffer, or other runtime-substrate claims
* treating Phase 9 runtime samples as extra Phase 5 evidence
* treating the trace-events packet as permission to reopen unrelated bytestream, kobject, or kretprobe reminder work here

## Boundary reminders

Phase 5 stays non-runtime.

Keep later runtime-facing sample work under the separate Phase 9 lane.

Keep these no-extra-sample reminders explicit too:

* `samples/zigux/trace_events_string_formatting_sample.zig` is a bounded trace-events formatting companion, not a fifth Phase 5 anchor and not a standalone helper packet
* there is no standalone `samples/zigux/*string*` Phase 5 reference sample on current `master` outside the bounded trace-events formatting companion and the shared reminder packet
* there is no standalone `samples/zigux/*kasprintf*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*strarray*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`

Respect the freeze map too.
Do not widen Phase 5 work toward `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
