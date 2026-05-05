# Phase 10 Virtio MMIO Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_mmio.c`.

## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-mmio-survey`
- `PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md`
- `PHASE10_FREEZE_BOUNDARY_STATUS=aligned`
- `PHASE10_FREEZE_STATUS_CHANGE_CLAIMED=false`
- `PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport`
- `PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=true`
- `PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=false`
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
The live repo already has a bounded `drivers/virtio/virtio.zig` core starter, a dedicated `zigux/tests/phase10_virtio_ring_survey.zig` gate, a `drivers/virtio/virtio_ring.zig` lab helper, and the newer `virtio_input` starter plus survey paths.
This survey now records that the repo has already advanced beyond the older note: a tiny `drivers/virtio/virtio_mmio.zig` helper is present, it now carries one bounded device-feature selector and read window, one small transport-backed config-word window, one config-write disposition summary, and one probe-preflight summary, and the dedicated MMIO replay now also proves that a shorter restaged config window clears stale second-word data instead of leaving old bytes readable. The remaining gap is still interrupt, queue-discovery, reset, and lifecycle work.

## Survey findings
- `drivers/virtio/virtio_mmio.c` is present on `master` at 829 lines and mixes feature negotiation, config-space reads and writes, status handling, generation checks, interrupt acknowledgement, queue selection, queue sizing, ready-state toggles, virtqueue discovery, reset paths, and probe or remove lifecycle work.
- the live repo already ships `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/tests/phase10_build.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, and `Documentation/zigux/phase10-virtio-mmio-slice.md`.
- the current Zigux MMIO surface already includes a bounded `drivers/virtio/virtio_mmio.zig` helper for identity-register reads, queue-selected register reads, queue_num_max and queue_num bookkeeping, queue_ready state, helper-local status writes, helper-local config-generation bumps, helper-local interrupt-status staging, one bounded device-feature selector plus read window, one small transport-backed config-word window backed by staged in-memory bytes, one config-write disposition summary that reports changed bytes without mutating config space, and one probe-preflight summary around identity constants, vendor presence, legacy guest-page-size intent, bounded queue-register readiness, and interrupt-ack readiness.
- the dedicated MMIO tests now replay two staged device-feature words plus two staged config words, prove that a shorter restage clears stale second-word data and shrinks the readable config window, and keep both windows inside the helper instead of implying interrupt acknowledgement, queue discovery, reset, or probe lifecycle behavior.
- the live repo still does not model interrupt acknowledgement, queue discovery, reset flows, or probe or remove lifecycle behavior.
- this means the roadmap's "virtqueue wrappers first, MMIO wrappers later" rule now has a real bounded config-window foothold plus preflight and write-disposition review points, while the riskier transport and lifecycle paths remain intentionally blocked.

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
- the landed `phase10-mmio-feature-word-selector-helper`
- the landed `phase10-mmio-config-window-helper`
- the landed `phase10-mmio-probe-preflight-helper`
- the landed `phase10-mmio-config-write-disposition-helper`
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`

This keeps the lane concrete and reviewable without overstating MMIO progress: the helper-backed queue, status, feature-word, config-window, probe-preflight, and config-write-disposition footholds are real, the shared Phase 10 packet now acknowledges them honestly, including the shorter-restage stale-data regression proof, and the riskier lifecycle paths remain intentionally blocked.

## Non-goals

This survey slice does not yet claim:
- transport-backed config-space writes against a real device
- interrupt acknowledgement parity
- reset flows
- queue discovery beyond the bounded queue-size, feature-word, and config-word windows already staged in memory
- probe, remove, or command-line device creation parity
- DMA-facing queue plumbing
