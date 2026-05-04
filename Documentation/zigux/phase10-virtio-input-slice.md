# Phase 10 Virtio Input Slice

This document tracks the first bounded `drivers/virtio/virtio_input.c` lab helper under Phase 10.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-input-lab-helper`
- scope: config identity snapshots, bounded property and event config bitmap summaries, bounded ABS metadata summaries, bounded capability-setup staging, bounded multitouch slot planning, a bounded registration-preflight summary, a bounded queue-callback preflight summary, a bounded probe-preflight summary, a bounded registration-blocker summary, event and status queue planning, static event-buffer fill behavior, ready-state gating, multitouch timestamp suppression, a reset-local teardown observation summary, dedicated Phase 10 input tests, and a slice note only
- product boundary:
  - `drivers/virtio/virtio_input.zig`
  - `drivers/virtio/virtio_input_registration_blocker.zig`
  - `zigux/tests/phase10_virtio_input.zig`
  - `zigux/tests/phase10_virtio_input_registration_blocker.zig`
  - `zigux/tests/phase10_virtio_input_registration_blocker_build.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap explicitly names `drivers/virtio/virtio_input.c` as a lab-driver anchor after the earlier virtio core and queue-wrapper footholds.

The live repo now has a bounded `drivers/virtio/virtio_input.zig` helper plus dedicated Phase 10 test wiring, but it still needs a lane note describing what that helper actually covers. This slice closes that reviewability gap without pretending to own transport setup, interrupt delivery, or full input-device registration.

## Landed starter surface

- module descriptor metadata anchored to `drivers/virtio/virtio_input.c`
- bounded config identity snapshots for name, serial, phys path, device IDs, and the small set of config selects already modeled by the helper
- in-memory property-bit and event-bit config bitmap summaries keyed by selector and subselector, including the event-type surfacing rule from `virtinput_cfg_bits()`
- in-memory ABS metadata summaries for min, max, fuzz, flat, and resolution keyed by ABS code, mirroring the bounded `virtinput_cfg_abs()` readout without claiming real `input_dev` mutation
- in-memory capability-setup staging that only advances when event-bit configuration exists and keeps ABS parameter intent gated on matching `EV_ABS` capability bits
- in-memory multitouch slot planning keyed off `ABS_MT_SLOT`, deriving the bounded `input_mt_init_slots()`-style slot-count intent from staged ABS metadata only
- a bounded registration-preflight summary that records when identity, capability, and multitouch slot-init intent are all staged before any `input_register_device()` or transport-backed queue work
- a bounded queue-callback preflight helper summary that records when registration intent is staged, event buffers are filled, the status queue is configured, and the device is ready before any transport-backed callback claim
- a bounded probe-preflight summary that records when identity, capability setup, registration intent, queue provisioning, and ready-state gating have all converged before any transport-backed probe handoff claim
- a bounded registration-blocker summary in `drivers/virtio/virtio_input_registration_blocker.zig` that keeps `input_register_device()` lifecycle, transport-backed queue callbacks, freeze or restore handling, and probe or remove work explicitly parked as `blocked_on_risky_transport` even after the preflight summaries converge in memory
- event and status queue descriptor-count validation with power-of-two bounds
- static event-buffer fill accounting capped to the helper's in-memory event-buffer capacity
- ready-state gating so status sends stay blocked until both queues are configured
- multitouch `EV_MSC` and `MSC_TIMESTAMP` suppression bookkeeping that mirrors the loop-prevention branch in `virtio_input.c`
- a reset-local teardown observation summary that reports queue, status, config, and ABS staging state together with explicit reset cleanup intent while preserving the identity strings already copied at init time
- dedicated Phase 10 helper tests, the dedicated registration-blocker replay, and shared build wiring for the landed input packet

The same parked input packet also participates in the shared closure evidence bundle through `Documentation/zigux/phase10-closure-evidence.md`, `zigux/tests/phase10_closure_manifest.json`, `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`, and `zigux/tests/phase10_virtio_input_registration_blocker.zig`, so the current review path is broader than the dedicated input test alone even though the landed helper surface remains input-local.

## Non-goals

This slice does not yet claim:

- real config-space bitmap or ABS metadata reads from transport-backed config space
- `input_dev` registration or capability setup
- real virtqueue buffers, interrupts, or DMA-facing queue behavior
- transport-backed probe, remove, freeze, restore, or reset paths

## Gates

1. run the shared closure inventory gate
- `python3 scripts/zigux/check-phase10-closure-inventory.py`

2. run the shared closure validation path
- `python3 scripts/zigux/validate-phase10-closure.py`
- `python3 scripts/zigux/validate-phase10.py`
- `make -C zigux phase10-validate`

3. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig --summary all`

4. run the convenience target
- `make -C zigux phase10`

5. run the dedicated registration blocker replay
- `zig build test --build-file zigux/tests/phase10_virtio_input_registration_blocker_build.zig --summary all`

## Next bounded step

Keep the Phase 10 virtio_input lane at the current probe-preflight boundary until a future transport-backed packet can justify callback plumbing, probe handoff, or input-device registration work without blurring the risky-transport guardrails.
