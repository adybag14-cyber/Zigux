# Phase 10 Virtio Input Slice

This document tracks the first bounded `drivers/virtio/virtio_input.c` lab helper under Phase 10.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-input-lab-helper`
- scope: config identity snapshots, bounded property and event config bitmap summaries, bounded ABS metadata summaries, bounded capability-setup staging, bounded multitouch slot planning, bounded probe-preflight summaries, bounded registration-preflight summaries, bounded queue-callback preflight summaries, bounded teardown-observation summaries, event and status queue planning, static event-buffer fill behavior, ready-state gating, multitouch timestamp suppression, bounded status-completion drain summaries, the wrapper-facing `drivers/virtio/virtio_input_verify.zig` replay, the focused `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig` replay, the focused `zigux/tests/phase10_virtio_input_registration_preflight.zig` replay, the focused `zigux/tests/phase10_virtio_input_teardown_observation.zig` replay, dedicated Phase 10 input tests, the committed input survey manifest and survey gate, the dedicated input-packet review guard, the focused status-drain replay, and the shared Phase 10 build-and-make routes
- product boundary:
  - `drivers/virtio/virtio_input.zig`
  - `drivers/virtio/virtio_input_verify.zig`
  - `zigux/tests/phase10_virtio_input.zig`
  - `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
  - `zigux/tests/phase10_virtio_input_registration_preflight.zig`
  - `zigux/tests/phase10_virtio_input_teardown_observation.zig`
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
  - `drivers/virtio/virtio_input_verify.zig`
  - `zigux/tests/phase10_virtio_input.zig`
  - `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
  - `zigux/tests/phase10_virtio_input_registration_preflight.zig`
  - `zigux/tests/phase10_virtio_input_teardown_observation.zig`
  - `zigux/tests/phase10_virtio_input_status_drain.zig`
  - `zigux/tests/phase10_virtio_input_manifest.json`
  - `zigux/tests/phase10_virtio_input_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`
- current review note:
  - current `master` carries an adjacent module slice, a dedicated survey note and survey gate, the committed `zigux/tests/phase10_virtio_input_manifest.json` anchor, the dedicated `check-phase10-input-packet.py` guard, the wrapper-facing `drivers/virtio/virtio_input_verify.zig` replay, the focused `phase10_virtio_input_queue_callback_preflight.zig`, `phase10_virtio_input_registration_preflight.zig`, `phase10_virtio_input_teardown_observation.zig`, and `phase10_virtio_input_status_drain.zig` replays, and the shared `phase10_build.zig` plus Linux-style `make -C zigux phase10-test` and `make -C zigux phase10` routes; reviewers should treat the input lane as one bounded manifest-backed checker-backed packet instead of a slice-note-only surface

## Why this slice exists

The Phase 10 roadmap explicitly names `drivers/virtio/virtio_input.c` as a lab-driver anchor after the earlier virtio core and queue-wrapper footholds.

The live repo now has a bounded `drivers/virtio/virtio_input.zig` helper plus dedicated Phase 10 test wiring, but it still needs a lane note describing what that helper actually covers. This slice closes that reviewability gap without pretending to own transport setup, interrupt delivery, or full input-device registration.

## Landed starter surface

- module descriptor metadata anchored to `drivers/virtio/virtio_input.c`
- bounded config identity snapshots for name, serial, phys path, device IDs, and the small set of config selects already modeled by the helper
- one bounded probe-preflight summary that keeps identity staging, queue-fill readiness, and capability-setup blockers explicit before any future ready-state toggle or `input_register_device()` handoff
- in-memory property-bit and event-bit config bitmap summaries keyed by selector and subselector, including the event-type surfacing rule from `virtinput_cfg_bits()`
- in-memory ABS metadata summaries for min, max, fuzz, flat, and resolution keyed by ABS code, mirroring the bounded `virtinput_cfg_abs()` readout without claiming real `input_dev` mutation
- in-memory capability-setup staging that only advances when event-bit configuration exists and keeps ABS parameter intent gated on matching `EV_ABS` capability bits
- one bounded in-memory multitouch slot-planning helper keyed off `ABS_MT_SLOT`, turning the staged ABS metadata into a capped slot count before any registration or transport work
- one bounded registration-preflight summary that reports queue, ready-state, capability-setup, and multitouch-slot blockers before any future `input_register_device()` handoff
- one bounded queue-callback preflight summary that reports event and status queue configuration, event-buffer fill state, and ready-state blockers before any future transport-backed callback handoff
- event and status queue descriptor-count validation with power-of-two bounds
- static event-buffer fill accounting capped to the helper's in-memory event-buffer capacity
- ready-state gating so status sends stay blocked until both queues are configured
- multitouch `EV_MSC` and `MSC_TIMESTAMP` suppression bookkeeping that mirrors the loop-prevention branch in `virtio_input.c`
- in-memory status-completion drain summaries that reclaim queued status sends without touching suppressed multitouch counters
- one bounded teardown-observation summary that keeps identity preservation plus runtime- and capability-state cleanup explicit before any future transport-backed remove, freeze, or restore work
- dedicated Phase 10 tests and build wiring for the helper, including the wrapper-facing `drivers/virtio/virtio_input_verify.zig` replay, the focused queue-callback-preflight replay, the focused registration-preflight replay, the focused teardown-observation replay, and the focused status-drain replay
- an adjacent manifest-backed survey-and-checker packet: the current input lane is also reviewed through the module slice, the dedicated survey note and survey gate, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, the dedicated input-packet guard, the focused queue-callback-preflight replay, the focused registration-preflight replay, the focused teardown-observation replay, the focused status-drain replay, `phase10_build.zig`, and the shared `make -C zigux phase10-test` plus `make -C zigux phase10` routes

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

2. run the dedicated helper-facing input replay
- `zig test zigux/tests/phase10_virtio_input.zig`

3. run the wrapper-facing verify replay
- `zig test drivers/virtio/virtio_input_verify.zig`

4. run the focused queue-callback-preflight replay
- `zig test zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`

5. run the focused registration-preflight replay
- `zig test zigux/tests/phase10_virtio_input_registration_preflight.zig`

6. run the focused teardown-observation replay
- `zig test zigux/tests/phase10_virtio_input_teardown_observation.zig`

7. run the focused status-drain replay
- `zig test zigux/tests/phase10_virtio_input_status_drain.zig`

8. run the dedicated input survey gate
- `zig test zigux/tests/phase10_virtio_input_survey.zig`

9. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

10. run the Linux-style Phase 10 test entrypoints
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Taken together, these gates keep the bounded input helper plus the direct helper-facing replay, the wrapper-facing verify replay, the focused queue-callback-preflight replay, the focused registration-preflight replay, the focused teardown-observation replay, the focused status-drain replay, and the dedicated survey replay reviewable through the dedicated packet guard, the direct build replay, and the shipped Linux-style Phase 10 test entrypoints on `master`.

## Next bounded step

Stay in the Phase 10 virtio_input lane and prefer one small manifest, survey, or helper-test truthfulness repair next so the lab slice stays reviewable before any transport, interrupt, or input-device registration work.
