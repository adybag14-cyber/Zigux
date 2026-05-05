# Phase 10 Virtio MMIO Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_mmio.c`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-mmio-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 10 build wiring, and a lane-level note that records what is present in the live repo plus the remaining MMIO transport gap against the roadmap
- product boundary:
  - `zigux/tests/phase10_virtio_mmio_manifest.json`
  - `zigux/tests/phase10_virtio_mmio_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-mmio-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_mmio.c` as a primary anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo already has a bounded `drivers/virtio/virtio.zig` core starter, a dedicated `zigux/tests/phase10_virtio_ring_survey.zig` gate, a `drivers/virtio/virtio_ring.zig` lab helper that now reaches used-buffer polling, callback re-enable, and delayed-callback pacing, and the newer `virtio_input` starter plus survey paths. This survey makes the remaining MMIO transport gap explicit without pretending `drivers/virtio/virtio_mmio.zig` already exists.

## Survey findings

- `drivers/virtio/virtio_mmio.c` is present on `master` at 829 lines and mixes feature negotiation, config-space reads and writes, status handling, generation checks, interrupt acknowledgement, queue selection, queue sizing, ready-state toggles, virtqueue discovery, reset paths, and probe or remove lifecycle work.
- the live repo already ships `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `zigux/tests/phase10_build.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, and `Documentation/zigux/phase10-virtio-input-survey.md`.
- the live repo still does not ship `drivers/virtio/virtio_mmio.zig`.
- this means the roadmap's "virtqueue wrappers first, MMIO wrappers later" rule now points to one tiny in-memory MMIO register-window helper next, while interrupt, reset, queue-discovery, and probe lifecycle paths stay blocked behind that first transport foothold.

## Recorded gaps

The survey manifest now records:

- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-ring-survey-gate`
- the landed `phase10-virtio-ring-lab-helper`
- the landed `phase10-virtio-ring-slice-note`
- the landed `phase10-virtio-mmio-survey-gate`
- the landed `phase10-virtio-mmio-survey-note`
- the landed `phase10-callback-delay-helper`
- the ready-next `phase10-mmio-register-window-helper`
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`

This keeps the lane concrete and reviewable without overstating MMIO progress: the queue-facing footholds are real, the delayed-callback blocker is closed, the first transport-facing register-window step is now the next honest move, and the riskier lifecycle work is still intentionally blocked.

## Non-goals

This survey slice does not yet claim:

- real MMIO register reads or writes in Zig
- queue setup or teardown parity from `vm_setup_vq()` and `vm_del_vqs()`
- interrupt handling parity from `vm_interrupt()`
- probe, remove, or command-line device creation parity
- DMA-facing queue plumbing

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Stay in the Phase 10 MMIO lane and add one small in-memory register-window helper next before widening into interrupt acknowledgement, queue discovery, reset paths, or probe lifecycle work.
