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
- the Phase 5 trace-events packet still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` reference sample, so keep treating the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` as the approved formatting idiom cue
- standalone formatting-helper evidence stays under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet
- later runtime follow-ons stay under the separate Phase 9 `samples/zigux/runtime_*` family and should not be counted as extra Phase 5 reference anchors
