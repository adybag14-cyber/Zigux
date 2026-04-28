# Phase 10 Virtio Core Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio.c`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-core-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 10 build wiring, and a lane-level note that compares the already-landed core starter against the remaining roadmap gap
- product boundary:
  - `zigux/tests/phase10_virtio_core_manifest.json`
  - `zigux/tests/phase10_virtio_core_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-core-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio.c` as the first virtio-core anchor, and the live repo already ships a bounded `drivers/virtio/virtio.zig` helper plus dedicated implementation tests.

This survey exists so the core lane no longer relies on the slice note alone while the adjacent Phase 10 lanes already use manifest-backed survey records. It keeps the closure bundle honest about what the virtio core slice now covers and what still remains blocked.

## Survey findings

- `drivers/virtio/virtio.c` is present on `master` at 730 lines and mixes status sequencing, feature negotiation, config-change enable and disable handling, config-change delivery gating, reset, and broader probe or remove lifecycle paths.
- the live repo already ships `drivers/virtio/virtio.zig`, `zigux/tests/phase10_virtio_core.zig`, and `Documentation/zigux/phase10-virtio-core-slice.md`.
- the landed Zigux helper now covers bounded status sequencing, feature negotiation, queue callback bookkeeping, queue descriptor-shape metadata, config-change pending and flush bookkeeping, and the small driver-binding branch around `drv && drv->config_changed` in memory only.
- the live repo now models bounded config-generation increments, last-observed generation state, and pending-generation visibility beside the earlier config-change bookkeeping.
- the live repo still does not model probe or remove lifecycle parity, transport-backed reset paths, or MMIO and virtqueue setup behavior.
- this means the virtio core lane no longer has another honest core-local starter to claim before risky lifecycle work; the remaining broader lifecycle gap should stay blocked instead of quietly widening.

## Recorded gaps

The survey manifest now records:

- the landed `phase10-build-gate`
- the landed `phase10-closure-evidence-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-core-lab-gate`
- the landed `phase10-virtio-core-slice-note`
- the landed `phase10-virtio-core-survey-gate`
- the landed `phase10-virtio-core-survey-note`
- the landed `phase10-config-change-bookkeeping-helper`
- the landed `phase10-driver-binding-bookkeeping-helper`
- the landed `phase10-config-generation-summary-helper`
- the still-blocked `phase10-core-probe-remove-lifecycle`

This keeps the lane reviewable without overstating progress: the core starter is real and materially useful, but the broader lifecycle and transport-facing parts of `virtio.c` remain intentionally out of scope.

## Non-goals

This survey slice does not yet claim:

- config-generation parity beyond one future bounded summary helper
- probe, remove, or transport-backed reset lifecycle parity
- real virtqueue wrappers from `virtio_ring.c`
- real MMIO register-window or interrupt behavior from `virtio_mmio.c`
- broader transport-backed driver registration or teardown work

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Leave the Phase 10 virtio-core helper parked unless fresh repo inspection finds review drift in the landed config-generation summary packet. Any broader follow-up in this lane should stay explicitly blocked on risky transport-backed probe, remove, or reset lifecycle work rather than widening core claims indirectly through ring or MMIO changes.
