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

Current `master` still keeps the shared Phase 10 closure packet, this MMIO survey note, and the broader freeze-map reminder surfaces explicit. This run re-verified the MMIO lane only partway: the public GitHub tree still shows `drivers/virtio/virtio_mmio.zig` and `drivers/virtio/virtio_mmio_verify.zig` under `drivers/virtio/`, but the authenticated contents bridge returned 404 for the driver-local verifier, the packet-local manifest, the focused MMIO replay files, the shared `phase10_build.zig` gate, and both dedicated MMIO checker paths. Keeping that split explicit makes the MMIO lane truthful without claiming a focused compile or lab replay that this run could not directly re-read.

## Survey findings

- `drivers/virtio/virtio_mmio.c` remains the Phase 10 MMIO anchor from the roadmap.
- the shared Phase 10 closure packet still records MMIO wrappers and helper-ladder progress, but this run only re-verified wrapper-surface visibility through the public GitHub tree; the authenticated contents bridge returned 404 for `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `zigux/tests/phase10_virtio_mmio_manifest.json`, so the focused MMIO replay packet was not directly re-readable here
- the shared closure manifest still keeps the landed MMIO helper ladder explicit through `phase10-mmio-register-window-helper`, `phase10-mmio-queue-size-helper`, `phase10-mmio-feature-word-selector-helper`, `phase10-mmio-feature-negotiation-summary-helper`, `phase10-mmio-config-window-helper`, `phase10-mmio-config-write-plan-helper`, `phase10-mmio-transport-identity-helper`, `phase10-mmio-probe-preflight-helper`, `phase10-mmio-config-write-disposition-helper`, and `phase10-mmio-selected-queue-readiness-helper`
- the same closure packet keeps the honest blocked transport-facing follow-through explicit through `phase10-mmio-lifecycle-and-irq-paths`, so the current MMIO lane is still a bounded wrapper and lab-validation packet rather than a claim of queue reset execution, IRQ parity, or full probe-remove lifecycle closure
- the shared reminder surfaces still keep `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` explicit, but this run could not directly re-read `zigux/tests/phase10_build.zig`, so those routes remain broader closure evidence rather than a fresh MMIO-only compile replay
- this run also got 404s from the authenticated contents bridge for `scripts/zigux/check-phase10-mmio-packet.py` and `scripts/zigux/check-phase10-mmio-freeze-boundary.py`, so the dedicated checker pair should stay treated as previously recorded review surfaces until a fresh direct contents read or public blob fallback reconfirms them again

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
- the authenticated contents bridge returned 404 for `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `scripts/zigux/check-phase10-mmio-packet.py`, and `scripts/zigux/check-phase10-mmio-freeze-boundary.py` in this run, so direct compile and focused replay verification remain blocked by incomplete readback
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`

That keeps the MMIO lane aligned with current repo evidence: the helper ladder and blocked transport follow-through are still recorded in the shared closure packet, the public tree still shows the MMIO wrapper family under `drivers/virtio/`, and the focused compile or lab replay remains unverified until the missing direct reads become reproducible again.

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

2. run the focused MMIO replay pair through the shared build packet only after the packet-local files and `zigux/tests/phase10_build.zig` are directly readable again
- `zig build test --build-file zigux/tests/phase10_build.zig`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

3. keep the dedicated MMIO packet checker, dedicated freeze-boundary checker, and packet-local MMIO manifest aligned with the next successful direct-read or public-blob revalidation instead of treating this run's incomplete contents reads as proof that the focused MMIO packet was freshly replayed

Taken together, these gates keep the bounded MMIO wrapper packet reviewable without implying risky transport closure or a compile replay this run did not actually complete.

## Next bounded step

Leave the Phase 10 MMIO lane parked unless fresh repo inspection finds another directly coupled drift inside this reminder packet. If the lane reopens, start by re-running direct contents reads or a public blob fallback for `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `scripts/zigux/check-phase10-mmio-packet.py`, and `scripts/zigux/check-phase10-mmio-freeze-boundary.py`, then only refresh one same-lane note or replay surface after that readback becomes reproducible again.