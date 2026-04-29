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

String-work boundary checks
- verify the current Phase 5 sample-root inventory stays the four roadmap anchors only: `find samples/zigux -maxdepth 1 -type f | sort`
- verify no Phase 5 string sample has appeared under this sample root: `find samples/zigux -maxdepth 1 -type f | sort | rg 'string'`
- verify the shared docs still keep string-helper evidence in Phase 7 instead of `samples/zigux/`: `rg -n "samples/zigux/\\*string\\*|Phase 7 helper bundle|helper-only under \`lib/string_helpers.zig\`" Documentation/zigux/README.md Documentation/zigux/review-checklist.md samples/zigux/README.md`
- verify the four shipped Phase 5 sample packets still pass together: `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
- verify the shipped string-helper evidence still lives under the separate Phase 7 helper bundle: `python3 scripts/zigux/validate-phase7.py`
