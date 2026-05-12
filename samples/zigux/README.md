# samples/zigux

This directory is the sample-root boundary for Zigux.

## Current repo reality on `master`

Current `master` keeps most of the bounded non-runtime Phase 5 reference-sample packet directly visible from this directory:

* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/trace_events_sample.zig`

Treat those directly readable files as part of the shipped non-runtime Phase 5 sample packet on current `master`.

The kobject anchor needs one narrower reminder here. Current shared Phase 5 guidance still treats `samples/kobject/kobject-example.c` as one of the four approved anchors, but direct public-tree readback for this lane is currently narrower than several shared reminders implied:

* `Documentation/zigux/phase5-kobject-sample-survey.md`
* `zigux/tests/phase5_kobject_example.zig`
* `zigux/tests/phase5_kobject_example_manifest.json`

Keep shared sample-root wording aligned with that narrower kobject packet until a fresh direct sample-root read confirms `samples/zigux/kobject_example.zig` is readable again on current `master`.

The same tree also still carries the later runtime-oriented sample family:

* `samples/zigux/runtime_atomic64.zig`
* `samples/zigux/runtime_atomic64_loader.zig`
* `samples/zigux/runtime_bitmap.zig`
* `samples/zigux/runtime_bitmap_loader.zig`
* `samples/zigux/runtime_bitmap_top_bit_contract.zig`
* `samples/zigux/runtime_kretprobe.zig`
* `samples/zigux/runtime_kretprobe_loader.zig`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_loader.zig`

Treat those files as the separate runtime sample family. Do not count them as extra Phase 5 evidence.

## Separate Phase 9 runtime pilot family

* `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` remains the shared owner map for the `runtime_loader` lane versus the four pilot-family packets, so the focused `phase9-runtime-bitmap-top-bit-tests` companion stays bitmap-local instead of drifting into shared loader evidence
* keep the older command and environment control boundary explicit too: `tools/lib/subcmd/exec-cmd.zig` still owns the deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` tooling cues, while `tools/lib/subcmd/help.zig` still owns the `LINES` and `COLUMNS` terminal-formatting cues; the Phase 9 loader packet remains a metadata-only handoff and should not be read as shipped runtime command or environment activation control on current `master`
* review the shipped Phase 9 runtime pilot family through `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, the focused `phase9-runtime-loader-shared-tests` step, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `.github/workflows/zigux-bootstrap.yml`, and `make -C zigux phase9`; keep those shared loader-handoff surfaces explicit, and keep `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root, and `depmod` script or manifest state explicit as blocked review-only module-metadata and depmod-publication boundaries instead of implying a dedicated `validate-phase9.py` route, a missing shared checker, a cleared runtime-substrate handoff, or shipped publication surfaces on current `master`

## Approved Phase 5 sample scope

The roadmap-backed Phase 5 sample anchors are still limited to these four Linux sample paths:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Those anchors remain the approved Phase 5 target set. On current `master`, shared contributor guidance should keep three directly readable `samples/zigux/*.zig` files explicit from this directory and keep the narrower kobject packet above explicit instead of restating a missing sample-root path as already readable.

## Contributor guidance

When touching Phase 5 contributor guidance:

* keep roadmap scope narrow to the four approved anchors above
* keep shared Phase 5 wording aligned with the directly readable `samples/zigux/bytestream_fifo.zig`, `samples/zigux/kretprobe_example.zig`, and `samples/zigux/trace_events_sample.zig` packet, and keep the kobject anchor aligned with `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` until the sample-root file is directly readable again
* do not treat review notes by themselves as proof of additional sample files beyond the current directly readable packet
* keep runtime-facing `runtime_*` files in the separate later runtime lane instead of folding them into Phase 5
* keep direct `bitmap` helper reviewability in its existing helper or runtime lanes instead of implying an extra Phase 5 sample

## Phase 7 no-sample boundaries

* current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample; keep that boundary under `Documentation/zigux/phase7-string-helpers-slice.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `lib/string_helpers.zig`, and `zigux/tests/phase7_build.zig`, and treat any new `samples/zigux/*string*.zig` file as review-blocking unless the roadmap lane is explicitly reopened
* current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; keep that boundary under `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `lib/cmdline.zig`, and `zigux/tests/phase7_build.zig`
* current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample; keep that boundary under `Documentation/zigux/phase7-argv-split-slice.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `lib/argv_split.zig`, `scripts/zigux/check-phase7-argv-split-packet.py`, and `zigux/tests/phase7_build.zig`
* current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample; keep that boundary under `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `lib/rbtree.zig`, `scripts/zigux/check-phase7-rbtree-parity.py`, and `zigux/tests/phase7_build.zig`

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

Use those shared surfaces to keep roadmap scope, contributor wording, the current directly readable Phase 5 packet plus the narrower kobject caveat, and the Phase 5-versus-runtime boundary honest.
