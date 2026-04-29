# Zigux Samples

This directory is the shared sample root for Zigux reference patterns and later runtime starter work.

Phase 5 reference samples
- `samples/zigux/bytestream_fifo.zig`
- `samples/zigux/kobject_example.zig`
- `samples/zigux/kretprobe_example.zig`
- `samples/zigux/trace_events_sample.zig`

Bytestream FIFO review packet
- keep `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and `Documentation/zigux/phase5-kfifo-sample-survey.md` aligned through the shared `zigux/tests/phase5_build.zig` entrypoint
- keep the landed replay contract explicit: exact queue-order replay, transfer counts, truncated preview, non-destructive snapshot, and fixed embedded 32-byte ring-buffer backing
- keep the helper-only review surface explicit outside the main replay path: empty-queue null handling, the capacity ceiling, and queue-only reset remain part of the shipped contract
- keep procfs, `kfifo_from_user()` or `kfifo_to_user()`, locking, and runtime registration out of scope so this sample stays a bounded in-memory idiom rather than a runtime module claim

Later runtime starters and loader-side follow-ons
- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_kretprobe.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`
- `samples/zigux/runtime_trace_events.zig`

Review rules
- keep the four Phase 5 reference samples reviewable as bounded in-memory or non-runtime idiom readings
- do not treat the later `runtime_*` files in this directory as Phase 5 approved reference idioms
- keep sample-root notes aligned with `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md`
- current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample; keep string-helper evidence under the separate Phase 7 helper bundle
