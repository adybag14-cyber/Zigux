# Phase 14 Ring Buffer Survey

This document records the bounded Phase 14 survey lane around `kernel/trace/ring_buffer.c`.

## Status

- `PHASE14_STATUS=study_only`
- `PHASE14_SLICE=ring-buffer-survey-gap`
- scope: the dedicated Phase 14 ring-buffer survey gate, its manifest, the shared Phase 14 build wiring, and this lane note that keeps the roadmap gap explicit without shipping a Zig bridge
- product boundary:
  - `zigux/tests/phase14_ring_buffer_survey.zig`
  - `zigux/tests/phase14_ring_buffer_manifest.json`
  - `zigux/tests/phase14_build.zig`
  - `Documentation/zigux/phase14-ring-buffer-survey.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 14 roadmap explicitly names `kernel/trace/ring_buffer.c` as a boundary-study target first, not a rewrite target. It also says `kernel/trace/ring_buffer.zig` is only appropriate if years of evidence justify it.

That caution matters because the live anchor is already 8,103 lines, its surrounding tracing surface is even larger, and the supporting docs expose consumer-facing behavior that sits on top of deep per-CPU page rotation, reserve and commit sequencing, reader handoff, overwrite and lost-event accounting, wakeups, and mmap-facing state.

The honest Phase 14 move here is therefore not to start a `ring_buffer.zig` file. It is to make the blocked state reviewable so future runs can stay disciplined about what remains study-only.

## Survey findings

- `kernel/trace/ring_buffer.c` is present on `master` at 8,103 lines.
- `kernel/trace/trace.c` adds another 10,017 lines of nearby trace-core coupling around the buffer.
- `Documentation/trace/ring-buffer-design.rst` is present at 983 lines and documents the reserve, commit, reader, and nested writer model in detail.
- `Documentation/trace/ring-buffer-map.rst` is present at 106 lines and adds mmap-facing reader and sub-buffer behavior that would be easy to understate in a premature Zig wrapper.
- `kernel/trace/simple_ring_buffer.c` exists as a much smaller 517-line companion, which reinforces that the full tracing ring buffer is the complex path and should not be treated like a straightforward helper port.
- the live repo already had `zigux/tests/phase14_build.zig`, `zigux/Makefile` Phase 14 wiring, `Documentation/zigux/freeze-map.md`, and the workqueue bridge slice, so the highest-value non-overlapping ring-buffer step is a survey gate rather than another starter implementation.

## Recorded gaps

The current lane state is:

- landed `phase14-build-gate`
- landed `phase14-make-target`
- landed `phase14-freeze-map-note`
- landed `phase14-ring-buffer-survey-gate`
- landed `phase14-ring-buffer-survey-note`
- ready-next `phase14-ring-buffer-boundary-decision-checklist`
- blocked `phase14-ring-buffer-zig-port-blocker`

This keeps the lane honest: Zigux now has an explicit reviewable record that `kernel/trace/ring_buffer.c` belongs in the study-only set for now, and that the repo still does not ship `kernel/trace/ring_buffer.zig`.

## Non-goals

This survey slice does not claim:

- a `kernel/trace/ring_buffer.zig` implementation
- reserve or commit parity for `ring_buffer_lock_reserve()` and `ring_buffer_unlock_commit()`
- reader-page handoff parity for `rb_get_reader_page()`
- consuming or non-consuming read parity for `ring_buffer_consume()` and `ring_buffer_read_start()`
- overwrite, wakeup, or reset behavior
- mmap or splice behavior from the tracefs ring-buffer interfaces

## Gates

1. run the dedicated Phase 14 build
- `zig build test --build-file zigux/tests/phase14_build.zig`

2. run the convenience target
- `make -C zigux phase14`

## Next bounded step

Stay in the Phase 14 ring-buffer lane and add one small study-only decision checklist next, limited to reserve or commit ownership, reader-page rotation, overwrite and loss accounting, and mmap or splice-facing boundaries before anyone proposes `kernel/trace/ring_buffer.zig`.
