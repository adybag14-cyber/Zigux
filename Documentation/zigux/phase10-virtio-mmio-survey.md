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
- scope: survey manifest, dedicated survey gate, direct MMIO helper replay, dedicated packet review guard, shared Phase 10 core, ring, and input packet guards, the shared reset-queue, driver-id, ring-verify, input-verify, and input status-drain replays, shared Phase 10 build wiring, the shared Linux-style replay route, the live in-memory MMIO helper, a lane-level slice note, and a lane-level note that records what is present in the repo plus the remaining MMIO transport gap against the roadmap
- product boundary:
  - `drivers/virtio/virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio_manifest.json`
  - `zigux/tests/phase10_virtio_mmio_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-mmio-slice.md`
  - `Documentation/zigux/phase10-virtio-mmio-survey.md`
  - `scripts/zigux/check-phase10-mmio-packet.py`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_mmio.c` as a primary anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo already has a bounded `drivers/virtio/virtio.zig` core starter, a dedicated `zigux/tests/phase10_virtio_ring_survey.zig` gate, a `drivers/virtio/virtio_ring.zig` lab helper, and the newer `virtio_input` starter plus survey paths. This survey now records that the repo has already advanced beyond the older note: a tiny `drivers/virtio/virtio_mmio.zig` helper is present, it already carries one bounded device-feature selector and read window plus one small transport-backed config-word window, it now also plans one bounded config-word write against the staged window without mutating config space, it now also summarizes the absolute end offset and changed-byte mask of that prepared write without mutating config space, it now also exposes one explicit transport-identity summary for magic, version, device ID, vendor ID, and legacy guest-page-size posture, it now also exposes one bounded probe-preflight summary that consumes that identity snapshot for the earliest `virtio_mmio_probe()`-style checks, and it now also exposes one compact selected-queue readiness summary for `queue_num_max`, `queue_num`, `queue_ready`, programmed-size posture, and queue-ready-for-handoff posture without widening into queue discovery or reset flows. The remaining gap is still interrupt acknowledgement, queue discovery, reset, and lifecycle work, and that wider transport-facing bucket remains intentionally blocked.

## Freeze-Boundary Evidence

The current MMIO packet stays aligned with `Documentation/zigux/freeze-map.md` by keeping the risky transport posture explicit.

Allowed evidence for this lane remains limited to driver-local lab slices, survey manifests, and shared validation gates.

Allowed roadmap destinations for bounded follow-on work in this blocked packet remain `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` support surfaces; this survey does not claim a wider transport-facing home.

Forbidden transport claims remain queue setup or reset paths, IRQ parity, DMA paths, input registration lifecycle, and probe or remove lifecycle behavior.

Any status review beyond this blocked-on-risky-transport packet still needs an Architecture Council reopen request with fresh linked evidence attached; this survey does not attach one.

## Survey findings
- `drivers/virtio/virtio_mmio.c` is present on `master` at 829 lines and mixes feature negotiation, config-space reads and writes, status handling, generation checks, interrupt acknowledgement, queue selection, queue sizing, ready-state toggles, virtqueue discovery, reset paths, and probe or remove lifecycle work.
- the live repo already ships `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_input_verify.zig`, eleven dedicated Phase 10 virtio test or survey files under `zigux/tests/` (`phase10_virtio_core.zig`, `phase10_virtio_core_reset_queue.zig`, `phase10_virtio_core_survey.zig`, `phase10_virtio_driver_id.zig`, `phase10_virtio_ring.zig`, `phase10_virtio_ring_survey.zig`, `phase10_virtio_input.zig`, `phase10_virtio_input_status_drain.zig`, `phase10_virtio_input_survey.zig`, `phase10_virtio_mmio.zig`, and `phase10_virtio_mmio_survey.zig`), `zigux/tests/phase10_build.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, and `Documentation/zigux/phase10-virtio-mmio-slice.md`.
- the current Zigux MMIO surface already includes a bounded `drivers/virtio/virtio_mmio.zig` helper for identity-register reads, queue-selected register reads, queue_num_max and queue_num bookkeeping, queue_ready state, helper-local status writes, helper-local config-generation bumps, helper-local interrupt-status staging, one bounded device-feature selector plus read window, one small transport-backed config-word window backed by staged in-memory bytes, one bounded config-word write plan that reports the current generation and previous word value without mutating config space, one bounded config-write disposition summary that reports the absolute end of the prepared config-word window plus a changed-byte mask without mutating config space, one explicit transport-identity summary for magic, version, device ID, vendor ID, and legacy guest-page-size posture, one bounded probe-preflight summary that consumes that identity snapshot for the earliest `virtio_mmio_probe()`-style checks, and one compact selected-queue readiness summary for the currently selected queue's `queue_num_max`, `queue_num`, `queue_ready`, `queue_size_programmed`, and `queue_ready_for_handoff` posture.
- the dedicated MMIO tests now replay two staged device-feature words plus two staged config words, prove that a shorter restaged config window clears stale second-word data and shrinks the readable config window, prove that the helper plans one bounded config-word write without mutating config space or implying interrupt acknowledgement, queue discovery, reset, or probe lifecycle behavior, prove that the helper summarizes the absolute end offset and changed-byte mask of a prepared config-word write without mutating config space, prove the transport-identity summary for both legacy and missing-device or missing-vendor posture, prove that the probe-preflight summary preserves legacy guest-page-size intent while staying ready for handoff when the transport identity is otherwise aligned before it flips from ready to blocked when device presence or vendor presence falls away, and prove that the selected-queue readiness summary tracks the currently selected queue from empty to programmed to ready and back to an unprogrammed sibling queue before queue handoff.
- the live shared Phase 10 packet already keeps `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig` explicit beside `zigux/tests/phase10_build.zig`, the shipped ring, input, and MMIO survey notes, and the four dedicated packet guards, so the MMIO lane's shared review surface is not just the survey gate plus the helper-local replay.
- the live repo still does not model interrupt acknowledgement, queue discovery, reset flows, or probe or remove lifecycle behavior.
- this means the roadmap's `virtqueue wrappers first, MMIO wrappers later` rule now has a real bounded config-window foothold, one small lab-only config-write planning foothold, one small lab-only config-write disposition foothold, one explicit transport-identity foothold, one early probe-preflight observation foothold, one compact selected-queue readiness foothold, and an already-landed shared verifier packet around the ring and input lab slices, while the riskier transport and lifecycle paths remain intentionally blocked.

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
- the landed `phase10-mmio-config-write-plan-helper`
- the landed `phase10-mmio-transport-identity-helper`
- the landed `phase10-mmio-probe-preflight-helper`
- the landed `phase10-mmio-config-write-disposition-helper`
- the landed `phase10-mmio-selected-queue-readiness-helper`
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`

This keeps the lane concrete and reviewable without overstating MMIO progress: the queue-facing footholds are real, the shared Phase 10 packet now honestly records the bounded register-window, queue-size, selected-queue readiness, feature-word, config-window, config-write planning, transport-identity, config-write disposition, and probe-preflight surfaces together with the shorter-restage stale-data regression proof, the already-landed ring and input verifier replays, and the broader transport-facing lifecycle work is still intentionally blocked.

## Non-goals

This survey slice does not yet claim:
- transport-backed config-space writes against a real device
- interrupt acknowledgement parity
- reset flows
- queue discovery beyond the bounded queue-size, selected-queue readiness, feature-word, config-word, planning-only config-write, transport-identity, and probe-preflight windows already staged in memory
- probe, remove, or command-line device creation parity
- DMA-facing queue plumbing

## Gates

1. run the dedicated MMIO packet review guard
- `python3 scripts/zigux/check-phase10-mmio-packet.py --self-test`
- `python3 scripts/zigux/check-phase10-mmio-packet.py`

2. run the direct MMIO helper replay
- `zig test zigux/tests/phase10_virtio_mmio.zig`

3. run the dedicated MMIO survey gate
- `zig test zigux/tests/phase10_virtio_mmio_survey.zig`

4. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

5. run the Linux-style Phase 10 test entrypoints when the wider packet is available
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Taken together, these gates keep the bounded MMIO packet reviewable through the dedicated MMIO packet guard, the direct MMIO helper replay, the dedicated MMIO survey replay, the shared Phase 10 core, ring, and input packet guards behind the shared `phase10_build.zig` plus `make -C zigux phase10-test` route, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_input_verify.zig`, the shared `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig` replays, the direct build replay, and the shipped Linux-style Phase 10 test entrypoints on `master`.

## Next bounded step

Keep the Phase 10 MMIO lane parked unless fresh inspection finds another equally small survey, manifest, checker, or helper-test truthfulness gap inside the landed MMIO packet; do not widen into interrupt acknowledgement, queue discovery, reset paths, or probe lifecycle work without fresh reopen evidence.
