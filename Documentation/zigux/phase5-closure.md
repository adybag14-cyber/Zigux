# Phase 5 Closure

This document closes the bounded Phase 5 reference-sample tranche for Zigux.

## Status

- `PHASE5_STATUS=closed`
- scope: bounded non-runtime reference samples only
- product boundary: `samples/zigux/*` for the four shipped roadmap-backed samples plus their directly coupled survey and replay packets
- authority: current Linux C sample anchors remain authoritative for runtime-facing semantics and for every out-of-scope runtime boundary

## Closed Reference Sample Set

The bounded closed Phase 5 sample set is:

- `samples/zigux/bytestream_fifo.zig`
- `samples/zigux/kobject_example.zig`
- `samples/zigux/kretprobe_example.zig`
- `samples/zigux/trace_events_sample.zig`
- `PHASE5_SAMPLE_COUNT=4`
- shared survey guide: `Documentation/zigux/phase5-sample-review-guide.md`
- shared replay entrypoint: `zigux/tests/phase5_build.zig`

The directly coupled survey packet for that tranche is:

- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `PHASE5_SURVEY_NOTE_COUNT=4`

The directly coupled manifest-backed replay packet for that tranche is:

- `zigux/tests/phase5_bytestream_fifo_manifest.json`
- `zigux/tests/phase5_bytestream_fifo.zig`
- `zigux/tests/phase5_bytestream_fifo_survey.zig`
- `zigux/tests/phase5_kobject_example_manifest.json`
- `zigux/tests/phase5_kobject_example.zig`
- `zigux/tests/phase5_kobject_example_survey.zig`
- `zigux/tests/phase5_kretprobe_example_manifest.json`
- `zigux/tests/phase5_kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example_survey.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_survey.zig`
- `PHASE5_MANIFEST_COUNT=4`

## Closure Gates

Phase 5 is only considered closed when all of the following stay green and mutually aligned:

1. shared build replay
   - `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
2. Linux-style shared replay
   - `make -C zigux phase5-test`
3. bounded tranche replay
   - `make -C zigux phase5`
4. shared contributor packet alignment
   - `Documentation/zigux/phase5-sample-review-guide.md`
   - `samples/zigux/README.md`
   - `Documentation/zigux/review-checklist.md`
   - the four sample-owned Phase 5 survey notes under `Documentation/zigux/`

Current `master` intentionally closes this tranche without a shared `validate-phase5.py`, without any shipped `check-phase5-*.py` packet, and without a `phase5-validate` target. The build-backed replay routes and shared contributor surfaces above are the honest closure boundary for the current four-sample Phase 5 packet.

## Shared Review Packet

The closed Phase 5 reference-sample packet stays reviewable through these shared product surfaces:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `samples/zigux/README.md`
- the four survey notes under `Documentation/zigux/`
- the four reference samples under `samples/zigux/`
- the four manifest-backed test packets under `zigux/tests/`
- `zigux/tests/phase5_build.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
- `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
- `make -C zigux phase5-test`
- `make -C zigux phase5`

Reviewers should treat drift across those packet summaries, the sample-owned survey notes, the committed manifest-backed replays, the shared build entrypoint, and the Linux-style replay routes as a closure regression even when a sample body is unchanged.

## Boundary

Phase 5 closure does not imply:

- procfs parity
- user-copy parity
- sysfs creation parity
- `pt_regs` or tracepoint-macro parity
- module registration or unregister parity
- a standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample
- any transfer of the separate `samples/zigux/runtime_*` family out of Phase 9 runtime pilot scope

The current bounded Phase 5 closure is only the proof that the four roadmap-backed non-runtime samples remain reviewable as approved Zigux idioms for queue boundaries, ownership and lifetime, probe lifecycle, and tracing-plus-callback reviewability.

## Rollback

Rollback owner:

- Zigux product maintainers working in `samples/zigux`, `Documentation/zigux`, and `zigux/tests`

Fallback rule:

- if one reference sample or its directly coupled survey packet drifts out of sync, remove or narrow that sample from the shared Phase 5 packet before claiming the tranche is still closed

Disable path:

- update `zigux/tests/phase5_build.zig`
- update `samples/zigux/README.md`
- update `Documentation/zigux/phase5-sample-review-guide.md`
- refresh the affected sample-owned survey note and its directly coupled manifest-backed survey test
