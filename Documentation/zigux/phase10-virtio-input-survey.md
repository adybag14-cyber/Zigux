# Phase 10 Virtio Input Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_input.c`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-input-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 10 build wiring, and a lane-level note that compares the already-landed starter against the remaining roadmap gap
- product boundary:
  - `zigux/tests/phase10_virtio_input_manifest.json`
  - `zigux/tests/phase10_virtio_input_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-input-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_input.c` as a lab-driver anchor, but the repo has already moved past a blank starting point: the live tree now ships a bounded `drivers/virtio/virtio_input.zig` helper, dedicated tests, and slice notes.

This survey exists so the lane can compare that live starter against the roadmap and record the next honest gap without pretending the helper is either absent or already close to full driver parity.

## Survey findings

- `drivers/virtio/virtio_input.c` is present on `master` at 421 lines and mixes config-space selection, bitmap and ABS metadata reads, event-queue refill, status-queue sends, multitouch timestamp suppression, input-device registration, freeze or restore hooks, and teardown paths.
- the live repo already ships `drivers/virtio/virtio_input.zig`, `zigux/tests/phase10_virtio_input.zig`, `Documentation/zigux/phase10-virtio-input-slice.md`, and `Documentation/zigux/phase10-virtio-input-module-slice.md`.
- the landed Zigux starter now covers identity snapshots, property and event config bitmap summaries, ABS metadata summaries, fixed event and status queue planning, capped event-buffer fill accounting, ready-state gating, reset clearing, and multitouch `EV_MSC` plus `MSC_TIMESTAMP` suppression in memory only.
- the live repo still does not model capability setup staging, real event delivery, `input_register_device()` registration parity, freeze or restore parity, or transport-backed queue callbacks.
- this means the next honest virtio_input step is one tiny in-memory capability-setup helper, not probe, remove, MMIO, or input core lifecycle work.

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
- the ready-next `phase10-virtio-input-capability-setup-helper`
- the still-blocked `phase10-virtio-input-registration-lifecycle`

This keeps the lane concrete and reviewable without overstating progress: the starter helper is real, but most of the config and registration surface from `virtio_input.c` remains intentionally out of scope.

## Non-goals

This survey slice does not yet claim:

- in-memory capability setup staging for `input_set_capability()` or `input_set_abs_params()`
- `input_dev` capability setup or registration parity
- real event delivery or status completion callbacks
- freeze, restore, remove, or reset lifecycle parity
- MMIO-backed transport work or DMA-facing queue behavior

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Stay in the Phase 10 virtio_input lane and add one small in-memory capability-setup helper next inside `drivers/virtio/virtio_input.zig` so the lab slice can connect the already-recorded config bitmap and ABS metadata to bounded capability intent before any transport, interrupt, or input-device registration work.
