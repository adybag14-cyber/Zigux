# Phase 10 Virtio MMIO Survey

This document tracks the bounded Phase 10 MMIO lane around `drivers/virtio/virtio_mmio.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-mmio-survey`
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

Current `master` still keeps the shared Phase 10 closure packet, this MMIO survey note, and the broader freeze-map reminder surfaces explicit. Fresh authenticated contents reads for `scripts/zigux/check-phase10-mmio-freeze-boundary.py` and `zigux/tests/phase10_virtio_mmio_manifest.json` now return 404 on current `master`, so this note must treat those two paths as packet references or repo-reality gaps rather than directly materialized shipped evidence. Tightening that wording keeps the MMIO lane reviewable again without claiming new helper behavior.

## Survey findings

- `drivers/virtio/virtio_mmio.c` remains the Phase 10 MMIO anchor from the roadmap.
- the live shared Phase 10 closure packet still records MMIO wrappers as `starter_landed` through `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, and this survey note, while the packet-local `zigux/tests/phase10_virtio_mmio_manifest.json` reference could not be materialized through the authenticated contents bridge on current `master`
- the shared closure manifest still keeps the landed MMIO helper ladder explicit through `phase10-mmio-register-window-helper`, `phase10-mmio-queue-size-helper`, `phase10-mmio-feature-word-selector-helper`, `phase10-mmio-feature-negotiation-summary-helper`, `phase10-mmio-config-window-helper`, `phase10-mmio-config-write-plan-helper`, `phase10-mmio-transport-identity-helper`, `phase10-mmio-probe-preflight-helper`, `phase10-mmio-config-write-disposition-helper`, and `phase10-mmio-selected-queue-readiness-helper`
- the same closure packet keeps the honest blocked transport-facing follow-through explicit through `phase10-mmio-lifecycle-and-irq-paths`, so the current MMIO lane is a bounded wrapper and lab-validation packet rather than a claim of queue reset execution, IRQ parity, or full probe/remove lifecycle closure
- the directly shipped shared reminder surfaces still keep `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` explicit beside the dedicated MMIO packet wording and the focused MMIO replay pair
- the dedicated freeze-boundary checker path `scripts/zigux/check-phase10-mmio-freeze-boundary.py` is still named by the shared reminder packet, but it is not currently materialized through authenticated contents reads on current `master` and should be treated as a repo-reality gap until a future same-lane step restores it or confirms a new authoritative path

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
- the repo-reality gap at `zigux/tests/phase10_virtio_mmio_manifest.json`
- the repo-reality gap at `scripts/zigux/check-phase10-mmio-freeze-boundary.py`
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`

That keeps the MMIO lane aligned with the current closure packet: the wrapper ladder and lab-validation evidence are real, the packet-local manifest and dedicated freeze-boundary checker need a later same-lane restore or readback step, and IRQ plus lifecycle claims remain explicitly blocked.

## Freeze Boundary

This survey stays aligned with `Documentation/zigux/freeze-map.md` and the shared Phase 10 closure packet.

Allowed evidence for this lane remains limited to driver-local lab slices, survey manifests, and shared validation gates.

Allowed roadmap destinations remain `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` support surfaces; this note does not widen the tranche into new transport homes.

Forbidden transport claims remain queue setup or reset paths, IRQ parity, DMA paths, input registration lifecycle, and probe/remove lifecycle behavior.

The Phase 14 study-only anchors `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain outside this lane, and this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.

## Non-Goals

This survey slice does not claim:

- transport-backed queue discovery or reset execution
- IRQ parity or DMA paths
- probe/remove lifecycle closure
- a reopened Architecture Council decision

## Gates

1. run the shared Phase 10 validator packet
- `python3 scripts/zigux/validate-phase10.py`
- `python3 scripts/zigux/validate-phase10-closure.py`
- `make -C zigux phase10-validate`

2. run the focused MMIO replay pair through the shared build packet
- `zig build test --build-file zigux/tests/phase10_build.zig`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

3. treat the dedicated MMIO packet and freeze-boundary checker paths as follow-through targets, not directly runnable shipped gates, until `scripts/zigux/check-phase10-mmio-packet.py`, `scripts/zigux/check-phase10-mmio-freeze-boundary.py`, and `zigux/tests/phase10_virtio_mmio_manifest.json` are restored or directly re-readable on current `master`

Taken together, these gates keep the bounded MMIO wrapper and VM-friendly validation packet reviewable without implying risky transport closure.

## Next bounded step

Leave the Phase 10 MMIO lane parked unless fresh repo inspection finds another directly coupled drift inside this reminder packet. If the lane reopens, prefer the next one-file restore, survey, manifest, checker, or shared-summary truthfulness repair that makes the dedicated MMIO packet directly re-readable again before widening transport behavior, IRQ claims, reset execution, or lifecycle scope.
