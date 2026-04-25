# Phase 10 Virtio Input Slice

This document tracks the first bounded `drivers/virtio/virtio_input.c` lab helper under Phase 10.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-input-lab-helper`
- scope: config identity snapshots, bounded event and status queue planning, static event-buffer fill behavior, ready-state gating, multitouch timestamp suppression, dedicated Phase 10 input tests, and a slice note only
- product boundary:
  - `drivers/virtio/virtio_input.zig`
  - `zigux/tests/phase10_virtio_input.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap explicitly names `drivers/virtio/virtio_input.c` as a lab-driver anchor after the earlier virtio core and queue-wrapper footholds.

The live repo now has a bounded `drivers/virtio/virtio_input.zig` helper plus dedicated Phase 10 test wiring, but it still needs a lane note describing what that helper actually covers. This slice closes that reviewability gap without pretending to own transport setup, interrupt delivery, or full input-device registration.

## Landed starter surface

- module descriptor metadata anchored to `drivers/virtio/virtio_input.c`
- bounded config identity snapshots for name, serial, phys path, device IDs, and the small set of config selects already modeled by the helper
- event and status queue descriptor-count validation with power-of-two bounds
- static event-buffer fill accounting capped to the helper's in-memory event-buffer capacity
- ready-state gating so status sends stay blocked until both queues are configured
- multitouch `EV_MSC` and `MSC_TIMESTAMP` suppression bookkeeping that mirrors the loop-prevention branch in `virtio_input.c`
- dedicated Phase 10 tests and build wiring for the helper

## Non-goals

This slice does not yet claim:

- real config-space bitmap reads for properties, event bits, or absolute-axis metadata
- `input_dev` registration or capability setup
- real virtqueue buffers, interrupts, or DMA-facing queue behavior
- transport-backed probe, remove, freeze, restore, or reset paths

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Stay in the Phase 10 virtio_input lane and add one small in-memory config bitmap or absolute-axis metadata helper next so the lab slice can describe more of the `virtio_input_config` flow before any transport, interrupt, or input-device registration work.
