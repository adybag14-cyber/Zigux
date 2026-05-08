# samples/zigux

This directory holds the bounded sample surfaces that Zigux uses for reviewable product evidence.

Current Phase 5 reference anchors
- `samples/zigux/bytestream_fifo.zig`
- `samples/zigux/kobject_example.zig`
- `samples/zigux/kretprobe_example.zig`
- `samples/zigux/trace_events_sample.zig`

Separate helper-backed sample packet
- `samples/zigux/string_helpers_sample.zig` is a bounded Phase 7 string-helper replay, not a fifth Phase 5 reference anchor
- review that packet through `Documentation/zigux/phase7-string-helpers-slice.md`, `zigux/tests/phase7_string_helpers_sample_manifest.json`, `zigux/tests/phase7_string_helpers_sample_survey.zig`, and `zigux/tests/phase7_build.zig`
- keep the sample tied to the shared Phase 7 helper lane instead of treating it as a new standalone sample family

Separate runtime pilot family
- existing `samples/zigux/runtime_*.zig` files stay in the separate Phase 9 runtime pilot family and are not extra Phase 5 anchors
