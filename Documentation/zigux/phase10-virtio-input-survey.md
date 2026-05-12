# Phase 10 Virtio Input Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_input.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-input-survey`
- `PHASE10_LANE_KEY=P10-L13`
- `PHASE10_SURVEYED_COMMIT=7361ac51374149a96b7a7a2c6ea3c995d8cc1231`
- scope: survey manifest, dedicated survey gate, dedicated `check-phase10-input-packet.py` review guard, the helper-facing `drivers/virtio/virtio_input.zig` replay, the wrapper-facing `drivers/virtio/virtio_input_verify.zig` replay, the focused `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig` replay, the focused `zigux/tests/phase10_virtio_input_status_drain.zig` replay, the focused `zigux/tests/phase10_virtio_input_teardown_observation.zig` replay, the shared Phase 10 tests-root review companion, the shared Phase 10 driver lane sequencing note, the shared Phase 10 core, ring, and MMIO packet guards, shared Phase 10 build wiring, the shared Linux-style replay route, and a lane-level note that compares the already-landed starter against the remaining roadmap gap
- product boundary:
  - `scripts/zigux/check-phase10-input-packet.py`
  - `drivers/virtio/virtio_input.zig`
  - `drivers/virtio/virtio_input_verify.zig`
  - `zigux/tests/phase10_virtio_input.zig`
  - `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
  - `zigux/tests/phase10_virtio_input_status_drain.zig`
  - `zigux/tests/phase10_virtio_input_teardown_observation.zig`
  - `zigux/tests/phase10_virtio_input_manifest.json`
  - `zigux/tests/phase10_virtio_input_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-input-slice.md`
  - `Documentation/zigux/phase10-virtio-input-module-slice.md`
  - `Documentation/zigux/phase10-virtio-input-survey.md`
  - `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
  - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_input.c` as a lab-driver anchor, but the repo has already moved past a blank starting point: the live tree now ships a bounded `drivers/virtio/virtio_input.zig` helper, dedicated tests, and slice notes.

This survey exists so the lane can compare that live starter against the roadmap and record the next honest gap without pretending the helper is either absent or already close to full driver parity.

A dedicated `scripts/zigux/check-phase10-input-packet.py` guard now keeps the manifest, survey gate, slice notes, survey note, the helper-facing `drivers/virtio/virtio_input.zig` plus `zigux/tests/phase10_virtio_input.zig` replay, the wrapper-facing `drivers/virtio/virtio_input_verify.zig` replay, the focused `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig` replay, the focused `zigux/tests/phase10_virtio_input_status_drain.zig` replay, the focused `zigux/tests/phase10_virtio_input_teardown_observation.zig` replay, the shared tests-root review companion, the shared driver lane sequencing note, and the shared Phase 10 build-and-make packet aligned so future same-lane edits can catch review drift without reopening transport-facing helper growth.

This same packet is also the current roadmap-facing `lab-only driver validation` evidence for `virtio_input`: the dedicated input-packet guard, the helper-facing `drivers/virtio/virtio_input.zig` plus direct `zigux/tests/phase10_virtio_input.zig` replay, the wrapper-facing verify replay, the dedicated queue-callback-preflight replay, the focused status-drain replay, the dedicated teardown-observation replay, the shared tests-root review companion, the shared driver lane sequencing note, the shared `scripts/zigux/check-phase10-core-packet.py`, `scripts/zigux/check-phase10-ring-packet.py`, and `scripts/zigux/check-phase10-mmio-packet.py` guards, the shared Phase 10 build replay, and the shipped Linux-style `make -C zigux phase10-test` plus `make -C zigux phase10` routes keep the bounded starter reviewable without widening into transport-backed lifecycle claims.

## Survey findings

- `drivers/virtio/virtio_input.c` is present on `master` at 421 lines and mixes config-space selection, bitmap and ABS metadata reads, event-queue refill, status-queue sends, status-completion reclaim, multitouch timestamp suppression, input-device registration, freeze or restore hooks, and teardown paths.
- the live repo already ships `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, and `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`.
- the landed Zigux starter now covers identity snapshots, property and event config bitmap summaries, ABS metadata summaries, capability-setup staging, one bounded multitouch slot-planning helper keyed off `ABS_MT_SLOT`, one bounded probe-preflight summary that keeps identity staging, queue-fill readiness, and capability-setup blockers explicit before any future ready-state toggle or `input_register_device()` handoff, one bounded registration-preflight summary that reports queue, ready-state, capability-setup, and multitouch-slot blockers before any future `input_register_device()` handoff, one bounded queue-callback preflight summary that reports event and status queue configuration, event-buffer fill state, and ready-state blockers before any future transport-backed callback handoff, fixed event and status queue planning, capped event-buffer fill accounting, ready-state gating, one bounded in-memory status-drain helper that reclaims completed status sends without touching suppressed multitouch counters, one bounded teardown-observation summary that keeps identity preservation plus runtime- and capability-state cleanup explicit before any future transport-backed remove, freeze, or restore work, and multitouch `EV_MSC` plus `MSC_TIMESTAMP` suppression in memory only.
- the live repo also ships one dedicated queue-callback-preflight replay in `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, which keeps the bounded blocker ordering explicit beside the helper-facing tests, the wrapper-facing verify replay, and the focused status-drain replay instead of leaving that proof implicit inside broader packet summaries.
- the live repo also ships one dedicated teardown-observation replay in `zigux/tests/phase10_virtio_input_teardown_observation.zig`, which keeps identity preservation plus resettable runtime-state and capability-state cleanup explicit beside the helper-facing tests, the wrapper-facing verify replay, and the focused status-drain replay instead of leaving that teardown-local proof implicit inside broader packet summaries.
- the shared tests-root review companion and the shared driver lane sequencing note now also carry the input lane's focused verify and ownership surfaces, so the current lane packet stays explicit across the compact reviewer-facing summaries instead of leaving those bounded reminders implicit in the survey note alone.
- wrapper ownership stays with the already-landed shared Phase 10 packets: `drivers/virtio/virtio.zig` owns shared device-status bookkeeping, `drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning, and `drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning; the virtio_input lane only consumes those packets as prerequisites for lab-only driver validation.
- the live repo still does not model real event delivery, `input_register_device()` registration parity, freeze or restore parity, or transport-backed queue callbacks.
- this means the broader virtio_input roadmap gap has narrowed to validation truthfulness and the still-blocked transport-backed registration lifecycle work, not to another transport-facing helper jump.

## Recorded gaps

The survey manifest now records:

- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-ring-lab-helper`
- the landed `phase10-virtio-input-lab-helper`
- the landed `phase10-virtio-input-lab-gate`
- the landed `phase10-virtio-input-verify-replay`
- the landed `phase10-virtio-input-queue-callback-preflight-replay`
- the landed `phase10-virtio-input-teardown-observation-replay`
- the landed `phase10-virtio-input-slice-note`
- the landed `phase10-virtio-input-survey-gate`
- the landed `phase10-virtio-input-survey-note`
- the landed `phase10-virtio-input-capability-setup-helper`
- the landed `phase10-virtio-input-multitouch-slot-helper`
- the landed `phase10-virtio-input-probe-preflight-helper`
- the landed `phase10-virtio-input-registration-preflight-helper`
- the landed `phase10-virtio-input-queue-callback-preflight-helper`
- the landed `phase10-virtio-input-status-drain-helper`
- the landed `phase10-virtio-input-teardown-observation-helper`
- the landed `phase10-virtio-input-wrapper-ownership-note`
- the still-blocked `phase10-virtio-input-registration-lifecycle`

This keeps the lane concrete and reviewable without overstating progress: the starter helper is real, the dedicated wrapper-facing verify replay is now recorded as its own landed validation surface, the dedicated queue-callback-preflight replay is now recorded in the same packet, the dedicated teardown-observation replay is now recorded in the same packet, the slot-planning foothold, probe-preflight boundary, and registration-preflight boundary are now real, the queue-callback-preflight helper boundary is now real, the bounded status-drain replay and teardown-observation helper are now recorded in the same packet, the wrapper-ownership note is now real, and the risky registration and transport surface remains intentionally out of scope.

## Non-goals

This survey slice does not yet claim:

- `input_dev` capability setup or registration parity
- real event delivery or transport-backed status completion callbacks
- freeze, restore, remove, or reset lifecycle parity
- MMIO-backed transport work or DMA-facing queue behavior

## Gates

1. run the dedicated input-packet review guard
- `python3 scripts/zigux/check-phase10-input-packet.py --self-test`
- `python3 scripts/zigux/check-phase10-input-packet.py`

2. run the dedicated input survey gate
- `zig test zigux/tests/phase10_virtio_input_survey.zig`

3. run the helper-facing input replay
- `zig test zigux/tests/phase10_virtio_input.zig`

4. run the wrapper-facing verify replay
- `zig test drivers/virtio/virtio_input_verify.zig`

5. run the dedicated queue-callback-preflight replay
- `zig test zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`

6. run the focused status-drain replay
- `zig test zigux/tests/phase10_virtio_input_status_drain.zig`

7. run the dedicated teardown-observation replay
- `zig test zigux/tests/phase10_virtio_input_teardown_observation.zig`

8. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

9. run the Linux-style Phase 10 test entrypoints
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Taken together, these gates are the current roadmap-facing `lab-only driver validation` evidence for this lane through the dedicated input-packet guard, the helper-facing `drivers/virtio/virtio_input.zig` plus direct `zigux/tests/phase10_virtio_input.zig` replay, the wrapper-facing verify replay, the dedicated queue-callback-preflight replay, the dedicated survey replay, the focused status-drain replay, the dedicated teardown-observation replay, the shared tests-root review companion, the shared driver lane sequencing note, the shared Phase 10 core, ring, and MMIO packet guards, the direct build replay, and the shipped Linux-style Phase 10 test entrypoints.

## Next bounded step

Keep the Phase 10 virtio_input lane narrow and prefer one bounded manifest, survey, helper-test, checker, or ownership-note truthfulness repair next before widening into `input_register_device()` lifecycle, queue callbacks, or transport-backed work.
