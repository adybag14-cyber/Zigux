# samples/zigux

This directory is the sample-root boundary for Zigux.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-13 directly recovered these approved non-runtime Phase 5 sample-root files from current `master`:

* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kobject_example.zig`

Treat those two files as the current directly readable sample-root evidence for the roadmap-backed Phase 5 lane.

The roadmap-approved kobject anchor stays directly reviewable through this narrower packet too:

* `Documentation/zigux/phase5-kobject-sample-survey.md`
* `samples/zigux/kobject_example.zig`
* `zigux/tests/phase5_kobject_example.zig`
* `zigux/tests/phase5_kobject_example_manifest.json`

Keep shared sample-root wording aligned with that directly readable kobject packet. Do not restate `zigux/tests/phase5_kobject_example_survey.zig` or `zigux/tests/phase5_build.zig` as direct readback evidence until those paths return.

The bytestream FIFO anchor is still directly readable at the sample root through `samples/zigux/bytestream_fifo.zig`, so contributor guidance here should keep the bounded in-memory FIFO idiom explicit without overstating the currently missing shared build packet.

The docs-root survey notes for the other two approved Phase 5 anchors remain part of the current review surface:

* `Documentation/zigux/phase5-kretprobe-sample-survey.md`
* `Documentation/zigux/phase5-trace-events-sample-survey.md`

But fresh direct readback in this run did not recover `samples/zigux/kretprobe_example.zig`, `samples/zigux/trace_events_sample.zig`, or the shared `zigux/tests/phase5_build.zig` route. Keep contributor wording aligned with those survey notes instead of treating the missing sample-root or shared-build paths as directly readable shipped evidence on current `master`.

## Separate Phase 9 runtime pilot family

Keep later runtime-facing sample work in the separate Phase 9 lane instead of counting it as extra Phase 5 evidence.

* keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` as the shared owner map for the runtime-loader lane versus the pilot-family packets
* keep older command and environment control boundaries under the existing tooling lanes instead of reading the runtime loader packet as shipped command or environment activation control
* if a proposed sample needs runtime-loader wiring, scheduler-visible execution, workqueue handoff, ring-buffer substrate, or other live kernel execution context to make its contract honest, route it to the separate runtime lane instead of widening Phase 5

Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep direct bitmap helper reviewability in its existing helper and runtime lanes instead of counting runtime-facing bitmap work as a fifth approved Phase 5 sample idiom.

## Approved Phase 5 sample scope

The roadmap-backed Phase 5 sample anchors are still limited to these four Linux sample paths:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Those anchors remain the approved Phase 5 target set.

On current `master`, shared contributor guidance from this directory should keep the two directly readable sample-root files `samples/zigux/bytestream_fifo.zig` and `samples/zigux/kobject_example.zig` explicit, keep the kobject anchor aligned with `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json`, and keep the kretprobe plus trace-events anchors routed through their survey notes until a fresh reread proves the missing sample-root and shared-build paths returned.

## Contributor guidance

When touching Phase 5 contributor guidance:

* keep roadmap scope narrow to the four approved anchors above
* treat `samples/zigux/bytestream_fifo.zig` and `samples/zigux/kobject_example.zig` as the current directly readable sample-root evidence from this directory
* keep the kobject anchor aligned with `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json`, and do not claim `zigux/tests/phase5_kobject_example_survey.zig` or `zigux/tests/phase5_build.zig` as direct evidence until a fresh reread proves they returned
* keep the bytestream anchor aligned with `samples/zigux/bytestream_fifo.zig` as the current direct sample-root idiom cue, and do not restate the missing shared `phase5_build.zig` route from this directory as directly readable evidence
* keep kretprobe and trace-events contributor wording aligned with `Documentation/zigux/phase5-kretprobe-sample-survey.md` and `Documentation/zigux/phase5-trace-events-sample-survey.md` until the missing sample-root and shared-build paths are directly readable again
* do not treat review notes by themselves as proof of additional current sample files beyond the direct readback recovered in this run
* keep runtime-facing `runtime_*` work in the separate later runtime lane instead of folding it into Phase 5
* keep direct `bitmap` helper reviewability in its existing helper or runtime lanes instead of implying an extra Phase 5 sample

## Phase 7 no-sample boundaries

* current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample; keep that boundary under `Documentation/zigux/phase7-string-helpers-slice.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_manifest.json`, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, `zigux/tests/phase7_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`, and treat any new `samples/zigux/*string*.zig` file as review-blocking unless the roadmap lane is explicitly reopened
* current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; keep that boundary under `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-build-wiring.py`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `zigux/tests/phase7_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`
* current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample; keep that boundary under `Documentation/zigux/phase7-argv-split-slice.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/check-phase7-build-wiring.py`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, `zigux/tests/phase7_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`
* current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample; keep that boundary under `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-rbtree-parity.py`, `scripts/zigux/check-phase7-build-wiring.py`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `zigux/tests/phase7_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`

## Boundary notes

Respect the freeze map here too.

* do not add Phase 5 follow-ons derived from freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
* keep the study-only `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` families out of this directory until a later roadmap-backed lane explicitly reopens that boundary
* if a proposed sample needs runtime-loader wiring, scheduler-visible execution, workqueue handoff, ring-buffer substrate, or other live kernel execution context to make its contract honest, route it to the separate runtime lane instead of widening Phase 5

## Review pointers

For shared Phase 5 guidance, use:

* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/review-checklist.md`
* `Documentation/zigux/README.md`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`

Use those shared surfaces to keep roadmap scope, contributor wording, the currently directly readable bytestream and kobject sample-root evidence, the narrower directly readable kobject tests packet, the survey-note-backed kretprobe and trace-events anchors, and the Phase 5-versus-runtime boundary honest.