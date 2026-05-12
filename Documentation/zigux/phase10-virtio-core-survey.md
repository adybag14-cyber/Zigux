# Phase 10 Virtio Core Survey

This document tracks the bounded Phase 10 governance lane around `drivers/virtio/virtio.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-core-survey`
- lane: `P10-L01`
- surveyed inspected `master` head: `c11221dc7a68d7511ae1c69d64b3f08528287ed8`
- scope: compare the already-landed core survey packet against the remaining roadmap lab-driver gap, keep the slice note and shared build wiring aligned with that packet, and stay out of ring, MMIO, input, or transport-facing lifecycle work
- product boundary:
  - `zigux/tests/phase10_virtio_core_manifest.json`
  - `zigux/tests/phase10_virtio_core_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-core-survey.md`
  - `Documentation/zigux/phase10-virtio-core-slice.md`
  - `scripts/zigux/check-phase10-core-packet.py`
  - `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio.c` as the first virtio-core anchor, and the live repo already ships a bounded `drivers/virtio/virtio.zig` helper plus dedicated implementation tests.

Current `master` had drifted back to a slice-note-only review posture for the core lane even though the build and nearby Phase 10 packets still expect a dedicated core checker path, and the shipped bounded status_show and features_show-style summaries were only implicit in the helper and tests. This survey restores the small manifest-backed governance packet so the core lane is reviewable again without widening into new helper behavior, but the packet is not yet fully machine-checkable because the dedicated checker and survey gate still lag the refreshed note and manifest state.

This same packet is still the roadmap-facing `lab-only driver validation` evidence for `drivers/virtio/virtio.c`: the dedicated checker, the dedicated tests-root core-surfaces checker, the dedicated survey gate, the direct `drivers/virtio/virtio_verify.zig` replay, the shared Phase 10 build replay, and the shared `make -C zigux phase10-test` plus `make -C zigux phase10` routes keep the bounded starter reviewable without widening into transport-backed lifecycle claims. The slice note already keeps the roadmap's dual-implementation boundary explicit too, so this survey packet must carry that same blocked bridge instead of naming only the later probe or remove step, and the packet-local enforcement now needs to catch up to that two-blocker posture.

## Survey findings

- `drivers/virtio/virtio.c` is still the Phase 10 core anchor, and the live repo already ships `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `drivers/virtio/virtio_driver_id.zig`, and `zigux/tests/phase10_virtio_driver_id.zig`
- the landed core helper already covers bounded status sequencing, feature negotiation, driver-validation narrowing, status_show and features_show-style attribute summaries, queue callback bookkeeping, queue descriptor-shape metadata, config-generation bookkeeping, interrupt-ack bookkeeping, lifecycle guards, and reset replay in memory only
- the direct `drivers/virtio/virtio_verify.zig` replay already keeps the wrapper-facing lifecycle guard checkpoints, narrowed-feature summaries, failed-status teardown, and reset replay reviewable beside the helper-local packet and the shared Phase 10 build route
- the landed driver-id helper already keeps bounded `register_virtio_device()`, `virtio_uevent()`, `virtio_id_match()`, and `virtio_dev_match()` reviewable through exact, wildcard, and unmatched paths without claiming bus registration
- the landed driver-id coverage helper now makes exact coverage, wildcard coverage, wildcard shadowing, and unmatched table outcomes explicit without widening into probe or bus registration
- the roadmap-facing parity evidence for this bounded packet now explicitly spans the Phase 10 destination `drivers/virtio/*.zig` plus the justified bridging-helper boundary in `zigux/kernel/` and `zigux/helpers/`
- the honest roadmap gap here is no longer missing lab-driver evidence on the note, manifest, direct verify replay, tests-root companion, or shared build surfaces: those packet pieces already keep the bounded starter reviewable as `lab-only driver validation`
- the remaining packet-local drift is validation enforcement: `scripts/zigux/check-phase10-core-packet.py` still expects the older surveyed commit `7a4454d0474106972cad7e164b79293bd54a40c6`, only nine preexisting Phase 10 test files, and only the later probe/remove blocker, while `zigux/tests/phase10_virtio_core_manifest.json` now records surveyed commit `c11221dc7a68d7511ae1c69d64b3f08528287ed8`, eleven preexisting Phase 10 test files, and both the dual-implementation bridge plus the probe/remove lifecycle bridge as blocked transport-facing work
- the remaining roadmap bridges to a true lab driver are still blocked outside this lane: dual implementations for risky transport-facing paths plus probe, full remove, and reset lifecycle state remain too risky to claim from the core helper alone

## Freeze Boundary

The current core packet stays aligned with `Documentation/zigux/freeze-map.md` by keeping the risky transport posture explicit.

Allowed evidence for this lane remains limited to driver-local lab slices, survey manifests, and shared validation gates.

Allowed roadmap destinations for bounded follow-on work in this blocked packet remain `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` support surfaces; this survey does not claim a wider transport-facing home.

Forbidden transport claims remain queue setup or reset paths, IRQ parity, DMA paths, input registration lifecycle, and probe or remove lifecycle behavior.

Any status review beyond this blocked-on-risky-transport packet still needs an Architecture Council reopen request with fresh linked evidence attached; this survey does not attach one.

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
- the still-blocked `phase10-core-dual-implementation-bridge`
- the still-blocked `phase10-core-probe-remove-lifecycle`

This keeps the lane concrete and reviewable without overstating progress: the current core packet already owns the roadmap-facing `lab-only driver validation` evidence on the survey note, manifest, direct verify replay, tests-root companion, and shared build surfaces; the still-missing dual-implementation boundary for risky transport-facing paths remains explicit; the remaining transport-backed probe or remove bridge to a true lab driver is still blocked rather than implied; and the next lane-local repair is to refresh the dedicated checker and the survey gate so they enforce this same two-blocker packet instead of the older single-blocker snapshot.

## Non-goals

This survey slice does not claim:

- probe, full remove, or transport-backed reset lifecycle parity
- real virtqueue wrappers from `virtio_ring.c`
- real MMIO register-window or IRQ behavior from `virtio_mmio.c`
- broader transport-backed registration or teardown work

## Gates

1. refresh the dedicated core governance checker to the current packet state
- `python3 scripts/zigux/check-phase10-core-packet.py --self-test`
- `python3 scripts/zigux/check-phase10-core-packet.py`

2. refresh the dedicated core survey gate to the same packet state
- `zig test zigux/tests/phase10_virtio_core_survey.zig`

3. rerun the shared Phase 10 build once the packet-local enforcement is aligned
- `zig build test --build-file zigux/tests/phase10_build.zig`

4. rerun the Linux-style Phase 10 entrypoints when the wider packet is available
- `make -C zigux phase10-test`
- `make -C zigux phase10`

## Next bounded step

Refresh `scripts/zigux/check-phase10-core-packet.py` and `zigux/tests/phase10_virtio_core_survey.zig` so both surfaces accept the refreshed `c11221dc7a68d7511ae1c69d64b3f08528287ed8` survey snapshot, eleven preexisting Phase 10 test files, and the two blocked transport-facing bridges recorded in `zigux/tests/phase10_virtio_core_manifest.json`, then rerun the dedicated checker, survey gate, and shared Phase 10 build without widening into ring, MMIO, input, or transport-backed lifecycle work.
