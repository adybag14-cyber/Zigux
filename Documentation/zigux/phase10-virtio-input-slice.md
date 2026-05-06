# Phase 10 Virtio Input Slice

This document tracks the first bounded `drivers/virtio/virtio_input.c` lab helper under Phase 10.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-input-lab-helper`
- scope: config identity snapshots, bounded property and event config bitmap summaries, bounded ABS metadata summaries, bounded capability-setup staging, bounded multitouch slot planning, event and status queue planning, static event-buffer fill behavior, ready-state gating, multitouch timestamp suppression, bounded status-completion drain summaries, dedicated Phase 10 input tests, the committed input survey manifest and survey gate, the dedicated input-packet review guard, the focused status-drain replay, and the shared Phase 10 build-and-make routes
- product boundary:
  - `drivers/virtio/virtio_input.zig`
  - `zigux/tests/phase10_virtio_input.zig`
  - `zigux/tests/phase10_virtio_input_status_drain.zig`
  - `zigux/tests/phase10_virtio_input_manifest.json`
  - `zigux/tests/phase10_virtio_input_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`
  - `scripts/zigux/check-phase10-input-packet.py`
- review surface:
  - `Documentation/zigux/phase10-virtio-input-slice.md`
  - `Documentation/zigux/phase10-virtio-input-module-slice.md`
  - `Documentation/zigux/phase10-virtio-input-survey.md`
  - `scripts/zigux/check-phase10-input-packet.py`
  - `zigux/tests/phase10_virtio_input.zig`
  - `zigux/tests/phase10_virtio_input_status_drain.zig`
  - `zigux/tests/phase10_virtio_input_manifest.json`
  - `zigux/tests/phase10_virtio_input_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`
- current review note:
  - current `master` carries an adjacent module slice, a dedicated survey note and survey gate, the committed `zigux/tests/phase10_virtio_input_manifest.json` anchor, the dedicated `check-phase10-input-packet.py` guard, the focused `phase10_virtio_input_status_drain.zig` replay, and the shared `phase10_build.zig` plus Linux-style `make -C zigux phase10-test` and `make -C zigux phase10` routes; reviewers should treat the input lane as one bounded manifest-backed checker-backed packet instead of a slice-note-only surface

## Why this slice exists

The Phase 10 roadmap explicitly names `drivers/virtio/virtio_input.c` as a lab-driver anchor after the earlier virtio core and queue-wrapper footholds.

The live repo now has a bounded `drivers/virtio/virtio_input.zig` helper plus dedicated Phase 10 test wiring, but it still needs a lane note describing what that helper actually covers. This slice closes that reviewability gap without pretending to own transport setup, interrupt delivery, or full input-device registration.

## Landed starter surface

- module descriptor metadata anchored to `drivers/virtio/virtio_input.c`
- bounded config identity snapshots for name, serial, phys path, device IDs, and the small set of config selects already modeled by the helper
- in-memory property-bit and event-bit config bitmap summaries keyed by selector and subselector, including the event-type surfacing rule from `virtinput_cfg_bits()`
- in-memory ABS metadata summaries for min, max, fuzz, flat, and resolution keyed by ABS code, mirroring the bounded `virtinput_cfg_abs()` readout without claiming real `input_dev` mutation
- in-memory capability-setup staging that only advances when event-bit configuration exists and keeps ABS parameter intent gated on matching `EV_ABS` capability bits
- one bounded in-memory multitouch slot-planning helper keyed off `ABS_MT_SLOT`, turning the staged ABS metadata into a capped slot count before any registration or transport work
- event and status queue descriptor-count validation with power-of-two bounds
- static event-buffer fill accounting capped to the helper's in-memory event-buffer capacity
- ready-state gating so status sends stay blocked until both queues are configured
- multitouch `EV_MSC` and `MSC_TIMESTAMP` suppression bookkeeping that mirrors the loop-prevention branch in `virtio_input.c`
- in-memory status-completion drain summaries that reclaim queued status sends without touching suppressed multitouch counters
- dedicated Phase 10 tests and build wiring for the helper, including a focused status-drain replay
- an adjacent manifest-backed survey-and-checker packet: the current input lane is also reviewed through the module slice, the dedicated survey note and survey gate, `zigux/tests/phase10_virtio_input_manifest.json`, the dedicated input-packet guard, the focused status-drain replay, `phase10_build.zig`, and the shared `make -C zigux phase10-test` plus `make -C zigux phase10` routes

## Non-goals

This slice does not yet claim:

- real config-space bitmap or ABS metadata reads from transport-backed config space
- `input_dev` registration or capability setup
- real virtqueue buffers, interrupts, or DMA-facing queue behavior
- transport-backed probe, remove, freeze, restore, or reset paths

## Gates

1. run the dedicated input-packet review guard
- `python3 scripts/zigux/check-phase10-input-packet.py --self-test`
- `python3 scripts/zigux/check-phase10-input-packet.py`

2. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

3. run the Linux-style Phase 10 test entrypoints
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Taken together, these gates keep the bounded input helper plus the focused status-drain replay reviewable through the dedicated packet guard, the direct build replay, and the shipped Linux-style Phase 10 test entrypoints on `master`.

## Next bounded step

Stay in the Phase 10 virtio_input lane and prefer one small manifest, survey, or helper-test truthfulness repair next so the lab slice stays reviewable before any transport, interrupt, or input-device registration work.
