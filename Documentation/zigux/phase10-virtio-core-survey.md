# Phase 10 Virtio Core Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio.c`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-core-survey`
- lane: `P10-L01`
- surveyed inspected `master` head: `d30cbe483a2f019ae797b309a29556bd58fe00d0`
- scope: survey manifest, dedicated survey gate, shared Phase 10 build wiring, and a lane-level note that compares the already-landed core starter against the remaining roadmap gap
- product boundary:
  - `zigux/tests/phase10_virtio_core_manifest.json`
  - `zigux/tests/phase10_virtio_core_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-core-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio.c` as the first virtio-core anchor, and the live repo already ships a bounded `drivers/virtio/virtio.zig` helper plus dedicated implementation tests.

This survey exists so the core lane no longer relies on the slice note alone while the adjacent Phase 10 lanes already use manifest-backed survey records. It keeps the closure bundle honest about what the virtio core slice now covers and what still remains blocked.

The live validation path is intentionally split too: `scripts/zigux/check-phase10-core-packet.py`, the closure-inventory gate, the closure validator, and the all-up Phase 10 build keep the core slice inside the shared evidence bundle, while the standalone `scripts/zigux/validate-phase10.py` packet still directly guards the adjacent ring, input, and MMIO review surface rather than the core-local files themselves.

## Survey findings

- `drivers/virtio/virtio.c` is present on `master` at 730 lines and mixes status sequencing, feature negotiation, config-change enable and disable handling, config-change delivery gating, reset, and broader probe or remove lifecycle paths.
- the live repo already ships `drivers/virtio/virtio.zig`, `zigux/tests/phase10_virtio_core.zig`, and `Documentation/zigux/phase10-virtio-core-slice.md`.
- the landed Zigux helper now covers bounded status sequencing, feature negotiation, queue callback bookkeeping, queue descriptor-shape metadata, config-change pending and flush bookkeeping, the documented non-nestable driver-side config toggle rule, one bounded config-generation counter plus observation summaries, the small driver-binding branch around `drv && drv->config_changed`, one bounded driver ID-table match path for `virtio_id_match()` and first-match `virtio_dev_match()` ordering, one bounded remove-side handoff that re-acknowledges the device in memory after clearing handler and queue bookkeeping, and an explicit last-disposition summary for whether the most recent config change was deferred, delivered, or ignored in memory only.
- the live repo still does not model full probe or remove lifecycle parity, transport-backed reset paths, or MMIO and virtqueue setup behavior.
- the live Phase 10 review path is now explicit about ownership boundaries: `python3 scripts/zigux/check-phase10-core-packet.py`, `python3 scripts/zigux/check-phase10-closure-inventory.py`, `python3 scripts/zigux/validate-phase10-closure.py`, and `zig build test --build-file zigux/tests/phase10_build.zig --summary all` keep the core survey inside the closure packet, while `python3 scripts/zigux/validate-phase10.py` remains the narrower shared validator for the adjacent ring-plus-input-plus-MMIO packet.
- this means the virtio-core packet is still parked at a clean boundary: one more reviewable driver-model branch is now concrete, but the next broader Phase 10 work still belongs in adjacent ring or MMIO wrappers rather than in transport-facing core lifecycle claims.

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
- the landed `phase10-driver-id-match-helper`
- the landed `phase10-driver-remove-bookkeeping-helper`
- the landed `phase10-config-generation-summary-helper`
- the landed `phase10-config-delivery-disposition-helper`
- the landed `phase10-config-driver-toggle-guard-helper`
- the still-blocked `phase10-core-probe-remove-lifecycle`

This keeps the lane reviewable without overstating progress: the core starter is real and materially useful, including the bounded driver ID-table match path, the last config-change branch outcome, the nested driver-toggle guard, and one bounded remove-side handoff, but the broader lifecycle and transport-facing parts of `virtio.c` remain intentionally out of scope.

## Roadmap Boundary

- `PHASE10_CORE_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/kernel/,zigux/helpers/`
- `PHASE10_CORE_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport`
- `PHASE10_CORE_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes`
- `PHASE10_CORE_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no`
- `PHASE10_CORE_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle`

The Phase 10 roadmap keeps this core lane inside `drivers/virtio/*.zig`, with justified bridge helpers allowed in `zigux/kernel/` or `zigux/helpers/` where needed, while the wider transport-facing posture stays intentionally blocked. This survey therefore records the same bounded roadmap reading that the adjacent input, ring, and MMIO survey packets already publish instead of leaving the core packet's destination policy implicit.

That same boundary means this note is still not using the landed driver-ID, remove-side bookkeeping, config-generation, config-delivery, or config-driver-toggle helpers as a pretext for transport-backed reset, queue setup, MMIO, DMA, or lifecycle parity claims. Those broader steps remain outside this lane until a later Phase 10 packet can justify them with explicit risky-transport evidence.

## Non-goals

This survey slice does not yet claim:

- probe, full remove, or transport-backed reset lifecycle parity
- real virtqueue wrappers from `virtio_ring.c`
- real MMIO register-window or interrupt behavior from `virtio_mmio.c`
- broader transport-backed driver registration or teardown work

## Gates

1. run the core-local and closure-backed packet guards
- `python3 scripts/zigux/check-phase10-core-packet.py`
- `python3 scripts/zigux/check-phase10-closure-inventory.py`
- `python3 scripts/zigux/validate-phase10-closure.py`

2. run the adjacent shared validator-first path
- `python3 scripts/zigux/validate-phase10.py`
- `make -C zigux phase10-validate`

The standalone shared validator still directly guards the adjacent ring-plus-input-plus-MMIO packet, while the dedicated core checker, closure inventory, closure validator, and all-up build keep the core slice inside the same bounded evidence bundle.

3. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig --summary all`

4. run the Linux-style Phase 10 test entrypoint
- `make -C zigux phase10-test`

This keeps the core survey note aligned with the shared closure packet's exact check list instead of implying the direct build replay alone is the only test surface that matters here.

5. run the convenience target
- `make -C zigux phase10`

## Latest verification snapshot

- verified the original survey packet against `master` head `d30cbe483a2f019ae797b309a29556bd58fe00d0`
- later focused verification in the parked `P10-L03` core packet reconstructed the then-current `drivers/virtio/virtio.zig` and `zigux/tests/phase10_virtio_core.zig` pair on a newer `master` head, then passed attached-Zig `zig fmt --check` plus `zig build test --build-file build.zig --summary all` with `3/3` build steps and `25/25` tests
- observed results:
  - the original survey-lane helper replay covered `virtio_id_match()` and first-match `virtio_dev_match()` behavior for exact, wildcard, unmatched, and missing-identity cases plus the documented non-nestable `virtio_config_driver_disable()` and `virtio_config_driver_enable()` rule
  - the later focused core replay confirmed that the earlier memory-only compile warning is stale for the current bounded core packet rather than a live same-lane defect
  - broader Phase 10 closure and all-up build replay were still not reopened in that later parked verification step because no ring, MMIO, input, or transport-facing behavior changed

## Next bounded step

Leave the original Phase 10 virtio-core survey packet parked unless fresh repo inspection finds a directly coupled drift inside the manifest-backed core survey note, survey gate, or the already-landed core-local evidence. The next honest same-family follow-up is another bounded note or ownership refresh if the parked core packet moves again; any new wrapper work should still stay in adjacent ring or MMIO lanes instead of widening core lifecycle claims.
