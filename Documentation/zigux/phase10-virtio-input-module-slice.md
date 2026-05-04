# Phase 10 Virtio Input Module Slice

This bounded Phase 10 slice adds the first Zigux `virtio_input` lab driver starter anchored to `drivers/virtio/virtio_input.c`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-input-module-lab-helper`
- scope: identity and config snapshots, bounded capability-setup staging, bounded multitouch slot-init intent, one bounded registration-preflight summary, one bounded queue-callback preflight helper summary, one bounded probe-preflight summary, one bounded registration-blocker summary, queue planning, ready-state gating, multitouch timestamp suppression, a reset-local teardown observation summary, and the shared Phase 10 review path only
- product boundary:
  - `drivers/virtio/virtio_input.zig`
  - `drivers/virtio/virtio_input_registration_blocker.zig`
  - `zigux/tests/phase10_virtio_input.zig`
  - `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`
  - `zigux/tests/phase10_virtio_input_registration_blocker.zig`
  - `scripts/zigux/validate-phase10.py`
  - `scripts/zigux/check-phase10-harness-coverage.py`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_input.c` as a VM-friendly lab-driver anchor, but the freeze map and risky-transport posture still block any claim of real registration lifecycle, interrupt delivery, or transport-backed queue callback parity.

This module note exists to keep the landed helper surface readable on its own while still making the shared Phase 10 review packet explicit.

## Landed starter surface

- snapshots the input identity/config surface around name, serial, phys, and device IDs
- records bounded property-bit, event-bit, and ABS metadata summaries from the `virtio_input_config` surface
- stages bounded capability-setup intent so ABS metadata only advances when matching `EV_ABS` capability bits are present
- derives bounded multitouch slot-init intent from `ABS_MT_SLOT` metadata without claiming `input_mt_init_slots()` side effects
- records one bounded registration-preflight summary so identity, capability, and multitouch slot-init intent stay reviewable before any `input_register_device()` claim
- records one bounded queue-callback preflight helper summary so registration intent, queue fill state, status-queue setup, and ready-state gating stay explicit before any transport-backed callback claim
- records one bounded probe-preflight summary so identity, capability setup, registration intent, queue provisioning, and ready-state gating stay explicit before any transport-backed probe handoff claim
- records one bounded registration-blocker summary so `input_register_device()` lifecycle, transport-backed queue callbacks, freeze or restore handling, and probe or remove work stay explicitly parked as `blocked_on_risky_transport` even after the preflight summaries converge
- models the fixed two-queue plan used by the Linux driver: events and status
- caps prequeued event buffers to the static 64-entry event pool used by the C driver
- keeps status sending in-memory only and suppresses `EV_MSC` plus `MSC_TIMESTAMP` loops when multitouch forwarding is enabled
- exposes a reset-local teardown observation summary so queue, status, config, and ABS staging cleanup stays reviewable while init-time identity strings remain intact

The same parked input-module packet also participates in the shared Phase 10 closure bundle through `Documentation/zigux/phase10-closure-evidence.md`, `zigux/tests/phase10_closure_manifest.json`, `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`, the focused multitouch-ready replay in `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`, the dedicated blocker replay in `zigux/tests/phase10_virtio_input_registration_blocker.zig`, the shared validator route in `scripts/zigux/validate-phase10.py`, and the focused harness-coverage gate in `scripts/zigux/check-phase10-harness-coverage.py`, so this note is part of the broader lab-validation surface rather than a standalone helper stub.

## Non-goals

This slice does not yet claim:

- MMIO transport work
- DMA-facing queue plumbing
- input core capability registration
- transport-backed config reads
- probe, remove, freeze, restore, or registration lifecycle parity

## Gates

1. run the shared closure inventory gate
- `python3 scripts/zigux/check-phase10-closure-inventory.py`

2. run the shared validation path
- `python3 scripts/zigux/validate-phase10.py`
- `python3 scripts/zigux/check-phase10-harness-coverage.py`
- `python3 scripts/zigux/validate-phase10-closure.py`
- `make -C zigux phase10-validate`

3. run the shared Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig --summary all`

4. run the convenience target
- `make -C zigux phase10`

5. run the dedicated registration blocker replay
- `zig test zigux/tests/phase10_virtio_input_registration_blocker.zig`

## Next bounded step

Leave the lane parked at the current probe-preflight boundary unless fresh inspection finds another directly coupled review-surface drift inside the landed registration-preflight, queue-callback preflight, probe-preflight, registration-blocker, or teardown-observation packet. Any later widening into registration lifecycle, interrupts, or transport-backed callbacks still needs a separate risky-transport packet rather than another silent helper-only expansion.
