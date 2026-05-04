# Phase 14 Ring Buffer Survey

This document records the bounded Phase 14 survey lane around `kernel/trace/ring_buffer.c`.

## Status

- `PHASE14_LANE_KEY=P14-L08`
- `PHASE14_STATUS=study_only`
- `PHASE14_SLICE=ring-buffer-survey-gap`
- `PHASE14_SURVEYED_COMMIT=f9a7a6e93c8e6a1b6550fd7b2aa5571729aab05b`
- scope: the dedicated Phase 14 ring-buffer survey gate, its manifest, the shared Phase 14 build wiring, and this lane note that keeps the roadmap gap explicit without shipping a Zig bridge
- survey provenance refreshed against verified `master` head `f9a7a6e93c8e6a1b6550fd7b2aa5571729aab05b`
- live follow-up: current repo inspection added one more bounded tracefs reader-serialization audit around `trace_access_lock()`, `trace_access_unlock()`, and the shared consumed-page lifetime rule for read or splice consumers without widening this packet into a reader wrapper claim
- product boundary:
  - `zigux/tests/phase14_ring_buffer_survey.zig`
  - `zigux/tests/phase14_ring_buffer_manifest.json`
  - `zigux/tests/phase14_build.zig`
  - `Documentation/zigux/phase14-ring-buffer-survey.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 14 roadmap explicitly names `kernel/trace/ring_buffer.c` as a boundary-study target first, not a rewrite target. It also says `kernel/trace/ring_buffer.zig` is only appropriate if years of evidence justify it.

That caution matters because the live anchor is already 8,103 lines, its surrounding tracing surface is even larger, and the supporting docs expose consumer-facing behavior that sits on top of deep per-CPU page rotation, reserve and commit sequencing, reader handoff, overwrite and lost-event accounting, wakeups, mmap-facing state, and tracefs mapping lockouts around resize, snapshot, and splice behavior.

The honest Phase 14 move here is therefore not to start a `ring_buffer.zig` file. It is to make the blocked state reviewable and record the first stay-in-C checklist seams so future runs can stay disciplined about what remains study-only.

## Survey findings

- `kernel/trace/ring_buffer.c` is present on `master` at 8,103 lines.
- `kernel/trace/trace.c` adds another 10,017 lines of nearby trace-core coupling around the buffer.
- `Documentation/trace/ring-buffer-design.rst` is present at 983 lines and documents the reserve, commit, reader, overwrite, and nested writer model in detail.
- `Documentation/trace/ring-buffer-map.rst` is present at 106 lines and adds mmap-facing reader, sub-buffer, and tracefs limitation behavior that would be easy to understate in a premature Zig wrapper.
- `kernel/trace/simple_ring_buffer.c` exists as a much smaller 517-line companion, which reinforces that the full tracing ring buffer is the complex path and should not be treated like a straightforward helper port.
- the live repo already had `zigux/tests/phase14_build.zig`, `zigux/Makefile` Phase 14 wiring, `Documentation/zigux/freeze-map.md`, and the workqueue bridge slice, so the highest-value non-overlapping ring-buffer step is a survey gate rather than another starter implementation.
- the survey manifest now records a landed decision checklist around reserve or commit publication, head-page and reader-page handoff, remote-reader metadata, wakeup or mmap-facing publication, tracefs mapping limitations, reader-page consume boundaries, page-count resize workqueue coordination, and reset or clear-path governance so later runs can deepen the audit without inventing `kernel/trace/ring_buffer.zig`.

## Decision checklist

- landed `phase14-ring-buffer-boundary-decision-checklist`
- `reserve-commit-publication`: keep `ring_buffer_lock_reserve()`, `ring_buffer_unlock_commit()`, and `rb_move_tail()` in C because nested writers, pending commits, and per-CPU commit publication remain coupled.
- `head-page-reader-handoff`: keep `rb_handle_head_page()`, `rb_set_head_page()`, and `ring_buffer_read_page()` in C because head-page rotation, reader-page extraction, and commit-page adjacency still move together.
- `remote-reader-metadata`: keep `rb_read_remote_meta_page()` and `__rb_get_reader_page_from_remote()` in C because callback-driven metadata refresh and remote reader-page import rules sit on top of the already-coupled local model.
- `wakeup-watermark-mmap-boundary`: keep `rb_wake_up_waiters()`, `rb_watermark_hit()`, `ring_buffer_wait()`, `ring_buffer_poll_wait()`, and `rb_update_meta_page()` in C because irq-work wakeups, full-waiter watermarks, and mapped-reader publication still describe one shared reader-visible contract.
- `tracefs-mapping-limitations`: keep `ring_buffer_map()`, `ring_buffer_resize()`, `ring_buffer_swap_cpu()`, `ring_buffer_map_get_reader()`, and `tracing_buffers_splice_read()` in C because mapped-reader lockouts, snapshot restrictions, and splice fallback remain one shared tracefs-facing policy surface.
- `reader-page-consume-boundary`: keep `rb_get_reader_page()`, `ring_buffer_read_start()`, and `ring_buffer_consume()` in C because reader-page swaps, lost-event publication, iterator setup, and reader-side resize pinning still form one shared handoff rather than a wrapper-safe helper seam.

## Remote-reader metadata audit

- `rb_read_remote_meta_page()` is not a side-channel helper. It refuses to fabricate metadata unless the remote buffer registered a `meta_page_update` callback, invokes that callback to refresh the exporter-visible page, and only then republishes the mapped-reader counters through the same meta-page contract, so remote metadata publication still depends on callback-owned producer state.
- `__rb_get_reader_page_from_remote()` keeps page import coupled to that same callback boundary. The remote path can only advance once the current reader page is fully consumed, then it asks the remote `reader_page()` callback for the next page and refuses to pretend a handoff happened when the callback returns nothing useful or leaves the reader effectively caught up with the remote commit state.
- Lost-event accounting remains in the same C-owned handoff. When a new remote page really arrives, `__rb_get_reader_page_from_remote()` updates `lost_events` from the exported overrun delta and `rb_read_remote_meta_page()` then republishes the refreshed reader position and counters through the same mapped meta-page shape, which means remote imports still bundle page movement, accounting, and metadata refresh together.
- The surrounding docs explain why this should stay conservative. `Documentation/trace/ring-buffer-design.rst` already says readers serialize around one reader page and `Documentation/trace/ring-buffer-map.rst` says mapped readers compete unpredictably, so the extra remote callbacks deepen the same shared contract instead of creating an isolated Zig seam.

## Overwrite and lost-event audit

- `rb_move_tail()` is still the key overwrite boundary. When the tail page catches the head page and overwrite mode is disabled, the writer increments `dropped_events` and backs out. When overwrite mode is enabled, it must move the head-page state forward before the write can proceed, which keeps the overwrite path coupled to the same reader-visible page choreography described in `Documentation/trace/ring-buffer-design.rst`.
- The overwrite toggle is not a tiny local policy bit. `ring_buffer_change_overwrite()` changes whether the full-buffer path drops new events or advances the head to evict old ones, so the Phase 14 lane should keep overwrite behavior as a traced C-owned contract instead of implying a Zig-side helper can safely own it.
- Lost-event reporting is finalized on the reader side, not at the overwrite point itself. After the reader swaps in the next page, the code compares `overrun` against `last_overrun` and publishes the delta through `lost_events`, which means overwrite accounting stays coupled to reader-page replacement and should remain study-only for now.
- The supporting docs line up with that code path: `Documentation/trace/ring-buffer-design.rst` explains that overwrite mode must move the head page before the tail can advance, and `Documentation/trace/ftrace.rst` distinguishes dropped events from overwritten or unread data in the exposed trace stats.

## Wakeup and mmap audit

- `ring_buffer_wait()` and `ring_buffer_poll_wait()` are not just passive wrappers around a waitqueue. They share `rb_wait_cond()` and `rb_watermark_hit()` and use `waiters_pending`, `full_waiters_pending`, `wakeup_full`, and `shortest_full` state to decide whether normal readers or watermark-triggered readers should wake, which keeps the visible wait contract coupled to the same buffer fullness accounting that writers update.
- `rb_wake_up_waiters()` finalizes that contract through `irq_work`. It fans out to both ordinary waiters and full-buffer waiters, clears pending flags, and only promotes the full-wakeup path after the watermark checks have been published, so the wakeup side is still inseparable from the C-owned irq-work and memory-ordering choreography.
- The mmap path extends that same reader contract instead of simplifying it. `Documentation/trace/ring-buffer-map.rst` says mapped readers consume the tracefs `trace_pipe_raw` interface through a meta-page plus sub-buffer mapping, then advance the reader with `TRACE_MMAP_IOCTL_GET_READER`, which means mapped-reader publication still depends on the same `reader.id`, `lost_events`, and page-handoff state that `rb_update_meta_page()` and `rb_read_remote_meta_page()` maintain.
- Concurrent readers remain another reason to stay cautious. The mapping docs say they are allowed but not recommended because they compete for the same ring buffer and make output unpredictable, which confirms that wakeup and mapped-reader publication still depend on shared global behavior rather than an isolated helper seam.

## Tracefs mapping limitations audit

- The tracefs mapping docs make the first boundary explicit: once a buffer is mapped, it cannot be resized, snapshot mode is unavailable, and splice falls back to copying instead of the copyless page swap. That limitation is product-visible behavior, not a hidden implementation detail.
- The C implementation keeps that lockout wired directly into the buffer state. `ring_buffer_map()` increments `resize_disabled` before the user mapping is published, and `ring_buffer_resize()` refuses to proceed when `resize_disabled` is set because a mapped reader expects stable page layout while it is active.
- Snapshot behavior stays coupled to the same mapping state. `ring_buffer_swap_cpu()` rejects mapped buffers outright, and `kernel/trace/trace.c` only allocates snapshot buffers for non-mapped instances, which means snapshot support still depends on shared trace-array and mapped-buffer coordination rather than a local wrapper seam.
- Splice behavior also remains tied to the mapped-reader contract. The docs say mapped buffers lose the copyless swap path, and `tracing_buffers_splice_read()` falls back to allocating read pages, calling `ring_buffer_read_page()`, and pushing those pages through `splice_to_pipe()`, so the tracefs read path stays coupled to the same mapped-reader bookkeeping instead of exposing a separate zero-copy bridge candidate.
- `TRACE_MMAP_IOCTL_GET_READER` reinforces that this is still one shared boundary. The ioctl waits through `ring_buffer_wait()` when blocking reads are allowed and then delegates to `ring_buffer_map_get_reader()`, so mapped-reader advancement, wakeups, lost-event publication, and the resize or snapshot lockouts all remain coordinated in C.

## Mapped-reader ioctl audit

- `tracing_buffers_ioctl()` keeps the mapped-reader handoff attached to the existing wait and wake contract. Blocking callers of `TRACE_MMAP_IOCTL_GET_READER` first go through `ring_buffer_wait()`, while non-blocking callers skip straight to the same reader handoff, so the ioctl does not create an independent reader-visible policy surface.
- `ring_buffer_map_get_reader()` also refuses to operate on an unmapped buffer. It enters through `rb_get_mapped_buffer()`, which depends on the mapping state built by `ring_buffer_map()`, and then serializes the reader transition under `reader_lock`, so the ioctl path still shares ownership with the same mapped-buffer lifetime rules and lock choreography as the rest of the tracefs mapping surface.
- The handoff is not a tiny pointer swap. If the current reader page still has unread bytes, `ring_buffer_map_get_reader()` advances the in-page reader to the end before it will consider a new page, and if the reader has already caught up with `commit_page` it stops instead of fabricating a handoff. Only when a new page is truly needed does it call `rb_get_reader_page()`, which keeps mapped-reader advancement coupled to the same reader-page rotation rules that already block wrapper-first ownership elsewhere in the survey.
- Lost-event and metadata publication stay in the same C-owned handoff. When missed events exist, `ring_buffer_map_get_reader()` tries to encode them into the exported page state, then flushes the mapped range and calls `rb_update_meta_page()` before releasing `reader_lock`, so user space still depends on one combined kernel handoff for page contents, loss accounting, and meta-page refresh.
- The concurrent-reader warning in `Documentation/trace/ring-buffer-map.rst` lines up with the implementation details. Multiple user mappings increment `user_mapped`, `ring_buffer_map_dup()` preserves that shared state across duplicated mappings, and the docs still call the resulting output unpredictable, which confirms that `TRACE_MMAP_IOCTL_GET_READER` remains part of a shared reader-competition contract rather than a clean Zig bridge seam.

## Reader-page consume audit

- `__rb_get_reader_page()` is already a stay-in-C state machine, not a lightweight accessor. Under local IRQ disable and `cpu_buffer->lock`, it returns the current reader page only when unread bytes remain, otherwise it zeroes the out-of-ring reader page, splices that page around the current head, retries while writers are moving the head marker, and only then updates `reader_page`, `read_stamp`, and page counters.
- Lost-event publication is attached to that same reader-page swap. `__rb_get_reader_page()` snapshots `overrun` after the new reader-page links are prepared, compares it with `last_overrun` after the replacement succeeds, and stores the delta in `lost_events`, which means page acquisition and reader-visible loss accounting are still one combined handoff.
- `ring_buffer_consume()` builds directly on that shared handoff instead of exposing a smaller seam. It enters under `reader_lock`, peeks through `rb_buffer_peek()`, clears `cpu_buffer->lost_events` only after a concrete event is returned, and then advances the in-kernel reader with `rb_advance_reader()`, so consuming reads remain coupled to the same reader-page rotation and lost-event lifecycle as the acquisition path.
- Non-consuming iteration stays tied to the same boundary. `ring_buffer_read_start()` allocates an iterator, increments `resize_disabled`, takes `reader_lock` plus `cpu_buffer->lock`, and resets the iterator against the live reader state, so even the supposedly observational path still pins resize behavior and shares the same reader serialization contract.
- The design docs back up that code-level coupling. `Documentation/trace/ring-buffer-design.rst` says no two readers may run at the same time and describes the dedicated reader page swapping with the head page, which matches the implementation detail that consuming and non-consuming readers still revolve around one C-owned reader-page choreography instead of a wrapper-first helper surface.

## Read-page extraction audit

- `ring_buffer_read_page()` is still a stay-in-C extraction boundary, not a helper seam. It rejects mismatched CPUs, undersized reads, missing read pages, and caller pages whose `order` no longer matches `buffer->subbuf_order`, then enters under `reader_lock` and pulls the active reader state from `rb_get_reader_page()`.
- The copy-versus-swap split stays coupled to the live reader contract. The function forces a memcpy path whenever the reader already consumed part of the page, the caller did not provide enough room for the remaining committed bytes, the writer is still on the reader page, or the buffer is mapped or remote. Only the clean full-page path is allowed to swap pages.
- The `full` mode confirms this is not a loose wrapper API. If the page was already partially read, the remaining committed bytes do not fit, or `commit_page` is still the reader page, `ring_buffer_read_page()` returns `-1` instead of pretending a full handoff is available.
- The swap path also carries reader-visible accounting. When the page can be handed off whole, the function swaps the caller-provided page into the ring, preserves `real_end` for the committed payload length, appends missed-event metadata when there is room, and zeroes the unread tail before returning, so extraction, loss publication, and exported page shape still move together.
- The `resize_disabled` story still belongs to the surrounding C-owned mapping contract, not a new Zig bridge. `ring_buffer_read_page()` forces memcpy whenever the buffer is mapped, and the earlier mapping audit already shows that mapped readers pin `resize_disabled` through `ring_buffer_map()`, which keeps read-page extraction tied to the same tracefs lifetime rules instead of opening a separate wrapper-first path.

## Read-page allocation contract audit

- `ring_buffer_alloc_read_page()` is not a generic allocator shim. It records the current `buffer->subbuf_order` into the returned wrapper, opportunistically reuses `cpu_buffer->free_page` under the per-CPU lock, and only falls back to `alloc_cpu_data()` when no cached page is available, which means the allocation path is already tied to the live per-CPU reuse contract.
- `ring_buffer_free_read_page()` keeps that reuse contract in C. It only returns the page to `cpu_buffer->free_page` when the page is not shared anywhere else and when the wrapper's saved `order` still matches the buffer's current `subbuf_order`; otherwise it frees the backing pages outright instead of pretending the caller can safely recycle them across size changes.
- The tracefs callers prove that this is one shared contract, not a helper seam. `tracing_buffers_read()` caches one spare page per open file, remembers both `spare_cpu` and `spare_size`, and explicitly frees and reallocates the spare page when the sub-buffer size changes before retrying `ring_buffer_read_page()`.
- The splice path stays under the same ownership. `tracing_buffers_splice_read()` allocates a fresh read page, passes it into `ring_buffer_read_page(..., full = 1)`, and only hands the page downstream after the read succeeds, so the caller-visible lifecycle is still "allocate from the buffer contract, consume through the buffer contract, free back through the buffer contract."
- The sleep and wake responsibility remains deliberately outside the allocator itself. `ring_buffer_read_page()` says the calling layer must decide when to sleep or wake because the ring buffer is shared across kernel contexts, and `tracing_buffers_read()` is the code that turns a negative read into `wait_on_pipe()` or `-EAGAIN`, which confirms that allocation, reuse, and wake policy still have to be reviewed as one C-owned tracefs contract.

## Sub-buffer order reconfiguration audit

- `ring_buffer_subbuf_order_set()` is still a stay-in-C resize transaction, not a wrapper seam. It validates the requested order against both the per-page header size and the ring-buffer write-counter ceiling, records the old order and payload size, blocks concurrent mutation under `buffer->mutex`, and raises `record_disabled` before `synchronize_rcu()` so in-flight commits clear before any page layout changes.
- The per-CPU rebuild is coupled to mapping state and reader-page replacement. For every active CPU buffer the function refuses to proceed when `cpu_buffer->mapped` is set, computes a new page count from the previous payload footprint, preallocates a replacement list including a fresh reader page, then swaps that list under `reader_lock` while resetting `head_page`, `tail_page`, `commit_page`, and `nr_pages_to_update`, which means resize-time topology, reader handoff, and mapping lockout still move as one C-owned operation.
- Cached read-page reuse is explicitly invalidated during that same transition. After the new list is installed, `ring_buffer_subbuf_order_set()` clears `cpu_buffer->free_page` and frees the old cached page by `old_order`, and `ring_buffer_free_read_page()` separately refuses to recycle any page whose saved `order` no longer matches `buffer->subbuf_order`, so stale spare pages are not allowed to leak across a sub-buffer-order change.
- The tracefs control path keeps that same contract intact instead of introducing a friendlier outer API. `buffer_subbuf_size_write()` stops tracing, converts the requested kilobyte size into an order, updates the main buffer through `ring_buffer_subbuf_order_set()`, and then attempts the same change on the snapshot buffer when one exists; if the snapshot resize fails it tries to roll the main buffer back to `old_order`, and if that rollback also fails it disables tracing outright rather than claiming a partially resized state is safe.
- `tracing_buffers_read()` closes the loop on open file descriptors. It re-reads the current `ring_buffer_subbuf_size_get()` result for each read, frees any cached spare page when `page_size != info->spare_size`, and only then allocates a new read page and refreshes `spare_cpu` or `spare_size`, which confirms that resize-time reader-page invalidation is shared between the core buffer transaction and the tracefs caller contract instead of being an isolated helper concern.

## Page-count resize workqueue audit

- `ring_buffer_resize()` is not a local size-field update. It raises `buffer->resizing`, blocks shared mutation under `buffer->mutex`, and either runs `rb_update_pages()` on the current CPU or schedules `update_pages_work` onto the target CPU before waiting for `update_done`, so page-count resizing already spans global buffer state, per-CPU worker context, and a synchronous caller-visible completion boundary.
- The per-CPU resize fan-out remains coupled across the whole trace buffer. For all-CPU requests the function stores each shard's delta in `nr_pages_to_update`, sends remote work through `schedule_work_on(cpu, &cpu_buffer->update_pages_work)` when needed, and then waits for every outstanding `update_done` before clearing the pending deltas, which means the visible resize result only exists after the full shard set reaches the same completion barrier.
- Reader and writer safety stay inside that same C-owned transaction. `ring_buffer_resize()` refuses to proceed when `resize_disabled` is held because an active reader still expects stable page topology, and the worker path mutates the same per-CPU page lists, counters, and reader-visible topology that normal reserve, consume, and read-page flows already share, so deferred page-count updates are still not a wrapper-safe helper seam.
- The broader tracefs resize path in `trace.c` keeps that coordination shared above the ring buffer core. Snapshot-aware callers still pair the live and snapshot resize decisions and the existing rollback logic may disable tracing if the two sides cannot be restored to a consistent state, so page-count updates and tracefs-facing resize policy remain one safety contract instead of a helper-first Zig candidate.

## Snapshot rollback failure-path audit

- `buffer_subbuf_size_write()` does not treat snapshot rollback failure as a local tracefs annoyance. It stops tracing before the resize starts, updates the main buffer first, then tries to apply the same sub-buffer order to the snapshot buffer, which means a failure already leaves the live and snapshot halves of the trace array on different layouts unless the rollback succeeds.
- The rollback itself is still part of the same C-owned safety policy. When the snapshot resize fails, `buffer_subbuf_size_write()` immediately calls `ring_buffer_subbuf_order_set()` again on the main buffer with `old_order`, so the tracefs write path is explicitly trying to restore one shared snapshot-compatible layout rather than letting the two buffers drift independently.
- The rare emergency case is global, not per-instance. If that rollback call also fails, the code sets `tracing_disabled = 1`, and the later `tracing_start_tr(tr)` path returns early when `tracing_disabled` is set, so the buffer-size write can leave tracing permanently off instead of pretending a mixed-order snapshot state is still safe to run.
- The same kill-switch pattern appears in `tracing_resize_ring_buffer()`, where a snapshot resize failure also tries to restore the main buffer and sets `tracing_disabled = 1` if the restore cannot be completed. That repetition is a useful Phase 14 signal: the snapshot rollback rule is a shared trace-array integrity contract, not an incidental quirk of one tracefs file operation.
- The snapshot documentation explains why that caution exists. `Documentation/trace/ftrace.rst` describes snapshot mode as a swap between the current trace buffer and a spare snapshot buffer while tracing continues, so the rollback path is guarding a coupled buffer-pair contract that should remain study-only instead of being split across any future Zig wrapper seam.

## Tracing-disabled Recovery Audit

- The documented user-facing recovery knobs are narrower than the rollback kill-switch. `Documentation/trace/ftrace.rst` says `tracing_on` can re-enable tracing after ordinary `tracing_off()` or `traceoff` trigger use, and `trace.c` repeats that quick-start guidance next to `current_tracer`, but those controls only describe normal buffer recording state.
- The runtime guard for `tracing_disabled` is stronger. `tracing_check_open_get_tr()` returns `-ENODEV` when `tracing_disabled` is set, and the same `-ENODEV` gate appears in other tracefs entry points, so the tracefs control plane stops looking like a temporarily paused tracer and instead behaves like tracing infrastructure that is unavailable to user space.
- The state transition evidence also points at a one-way failure path during a live session. `trace.c` initializes `tracing_disabled = 1`, clears it to `0` only after `tracer_alloc_buffers()` succeeds during setup, and then sets it back to `1` in the snapshot rollback failure paths inside both `tracing_resize_ring_buffer()` and `buffer_subbuf_size_write()`.
- The current evidence therefore does not show a documented user-visible recovery path after `tracing_disabled = 1` is raised by those rollback failures. The ordinary `echo 1 > tracing_on` guidance is about resuming an already-live tracer, not reviving this kill-switch state, so the honest Phase 14 boundary remains "treat the failure as terminal until reboot or re-initialization" rather than implying a wrapper-safe control seam.

## Mapped-reader duplicate and final-unmap lifetime audit

- `ring_buffer_map_dup()` is not a harmless bookkeeping helper. It exists specifically for duplicated VMAs such as `fork()`, and it reuses `__rb_inc_dec_mapped()` to increment both `user_mapped` and `mapped` under `mapping_lock`, `buffer->mutex`, and `reader_lock`, which means duplicate mappings extend the same shared mapped-reader lifetime instead of creating an independent wrapper-safe session.
- That shared lifetime keeps resize and remap policy pinned in C. The first successful `ring_buffer_map()` increments `resize_disabled`, builds `subbuf_ids`, and allocates the meta-page, while duplicate mappings only bump the mapped counters; there is no second setup path that would let a later wrapper treat one mapping as separately owned.
- The last-unmap path also stays coupled to the same kernel-owned teardown. `ring_buffer_unmap()` takes the fast decrement path while `user_mapped > 1`, but when the final user mapping goes away it drops `mapped` to match `user_mapped = 0`, frees `subbuf_ids`, frees the meta-page, and only then decrements `resize_disabled`, so resize remains blocked until the very last shared mapping disappears.
- The docs and implementation line up on why this should stay study-only. `Documentation/trace/ring-buffer-map.rst` warns that concurrent mapped readers compete for one unpredictable shared stream, and the VMA-dup plus final-unmap rules show that the kernel deliberately treats those readers as one shared lifetime contract rather than as isolated consumer handles that a Zig bridge could own piecemeal.

## CPU hotplug prepare lifetime audit

- `trace_rb_cpu_prepare()` makes the per-CPU lifetime rule explicit. When a CPU comes online it allocates a new ring-buffer shard if one does not already exist, but the function comment says those buffers are never freed when the CPU goes down because users would otherwise lose trace data that is still parked in that per-CPU buffer.
- The prepare path also keeps sizing and publication coupled in C. It reuses the common page count only when all existing CPU buffers agree, falls back to a two-page minimum when sizes differ, and only advertises the new CPU in `buffer->cpumask` after `on_each_cpu(rb_cpu_sync, NULL, 1)` plus the matching write barrier, so reader visibility and CPU-online enrollment still share one ordered transition.
- `tracer_alloc_buffers()` wires that same path into `cpuhp_setup_state_multi(CPUHP_TRACE_RB_PREPARE, "trace/RB:prepare", trace_rb_cpu_prepare, NULL)`, which keeps hotplug allocation, publication ordering, and later instance teardown inside one tracing-core control surface rather than a wrapper-safe helper seam.
- Because offline CPUs keep their old buffers and later online transitions reuse the same contract, the honest Phase 14 posture is still stay-in-C evidence only: a future Zig bridge should not imply independent ownership of per-CPU hotplug churn, retained unread data, or cross-CPU publication ordering.

## Tracefs reader-serialization audit

- `trace_access_lock()` and `trace_access_unlock()` are not disposable wrapper helpers. On SMP they coordinate the all-CPU `all_cpu_access_lock` with the per-CPU `cpu_access_lock`, and on non-SMP they still collapse to one shared mutex, so tracefs readers keep one C-owned rule for whole-buffer versus per-CPU consumption instead of splitting that ownership across bridge seams.
- The reason stays concrete in the surrounding `trace.c` comment: ring-buffer internals serialize low-level reader movement, but they do not keep previously returned events valid once another consumer turns a page back into normal ring-buffer use or hands it to `splice_read()`. That means the lifetime of consumed events is still governed above the raw buffer helpers, not by `ring_buffer_consume()` or `ring_buffer_read_page()` alone.
- `tracing_buffers_read()` and the splice path rely on that same top-level contract. The read side takes `trace_access_lock(iter->cpu_file)` before consuming pages, and the shared comment explains that the pages behind those events may otherwise be rewritten by producers or returned to the system after splice, so cross-reader exclusion remains part of one tracefs-facing lifetime rule.
- The net result stays study-only: reader serialization, consumed-event lifetime, and whole-buffer versus per-CPU exclusion remain explicitly in C, not as a new opening for `kernel/trace/ring_buffer.zig`.

## Reset and clear-path governance audit

- `include/linux/ring_buffer.h` exposes `ring_buffer_reset_cpu()`, `ring_buffer_reset_online_cpus()`, and `ring_buffer_reset()` as public entry points, and the same header lets remote exporters provide a `reset` callback through `struct ring_buffer_remote`, so reset is already a multi-entry contract rather than a private helper that a Zig wrapper could quietly duplicate.
- The user-facing clear paths are broader than a single buffer helper. `Documentation/trace/ftrace.rst` says changing `current_tracer` clears the ring buffer and the snapshot buffer, opening `trace` for writing with `O_TRUNC` clears the ring buffer contents, and changing `buffer_subbuf_size_kb` discards both live and snapshot data while tracing is stopped, which means tracefs already treats clear operations as shared tracing policy.
- `kernel/trace/trace.c` keeps that policy serialized above the raw ring-buffer internals. The `trace_access_lock()` commentary explains that consumed events cannot be exposed concurrently because pages may return to normal ring-buffer use or be handed to splice readers, and the same file routes `tracing_on` resume plus tracer selection through tracefs-wide control surfaces instead of a wrapper-safe per-helper reset seam.
- The honest Phase 14 decision is therefore to keep reset ownership in C. Any future reconsideration would need to explain how per-CPU reset, all-CPU reset, remote reset callbacks, tracefs clear-on-truncate behavior, and snapshot discard semantics remain aligned without weakening the current tracefs contract.

## Attached toolchain fallback guidance

- This anchor-local survey still rides the shared Phase 14 validator and build entrypoints; only the Zig binary changes when `zig` is not on `PATH`.
- Use `make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>` before replaying the shared bundle.
- Use `<attached-zig-path> build test --build-file zigux/tests/phase14_build.zig --summary all` for the direct shared build replay that includes this survey.
- Use `make -C zigux phase14 ZIG=<attached-zig-path>` for the wrapper path when the mounted toolchain is the only Zig available.

## Recorded gaps

The current lane state is:

- landed `phase14-build-gate`
- landed `phase14-make-target`
- landed `phase14-freeze-map-note`
- landed `phase14-ring-buffer-survey-gate`
- landed `phase14-ring-buffer-survey-note`
- landed `phase14-ring-buffer-boundary-decision-checklist`
- landed `phase14-ring-buffer-remote-reader-metadata-followup`
- landed `phase14-ring-buffer-overwrite-audit`
- landed `phase14-ring-buffer-wakeup-mmap-followup`
- landed `phase14-ring-buffer-splice-resize-followup`
- landed `phase14-ring-buffer-mapped-reader-ioctl-followup`
- landed `phase14-ring-buffer-reader-page-consume-followup`
- landed `phase14-ring-buffer-read-page-extraction-followup`
- landed `phase14-ring-buffer-read-page-allocation-contract-followup`
- landed `phase14-ring-buffer-subbuf-order-reconfig-followup`
- landed `phase14-ring-buffer-page-count-resize-workqueue-followup`
- landed `phase14-ring-buffer-snapshot-rollback-failure-followup`
- landed `phase14-ring-buffer-tracing-disabled-recovery-followup`
- landed `phase14-ring-buffer-map-dup-unmap-lifetime-followup`
- landed `phase14-ring-buffer-cpu-hotplug-lifetime-followup`
- landed `phase14-ring-buffer-reset-governance-followup`
- blocked `phase14-ring-buffer-zig-port-blocker`

This keeps the lane honest: Zigux now has an explicit reviewable record that `kernel/trace/ring_buffer.c` belongs in the study-only set for now, and that the repo still does not ship `kernel/trace/ring_buffer.zig`.

## Non-goals

This survey slice does not claim:

- a `kernel/trace/ring_buffer.zig` implementation
- reserve or commit parity for `ring_buffer_lock_reserve()` and `ring_buffer_unlock_commit()`
- reader-page handoff parity for `rb_get_reader_page()`
- consuming or non-consuming read parity for `ring_buffer_consume()` and `ring_buffer_read_start()`
- page-extraction parity for `ring_buffer_read_page()`
- overwrite, wakeup, resize, snapshot, or reset ownership
- mmap or splice ownership for the tracefs ring-buffer interfaces

## Gates

1. run the dedicated Phase 14 build
- `zig build test --build-file zigux/tests/phase14_build.zig`

2. run the convenience target
- `make -C zigux phase14`

3. run the attached-toolchain fallback path when `zig` is not on `PATH`
- `make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`
- `<attached-zig-path> build test --build-file zigux/tests/phase14_build.zig --summary all`
- `make -C zigux phase14 ZIG=<attached-zig-path>`

## Next bounded step

Keep the Phase 14 ring-buffer packet parked unless it drifts again or a future study-only step can stay narrower than the existing remote-reader, resize, rollback, reader-page, mapped-reader, kill-switch-recovery, hotplug-lifetime, and reset-governance audits; the next honest follow-up would need another concrete source-of-truth drift or a still-smaller tracefs evidence gap instead of reopening bridge code or generic tracing UX work.
