# Phase 10 Virtio Input Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_input.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-input-survey`
- `PHASE10_LANE_KEY=P10-L13`
- `PHASE10_SURVEYED_COMMIT=7361ac51374149a96b7a7a2c6ea3c995d8cc1231`
- scope: survey manifest, dedicated survey gate, dedicated `check-phase10-input-packet.py` review guard, shared Phase 10 build wiring, and a lane-level note that compares the already-landed starter against the remaining roadmap gap
- product boundary:
  - `scripts/zigux/check-phase10-input-packet.py`
  - `zigux/tests/phase10_virtio_input_manifest.json`
  - `zigux/tests/phase10_virtio_input_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-input-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_input.c` as a lab-driver anchor, but the repo has already moved past a blank starting point: the live tree now ships a bounded `drivers/virtio/virtio_input.zig` helper, dedicated tests, and slice notes.

This survey exists so the lane can compare that live starter against the roadmap and record the next honest gap without pretending the helper is either absent or already close to full driver parity.

A dedicated `scripts/zigux/check-phase10-input-packet.py` guard now keeps the manifest, survey gate, slice notes, and survey note aligned so future same-lane edits can catch review drift without reopening transport-facing helper growth.

This same packet is also the current roadmap-facing `lab-only driver validation` evidence for `virtio_input`: the dedicated input-packet guard, the shared Phase 10 build replay, and the shipped Linux-style `make -C zigux phase10-test` plus `make -C zigux phase10` routes keep the bounded starter reviewable without widening into transport-backed lifecycle claims.

## Survey findings

- `drivers/virtio/virtio_input.c` is present on `master` at 421 lines and mixes config-space selection, bitmap and ABS metadata reads, event-queue refill, status-queue sends, status-completion reclaim, multitouch timestamp suppression, input-device registration, freeze or restore hooks, and teardown paths.
- the live repo already ships `drivers/virtio/virtio_input.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `Documentation/zigux/phase10-virtio-input-slice.md`, and `Documentation/zigux/phase10-virtio-input-module-slice.md`.
- the landed Zigux starter now covers identity snapshots, property and event config bitmap summaries, ABS metadata summaries, capability-setup staging, one bounded multitouch slot-planning helper keyed off `ABS_MT_SLOT`, one bounded registration-preflight summary that reports queue, ready-state, capability-setup, and multitouch-slot blockers before any future `input_register_device()` handoff, fixed event and status queue planning, capped event-buffer fill accounting, ready-state gating, one bounded in-memory status-drain helper that reclaims completed status sends without touching suppressed multitouch counters, reset clearing, and multitouch `EV_MSC` plus `MSC_TIMESTAMP` suppression in memory only.
- the shared Phase 10 build packet can now keep both the main helper tests and the focused status-drain replay reviewable together instead of leaving the drain path outside the default lane gate.
- the live repo still does not model real event delivery, `input_register_device()` registration parity, freeze or restore parity, or transport-backed queue callbacks.
- this means the broader virtio_input roadmap gap has narrowed to validation truthfulness and the still-blocked transport-backed registration lifecycle work, not to another transport-facing helper jump.

## Recorded gaps

The survey manifest now records:

- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-ring-lab-helper`
- the landed `phase10-virtio-input-lab-helper`
- the landed `phase10-virtio-input-lab-gate`
- the landed `phase10-virtio-input-slice-note`
- the landed `phase10-virtio-input-survey-gate`
- the landed `phase10-virtio-input-survey-note`
- the landed `phase10-virtio-input-capability-setup-helper`
- the landed `phase10-virtio-input-multitouch-slot-helper`
- the landed `phase10-virtio-input-registration-preflight-helper`
- the landed `phase10-virtio-input-status-drain-helper`
- the still-blocked `phase10-virtio-input-registration-lifecycle`

This keeps the lane concrete and reviewable without overstating progress: the starter helper is real, the slot-planning foothold and registration-preflight boundary are now real, the bounded status-drain replay is now recorded in the same packet, and the risky registration and transport surface remains intentionally out of scope.

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

3. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

4. run the Linux-style Phase 10 test entrypoints
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Taken together, these gates are the current roadmap-facing `lab-only driver validation` evidence for this lane through the dedicated input-packet guard, the dedicated survey replay, the direct build replay, and the shipped Linux-style Phase 10 test entrypoints.

## Next bounded step

Keep the Phase 10 virtio_input lane narrow and prefer one bounded manifest, survey, helper-test, or checker truthfulness repair next before widening into `input_register_device()` lifecycle, queue callbacks, or transport-backed work.
