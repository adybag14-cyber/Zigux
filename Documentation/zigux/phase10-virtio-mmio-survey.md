# Phase 10 Virtio MMIO Survey

This document tracks the bounded Phase 10 MMIO lane around `drivers/virtio/virtio_mmio.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-mmio-survey`
- `PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport`
- lane: `P10-L10`
- surveyed commit: `84f90e23ad1c28ae345905d5293a8c5395f37d43`
- roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- scope: keep the dedicated MMIO survey path visible beside the shared closure packet, the MMIO helper ladder recorded by the shared closure manifest, the dedicated freeze-boundary reminder, and the blocked transport-facing gap without widening into risky lifecycle claims
- product boundary:
  - `Documentation/zigux/phase10-virtio-mmio-survey.md`
  - `Documentation/zigux/phase10-virtio-mmio-slice.md`
  - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  - `Documentation/zigux/phase10-closure-evidence.md`
  - `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/freeze-map.md`
  - `scripts/zigux/README.md`
  - `scripts/zigux/check-phase10-mmio-packet.py`
  - `scripts/zigux/check-phase10-mmio-freeze-boundary.py`
  - `scripts/zigux/check-phase10-harness-coverage.py`
  - `scripts/zigux/validate-phase10.py`
  - `scripts/zigux/validate-phase10-closure.py`
  - `zigux/tests/phase10_closure_manifest.json`
  - `zigux/tests/phase10_virtio_mmio_manifest.json`
  - `zigux/tests/phase10_build.zig`
  - `zigux/tests/phase10_virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio_survey.zig`
  - `drivers/virtio/virtio_mmio.zig`
  - `drivers/virtio/virtio_mmio_verify.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_mmio.c` as a primary lab-driver anchor and requires MMIO wrappers plus VM-friendly validation before riskier transport work.

Current `master` still keeps the shared Phase 10 closure packet, this MMIO survey note, and the broader freeze-map reminder surfaces explicit. The live packet-local manifest `zigux/tests/phase10_virtio_mmio_manifest.json` still carries the parked MMIO helper ladder and blocked transport follow-through recorded by the shared closure packet, and current raw GitHub fallback now directly re-reads that manifest beside `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, and `zigux/tests/phase10_virtio_mmio_survey.zig`. The authenticated contents bridge still returned 404 for the driver-local verifier and also still missed those shared build and focused MMIO replay files, so this note keeps the narrower readback split explicit instead of repeating the older manifest-only fallback story.

The shipped packet checker now also treats the current MMIO reminder packet as larger than the older 404-only story: it expects the bounded MMIO packet to stay visible beside fifteen dedicated Phase 10 virtio test or survey files under `zigux/tests/`, the shared `drivers/virtio/virtio_ring_verify.zig` and `drivers/virtio/virtio_input_verify.zig` review surfaces, and the directly named input-side replay files `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig`.

## Survey findings

- `drivers/virtio/virtio_mmio.c` remains the Phase 10 MMIO anchor from the roadmap.
- the shared Phase 10 closure packet still records MMIO wrappers and helper-ladder progress, and this run re-verified the reminder packet through the public GitHub tree, the raw GitHub fallback for `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, and `zigux/tests/phase10_virtio_mmio_survey.zig`, and the directly readable dedicated MMIO packet checker; the authenticated contents bridge still returned 404 for `drivers/virtio/virtio_mmio_verify.zig`, and the same bridge still missed the build and focused MMIO replay files that raw fallback recovered, so direct verifier-backed compile or replay validation was still not fully re-readable here
- the live packet-local manifest `zigux/tests/phase10_virtio_mmio_manifest.json` still keeps the landed MMIO helper ladder explicit through `phase10-mmio-register-window-helper`, `phase10-mmio-queue-size-helper`, `phase10-mmio-feature-word-selector-helper`, `phase10-mmio-feature-negotiation-summary-helper`, `phase10-mmio-config-window-helper`, `phase10-mmio-config-write-plan-helper`, `phase10-mmio-transport-identity-helper`, `phase10-mmio-probe-preflight-helper`, `phase10-mmio-config-write-disposition-helper`, and `phase10-mmio-selected-queue-readiness-helper`
- the shipped MMIO review packet now expects the transport-identity summary to stay explicit, expects the bounded probe-preflight summary to say that it consumes that identity snapshot, and keeps the shared `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig` review markers visible beside the MMIO lane
- the same review packet now expects the selected-queue readiness summary, the configured-queue coverage summary, the generation-scoped config-review posture, the queue-ready-for-handoff posture, and the way the probe-preflight summary flips from ready to blocked when identity or readiness drifts to remain explicit in this survey note
- the same closure packet keeps the honest blocked transport-facing follow-through explicit through `phase10-mmio-lifecycle-and-irq-paths`, so the current MMIO lane is still a bounded wrapper and lab-validation packet rather than a claim of queue reset execution, IRQ parity, or full probe-remove lifecycle closure
- the shared reminder surfaces still keep `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, and the focused `zig test zigux/tests/phase10_virtio_mmio.zig` route explicit, but this run did not rerun those MMIO-only compile or replay paths

## Recorded gaps

This survey keeps the MMIO lane concrete without overstating progress:

- the landed `phase10-mmio-register-window-helper`
- the landed `phase10-mmio-queue-size-helper`
- the landed `phase10-mmio-feature-word-selector-helper`
- the landed `phase10-mmio-feature-negotiation-summary-helper`
- the landed `phase10-mmio-config-window-helper`
- the landed `phase10-mmio-config-write-plan-helper`
- the landed `phase10-mmio-transport-identity-helper`
- the landed `phase10-mmio-probe-preflight-helper`
- the landed `phase10-mmio-config-write-disposition-helper`
- the landed `phase10-mmio-selected-queue-readiness-helper`
- raw GitHub fallback now directly re-reads `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, and `zigux/tests/phase10_virtio_mmio_survey.zig`, but the authenticated contents bridge still returned 404 for `drivers/virtio/virtio_mmio_verify.zig` and still missed the build plus focused MMIO replay files in this run, so direct verifier-backed compile and focused replay validation remain unverified here
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`

That keeps the MMIO lane aligned with current repo evidence: the helper ladder and blocked transport follow-through are still recorded in the shared closure packet, the public tree still shows the MMIO wrapper family under `drivers/virtio/`, raw fallback now recovers the focused tests-root MMIO packet plus the shared build gate, and the dedicated driver-local verifier remains the unreadable boundary that still blocks a fresh verifier-backed compile or replay claim.

## Freeze Boundary

This survey stays aligned with `Documentation/zigux/freeze-map.md` and the shared Phase 10 closure packet.

Allowed evidence for this lane remains limited to driver-local lab slices, survey manifests, and shared validation gates.

Allowed roadmap destinations remain `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` support surfaces; this note does not widen the tranche into new transport homes.

Forbidden transport claims remain queue setup or reset paths, IRQ parity, DMA paths, input registration lifecycle, and probe-remove lifecycle behavior.

The Phase 14 study-only anchors `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain outside this lane, and this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.

## Non-Goals

This survey slice does not claim:

- transport-backed queue discovery or reset execution
- IRQ parity or DMA paths
- probe-remove lifecycle closure
- a reopened Architecture Council decision

## Gates

1. run the shared Phase 10 validator packet
- `python3 scripts/zigux/validate-phase10.py`
- `python3 scripts/zigux/validate-phase10-closure.py`
- `make -C zigux phase10-validate`

2. run the focused MMIO replay pair through the shared build packet only after the driver-local verifier is directly readable again; current raw GitHub fallback already re-reads `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, and `zigux/tests/phase10_virtio_mmio_survey.zig`, but `drivers/virtio/virtio_mmio_verify.zig` remained unreadable in this run
- `zig build test --build-file zigux/tests/phase10_build.zig`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

3. keep the dedicated MMIO packet checker and dedicated freeze-boundary checker aligned with the next successful direct-read or fallback revalidation of the driver-local MMIO verifier instead of treating the already-recovered tests-root files alone as proof that the focused MMIO packet was freshly replayed

Taken together, these gates keep the bounded MMIO wrapper packet reviewable without implying risky transport closure or a compile replay this run did not actually complete.

## Next bounded step

Leave the Phase 10 MMIO lane parked unless fresh repo inspection finds another directly coupled drift inside this reminder packet. If the lane reopens, start by re-running direct contents reads or a public raw fallback for `drivers/virtio/virtio_mmio_verify.zig`, then only refresh one same-lane note or replay surface after that verifier readback becomes reproducible again.
