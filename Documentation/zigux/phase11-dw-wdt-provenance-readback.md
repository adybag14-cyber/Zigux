# Phase 11 DesignWare Watchdog Provenance Readback

This note records the current survey-facing repo reality for the Phase 11 `dw_wdt` packet on `master`.

## Live Readback

- `zigux/tests/phase11_dw_wdt_manifest.json` currently records archival continuity lane `P11-L05` at surveyed commit `75f8336c4305beed127d7abfae37d3999b7cc57c`.
- current survey-facing reminder follow-through stays parked under `P11-L09`, while the deeper platform-registration scaffold follow-through remains `P11-L10`; treat the retained manifest lane key `P11-L05` as archived survey identity for the current packet, not as the next lane to reserve.
- current raw `master` fallback rereads rematerialize `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` and `Documentation/zigux/phase11-dw-wdt-survey.md`.
- current authenticated contents reads still clip `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, and `zigux/tests/phase11_dw_wdt_survey.zig`, so those survey-facing surfaces remain returned-through-fallback evidence in this environment rather than directly readable through the same bridge that serves the rest of the packet.
- current authenticated contents reads do materialize `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`.
- the newly rematerialized survey note and validation matrix do not actually align with the readable manifest: the manifest still marks `phase11-build-gate` as `shared_gap_current_head` and keeps `preexisting_phase11_build_present` false, while the raw-read survey note and validation matrix both still describe `zigux/tests/phase11_build.zig` as a landed shared replay route.
- that means the surviving survey packet has reopened a real same-lane truthfulness gap around the simple-driver roadmap's shared validation surface, even though the rest of the helper-backed DesignWare packet remains reviewable on `master`.
- the roadmap still keeps this family inside Phase 11 simple-driver starter discipline: keep survey truthfulness bounded and leave the next substantive step on platform-backed acquisition scaffolding rather than widening into PM, IRQ, reset, or live MMIO behavior.

## Why This Matters

- the current DesignWare packet is still meaningful Phase 11 product work because the bounded driver, verify-helper, replay, manifest, scaffold, reminder notes, and checker surfaces remain reviewable on `master`, while the survey note, validation matrix, and dedicated survey gate are still available through raw fallback readback.
- the honest survey-lane move is no longer just to park historical patch context; it is to record that the current survey-facing packet overclaims the shared `phase11_build.zig` route relative to the still-readable manifest and therefore needs one fresh survey-only repair from current head.
- the active routing split also needs to stay explicit while that repair waits: `P11-L09` owns the next survey-only truthfulness fix, `P11-L10` owns the deeper platform-registration scaffold follow-through, and the manifest's retained `P11-L05` tag is only archival continuity for this packet.
- this is survey-facing reminder drift only; it is not a reason to widen into driver code, registration scaffolding, verify-helper semantics, or shared Phase 11 churn.

## Next Bounded Step

- reserve `P11-L09`, then reread the live manifest, survey note, validation matrix, and dedicated survey gate together from the same exact checkout before landing a new survey-only fix.
- keep that repair narrowed to the direct survey packet so the manifest, survey note, validation matrix, and survey gate stop disagreeing about whether `zigux/tests/phase11_build.zig` is a landed shared replay or a current-head shared gap.
- keep the next substantive non-doc DesignWare follow-through on `P11-L10`, the separately owned platform-registration scaffold lane, rather than widening this survey reminder gap into driver-local work.
- do not reopen `P11-L05` unless a fresh reread shows current `master` has collapsed back to the older survey-only packet shape again.
