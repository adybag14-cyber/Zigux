# Phase 11 DesignWare Watchdog Provenance Readback

This note records the current survey-facing repo reality for the Phase 11 `dw_wdt` packet on `master`.

## Live Readback
- `zigux/tests/phase11_dw_wdt_manifest.json` currently records continuity lane `P11-L05` at surveyed commit `75f8336c4305beed127d7abfae37d3999b7cc57c`.
- current direct tree readback still materializes `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`.
- current direct contents reads in this run did not rematerialize `Documentation/zigux/phase11-dw-wdt-survey.md` or `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so the older manifest-versus-survey mismatch tracked by this lane cannot be re-proven from current head readback today.
- the saved `P11-L09` survey realignment handoff assumed a newer `P11-L10` manifest-backed packet, but the current readable manifest no longer supports replaying that exact handoff as-is.
- the roadmap still keeps this family inside Phase 11 simple-driver starter discipline: keep survey truthfulness bounded and leave the next substantive step on platform-backed acquisition scaffolding rather than widening into PM, IRQ, reset, or live MMIO behavior.

## Why This Matters
- the current DesignWare packet is still meaningful Phase 11 product work because the bounded driver, verify-helper, manifest, scaffold, and checker surfaces remain reviewable on `master`
- the honest survey-lane move is to keep the continuity trail truthful about what current `master` actually materializes, not to replay an older survey-note fix against a shifted packet
- this is survey-facing reminder drift only; it is not a reason to widen into driver code, registration scaffolding, verify-helper semantics, or shared Phase 11 churn

## Next Bounded Step
- leave `/workspace/memory/pending-patches/P11-L09-dw-wdt-survey-packet-realignment.patch` parked as historical context until `Documentation/zigux/phase11-dw-wdt-survey.md` and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` rematerialize through a current readable path again
- if those survey surfaces return, reread them against the live manifest before preparing any new survey-only repair
- until then, keep the next substantive non-doc DesignWare follow-through on the separately owned platform-registration scaffold lane rather than reopening this survey lane with stale assumptions
