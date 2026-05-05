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
- later runtime follow-ons stay under the separate Phase 9 `samples/zigux/runtime_*` family and should not be counted as extra Phase 5 reference anchors
