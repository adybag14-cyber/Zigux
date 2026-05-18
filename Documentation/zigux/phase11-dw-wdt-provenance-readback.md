# Phase 11 DesignWare Watchdog Provenance Readback

This note records the current survey-facing repo reality for the Phase 11 `dw_wdt` packet on `master`.

## Live Readback
- `zigux/tests/phase11_dw_wdt_manifest.json` currently records continuity lane `P11-L05` at surveyed commit `75f8336c4305beed127d7abfae37d3999b7cc57c`.
- current direct tree readback materializes `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, and `Documentation/zigux/phase11-driver-lane-sequencing.md`.
- current direct tree readback also materializes `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`.
- the saved `P11-L09` survey realignment handoff assumed a narrower docs-and-scaffold packet than current `master` now exposes, so future survey-only work should start from this returned helper-backed packet instead of the older reduced readback assumption.
- the roadmap still keeps this family inside Phase 11 simple-driver starter discipline: keep survey truthfulness bounded and leave the next substantive step on platform-backed acquisition scaffolding rather than widening into PM, IRQ, reset, or live MMIO behavior.

## Why This Matters
- the current DesignWare packet is still meaningful Phase 11 product work because the bounded driver, verify-helper, replay, survey replay, manifest, scaffold, reminder notes, and checker surfaces remain reviewable on `master`
- the honest survey-lane move is to keep the continuity trail truthful about what current `master` actually materializes, not to replay an older reduced-readback fix against a returned packet
- this is survey-facing reminder drift only; it is not a reason to widen into driver code, registration scaffolding, verify-helper semantics, or shared Phase 11 churn

## Next Bounded Step
- leave historical survey-only patch context parked until the survey lane actually needs another reminder-surface repair
- if the survey lane reopens, reread the live manifest, survey note, validation matrix, and current helper-backed packet together before preparing a new survey-only fix
- until then, keep the next substantive non-doc DesignWare follow-through on the separately owned platform-registration scaffold lane rather than reopening this survey lane with stale assumptions
