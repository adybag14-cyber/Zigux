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
- current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample; keep `rbtree` reviewability under `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, and `zigux/tests/phase7_build.zig` instead of counting it as a fifth Phase 5 sample
- the Kretprobe review packet lives in `samples/zigux/kretprobe_example.zig` and `zigux/tests/phase5_kretprobe_example_survey.zig`, keeping pre-init retargeting, the fixed `maxactive = 20` ceiling, timestamp-order rejection and recovery, and post-exit handler rejection explicit in the bounded Phase 5 sample lane
- the Phase 5 trace-events packet keeps `samples/zigux/trace_events_sample.zig` as the approved payload-and-callback idiom for the non-runtime selected-string, `iter=%d`, relative-location, and balanced register-then-unregister callback review surface
- review the four landed Phase 5 reference packets through `zig build test --build-file zigux/tests/phase5_build.zig --summary all`; keep any sample-local direct `zig test` replay and paired survey gate aligned with that shared packet instead of implying a separate runtime validation lane
- the Phase 5 trace-events packet still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` reference sample, so keep treating the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` as the approved formatting idiom cue
- standalone formatting-helper evidence stays under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet
- later runtime follow-ons stay under the separate Phase 9 `samples/zigux/runtime_*` family and should not be counted as extra Phase 5 reference anchors
