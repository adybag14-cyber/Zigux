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
- scope: survey manifest, dedicated survey gate, direct MMIO helper replay, direct MMIO verifier replay, dedicated packet review guard, dedicated MMIO freeze-boundary guard, shared Phase 10 core, ring, and input packet guards, the shared reset-queue, driver-id, ring-verify, input-verify, input queue-callback-preflight, input registration-preflight, input teardown-observation, mmio-verify, and input status-drain replays, shared Phase 10 build wiring, the shared tests-root review companion, the shared driver-lane sequencing note, the shared closure manifest, the shared Linux-style replay route, the live in-memory MMIO helper, a lane-level slice note, and a lane-level note that records what is present in the repo plus the remaining MMIO transport gap against the roadmap
- product boundary:
  - `drivers/virtio/virtio_mmio.zig`
  - `drivers/virtio/virtio_mmio_verify.zig`
  - `zigux/tests/phase10_virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio_manifest.json`
  - `zigux/tests/phase10_virtio_mmio_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-mmio-slice.md`
  - `Documentation/zigux/phase10-virtio-mmio-survey.md`
  - `scripts/zigux/check-phase10-mmio-packet.py`
  - `scripts/zigux/check-phase10-mmio-freeze-boundary.py`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_mmio.c` as a primary anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo already has a bounded `drivers/virtio/virtio.zig` core starter, a dedicated `zigux/tests/phase10_virtio_ring_survey.zig` gate, a `drivers/virtio/virtio_ring.zig` lab helper, and the newer `virtio_input` starter plus survey paths. This survey now records that the repo has already advanced beyond the older note: a tiny `drivers/virtio/virtio_mmio.zig` helper is present, it already carries one bounded device-feature selector and read window plus one compact feature-negotiation summary for the selected feature word, staged device-feature bits, and staged driver-feature register value, it already carries one small transport-backed config-word window, it now also plans one bounded config-word write against the staged window without mutating config space, it now also summarizes the absolute end offset and changed-byte mask of that prepared write without mutating config space, it now also exposes one explicit transport-identity summary for magic, version, device ID, vendor ID, and legacy guest-page-size posture, it now also exposes one bounded probe-preflight summary that consumes that identity snapshot for the earliest `virtio_mmio_probe()`-style checks, it now also exposes one compact selected-queue readiness summary for `queue_num_max`, `queue_num`, `queue_ready`, programmed-size posture, and queue-ready-for-handoff posture plus one bounded configured-queue coverage summary for configured, programmed, ready, and handoff-ready queue counts across the staged queue window without widening into queue discovery or reset flows, and it now also ships a dedicated `drivers/virtio/virtio_mmio_verify.zig` replay that keeps the current wrapper-facing probe-preflight, config-review, selected-queue-local handoff, and configured-queue coverage posture reviewable. The remaining gap is still interrupt acknowledgement, queue discovery, reset, and lifecycle work, and that wider transport-facing bucket remains intentionally blocked.

## Freeze-Boundary Evidence

The current MMIO packet stays aligned with `Documentation/zigux/freeze-map.md` by keeping the risky transport posture explicit.

Allowed evidence for this lane remains limited to driver-local lab slices, survey manifests, and shared validation gates.

Allowed roadmap destinations for bounded follow-on work in this blocked packet remain `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` support surfaces; this survey does not claim a wider transport-facing home.

Forbidden transport claims remain queue setup or reset paths, IRQ parity, DMA paths, input registration lifecycle, and probe or remove lifecycle behavior.

Any status review beyond this blocked-on-risky-transport packet still needs an Architecture Council reopen request with fresh linked evidence attached; this survey does not attach one.

## Survey findings
- `drivers/virtio/virtio_mmio.c` is present on `master` at 829 lines and mixes feature negotiation, config-space reads and writes, status handling, generation checks, interrupt acknowledgement, queue selection, queue sizing, ready-state toggles, virtqueue discovery, reset paths, and probe or remove lifecycle work.
- the live repo already ships `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio_verify.zig`, fourteen dedicated Phase 10 virtio test or survey files under `zigux/tests/` (`phase10_virtio_core.zig`, `phase10_virtio_core_reset_queue.zig`, `phase10_virtio_core_survey.zig`, `phase10_virtio_driver_id.zig`, `phase10_virtio_ring.zig`, `phase10_virtio_ring_survey.zig`, `phase10_virtio_input.zig`, `phase10_virtio_input_queue_callback_preflight.zig`, `phase10_virtio_input_registration_preflight.zig`, `phase10_virtio_input_teardown_observation.zig`, `phase10_virtio_input_status_drain.zig`, `phase10_virtio_input_survey.zig`, `phase10_virtio_mmio.zig`, and `phase10_virtio_mmio_survey.zig`), `zigux/tests/phase10_build.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, and `Documentation/zigux/phase10-virtio-mmio-slice.md`.
- the current Zigux MMIO surface already includes a bounded `drivers/virtio/virtio_mmio.zig` helper for identity-register reads, queue-selected register reads, queue_num_max and queue_num bookkeeping, queue_ready state, helper-local status writes, helper-local config-generation bumps, helper-local interrupt-status staging, one bounded device-feature selector plus read window, one compact feature-negotiation summary for the selected device-feature word, the staged device-feature bits, and the staged driver-feature register value, one small transport-backed config-word window backed by staged in-memory bytes, one bounded config-word write plan that reports the current generation and previous word value without mutating config space, one bounded config-write disposition summary that reports the absolute end of the prepared config-word window plus a changed-byte mask without mutating config space, one explicit transport-identity summary for magic, version, device ID, vendor ID, and legacy guest-page-size posture, one bounded probe-preflight summary that consumes that identity snapshot for the earliest `virtio_mmio_probe()`-style checks, one compact selected-queue readiness summary for the currently selected queue's `queue_num_max`, `queue_num`, `queue_ready`, `queue_size_programmed`, and `queue_ready_for_handoff` posture, one bounded configured-queue coverage summary for configured, programmed, ready, and handoff-ready queue counts plus full-coverage posture across the staged queue window, and one dedicated `drivers/virtio/virtio_mmio_verify.zig` replay that keeps wrapper-facing probe-preflight blockers, generation-scoped config review, selected-queue-local handoff posture, and configured-queue coverage posture live.
- the dedicated MMIO tests now replay two staged device-feature words plus the compact feature-negotiation summary for both in-range and drifted selector posture, two staged config words, prove that a shorter restaged config window clears stale second-word data and shrinks the readable config window instead of leaving old bytes readable, prove that the helper plans one bounded config-word write without mutating config space or implying interrupt acknowledgement, queue discovery, reset, or probe lifecycle behavior, prove that the helper summarizes the absolute end offset and changed-byte mask of a prepared config-word write without mutating config space, prove the transport-identity summary for both legacy and missing-device or missing-vendor posture, prove that the probe-preflight summary preserves legacy guest-page-size intent while staying ready for handoff when the transport identity is otherwise aligned before it flips from ready to blocked when device presence or vendor presence falls away, prove that the selected-queue readiness summary tracks the currently selected queue from empty to programmed to ready and back to an unprogrammed sibling queue before queue handoff, and prove that the configured-queue coverage summary tracks staged queues from empty to partially programmed to fully handoff-ready across the configured queue window.
- the dedicated MMIO verifier now replays wrapper-facing probe-preflight blockers, generation-scoped config-review posture, selected-queue-local handoff behavior, and configured-queue coverage posture directly from `drivers/virtio/virtio_mmio_verify.zig`, so the packet's build route no longer relies on the helper-local test file alone to keep that narrower wrapper-facing surface live.
- the live shared Phase 10 packet already keeps `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `zigux/tests/phase10_closure_manifest.json`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig` explicit beside `zigux/tests/phase10_build.zig`, the shipped ring, input, and MMIO survey notes, the four dedicated packet guards, and the dedicated `scripts/zigux/check-phase10-mmio-freeze-boundary.py` guard, so the MMIO lane's shared review surface is not just the survey gate plus the helper-local replay.
- the live repo still does not model interrupt acknowledgement, queue discovery, reset flows, or probe or remove lifecycle behavior.
- this means the roadmap's `virtqueue wrappers first, MMIO wrappers later` rule now has a real bounded config-window foothold, one small lab-only feature-negotiation foothold, one small lab-only config-write planning foothold, one small lab-only config-write disposition foothold, one explicit transport-identity foothold, one early probe-preflight observation foothold, one compact selected-queue readiness foothold, one compact configured-queue coverage foothold, one dedicated MMIO verifier foothold, one dedicated MMIO freeze-boundary guard, and an already-landed shared verifier packet around the ring and input lab slices, while the riskier transport and lifecycle paths remain intentionally blocked.

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
- the landed `phase10-mmio-feature-negotiation-summary-helper`
- the landed `phase10-mmio-config-window-helper`
- the landed `phase10-mmio-config-write-plan-helper`
- the landed `phase10-mmio-transport-identity-helper`
- the landed `phase10-mmio-probe-preflight-helper`
- the landed `phase10-mmio-config-write-disposition-helper`
- the landed `phase10-mmio-selected-queue-readiness-helper`
- the landed `phase10-mmio-configured-queue-coverage-helper`
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`

This keeps the lane concrete and reviewable without overstating MMIO progress: the queue-facing footholds are real, the shared Phase 10 packet now honestly records the bounded register-window, queue-size, feature-negotiation, selected-queue readiness, configured-queue coverage, feature-word, config-window, planning-only config-write, transport-identity, config-write disposition, probe-preflight, dedicated freeze-boundary, and dedicated verifier surfaces together with the shorter-restage stale-data regression proof, the already-landed ring and input verifier replays, the shared input queue-callback-preflight, registration-preflight, teardown-observation, and status-drain replays, the shared tests-root companion, the driver-lane sequencing note, the shared closure manifest, and the broader transport-facing lifecycle work is still intentionally blocked.

## Non-goals

This survey slice does not yet claim:
- transport-backed config-space writes against a real device
- interrupt acknowledgement parity
- reset flows
- queue discovery beyond the bounded queue-size, selected-queue readiness, configured-queue coverage, feature-word, feature-negotiation, config-word, planning-only config-write, transport-identity, and probe-preflight windows already staged in memory
- probe, remove, or command-line device creation parity
- DMA-facing queue plumbing

## Gates

1. run the dedicated MMIO packet review guards
- `python3 scripts/zigux/check-phase10-mmio-packet.py --self-test`
- `python3 scripts/zigux/check-phase10-mmio-packet.py`
- `python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py --self-test`
- `python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py`

2. run the direct MMIO helper replay
- `zig test zigux/tests/phase10_virtio_mmio.zig`

3. run the direct MMIO verifier replay
- `zig test drivers/virtio/virtio_mmio_verify.zig`

4. run the dedicated MMIO survey gate
- `zig test zigux/tests/phase10_virtio_mmio_survey.zig`

5. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

6. run the Linux-style Phase 10 test entrypoints when the wider packet is available
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Taken together, these gates keep the bounded MMIO packet reviewable through the dedicated MMIO packet guard, the dedicated MMIO freeze-boundary guard, the direct MMIO helper replay, the direct MMIO verifier replay, the dedicated MMIO survey replay, the shared Phase 10 core, ring, and input packet guards behind the shared `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `zigux/tests/phase10_closure_manifest.json`, `phase10_build.zig` plus `make -C zigux phase10-test` route, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio_verify.zig`, the shared `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig` replays, the direct build replay, and the shipped Linux-style Phase 10 test entrypoints on `master`.

## Next bounded step

Keep the Phase 10 MMIO lane parked unless fresh inspection finds another equally small survey, manifest, checker, or helper-test truthfulness gap inside the landed MMIO packet; do not widen into interrupt acknowledgement, queue discovery, reset paths, or probe lifecycle work without fresh reopen evidence.
