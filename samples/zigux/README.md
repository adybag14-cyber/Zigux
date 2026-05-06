# samples/zigux

This directory holds the bounded Phase 5 reference samples for Zigux.

Current Phase 5 reference anchors
- `samples/zigux/bytestream_fifo.zig`
- `samples/zigux/kobject_example.zig`
- `samples/zigux/kretprobe_example.zig`
- `samples/zigux/trace_events_sample.zig`

Boundary notes
- current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample; treat any new `samples/zigux/*string*.zig` file as review-blocking until the roadmap boundary is revisited
- the separate string-helper packet lives under `Documentation/zigux/phase7-string-helpers-slice.md`, `lib/string_helpers.zig`, and `zigux/tests/phase7_build.zig`
- current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; keep cmdline reviewability under `Documentation/zigux/phase7-cmdline-slice.md`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, and `zigux/tests/phase7_build.zig` instead of counting it as a fifth Phase 5 sample
- current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample; keep `rbtree` reviewability under `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, and `zigux/tests/phase7_build.zig` instead of counting it as a fifth Phase 5 sample
- the Phase 5 bytestream FIFO packet keeps `samples/zigux/bytestream_fifo.zig` as the approved in-memory queue-order and ownership-and-lifetime idiom for the roadmap's `samples/kfifo/bytestream-example.c` anchor
- review that FIFO packet through `Documentation/zigux/phase5-kfifo-sample-survey.md`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and `zig build test --build-file zigux/tests/phase5_build.zig --summary all` plus `make -C zigux phase5`; keep procfs, `kfifo_from_user()`, `kfifo_to_user()`, locking, and module registration out of scope until a later runtime-backed lane lands the needed substrate
- the Phase 5 kobject packet keeps `samples/zigux/kobject_example.zig` as the approved in-memory ownership-and-lifetime idiom for the roadmap's `samples/kobject/kobject-example.c` anchor
- review that kobject packet through `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, `zigux/tests/phase5_kobject_example_survey.zig`, and `zig build test --build-file zigux/tests/phase5_build.zig --summary all` plus `make -C zigux phase5`; keep sysfs creation, `kernel_kobj` integration, uevents, and module registration out of scope until a later runtime-backed lane lands the needed substrate
- the Kretprobe review packet lives in `samples/zigux/kretprobe_example.zig`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`, keeping pre-init retargeting, the fixed `maxactive = 20` ceiling, timestamp-order rejection and recovery, post-exit handler rejection, and the shared `phase5_build.zig` replay route explicit in the bounded Phase 5 sample lane
- the Phase 5 trace-events packet keeps `samples/zigux/trace_events_sample.zig` as the approved payload-and-callback idiom for the non-runtime selected-string, `iter=%d`, relative-location, and balanced register-then-unregister callback review surface
- the trace-events review packet lives in `samples/zigux/trace_events_sample.zig`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`, keeping the public `runPayloadBoundaryReplay()` helper, bounded vararg-payload plus relative-location cues, and the shared `phase5_build.zig` replay route explicit in the bounded Phase 5 sample lane
- review the four landed Phase 5 reference packets through `zig build test --build-file zigux/tests/phase5_build.zig --summary all` and `make -C zigux phase5`; keep any sample-local direct `zig test` replay and paired survey gate aligned with that shared packet instead of implying a separate runtime validation lane
- the Phase 5 trace-events packet still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` reference sample, so keep treating the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` as the approved formatting idiom cue
- standalone formatting-helper evidence stays under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet
- later runtime follow-ons stay under the separate Phase 9 `samples/zigux/runtime_*` family and should not be counted as extra Phase 5 reference anchors

Separate Phase 9 runtime pilot family
- `samples/zigux/runtime_atomic64.zig` and `samples/zigux/runtime_atomic64_loader.zig` keep the `lib/atomic64_test.c` starter and loader handoff distinct from the Phase 5 sample packet
- `samples/zigux/runtime_bitmap.zig` and `samples/zigux/runtime_bitmap_loader.zig` keep the `lib/test_bitmap.c` starter and loader handoff distinct from the Phase 5 sample packet
- `samples/zigux/runtime_trace_events.zig` and `samples/zigux/runtime_trace_events_loader.zig` keep the runtime trace-events pilot separate from the approved non-runtime `samples/zigux/trace_events_sample.zig` reference sample
- `samples/zigux/runtime_kretprobe.zig` and `samples/zigux/runtime_kretprobe_loader.zig` keep the runtime kretprobe pilot separate from the approved non-runtime `samples/zigux/kretprobe_example.zig` reference sample
- review the shipped Phase 9 runtime pilot family through `zigux/tests/phase9_build.zig`, the focused `phase9-runtime-loader-shared-tests` step, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `make -C zigux phase9`; keep those shared loader-handoff surfaces explicit instead of implying a dedicated `validate-phase9.py` route or a cleared runtime-substrate handoff on current `master`
