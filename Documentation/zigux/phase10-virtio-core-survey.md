# Phase 10 Virtio Core Survey

This document tracks the bounded Phase 10 governance lane around `drivers/virtio/virtio.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-core-survey`
- lane: `P10-L01`
- surveyed packet commit recorded by the live core manifest: `c11221dc7a68d7511ae1c69d64b3f08528287ed8`
- surveyed inspected `master` head: mixed readback on `2026-05-21` using direct connector reads for this note plus `zigux/tests/phase10_virtio_core_manifest.json`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, and `zigux/tests/phase10_closure_manifest.json`, public current-`master` blob readback that reconfirmed `Documentation/zigux/phase10-virtio-core-slice.md` and the broader restored core packet surfaces, and connector-visible `404` failures on some exact-path contents reads that remain unreliable in this environment
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

- `drivers/virtio/virtio.c` remains the roadmap's Phase 10 core anchor, and current `master` publicly materializes `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_verify.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, and `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`
- the live manifest still records lane `P10-L01`, surveyed commit `c11221dc7a68d7511ae1c69d64b3f08528287ed8`, roadmap destinations `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`, `preexisting_phase10_test_files: 11`, and a mostly landed starter packet, while the shared closure packet and lane-sequencing note now also keep the directly re-readable core survey, core test, shared validator pair, and Makefile-backed build route explicit beside that manifest-backed packet; only the exact-path `drivers/virtio/virtio_driver_id.zig` plus `zigux/tests/phase10_virtio_driver_id.zig` pair still remains outside the directly returned set in this runtime
- that same manifest keeps the risky transport boundary explicit through `phase10-core-dual-implementation-bridge` and `phase10-core-probe-remove-lifecycle`, so this is still lab-only driver validation evidence rather than a true lab driver for probe, full remove, and reset parity
- the current packet's roadmap-destination evidence still points to `drivers/virtio/*.zig` as the landed lab-driver home while keeping `zigux/kernel/` and `zigux/helpers/` reserved as the only justified bridge-helper spill points if later bounded follow-through needs them
- the direct `phase10_virtio_core` attribute-summary replay keeps the core `status_show` review surface starts at `0x00000000\n`, reaches `0x0000000f\n`, while the direct `phase10_virtio_core` and `phase10_virtio_core_interrupt_compound_ack` replays keep `features_show`-style device, driver, and negotiated bitstrings plus the combined queue-used plus config-change acknowledgement path reviewable as lab-only driver validation evidence
- public current-`master` readback of `zigux/tests/phase10_build.zig` now exposes both `phase10-virtio-core-tests` and the dedicated `phase10_virtio_core_survey_module` / `phase10-virtio-core-survey-tests` / `run_phase10_virtio_core_survey_tests` shared-build route, so the core packet's direct lab-validation and survey gates are both wired into the live Phase 10 build surface
- exact-path contents reads remain partially flaky in this environment: direct connector readback now returns `zigux/tests/phase10_virtio_core_manifest.json`, but `zigux/tests/phase10_virtio_core_survey.zig` still returns `404` even while public blob readback materializes that survey gate, so lane truthfulness here must stay grounded in mixed evidence rather than treating one read mode as authoritative
- the narrower driver-id packet is the remaining same-lane visibility mismatch: direct connector reads and public raw current-`master` readback both still fail for `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`, so the current core survey can no longer treat that helper-and-replay pair as landed evidence on the live branch

## Recorded gaps

Current `master` keeps these same-lane gaps explicit:

- narrower mixed-read visibility drift: exact-path connector reads for the core survey gate still fail from this environment even though direct connector readback now returns the core manifest and public current-`master` blob readback materializes the survey gate, so future same-lane rereads should preserve that mixed-source verification path
- survey-local wording drift: the shared closure packet and lane-sequencing note now already treat the returned validator pair, closure manifest, Makefile-backed build gate, and directly re-readable core survey/test packet as live shared evidence, so this note should keep that broader returned-core context explicit while still leaving the exact-path `virtio_driver_id` pair in the narrower gap bucket
- stale guardrail reference drift: this survey previously named `scripts/zigux/check-phase10-core-packet.py` as a live core-packet surface even though current exact-path connector reads and repo search show that it still does not materialize on `master`, while `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, and `scripts/zigux/validate-phase10.py` do remain live guardrails for the packet
- still-blocked transport-facing bridge: `phase10-core-dual-implementation-bridge` and `phase10-core-probe-remove-lifecycle` remain outside the allowed Phase 10 core packet until a fresh Architecture Council reopen request attaches new evidence

This keeps the lane concrete without pretending the whole core packet is absent and without widening into ring, MMIO, input, or transport-facing implementation work owned by other lanes.

## Non-goals

This survey slice does not claim:

- dual implementations for risky transport-facing paths
- probe, full remove, or transport-backed reset lifecycle parity
- real virtqueue wrappers from `virtio_ring.c`
- MMIO register-window or IRQ behavior from `virtio_mmio.c`
- input registration lifecycle behavior from `virtio_input.c`
- that the bootstrap ledger already closes a Phase 10 core tranche

## Gates

The honest current lane checks are mixed repository-readback checks plus the existing core packet guardrails:

1. confirm the roadmap anchor still names Phase 10 as virtio lab-driver work
- `agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md`

2. confirm the bootstrap ledger still stops short of a dedicated Phase 10 core tranche
- `agent_files/BOOTSTRAP_COMMIT_LEDGER.md`

3. confirm the current core packet still exposes the manifest-backed lab surfaces without overstating the missing driver-id pair
- direct readback of `Documentation/zigux/phase10-virtio-core-survey.md`
- direct readback of `zigux/tests/phase10_virtio_core_manifest.json`
- public current-`master` blob readback of `Documentation/zigux/phase10-virtio-core-slice.md`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_build.zig`, `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, and `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`
- connector and public raw readback both still fail for `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`

4. confirm the risky transport posture is still blocked and machine-readable
- `phase10-lifecycle-guard-bookkeeping-helper`
- `phase10-reset-replay-bookkeeping-helper`
- `phase10-core-slice-note`
- `phase10-core-lab-validation-evidence`
- `phase10-interrupt-compound-ack-gate`
- `phase10-core-dual-implementation-bridge`
- `phase10-core-probe-remove-lifecycle`
- `scripts/zigux/validate-phase10.py`
- `zigux/tests/phase10_virtio_core_manifest.json`
- `zigux/tests/phase10_virtio_core_survey.zig`

No attached-Zig replay was available in this run because there is still no writable live Zigux checkout in this workspace. Public current-`master` readback now shows the direct core-survey shared-build route again, so the remaining same-packet follow-through is truthfulness around mixed-source visibility, the survey note's stale overclaim, and the narrower missing driver-id pair rather than missing build wiring.

## Next bounded step

Keep the follow-through inside the same core packet only:

- keep `Documentation/zigux/phase10-virtio-core-survey.md` aligned with the already-correct packet-local truth on current `master`: the `virtio_driver_id` helper-and-replay pair is not shipped evidence until those two paths actually materialize again, while the returned validator pair, closure manifest, Makefile-backed build gate, and directly re-readable core survey/test packet stay explicit as current shared evidence
- keep broader core-packet truthfulness and any future manifest-or-slice follow-through under the live `P10-L01` core owner lane; reopen `P10-L04` only if this survey note itself falls behind the directly returned core packet, shared validator/build route stack, or the exact-path driver-id gap posture
- if a writable checkout becomes available, rerun the narrowest honest replay with `zig build phase10-virtio-core-survey-tests --build-file zigux/tests/phase10_build.zig` before widening any further
