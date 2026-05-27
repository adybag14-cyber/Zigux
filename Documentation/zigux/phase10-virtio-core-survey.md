# Phase 10 Virtio Core Survey

This document tracks the bounded Phase 10 governance lane around `drivers/virtio/virtio.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-core-survey`
- lane: `P10-L01`
- surveyed packet commit recorded by the live core manifest: `c11221dc7a68d7511ae1c69d64b3f08528287ed8`
- surveyed inspected `master` head: direct connector readback on `2026-05-26` for this note, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `scripts/zigux/check-phase10-core-packet.py`, `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `zigux/tests/build.zig`, `zigux/tests/phase10_build.zig`, and `zigux/tests/phase10_closure_manifest.json`
- scope: compare the Phase 10 core lane's current repo-visible evidence against the roadmap's lab-driver target and the bootstrap ledger's tranche discipline, then keep this survey aligned with the current core packet without widening into ring, MMIO, input, or transport-facing lifecycle work
- product boundary:
  - `drivers/virtio/virtio.zig`
  - `Documentation/zigux/phase10-virtio-core-survey.md`
  - `Documentation/zigux/phase10-virtio-core-slice.md`
  - `zigux/tests/phase10_virtio_core_manifest.json`
  - `zigux/tests/phase10_virtio_core_survey.zig`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio.c` as the first virtio-core anchor and keeps the phase focused on VM-friendly lab-driver proof before riskier transport work.

Current `master` does ship a bounded core packet under the recommended `drivers/virtio/*.zig` destination, and the live core manifest still records the full roadmap destination envelope of `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/` so the packet keeps the helper-bridge spill points explicit without pretending they are already widened into active shared-helper work.

The bootstrap ledger still stops earlier in the commit train and does not yet record a dedicated Phase 10 core tranche, so this survey remains the truthfulness surface that ties the live packet back to the roadmap's tranche discipline.

## Survey findings

- `drivers/virtio/virtio.c` remains the roadmap's Phase 10 core anchor, and current `master` directly materializes `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `scripts/zigux/check-phase10-core-packet.py`, and `scripts/zigux/validate-phase10.py`
- the live manifest still records lane `P10-L01`, surveyed commit `c11221dc7a68d7511ae1c69d64b3f08528287ed8`, roadmap destinations `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`, `preexisting_phase10_test_files: 11`, the returned `preexisting_virtio_driver_id_zig_present: true` and `preexisting_virtio_driver_id_test_present: true` flags, and a mostly landed starter packet
- the direct `phase10_virtio_core` attribute-summary replay keeps the core `status_show` review surface visible from `0x00000000\n` through `0x0000000f\n`, while the direct `phase10_virtio_core`, `drivers/virtio/virtio_verify.zig`, and `phase10_virtio_core_interrupt_compound_ack` replays keep `features_show`-style device, driver, and negotiated bitstrings plus the combined queue-used plus config-change acknowledgement path reviewable as lab-only driver validation evidence
- the same direct core packet now also keeps the wrapper-facing `driverModelSummary()` and `DriverModelStage` progression explicit from `unattached` through `queue_registration_ready`, `driver_ready`, `device_needs_reset`, and `device_failed`, so staged readiness remains reviewable without claiming transport-backed probe or remove parity
- that same core packet now also keeps `probeRemoveDispositionSummary()` explicit as a preflight-only helper boundary: the direct `phase10_virtio_core` replay exercises unattached, tracked-driver-state, pending-interrupt, and reset-cleanup-required branches so probe and remove disposition evidence stays reviewable without crossing into transport-backed probe, full remove, or reset lifecycle parity
- the returned `drivers/virtio/virtio_driver_id.zig` helper plus `zigux/tests/phase10_virtio_driver_id.zig` replay keep the narrower `phase10-driver-id-helper` and `phase10-driver-id-coverage-disposition-helper` packet reviewable beside the core helper, verify, and survey packet rather than leaving driver-id reviewability implied
- direct readback of `zigux/tests/phase10_build.zig` exposes `phase10-virtio-core-tests`, `phase10-virtio-core-interrupt-compound-ack-tests`, `phase10-virtio-core-reset-queue-tests`, `phase10-virtio-core-verify-tests`, `phase10-virtio-core-survey-tests`, and `phase10-virtio-driver-id-tests`, so the core packet's direct lab-validation, narrower driver-id replay, and survey gates are all wired into the live Phase 10 build surface
- direct readback of `zigux/tests/build.zig` now exposes `phase10-virtio-core-survey`, so the bounded core survey anchor is visible in the shared tests-root smoke beside the later phase survey anchors instead of living only under the dedicated Phase 10 build file
- direct readback of `scripts/zigux/check-phase10-core-packet.py` now materializes the dedicated core-packet checker on `master`, so the live guardrail stack is the manifest, survey gate, dedicated checker, shared validator, shared build route, and the closure manifest rather than a mixed-read fallback story
- that same manifest keeps the risky transport boundary explicit through `phase10-core-dual-implementation-bridge` and `phase10-core-probe-remove-lifecycle`, so this is still lab-only driver validation evidence rather than a true lab driver for probe, full remove, and reset parity

## Roadmap helper parity scoreboard

Fresh repo inspection keeps the roadmap-facing core packet concrete through these narrower same-lane results:

- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-core-lab-gate`
- the landed `phase10-virtio-core-reset-queue-gate`
- the landed `phase10-virtio-core-slice-note`
- the landed `phase10-virtio-core-survey-gate`
- the landed `phase10-virtio-core-survey-note`
- the landed `phase10-virtio-core-verify-replay`
- the landed `phase10-queue-shape-bookkeeping-helper`
- the landed `phase10-config-generation-bookkeeping-helper`
- the landed `phase10-interrupt-ack-bookkeeping-helper`
- the landed `phase10-lifecycle-guard-bookkeeping-helper`
- the landed `phase10-driver-validation-narrowing-helper`
- the landed `phase10-core-attribute-summary-helper`
- the landed `phase10-reset-replay-bookkeeping-helper`
- the landed `phase10-core-lab-validation-evidence`
- the landed `phase10-driver-id-helper`
- the landed `phase10-driver-id-coverage-disposition-helper`
- the landed `phase10-driver-id-review-gate`
- the landed `phase10-interrupt-compound-ack-gate`
- the still-blocked `phase10-core-dual-implementation-bridge`
- the still-blocked `phase10-core-probe-remove-lifecycle`, now backed by direct preflight-only `probeRemoveDispositionSummary()` evidence in `drivers/virtio/virtio.zig` and the direct `phase10_virtio_core` replay so the roadmap gap stays reviewable without being overstated as landed lifecycle parity

That scoreboard now mirrors the live manifest IDs directly, keeping the helper, replay, checker, survey-gate, and shared-build evidence tied to the roadmap's Phase 10 lab-driver posture without overstating transport-backed lifecycle parity or pretending the bootstrap ledger already closes a dedicated Phase 10 core tranche.

## Recorded gaps

Current `master` keeps one same-lane roadmap gap explicit:

- still-blocked transport-facing bridge: `phase10-core-dual-implementation-bridge` and `phase10-core-probe-remove-lifecycle` remain outside the allowed Phase 10 core packet until a fresh Architecture Council reopen request attaches new evidence

Within this survey packet itself, the current `master` readback on `2026-05-26` is still aligned: `lifecycleGuardSummary()`, `driverModelSummary()`, `DriverModelStage`, and the preflight-only `probeRemoveDispositionSummary()` replay keep the wrapper-discipline evidence explicit beside the manifest-backed scoreboard above, the driver-id helper pair, the dedicated core survey gate, the dedicated core-packet checker, the shared validator, the shared tests-root build route, and the shared Phase 10 build route, while transport-backed probe, remove, and reset lifecycle work remains intentionally outside this lane.

## Non-goals

This survey slice does not claim:

- dual implementations for risky transport-facing paths
- probe, full remove, or transport-backed reset lifecycle parity
- real virtqueue wrappers from `virtio_ring.c`
- MMIO register-window or IRQ behavior from `virtio_mmio.c`
- input registration lifecycle behavior from `virtio_input.c`
- that the bootstrap ledger already closes a Phase 10 core tranche

## Gates

The honest current lane checks are direct repository readback plus the existing core packet guardrails:

1. confirm the roadmap anchor still names Phase 10 as virtio lab-driver work
- `agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md`

2. confirm the bootstrap ledger still stops short of a dedicated Phase 10 core tranche
- `agent_files/BOOTSTRAP_COMMIT_LEDGER.md`

3. confirm the current core packet still exposes the manifest-backed lab surfaces without overstating the missing transport bridge
- direct readback of `Documentation/zigux/phase10-virtio-core-survey.md`
- direct readback of `Documentation/zigux/phase10-virtio-core-slice.md`
- direct readback of `zigux/tests/phase10_virtio_core_manifest.json`
- direct readback of `zigux/tests/phase10_virtio_core_survey.zig`
- direct readback of `scripts/zigux/check-phase10-core-packet.py`
- direct readback of `drivers/virtio/virtio.zig`
- direct readback of `drivers/virtio/virtio_driver_id.zig`
- direct readback of `drivers/virtio/virtio_verify.zig`
- direct readback of `zigux/tests/phase10_virtio_core.zig`
- direct readback of `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`
- direct readback of `zigux/tests/phase10_virtio_core_reset_queue.zig`
- direct readback of `zigux/tests/phase10_virtio_driver_id.zig`
- direct readback of `zigux/tests/build.zig`
- direct readback of `zigux/tests/phase10_build.zig`
- direct readback of `zigux/tests/phase10_closure_manifest.json`

4. confirm the risky transport posture is still blocked and machine-readable
- `phase10-build-gate`
- `phase10-driver-id-helper`
- `phase10-driver-id-coverage-disposition-helper`
- `phase10-lifecycle-guard-bookkeeping-helper`
- `phase10-reset-replay-bookkeeping-helper`
- `phase10-virtio-core-slice-note`
- `phase10-virtio-core-survey-gate`
- `phase10-virtio-core-survey-note`
- `phase10-core-lab-validation-evidence`
- `phase10-driver-id-review-gate`
- `phase10-interrupt-compound-ack-gate`
- `phase10-core-dual-implementation-bridge`
- `phase10-core-probe-remove-lifecycle`
- `drivers/virtio/virtio.zig` via `probeRemoveDispositionSummary()`
- `zigux/tests/phase10_virtio_core.zig` via the direct probe/remove disposition replay
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/validate-phase10.py`
- `zigux/tests/phase10_virtio_core_manifest.json`
- `zigux/tests/phase10_virtio_core_survey.zig`

The narrowest honest same-lane replay here remains `zig test zigux/tests/phase10_virtio_core_survey.zig` once a scratch current-`master` core packet is rebuilt from live connector readback or a writable checkout is available. That replay keeps the dedicated survey gate aligned with the direct core file's `driverModelSummary()` and `DriverModelStage` surface, the direct preflight-only `probeRemoveDispositionSummary()` replay inside `zigux/tests/phase10_virtio_core.zig`, the dedicated driver-model replay inside `zigux/tests/phase10_virtio_core.zig`, the returned core verify replay, the focused reset-queue and interrupt-compound-ack replays, the closure-manifest evidence, and the compact-form manifest markers that still define the current packet. The remaining same-lane follow-through is still to keep those truthfulness surfaces aligned while the transport-facing bridge stays blocked.

## Next bounded step

Keep the follow-through inside the same core packet only:

- keep `Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core_survey.zig`, `drivers/virtio/virtio.zig`, and `zigux/tests/phase10_virtio_core.zig` aligned whenever the current core packet gains or drops directly re-readable driver-model, probe/remove-disposition, or wrapper-discipline guardrails
- keep broader core-packet truthfulness and any future manifest-or-slice follow-through under the live `P10-L01` core owner lane rather than widening into ring, MMIO, input, or transport-backed lifecycle work
- rerun `zig test zigux/tests/phase10_virtio_core_survey.zig` whenever the survey note, slice note, core manifest, closure manifest, core helper, focused core replay, or shared tests-root build route changes in a way that could hide roadmap-backed core evidence behind JSON formatting or stale note text
- if a writable full checkout becomes available, extend that replay to `zig build phase10-virtio-core-survey-tests --build-file zigux/tests/phase10_build.zig`, `zig build phase10-virtio-core-survey --build-file zigux/tests/build.zig`, and `zig build phase10-virtio-driver-id-tests --build-file zigux/tests/phase10_build.zig` before widening any further
