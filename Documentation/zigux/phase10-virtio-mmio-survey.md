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

Current `master` still keeps the shared Phase 10 closure packet, this MMIO survey note, and the broader freeze-map reminder surfaces explicit. Fresh repo rereads for `zigux/tests/phase10_virtio_mmio_manifest.json`, `scripts/zigux/check-phase10-mmio-packet.py`, and `scripts/zigux/check-phase10-mmio-freeze-boundary.py` confirm that the packet-local manifest and both dedicated MMIO checker paths still materialize on current `master`; the manifest now reads back through public raw fallback, and the two checker paths remain visible through public GitHub blob fallback even when the authenticated contents bridge stays incomplete for them. Keeping that distinction explicit makes the MMIO lane truthful without claiming new helper behavior.

## Survey findings

- `drivers/virtio/virtio_mmio.c` remains the Phase 10 MMIO anchor from the roadmap.
- the live shared Phase 10 closure packet still records MMIO wrappers as `starter_landed` through `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, this survey note, and the directly re-readable packet-local manifest `zigux/tests/phase10_virtio_mmio_manifest.json`
- the shared closure manifest still keeps the landed MMIO helper ladder explicit through `phase10-mmio-register-window-helper`, `phase10-mmio-queue-size-helper`, `phase10-mmio-feature-word-selector-helper`, `phase10-mmio-feature-negotiation-summary-helper`, `phase10-mmio-config-window-helper`, `phase10-mmio-config-write-plan-helper`, `phase10-mmio-transport-identity-helper`, `phase10-mmio-probe-preflight-helper`, `phase10-mmio-config-write-disposition-helper`, and `phase10-mmio-selected-queue-readiness-helper`
- the same closure packet keeps the honest blocked transport-facing follow-through explicit through `phase10-mmio-lifecycle-and-irq-paths`, so the current MMIO lane is a bounded wrapper and lab-validation packet rather than a claim of queue reset execution, IRQ parity, or full probe/remove lifecycle closure
- the directly shipped shared reminder surfaces still keep `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` explicit beside the dedicated MMIO wording and the focused MMIO replay pair
- the dedicated MMIO packet checker path `scripts/zigux/check-phase10-mmio-packet.py` is still a live Phase 10 review surface on current `master`; this run re-read it through public GitHub blob fallback, so the shared reminder packet should keep treating it as current checker evidence rather than a repo-reality gap
- the dedicated freeze-boundary checker path `scripts/zigux/check-phase10-mmio-freeze-boundary.py` is still a live Phase 10 review surface on current `master`; this run re-read it through public GitHub blob fallback, so the shared reminder packet should keep treating it as current checker evidence rather than a repo-reality gap

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
- the live packet-local manifest `zigux/tests/phase10_virtio_mmio_manifest.json`
- the live dedicated MMIO packet checker `scripts/zigux/check-phase10-mmio-packet.py`
- the live dedicated MMIO freeze-boundary checker `scripts/zigux/check-phase10-mmio-freeze-boundary.py`
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`

That keeps the MMIO lane aligned with the current closure packet: the wrapper ladder, packet-local manifest, and dedicated MMIO checker pair are all present review surfaces on current `master`, while IRQ plus lifecycle claims remain explicitly blocked.

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

3. keep the dedicated MMIO packet checker, dedicated freeze-boundary checker, and packet-local MMIO manifest aligned as live Phase 10 review surfaces whenever shared reminder wording changes, instead of demoting them back into repo-reality gaps while the files are still present on current `master`

Taken together, these gates keep the bounded MMIO wrapper and VM-friendly validation packet reviewable without implying risky transport closure.

## Next bounded step

Leave the Phase 10 MMIO lane parked unless fresh repo inspection finds another directly coupled drift inside this reminder packet. If the lane reopens, prefer the next one-file shared-summary or checker truthfulness repair around the live packet-local manifest and dedicated MMIO checker pair before widening transport behavior, IRQ claims, reset execution, or lifecycle scope.
