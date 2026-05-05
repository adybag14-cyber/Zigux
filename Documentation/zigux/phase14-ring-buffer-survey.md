# Phase 14 Ring Buffer Survey

This document records the bounded Phase 14 survey lane around `kernel/trace/ring_buffer.c`.

## Status

- `PHASE14_STATUS=study_only`
- `PHASE14_SLICE=ring-buffer-survey-gap`
- `PHASE14_LANE_KEY=P14-L08`
- `PHASE14_SURVEYED_COMMIT=946d5c73fdb763ba860a20879b05da54e1896e8c`
- scope: the dedicated Phase 14 ring-buffer survey gate, its manifest, the shared Phase 14 build wiring, and this lane note that keeps the roadmap gap explicit without shipping a Zig bridge
- survey provenance refreshed against verified `master` head `946d5c73fdb763ba860a20879b05da54e1896e8c`
- product boundary:
  - `zigux/tests/phase14_ring_buffer_survey.zig`
  - `zigux/tests/phase14_ring_buffer_manifest.json`
  - `zigux/tests/phase14_build.zig`
  - `Documentation/zigux/phase14-ring-buffer-survey.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 14 roadmap explicitly names `kernel/trace/ring_buffer.c` as a boundary-study target first, not a rewrite target.
It also says `kernel/trace/ring_buffer.zig` is only appropriate if years of evidence justify it.
That caution matters because the live anchor is already 8,103 lines, its surrounding tracing surface is even larger, and the supporting docs expose consumer-facing behavior that sits on top of deep per-CPU page rotation, reserve and commit sequencing, reader handoff, overwrite and lost-event accounting, wakeups, mmap-facing state, and tracefs mapping lockouts around resize, snapshot, and splice behavior.
The honest Phase 14 move here is therefore not to start a `ring_buffer.zig` file.
It is to make the blocked state reviewable and record the first stay-in-C checklist seams so future runs can stay disciplined about what remains study-only.

## Survey findings

- `kernel/trace/ring_buffer.c` is present on `master` at 8,103 lines.
- `kernel/trace/trace.c` adds another 10,017 lines of nearby trace-core coupling around the buffer.
- `Documentation/trace/ring-buffer-design.rst` is present at 983 lines and documents the reserve, commit, reader, overwrite, and nested writer model in detail.
- `Documentation/trace/ring-buffer-map.rst` is present at 106 lines and adds mmap-facing reader, sub-buffer, and tracefs limitation behavior that would be easy to understate in a premature Zig wrapper.
- `kernel/trace/simple_ring_buffer.c` exists as a much smaller 517-line companion, which reinforces that the full tracing ring buffer is the complex path and should not be treated like a straightforward helper port.
- the live repo already had `zigux/tests/phase14_build.zig`, `zigux/Makefile` Phase 14 wiring, `Documentation/zigux/freeze-map.md`, and the workqueue bridge slice, so the highest-value non-overlapping ring-buffer step is a survey gate rather than another starter implementation.
- the survey manifest now records a landed decision checklist around reserve or commit publication, head-page and reader-page handoff, remote-reader metadata, wakeup or mmap-facing publication, and tracefs mapping limitations so later runs can deepen the audit without inventing `kernel/trace/ring_buffer.zig`.

## Decision checklist

- landed `phase14-ring-buffer-boundary-decision-checklist`
- `reserve-commit-publication`: keep `ring_buffer_lock_reserve()`, `ring_buffer_unlock_commit()`, and `rb_move_tail()` in C because nested writers, pending commits, and per-CPU commit publication remain coupled.
- `head-page-reader-handoff`: keep `rb_handle_head_page()`, `rb_set_head_page()`, and `ring_buffer_read_page()` in C because head-page rotation, reader-page extraction, and commit-page adjacency still move together.
- `remote-reader-metadata`: keep `rb_read_remote_meta_page()` and `__rb_get_reader_page_from_remote()` in C because callback-driven metadata refresh and remote reader-page import rules sit on top of the already-coupled local model.
- `wakeup-watermark-mmap-boundary`: keep `rb_wake_up_waiters()`, `rb_watermark_hit()`, `ring_buffer_wait()`, `ring_buffer_poll_wait()`, and `rb_update_meta_page()` in C because irq-work wakeups, full-waiter watermarks, and mapped-reader publication still describe one shared reader-visible contract.
- `tracefs-mapping-limitations`: keep `ring_buffer_map()`, `ring_buffer_resize()`, `ring_buffer_swap_cpu()`, `ring_buffer_map_get_reader()`, and `tracing_buffers_splice_read()` in C because mapped-reader lockouts, snapshot restrictions, and splice fallback remain one shared tracefs-facing policy surface.

## Overwrite and lost-event audit

- `rb_move_tail()` is still the key overwrite boundary.
When the tail page catches the head page and overwrite mode is disabled, the writer increments `dropped_events` and backs out. When overwrite mode is enabled, it must move the head-page state forward before the write can proceed, which keeps the overwrite path coupled to the same reader-visible page choreography described in `Documentation/trace/ring-buffer-design.rst`.
- The overwrite toggle is not a tiny local policy bit.
`ring_buffer_change_overwrite()` changes whether the full-buffer path drops new events or advances the head to evict old ones, so the Phase 14 lane should keep overwrite behavior as a traced C-owned contract instead of implying a Zig-side helper can safely own it.
- Lost-event reporting is finalized on the reader side, not at the overwrite point itself.
After the reader swaps in the next page, the code compares `overrun` against `last_overrun` and publishes the delta through `lost_events`, which means overwrite accounting stays coupled to reader-page replacement and should remain study-only for now.
- The supporting docs line up with that code path: `Documentation/trace/ring-buffer-design.rst` explains that overwrite mode must move the head page before the tail can advance, and `Documentation/trace/ftrace.rst` distinguishes dropped events from overwritten or unread data in the exposed trace stats.

## Wakeup and mmap audit

- `ring_buffer_wait()` and `ring_buffer_poll_wait()` are not just passive wrappers around a waitqueue.
They share `rb_wait_cond()` and `rb_watermark_hit()` and use `waiters_pending`, `full_waiters_pending`, `wakeup_full`, and `shortest_full` state to decide whether normal readers or watermark-triggered readers should wake, which keeps the visible wait contract coupled to the same buffer fullness accounting that writers update.
- `rb_wake_up_waiters()` finalizes that contract through `irq_work`.
It fans out to both ordinary waiters and full-buffer waiters, clears pending flags, and only promotes the full-wakeup path after the watermark checks have been published, so the wakeup side is still inseparable from the C-owned irq-work and memory-ordering choreography.
- The mmap path extends that same reader contract instead of simplifying it.
`Documentation/trace/ring-buffer-map.rst` says mapped readers consume the tracefs `trace_pipe_raw` interface through a meta-page plus sub-buffer mapping, then advance the reader with `TRACE_MMAP_IOCTL_GET_READER`, which means mapped-reader publication still depends on the same `reader.id`, `lost_events`, and page-handoff state that `rb_update_meta_page()` and `rb_read_remote_meta_page()` maintain.
- Concurrent readers remain another reason to stay cautious.
The mapping docs say they are allowed but not recommended because they compete for the same ring buffer and make output unpredictable, which confirms that wakeup and mapped-reader publication still depend on shared global behavior rather than an isolated helper seam.

## Tracefs mapping limitations audit

- The tracefs mapping docs make the first boundary explicit: once a buffer is mapped, it cannot be resized, snapshot mode is unavailable, and splice falls back to copying instead of the copyless page swap.
That limitation is product-visible behavior, not a hidden implementation detail.
- The C implementation keeps that lockout wired directly into the buffer state.
`ring_buffer_map()` increments `resize_disabled` before the user mapping is published, and `ring_buffer_resize()` refuses to proceed when `resize_disabled` is set because a mapped reader expects stable page layout while it is active.
- Snapshot behavior stays coupled to the same mapping state.
`ring_buffer_swap_cpu()` rejects mapped buffers outright, and `kernel/trace/trace.c` only allocates snapshot buffers for non-mapped instances, which means snapshot support still depends on shared trace-array and mapped-buffer coordination rather than a local wrapper seam.
- Splice behavior also remains tied to the mapped-reader contract.
The docs say mapped buffers lose the copyless swap path, and `tracing_buffers_splice_read()` falls back to allocating read pages, calling `ring_buffer_read_page()`, and pushing those pages through `splice_to_pipe()`, so the tracefs read path stays coupled to the same mapped-reader bookkeeping instead of exposing a separate zero-copy bridge candidate.
- `TRACE_MMAP_IOCTL_GET_READER` reinforces that this is still one shared boundary.
The ioctl waits through `ring_buffer_wait()` when blocking reads are allowed and then delegates to `ring_buffer_map_get_reader()`, so mapped-reader advancement, wakeups, lost-event publication, and the resize or snapshot lockouts all remain coordinated in C.

## Mapped-reader ioctl audit

- `tracing_buffers_ioctl()` keeps the mapped-reader handoff attached to the existing wait and wake contract.
Blocking callers of `TRACE_MMAP_IOCTL_GET_READER` first go through `ring_buffer_wait()`, while non-blocking callers skip straight to the same reader handoff, so the ioctl does not create an independent reader-visible policy surface.
- `ring_buffer_map_get_reader()` also refuses to operate on an unmapped buffer.
It enters through `rb_get_mapped_buffer()`, which depends on the mapping state built by `ring_buffer_map()`, and then serializes the reader transition under `reader_lock`, so the ioctl path still shares ownership with the same mapped-buffer lifetime rules and lock choreography as the rest of the tracefs mapping surface.
- The handoff is not a tiny pointer swap.
If the current reader page still has unread bytes, `ring_buffer_map_get_reader()` advances the in-page reader to the end before it will consider a new page, and if the reader has already caught up with `commit_page` it stops instead of fabricating a handoff. Only when a new page is truly needed does it call `rb_get_reader_page()`, which keeps mapped-reader advancement coupled to the same reader-page rotation rules that already block wrapper-first ownership elsewhere in the survey.
- Lost-event and metadata publication stay in the same C-owned handoff.
When missed events exist, `ring_buffer_map_get_reader()` tries to encode them into the exported page state, then flushes the mapped range and calls `rb_update_meta_page()` before releasing `reader_lock`, so user space still depends on one combined kernel handoff for page contents, loss accounting, and meta-page refresh.
- The concurrent-reader warning in `Documentation/trace/ring-buffer-map.rst` lines up with the implementation details.
Multiple user mappings increment `user_mapped`, `ring_buffer_map_dup()` preserves that shared state across duplicated mappings, and the docs still call the resulting output unpredictable, which confirms that `TRACE_MMAP_IOCTL_GET_READER` remains part of a shared reader-competition contract rather than a clean Zig bridge seam.

## Recorded gaps

The current lane state is:

- landed `phase14-build-gate`
- landed `phase14-make-target`
- landed `phase14-freeze-map-note`
- landed `phase14-ring-buffer-survey-gate`
- landed `phase14-ring-buffer-survey-note`
- landed `phase14-ring-buffer-boundary-decision-checklist`
- landed `phase14-ring-buffer-overwrite-audit`
- landed `phase14-ring-buffer-wakeup-mmap-followup`
- landed `phase14-ring-buffer-splice-resize-followup`
- landed `phase14-ring-buffer-mapped-reader-ioctl-followup`
- ready-next `phase14-ring-buffer-reader-page-consume-followup`
- blocked `phase14-ring-buffer-zig-port-blocker`

This keeps the lane honest: Zigux now has an explicit reviewable record that `kernel/trace/ring_buffer.c` belongs in the study-only set for now, and that the repo still does not ship `kernel/trace/ring_buffer.zig`.

## Non-goals

This survey slice does not claim:

- a `kernel/trace/ring_buffer.zig` implementation
- reserve or commit parity for `ring_buffer_lock_reserve()` and `ring_buffer_unlock_commit()`
- reader-page handoff parity for `rb_get_reader_page()`
- consuming or non-consuming read parity for `ring_buffer_consume()` and `ring_buffer_read_start()`
- overwrite, wakeup, resize, snapshot, or reset ownership
- mmap or splice ownership for the tracefs ring-buffer interfaces

## Gates

1. run the dedicated Phase 14 build
   - `zig build test --build-file zigux/tests/phase14_build.zig`
2. run the convenience target
   - `make -C zigux phase14`

## Next bounded step

Stay in the Phase 14 ring-buffer lane and add one small study-only reader-page follow-up next, limited to `rb_get_reader_page()`, `ring_buffer_read_start()`, and `ring_buffer_consume()` before anyone proposes `kernel/trace/ring_buffer.zig`.