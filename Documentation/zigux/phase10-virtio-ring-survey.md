# Phase 10 Virtio Ring Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_ring.c`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-ring-survey`
- lane: `P10-L07`
- surveyed inspected `master` head: `fe8a43ea2e186da0da152198b571dff57ea3c38c`
- scope: survey manifest, dedicated survey gate, shared Phase 10 build wiring, and a lane-level note that records what has now landed plus the remaining blocked MMIO lifecycle-and-IRQ boundary against the roadmap
- product boundary:
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `zigux/tests/phase10_virtio_ring_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_ring.c` as a primary anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo already has a bounded `drivers/virtio/virtio.zig` core starter with queue callback bookkeeping, descriptor-shape metadata, and notification accounting. This survey started by making the missing ring-helper gap explicit, and it now records that the first `drivers/virtio/virtio_ring.zig` lab slice has landed plus small used-buffer polling, callback disable and re-enable, callback enable-prepare, delayed-callback pacing, notify-prepare with rollover flushing, queue-reset guard plus drained-queue reset, and broken-queue recovery follow-ups while also keeping explicit that the MMIO helper ladder is already landed and only the blocked lifecycle and IRQ packet remains out of scope.

## Survey findings

- `drivers/virtio/virtio_ring.c` is present on `master` at 3940 lines and spans split rings, packed rings, descriptor state, DMA mapping helpers, callback toggling, notification bookkeeping, queue reset, resize, and break or unbreak handling.
- the live repo already ships `drivers/virtio/virtio.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_build.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, and `Documentation/zigux/phase10-virtio-core-survey.md`, so the ring lane now builds on both the bounded core helper and the dedicated core survey packet rather than the older core slice note alone.
- the current Zigux VirtIO surface now includes a bounded `drivers/virtio/virtio_ring.zig` helper for queue registration, layout metadata, outstanding-chain accounting, used-buffer polling, callback disable and re-enable bookkeeping, callback enable-prepare snapshots, delayed-callback pacing bookkeeping, notify-prepare bookkeeping with a 16-bit rollover flush, reset discipline that both refuses unsafe resets and clears drained queues without dropping shape metadata, and a tiny broken-queue recovery helper that reopens drained broken queues for teardown-safe queue reuse.
- the adjacent MMIO lane has now already landed the bounded register-window, queue-register, queue-notify, queue-address, config-window, config-write, and interrupt-ack helpers in `drivers/virtio/virtio_mmio.zig`, so no smaller ready transport follow-up remains ahead of the still-blocked lifecycle and IRQ packet.
- the live repo still does not model real descriptor tables, DMA helpers, interrupt callbacks, or transport-backed MMIO queue reset execution.
- this means the roadmap's "virtqueue wrappers first, MMIO wrappers later" rule is still satisfied through the landed MMIO interrupt-ack rung, and more speculative in-memory ring work should stay parked while the remaining transport-facing MMIO blocker stays explicit.

## Freeze-Boundary Posture

- `PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md`
- `PHASE10_FREEZE_BOUNDARY_STATUS=aligned`
- `PHASE10_FREEZE_BOUNDARY_OWNER=P10-L10`
- `PHASE10_FREEZE_BOUNDARY_ROLLBACK_OWNER=P10-L10`
- `PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport`
- `PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes`
- `PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no`
- `PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle`
- the freeze-in-C anchors remain `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`
- the separate Phase 14 study-only anchors remain `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`
- allowed Phase 10 delivery still stays inside `drivers/virtio/*.zig` plus justified bridge helpers in `zigux/kernel/` or `zigux/helpers/`
- the separate Phase 14 packet still owns those study-only anchors through `boundary maps`, `concurrency audits`, `explicit stay-in-C decisions where warranted`, and `wrapper-first or study-only posture`, and `kernel/workqueue_bridge.zig` plus `kernel/trace/ring_buffer.zig` remain only future Phase 14 destinations
- this survey uses the landed MMIO interrupt-ack rung only as evidence that no smaller ready transport follow-up remains ahead of `phase10-mmio-lifecycle-and-irq-paths`; it does not reopen `queue_setup_reset_paths`, `irq_parity`, `dma_paths`, `input_registration_lifecycle`, or `probe_remove_lifecycle`
- if the note, focused survey gate, or manifest stops carrying this freeze packet, the rollback owner for this lane is `P10-L10`, which must retire the lane back to its parked review-only posture instead of widening into new helper or transport claims

## Roadmap Parity Evidence

- `PHASE10_RING_ROADMAP_SCOREBOARD_ROWS=3`
- `PHASE10_RING_ROADMAP_VIRTQUEUE_WRAPPERS=starter_landed`
- evidence: `drivers/virtio/virtio_ring.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `Documentation/zigux/phase10-virtio-ring-survey.md`
- `PHASE10_RING_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed`
- evidence: `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `scripts/zigux/check-phase10-closure-inventory.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, and `zigux/Makefile`
- `PHASE10_RING_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport`
- evidence: `phase10-mmio-lifecycle-and-irq-paths`, `queue_setup_reset_paths`, `irq_parity`, and `dma_paths`

This keeps the ring survey honest against the roadmap without reopening the shared closure packet: the dedicated ring packet now says exactly which Phase 10 requirement rows it is helping prove, while the shared closure evidence still owns the separate MMIO wrappers row for the full cross-slice scoreboard.

## Recorded gaps

The survey manifest now records:

- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-ring-survey-gate`
- the landed `phase10-virtio-ring-survey-note`
- the landed `phase10-virtqueue-shape-helper`
- the landed `phase10-used-buffer-polling-helper`
- the landed `phase10-callback-disable-helper`
- the landed `phase10-callback-enable-helper`
- the landed `phase10-callback-enable-prepare-helper`
- the landed `phase10-callback-delay-helper`
- the landed `phase10-notify-prepare-helper`
- the landed `phase10-queue-reset-guard-helper`
- the landed `phase10-queue-reset-helper`
- the landed `phase10-broken-queue-recovery-helper`
- the landed `phase10-virtio-ring-slice-note`
- the landed `phase10-mmio-register-window-helper`
- the landed `phase10-mmio-queue-register-helper`
- the landed `phase10-mmio-queue-notify-helper`
- the landed `phase10-mmio-queue-address-helper`
- the landed `phase10-mmio-config-window-helper`
- the landed `phase10-mmio-config-write-helper`
- the landed `phase10-mmio-interrupt-ack-helper`
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`

This keeps the lane concrete and reviewable without overstating `virtio_ring` progress: the queue-shape foothold is real, used-buffer polling, callback disable and re-enable, callback enable-prepare snapshots, delayed-callback pacing, notify-prepare bookkeeping with rollover flushing, queue-reset guard plus drained-queue reset discipline, and broken-queue recovery for teardown-safe queue reuse are landed, the cross-lane MMIO ladder now truthfully records the landed register-window, queue-register, queue-notify, queue-address, config-window, config-write, and interrupt-ack steps, and only the broader transport-facing lifecycle and IRQ work remains intentionally constrained.

## Non-goals

This survey slice does not yet claim:

- real split-ring or packed-ring descriptor parity
- DMA mapping or unmapping wrappers
- `virtqueue_add_*`, `virtqueue_get_buf`, or `vring_interrupt` lifecycle behavior
- `virtio_mmio.c` transport glue
- any reopen of the Phase 14 study-only anchors `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`; this lane stays inside `drivers/virtio/*.zig` and does not use the landed MMIO interrupt-ack rung as a pretext for broader transport claims

## Gates

1. run the closure-backed validation guards
- `python3 scripts/zigux/check-phase10-closure-inventory.py`
- `python3 scripts/zigux/check-phase10-core-packet.py`
- `python3 scripts/zigux/validate-phase10.py`
- `python3 scripts/zigux/check-phase10-harness-coverage.py`
- `python3 scripts/zigux/validate-phase10-closure.py`
- `make -C zigux phase10-validate`

The direct closure-inventory guard, the direct bounded core-packet replay, and the direct harness-coverage replay now appear here explicitly because the manifest-backed ring packet depends on that published closure path to keep the landed broken-queue recovery rung, the focused multitouch-ready and queue-isolation harness replays, and the parked MMIO lifecycle blocker fail-closed together.

2. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig --summary all`

3. run the Linux-style Phase 10 test entrypoint
- `make -C zigux phase10-test`

4. run the convenience target
- `make -C zigux phase10`

This keeps the ring survey note aligned with the shared closure packet's exact test route instead of implying the direct build replay and combined convenience target are the only executable review surfaces for the current ring packet.

## Next bounded step

Do not reopen the ring lane for more speculative in-memory queue work. Leave this packet parked unless a future Phase 10 review can split `phase10-mmio-lifecycle-and-irq-paths` into a smaller transport-safe observation helper without widening the ring slice.
