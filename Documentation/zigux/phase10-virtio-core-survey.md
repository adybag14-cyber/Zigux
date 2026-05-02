# Phase 10 Virtio Core Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio.c`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-core-survey`
- lane: `P10-L03`
- surveyed inspected `master` head: `f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21`
- scope: survey manifest, dedicated survey gate, shared Phase 10 build wiring, and a lane-level note that compares the already-landed core starter against the remaining roadmap gap
- product boundary:
  - `zigux/tests/phase10_virtio_core_manifest.json`
  - `zigux/tests/phase10_virtio_core_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-core-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio.c` as the first virtio-core anchor, and the live repo already ships a bounded `drivers/virtio/virtio.zig` helper plus dedicated implementation tests.

This survey exists so the core lane no longer relies on the slice note alone while the adjacent Phase 10 lanes already use manifest-backed survey records. It keeps the closure bundle honest about what the virtio core slice now covers and what still remains blocked.

The live validation path is intentionally split too: the closure-inventory gate, the closure validator, and the all-up Phase 10 build keep the core slice inside the shared evidence bundle, while the standalone `scripts/zigux/validate-phase10.py` packet still directly guards the adjacent ring, input, and MMIO review surface rather than the core-local files themselves.

## Survey findings

- `drivers/virtio/virtio.c` is present on `master` at 730 lines and mixes status sequencing, feature negotiation, config-change enable and disable handling, config-change delivery gating, reset, and broader probe or remove lifecycle paths.
- the live repo already ships `drivers/virtio/virtio.zig`, `zigux/tests/phase10_virtio_core.zig`, and `Documentation/zigux/phase10-virtio-core-slice.md`.
- the landed Zigux helper now covers bounded status sequencing, feature negotiation, queue callback bookkeeping, queue descriptor-shape metadata, config-change pending and flush bookkeeping, one bounded config-generation counter plus observation summaries, the small driver-binding branch around `drv && drv->config_changed`, one bounded remove-side handoff that re-acknowledges the device in memory after clearing handler and queue bookkeeping, and an explicit last-disposition summary for whether the most recent config change was deferred, delivered, or ignored in memory only.
- the live repo still does not model full probe or remove lifecycle parity, transport-backed reset paths, or MMIO and virtqueue setup behavior.
- the live Phase 10 review path is now explicit about ownership boundaries: `python3 scripts/zigux/check-phase10-closure-inventory.py`, `python3 scripts/zigux/validate-phase10-closure.py`, and `zig build test --build-file zigux/tests/phase10_build.zig --summary all` keep the core survey inside the closure packet, while `python3 scripts/zigux/validate-phase10.py` remains the narrower shared validator for the adjacent ring-plus-input-plus-MMIO packet.
- this means the virtio-core packet is still parked at a clean boundary: one more reviewable remove-side bookkeeping branch is now concrete, but the next broader Phase 10 work still belongs in adjacent ring or MMIO wrappers rather than in transport-facing core lifecycle claims.

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
- the landed `phase10-driver-remove-bookkeeping-helper`
- the landed `phase10-config-generation-summary-helper`
- the landed `phase10-config-delivery-disposition-helper`
- the still-blocked `phase10-core-probe-remove-lifecycle`

This keeps the lane reviewable without overstating progress: the core starter is real and materially useful, including the last config-change branch outcome and one bounded remove-side handoff, but the broader lifecycle and transport-facing parts of `virtio.c` remain intentionally out of scope.

## Non-goals

This survey slice does not yet claim:

- probe, full remove, or transport-backed reset lifecycle parity
- real virtqueue wrappers from `virtio_ring.c`
- real MMIO register-window or interrupt behavior from `virtio_mmio.c`
- broader transport-backed driver registration or teardown work

## Gates

1. run the closure-backed inventory and packet guards
- `python3 scripts/zigux/check-phase10-closure-inventory.py`
- `python3 scripts/zigux/validate-phase10-closure.py`

2. run the adjacent shared validator-first path
- `python3 scripts/zigux/validate-phase10.py`
- `make -C zigux phase10-validate`

The standalone shared validator still directly guards the adjacent ring, input, and MMIO packet, while the closure inventory, closure validator, and all-up build keep the core slice inside the same bounded evidence bundle.

3. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig --summary all`

4. run the convenience target
- `make -C zigux phase10`

## Latest verification snapshot

- verified against current `master` head `f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21`
- `zig test zigux/tests/phase10_virtio_core_survey.zig`
- observed results:
  - focused Phase 10 virtio-core survey replay passed after syncing the manifest, survey note, and survey gate to the same inspected head
  - broader Phase 10 closure and all-up build replay were not rerun in this narrow drift-fix lane because no core helper, ring, MMIO, or transport-facing behavior changed

## Next bounded step

Leave the Phase 10 virtio-core lane parked again unless fresh repo inspection finds a directly coupled drift inside the landed core packet; the next new Phase 10 wrapper work should stay in adjacent ring or MMIO lanes instead of widening core lifecycle claims.
