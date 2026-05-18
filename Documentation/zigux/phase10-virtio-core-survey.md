# Phase 10 Virtio Core Survey

This document tracks the bounded Phase 10 governance lane around `drivers/virtio/virtio.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-core-survey`
- lane: `P10-L01`
- surveyed inspected `master` head: `7a4454d0474106972cad7e164b79293bd54a40c6`
- scope: compare the already-landed core survey packet against the remaining roadmap lab-driver gap, keep the slice note and shared build wiring aligned with that packet, and stay out of ring, MMIO, input, or transport-facing lifecycle work
- product boundary:
  - `zigux/tests/phase10_virtio_core_manifest.json`
  - `zigux/tests/phase10_virtio_core_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-core-survey.md`
  - `Documentation/zigux/phase10-virtio-core-slice.md`
  - `scripts/zigux/check-phase10-core-packet.py`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio.c` as the first virtio-core anchor, and the live repo already ships a bounded `drivers/virtio/virtio.zig` helper plus dedicated implementation tests.

Current `master` had drifted back to a slice-note-only review posture for the core lane even though the build and nearby Phase 10 packets still expect a dedicated core checker path. This survey restores the small manifest-backed governance packet so the core lane is machine-checkable again without widening into new helper behavior.

This same packet is now the roadmap-facing `lab-only driver validation` evidence for `drivers/virtio/virtio.c`: the dedicated checker, the dedicated survey gate, the direct `phase10_virtio_core.zig` attribute-summary replay, the direct `phase10_virtio_core_interrupt_compound_ack.zig` replay, the direct `drivers/virtio/virtio_verify.zig` replay, the shared Phase 10 build replay, and the shared `make -C zigux phase10-test` plus `make -C zigux phase10` routes keep the bounded starter reviewable without widening into transport-backed lifecycle claims.

That same bounded packet is also the roadmap-facing helper parity evidence that Zigux can honestly claim today: `zigux/tests/phase10_virtio_core.zig` keeps the core helper's bounded `status_show` and `features_show`-style review surface explicit, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig` keeps combined queue-used plus config-change acknowledgements reviewable, `zigux/tests/phase10_virtio_core_reset_queue.zig` keeps reset-required queue teardown bookkeeping visible, `drivers/virtio/virtio_verify.zig` keeps wrapper-facing lifecycle guard checkpoints, narrowed-feature summaries, failed-status teardown, and reset replay visible, and `zigux/tests/phase10_virtio_driver_id.zig` keeps exact, wildcard, and unmatched driver-ID outcomes reviewable without widening into probe or remove lifecycle claims.

## Survey findings

- `drivers/virtio/virtio.c` is still the Phase 10 core anchor, and the live repo already ships `drivers/virtio/virtio.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `drivers/virtio/virtio_driver_id.zig`, and `zigux/tests/phase10_virtio_driver_id.zig`
- the landed core helper already covers bounded status sequencing, feature negotiation, driver-validation narrowing, queue callback bookkeeping, queue descriptor-shape metadata, config-generation bookkeeping, interrupt-ack bookkeeping, lifecycle guards, and reset replay in memory only
- the landed driver-id helper already keeps bounded `register_virtio_device()`, `virtio_uevent()`, `virtio_id_match()`, and `virtio_dev_match()` reviewable through exact, wildcard, and unmatched paths without claiming bus registration
- the current packet also keeps wrapper-facing verify and compound interrupt-ack evidence explicit through `drivers/virtio/virtio_verify.zig` and `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, so queue-used plus config-change acknowledgement and failed-status teardown stay reviewable without widening into transport-backed IRQ or probe behavior
- the roadmap-facing parity evidence for this bounded packet now explicitly spans the Phase 10 destination `drivers/virtio/*.zig` plus the justified bridging-helper boundary in `zigux/kernel/` and `zigux/helpers/`
- the current helper parity evidence is no longer just implied by surrounding packet prose: `zigux/tests/phase10_virtio_core.zig` proves the bounded `status_show` and `features_show`-style summaries, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig` proves combined queue-used plus config-change acknowledgement, `zigux/tests/phase10_virtio_core_reset_queue.zig` proves the reset-required queue and teardown bookkeeping, `drivers/virtio/virtio_verify.zig` proves wrapper-facing lifecycle guard and failed-status teardown checkpoints, and `zigux/tests/phase10_virtio_driver_id.zig` proves the exact, wildcard, and unmatched identity-table outcomes that still stay below transport-backed probe or remove behavior
- the honest roadmap gap here is no longer missing lab-driver or helper-parity evidence: the manifest-backed survey note, survey gate, dedicated packet checker, direct replays, shared build replay, and shared Linux-style Phase 10 routes already keep the bounded starter reviewable as `lab-only driver validation`
- the remaining bridge to a true lab driver is still blocked outside this lane: dual implementations for transport-facing paths, plus probe, full remove, reset, and transport-backed lifecycle state, remain too risky to claim from the core helper alone

## Recorded gaps

The restored survey manifest records:

- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-core-lab-gate`
- the landed `phase10-virtio-core-reset-queue-gate`
- the landed `phase10-virtio-core-slice-note`
- the landed `phase10-virtio-core-survey-gate`
- the landed `phase10-virtio-core-survey-note`
- the landed `phase10-virtio-core-verify-replay`
- the landed `phase10-driver-id-helper`
- the landed `phase10-driver-id-coverage-disposition-helper`
- the landed `phase10-driver-id-gate`
- the landed `phase10-queue-shape-bookkeeping-helper`
- the landed `phase10-config-generation-bookkeeping-helper`
- the landed `phase10-interrupt-ack-bookkeeping-helper`
- the landed `phase10-lifecycle-guard-bookkeeping-helper`
- the landed `phase10-driver-validation-narrowing-helper`
- the landed `phase10-core-attribute-summary-helper`
- the landed `phase10-reset-replay-bookkeeping-helper`
- the landed `phase10-core-lab-validation-evidence`
- the landed `phase10-interrupt-compound-ack-gate`
- the still-blocked `phase10-core-dual-implementation-bridge`
- the still-blocked `phase10-core-probe-remove-lifecycle`

This keeps the lane concrete and reviewable without overstating progress: the current core packet already owns the roadmap-facing `lab-only driver validation` evidence, the direct `phase10_virtio_core.zig`, `phase10_virtio_core_interrupt_compound_ack.zig`, `phase10_virtio_core_reset_queue.zig`, `phase10_virtio_driver_id.zig`, and `drivers/virtio/virtio_verify.zig` replays now state the current helper parity and wrapper-facing proof plainly in the survey itself, and the remaining gap is still the transport-backed dual-implementation or probe/remove bridge to a true lab driver rather than a missing starter helper.

## Non-goals

This survey slice does not claim:

- probe, full remove, or transport-backed reset lifecycle parity
- real virtqueue wrappers from `virtio_ring.c`
- real MMIO register-window or IRQ behavior from `virtio_mmio.c`
- broader transport-backed registration or teardown work

## Gates

1. run the dedicated core governance checker
- `python3 scripts/zigux/check-phase10-core-packet.py --self-test`
- `python3 scripts/zigux/check-phase10-core-packet.py`

2. run the restored core survey gate
- `zig test zigux/tests/phase10_virtio_core_survey.zig`

3. run the shared Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

4. run the Linux-style Phase 10 entrypoints when the wider packet is available
- `make -C zigux phase10-test`
- `make -C zigux phase10`

## Next bounded step

Leave the Phase 10 virtio-core governance lane parked again unless fresh repo inspection finds another directly coupled drift across this lab-validation evidence, the blocked bridge wording, the core slice note, the restored survey packet, or the shared build wiring. Any new helper work should stay in adjacent ring or MMIO lanes instead of widening core lifecycle claims.
