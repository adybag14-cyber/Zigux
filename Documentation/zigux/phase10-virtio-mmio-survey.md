# Phase 10 Virtio MMIO Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_mmio.c` and the landed MMIO helper follow-ons.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-mmio-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 10 build wiring, a lane-level note that records what is present in the live repo plus the remaining MMIO transport gap against the roadmap, the first MMIO register-window helper, the bounded queue-register helper, and the queue-notify helper that now makes the next queue-address gap concrete
- product boundary:
  - `zigux/tests/phase10_virtio_mmio_manifest.json`
  - `zigux/tests/phase10_virtio_mmio_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-mmio-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_mmio.c` as a primary anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo already has a bounded `drivers/virtio/virtio.zig` core starter, a dedicated `zigux/tests/phase10_virtio_core_survey.zig` gate with its paired note, a dedicated `zigux/tests/phase10_virtio_ring_survey.zig` gate, a `drivers/virtio/virtio_ring.zig` lab helper that now reaches used-buffer polling, callback re-enable, delayed-callback pacing, and queue reset discipline, and the newer `virtio_input` starter plus survey paths. The repo now also ships a `drivers/virtio/virtio_mmio.zig` register-window helper, a bounded queue-register helper, and a queue-notify helper, so this survey can move from "MMIO is still absent" to an honest record of what tiny MMIO surface has landed and what larger transport work remains blocked.

## Survey findings

- `drivers/virtio/virtio_mmio.c` is present on `master` at 829 lines and mixes feature negotiation, config-space reads and writes, status handling, generation checks, interrupt acknowledgement, queue selection, queue sizing, ready-state toggles, queue notify side effects, queue-address programming, virtqueue discovery, reset paths, and probe or remove lifecycle work.
- the live repo already ships `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_mmio.zig`, eight dedicated Phase 10 virtio test or survey files under `zigux/tests/` (`phase10_virtio_core.zig`, `phase10_virtio_core_survey.zig`, `phase10_virtio_ring.zig`, `phase10_virtio_ring_survey.zig`, `phase10_virtio_input.zig`, `phase10_virtio_input_survey.zig`, `phase10_virtio_mmio.zig`, and `phase10_virtio_mmio_survey.zig`), `zigux/tests/phase10_build.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, and `Documentation/zigux/phase10-virtio-mmio-slice.md`.
- the landed MMIO helper stays intentionally narrow: it now models MMIO register offsets, bounded feature-page selection, queue-select and queue-size planning, queue-ready bookkeeping, queue-notify snapshots, status and reset bookkeeping, config-generation tracking, and interrupt-ack bookkeeping only.
- this means the roadmap's "virtqueue wrappers first, MMIO wrappers later" rule now holds for a small but real MMIO foothold, and the next honest follow-up is a version-scoped queue-address planning helper rather than probe, remove, DMA, or broader lifecycle glue.

## Recorded gaps

The survey manifest now records:

- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-core-survey-gate`
- the landed `phase10-virtio-core-survey-note`
- the landed `phase10-virtio-ring-survey-gate`
- the landed `phase10-virtio-ring-lab-helper`
- the landed `phase10-virtio-ring-slice-note`
- the landed `phase10-virtio-mmio-survey-gate`
- the landed `phase10-virtio-mmio-survey-note`
- the landed `phase10-callback-delay-helper`
- the landed `phase10-mmio-register-window-helper`
- the landed `phase10-mmio-queue-register-helper`
- the landed `phase10-mmio-queue-notify-helper`
- the ready-next `phase10-mmio-queue-address-helper`
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`

This keeps the lane concrete and reviewable without overstating MMIO progress: the queue-facing footholds are real, the bounded register-window, queue-register, and queue-notify steps are now landed, and the broader transport-facing lifecycle work is still intentionally blocked.

## Non-goals

This survey slice does not yet claim:

- real MMIO pointer-backed reads or writes in Zig
- queue-address register programming or full queue setup and teardown parity from `vm_setup_vq()` and `vm_del_vqs()`
- interrupt-handler parity from `vm_interrupt()`
- probe, remove, or command-line device creation parity
- DMA-facing queue plumbing

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Stay in the broader Phase 10 MMIO lane and add one small queue-address planning helper next around legacy PFN versus modern DESC, AVAIL, and USED register windows without claiming queue setup, IRQ delivery, probe, or remove parity.
