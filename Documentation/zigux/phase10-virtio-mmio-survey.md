# Phase 10 Virtio MMIO Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_mmio.c`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-mmio-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 10 build wiring, the live in-memory MMIO helper, a lane-level slice note, and a lane-level note that records what is present in the repo plus the remaining MMIO transport gap against the roadmap
- product boundary:
  - `drivers/virtio/virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio_manifest.json`
  - `zigux/tests/phase10_virtio_mmio_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-mmio-slice.md`
  - `Documentation/zigux/phase10-virtio-mmio-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_mmio.c` as a primary anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo already has a bounded `drivers/virtio/virtio.zig` core starter, a dedicated `zigux/tests/phase10_virtio_ring_survey.zig` gate, a `drivers/virtio/virtio_ring.zig` lab helper, and the newer `virtio_input` starter plus survey paths. This survey now records that the repo has already advanced one step farther than the older note claimed: a tiny `drivers/virtio/virtio_mmio.zig` helper is present and the remaining gap is now truthful shared build and documentation around that helper, not a missing first MMIO foothold.

## Survey findings

- `drivers/virtio/virtio_mmio.c` is present on `master` at 829 lines and mixes feature negotiation, config-space reads and writes, status handling, generation checks, interrupt acknowledgement, queue selection, queue sizing, ready-state toggles, virtqueue discovery, reset paths, and probe or remove lifecycle work.
- the live repo already ships `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/tests/phase10_build.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, and `Documentation/zigux/phase10-virtio-mmio-slice.md`.
- the current Zigux MMIO surface already includes a bounded `drivers/virtio/virtio_mmio.zig` helper for identity-register reads, queue-selected register reads, queue_num_max and queue_num bookkeeping, queue_ready state, helper-local status writes, helper-local config-generation bumps, and helper-local interrupt-status staging.
- the live repo now also carries `Documentation/zigux/phase10-virtio-mmio-slice.md`, which records that helper surface and its non-goals directly instead of leaving the transport foothold described only by tests and the survey note.
- the live repo still does not model device-feature selector windows, transport-backed config-space reads, interrupt acknowledgement, reset flows, or probe or remove lifecycle behavior.
- this means the roadmap's "virtqueue wrappers first, MMIO wrappers later" rule now points to one tiny feature-word selector helper next, while interrupt, reset, and lifecycle paths stay blocked behind that smaller transport follow-up.

## Recorded gaps

The survey manifest now records:

- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-ring-survey-gate`
- the landed `phase10-virtio-ring-lab-helper`
- the landed `phase10-virtio-ring-slice-note`
- the landed `phase10-virtio-mmio-survey-gate`
- the landed `phase10-virtio-mmio-survey-note`
- the landed `phase10-mmio-register-window-helper`
- the landed `phase10-mmio-queue-size-helper`
- the landed `phase10-virtio-mmio-slice-note`
- the ready-next `phase10-mmio-feature-word-selector-helper`
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`

This keeps the lane concrete and reviewable without overstating MMIO progress: the helper-backed queue and status footholds are real, the shared Phase 10 packet now acknowledges them honestly, the next honest move is still smaller than interrupt or reset work, and the riskier lifecycle paths remain intentionally blocked.

## Non-goals

This survey slice does not yet claim:

- device-feature selector or device-feature read-window parity
- transport-backed config-space reads or writes against a real device
- interrupt acknowledgement parity
- reset flows
- queue discovery beyond the bounded queue-size window already staged in memory
- probe, remove, or command-line device creation parity
- DMA-facing queue plumbing

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Stay in the Phase 10 MMIO lane and add one small device-feature selector and read-window helper next before widening into interrupt acknowledgement, reset paths, or probe lifecycle work.