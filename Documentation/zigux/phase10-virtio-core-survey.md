# Phase 10 Virtio Core Survey

This document tracks the bounded Phase 10 governance lane around `drivers/virtio/virtio.c`.

## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-core-survey`
- lane: `P10-L01`
- surveyed inspected `master` head: `c11221dc7a68d7511ae1c69d64b3f08528287ed8`
- roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- scope: compare the already-landed core survey packet against the remaining roadmap lab-driver gap, keep the dedicated note, manifest, and shared build wiring aligned with that packet, and stay out of ring, MMIO, input, or transport-facing lifecycle work
- product boundary:
  - `zigux/tests/phase10_virtio_core_manifest.json`
  - `zigux/tests/phase10_virtio_core_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-core-survey.md`
  - `scripts/zigux/check-phase10-core-packet.py`
  - `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio.c` as the first virtio-core anchor, and the live repo already ships a bounded `drivers/virtio/virtio.zig` helper plus dedicated implementation tests.

Current `master` still keeps the bounded core packet reviewable through the manifest-backed survey note, the dedicated core checker, the dedicated tests-root core-surfaces checker, the dedicated survey gate, the direct `drivers/virtio/virtio_verify.zig` replay, the shared Phase 10 build replay, and the shared `make -C zigux phase10-test` plus `make -C zigux phase10` routes. That packet keeps the core lane reviewable without widening into transport-backed lifecycle claims.

## Survey findings
- `drivers/virtio/virtio.c` is still the Phase 10 core anchor, and the live repo already ships `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `drivers/virtio/virtio_driver_id.zig`, and `zigux/tests/phase10_virtio_driver_id.zig`.
- the landed core helper already covers bounded status sequencing, feature negotiation, driver-validation narrowing, status_show and features_show-style attribute summaries, queue callback bookkeeping, queue descriptor-shape metadata, config-generation bookkeeping, interrupt-ack bookkeeping, lifecycle guards, and reset replay in memory only.
- the direct `drivers/virtio/virtio_verify.zig` replay already keeps the wrapper-facing lifecycle guard checkpoints, narrowed-feature summaries, failed-status teardown, and reset replay reviewable beside the helper-local packet and the shared Phase 10 build route.
- the landed driver-id helper already keeps bounded `register_virtio_device()`, `virtio_uevent()`, `virtio_id_match()`, and `virtio_dev_match()` reviewable through exact, wildcard, and unmatched paths without claiming bus registration, and its coverage-disposition helper keeps exact coverage, wildcard coverage, wildcard shadowing, and unmatched table outcomes explicit.
- the roadmap-facing parity evidence for this bounded packet now explicitly spans the Phase 10 destination family `drivers/virtio/*.zig` plus the justified bridging-helper boundary in `zigux/kernel/` and `zigux/helpers/`.
- shared Phase 10 reminder surfaces and the live docs tree still frame `Documentation/zigux/phase10-virtio-core-slice.md` as an absent packet-local companion on current `master`, so the core manifest, survey gate, and dedicated checker must keep that path explicit as a repo-reality gap rather than treating it as shipped validation evidence.
- the remaining roadmap bridges to a true lab driver are still blocked outside this lane: dual implementations for risky transport-facing paths plus probe, full remove, and reset lifecycle state remain too risky to claim from the core helper alone.

## Recorded gaps
- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-core-lab-gate`
- the landed `phase10-virtio-core-reset-queue-gate`
- the repo-reality gap `phase10-core-slice-note` for `Documentation/zigux/phase10-virtio-core-slice.md`
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
- the still-blocked `phase10-core-dual-implementation-bridge`
- the still-blocked `phase10-core-probe-remove-lifecycle`

That keeps the lane concrete and reviewable without overstating progress: the current core packet already owns the roadmap-facing `lab-only driver validation` evidence on the survey note, manifest, dedicated checker, direct verify replay, tests-root companion, and shared build surfaces; the packet-local slice-note companion remains a repo-reality gap; and the still-missing dual-implementation boundary plus the transport-backed probe or remove bridge remain explicitly blocked instead of implied.

## Freeze Boundary
The current core packet stays aligned with `Documentation/zigux/freeze-map.md` by keeping the risky transport posture explicit.

Allowed evidence for this lane remains limited to driver-local lab slices, survey manifests, and shared validation gates. Allowed roadmap destinations for bounded follow-on work in this blocked packet remain `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` support surfaces; this survey does not claim a wider transport-facing home.

Forbidden transport claims remain queue setup or reset paths, IRQ parity, DMA paths, input registration lifecycle, and probe or remove lifecycle behavior. Any status review beyond this blocked-on-risky-transport packet still needs an Architecture Council reopen request with fresh linked evidence attached; this survey does not attach one.

## Non-goals
This survey slice does not claim:
- probe, full remove, or transport-backed reset lifecycle parity
- real virtqueue wrappers from `virtio_ring.c`
- real MMIO register-window or IRQ behavior from `virtio_mmio.c`
- broader transport-backed registration or teardown work

## Gates
1. rerun the dedicated core governance checker
- `python3 scripts/zigux/check-phase10-core-packet.py --self-test`
- `python3 scripts/zigux/check-phase10-core-packet.py`
2. rerun the dedicated core survey gate
- `zig test zigux/tests/phase10_virtio_core_survey.zig`
3. rerun the shared Phase 10 build once the packet-local enforcement is aligned
- `zig build test --build-file zigux/tests/phase10_build.zig`
4. rerun the Linux-style Phase 10 entrypoints when the wider packet is available
- `make -C zigux phase10-test`
- `make -C zigux phase10`

## Next bounded step
Leave the broader Phase 10 virtio lane parked unless a fresh repo reread finds one more directly coupled same-lane drift. Inside this core packet, the next honest bounded step is to keep `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `scripts/zigux/check-phase10-core-packet.py`, and this survey note aligned around the repo-reality gap for `Documentation/zigux/phase10-virtio-core-slice.md` while preserving the blocked dual-implementation and probe/remove bridges.
