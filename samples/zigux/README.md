# samples/zigux

This directory holds the bounded sample surfaces that Zigux uses for reviewable product evidence.

Current Phase 5 reference anchors
- `samples/zigux/bytestream_fifo.zig`
- `samples/zigux/kobject_example.zig`
- `samples/zigux/kretprobe_example.zig`
- `samples/zigux/trace_events_sample.zig`

Boundary notes
- the four anchors above remain the freeze-aware Phase 5 sample set on current `master`; do not silently treat helper follow-ons as extra Phase 5 reference samples just because they live under `samples/zigux/` on a draft branch
- if a proposed sample needs runtime-loader wiring, workqueue handoff, ring-buffer substrate, scheduler-visible execution, or other non-sample kernel execution context to make its contract honest, route it to the separate Phase 9 or Phase 14 packets instead of widening the four shipped Phase 5 reference anchors

Separate helper-backed sample packet
- `samples/zigux/string_helpers_sample.zig` is a bounded Phase 7 string-helper replay, not a fifth Phase 5 reference anchor
- the roadmap-backed Phase 7 product destination here still remains `lib/string_helpers.zig`; this draft sample stays supporting review evidence for that helper lane rather than an approved sample-root idiom on its own
- review that packet through `Documentation/zigux/phase7-string-helpers-slice.md`, `zigux/tests/phase7_string_helpers_sample_manifest.json`, `zigux/tests/phase7_string_helpers_sample_survey.zig`, and `zigux/tests/phase7_build.zig`
- keep the sample tied to the shared Phase 7 helper lane instead of treating it as a new standalone sample family
- current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample; keep cmdline reviewability under the shared Phase 7 helper packet instead of counting it as a fifth Phase 5 sample
- current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample; keep `argv_split` reviewability under the shared Phase 7 helper packet instead of counting it as a fifth Phase 5 sample
- current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample; keep `rbtree` reviewability under the shared Phase 7 helper packet instead of counting it as a fifth Phase 5 sample
- later runtime follow-ons stay under the separate Phase 9 `samples/zigux/runtime_*` family and should not be counted as extra Phase 5 reference anchors

Separate runtime pilot family
- existing `samples/zigux/runtime_*.zig` files stay in the separate Phase 9 runtime pilot family and are not extra Phase 5 anchors
