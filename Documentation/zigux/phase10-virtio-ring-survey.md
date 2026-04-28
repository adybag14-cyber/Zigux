# Phase 10 Virtio Ring Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_ring.c`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-ring-survey`
- surveyed inspected `master` head: `42809b6eace69a1f8ec5a60ea39ca3ef6379182c`
- scope: survey manifest, dedicated survey gate, shared Phase 10 build wiring, and a lane-level note that records what has now landed plus the remaining MMIO follow-up ladder against the roadmap
- product boundary:
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `zigux/tests/phase10_virtio_ring_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_ring.c` as a primary anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo already has a bounded `drivers/virtio/virtio.zig` core starter with queue callback bookkeeping, descriptor-shape metadata, and notification accounting. This survey started by making the missing ring-helper gap explicit, and it now records that the first `drivers/virtio/virtio_ring.zig` lab slice has landed plus small used-buffer polling, callback disable and re-enable, callback enable-prepare, delayed-callback pacing, notify-prepare, and queue-reset guard follow-ups without pretending queue lifecycle parity is complete.

## Survey findings

- `drivers/virtio/virtio_ring.c` is present on `master` at 3940 lines and spans split rings, packed rings, descriptor state, DMA mapping helpers, callback toggling, notification bookkeeping, queue reset, resize, and break or unbreak handling.
- the live repo already ships `drivers/virtio/virtio.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_build.zig`, and `Documentation/zigux/phase10-virtio-core-slice.md`, and that core slice now covers queue callback bookkeeping, descriptor-shape metadata, and notification accounting.
- the current Zigux VirtIO surface now includes a bounded `drivers/virtio/virtio_ring.zig` helper for queue registration, layout metadata, outstanding-chain accounting, used-buffer polling, callback disable and re-enable bookkeeping, callback enable-prepare snapshots, delayed-callback pacing bookkeeping, notify-prepare bookkeeping, and reset-guard discipline that refuses queue resets while unpublished or unpolled work remains.
- the adjacent MMIO lane has now already landed the bounded register-window, queue-register, queue-notify, and queue-address helpers in `drivers/virtio/virtio_mmio.zig`, so the remaining honest cross-lane follow-up is the tiny config-window helper rather than the older queue-register step.
- the live repo still does not model real descriptor tables, DMA helpers, interrupt callbacks, or transport-backed queue reset execution.
- this means the roadmap's "virtqueue wrappers first, MMIO wrappers later" rule is still satisfied, and the next tiny cross-lane follow-up after the ring foothold is the `virtio_mmio` config-window helper rather than more speculative in-memory ring work.

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
- the landed `phase10-virtio-ring-slice-note`
- the landed `phase10-mmio-register-window-helper`
- the landed `phase10-mmio-queue-register-helper`
- the landed `phase10-mmio-queue-notify-helper`
- the landed `phase10-mmio-queue-address-helper`
- the ready-next `phase10-mmio-config-window-helper`
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`

This keeps the lane concrete and reviewable without overstating `virtio_ring` progress: the queue-shape foothold is real, used-buffer polling, callback disable and re-enable, callback enable-prepare snapshots, delayed-callback pacing, notify-prepare bookkeeping, and queue-reset guard discipline are landed, the cross-lane MMIO ladder now truthfully records the landed register-window, queue-register, queue-notify, and queue-address steps, and only the bounded config-window helper plus the broader transport-facing lifecycle and IRQ work remain intentionally constrained.

## Non-goals

This survey slice does not yet claim:

- real split-ring or packed-ring descriptor parity
- DMA mapping or unmapping wrappers
- `virtqueue_add_*`, `virtqueue_get_buf`, or `vring_interrupt` lifecycle behavior
- `virtio_mmio.c` transport glue
- any reopen of the Phase 14 study-only anchors `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`; this lane stays inside `drivers/virtio/*.zig` and only advances through the bounded `phase10-mmio-config-window-helper` follow-up

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Do not reopen the ring lane for more speculative in-memory queue work. The next bounded cross-lane follow-up is now the tiny `virtio_mmio` config-window helper, with IRQ, lifecycle, and other transport-facing MMIO work still blocked behind that smaller step.
