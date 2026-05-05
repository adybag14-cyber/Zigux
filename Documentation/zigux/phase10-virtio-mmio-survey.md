# Phase 10 Virtio MMIO Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_mmio.c`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-mmio-survey`
- scope: bounded MMIO register-window helper, dedicated helper and survey gates, shared Phase 10 build wiring, and a lane-level note that records what is present in the live repo plus the remaining MMIO transport gap against the roadmap
- product boundary:
  - `drivers/virtio/virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio_manifest.json`
  - `zigux/tests/phase10_virtio_mmio_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-mmio-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_mmio.c` as a primary anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo already has a bounded `drivers/virtio/virtio.zig` core starter, a dedicated `zigux/tests/phase10_virtio_ring_survey.zig` gate, a `drivers/virtio/virtio_ring.zig` lab helper that now reaches used-buffer polling, callback re-enable, and delayed-callback pacing, and the newer `virtio_input` starter plus survey paths. This survey now records that the first `virtio_mmio` step has landed as one tiny in-memory register-window helper instead of keeping that transport foothold merely hypothetical.

## Survey findings

- `drivers/virtio/virtio_mmio.c` is present on `master` at 829 lines and mixes feature negotiation, config-space reads and writes, status handling, generation checks, interrupt acknowledgement, queue selection, queue sizing, ready-state toggles, virtqueue discovery, reset paths, and probe or remove lifecycle work.
- the live repo now ships `drivers/virtio/virtio_mmio.zig` plus `zigux/tests/phase10_virtio_mmio.zig`, so the MMIO lane has a real bounded helper and not just a parked survey gap.
- the new helper stays intentionally small: it models aligned in-memory register-window reads, queue-select bookkeeping, bounded queue-size programming, queue-ready state, status writes, and config-generation reads without claiming queue discovery, reset, interrupt acknowledgement, or probe lifecycle behavior.
- the live repo still does not model full interrupt acknowledgement, queue discovery, reset parity, or transport-backed virtqueue setup and teardown.
- this means the next honest MMIO step is one tiny interrupt-status and acknowledgement helper, while broader lifecycle paths stay blocked behind that narrower transport foothold.

## Recorded gaps

The survey manifest now records:

- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-ring-survey-gate`
- the landed `phase10-virtio-ring-lab-helper`
- the landed `phase10-callback-delay-helper`
- the landed `phase10-virtio-mmio-lab-helper`
- the landed `phase10-virtio-mmio-lab-gate`
- the landed `phase10-virtio-mmio-survey-gate`
- the landed `phase10-virtio-mmio-survey-note`
- the ready-next `phase10-mmio-interrupt-ack-helper`
- the still-blocked `phase10-mmio-lifecycle-and-queue-discovery-paths`

This keeps the lane concrete and reviewable without overstating MMIO progress: the queue-facing footholds are real, the first transport-facing register-window step is now landed, and the riskier interrupt and lifecycle work is still intentionally blocked.

## Non-goals

This survey slice does not yet claim:

- real device-feature negotiation through MMIO selector registers
- queue discovery or teardown parity from `vm_find_vqs()` and `vm_del_vqs()`
- interrupt acknowledgement parity from `vm_interrupt()`
- reset, probe, remove, or command-line device creation parity
- DMA-facing queue plumbing

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Stay in the Phase 10 MMIO lane and add one small in-memory interrupt-status and acknowledgement helper next before widening into queue discovery, reset paths, or probe lifecycle work.
