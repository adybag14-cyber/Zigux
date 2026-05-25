# Phase 11 DesignWare Watchdog Provenance Readback

This note records the current survey-facing repo reality for the Phase 11 `dw_wdt` packet on `master`.

## Live Readback

- `zigux/tests/phase11_dw_wdt_manifest.json` currently records active lane continuity `P11-L10` at surveyed commit `75f8336c4305beed127d7abfae37d3999b7cc57c`.
- current authenticated contents reads now materialize `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_pm.zig`, `drivers/watchdog/dw_wdt_pm_scaffold.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`.
- current authenticated contents reads still do not rematerialize `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `drivers/watchdog/dw_wdt.zig`, or `zigux/tests/phase11_dw_wdt.zig`, so those broader driver, direct-replay, and older reminder surfaces remain fallback-visible evidence in this environment rather than part of the same authenticated current-head packet.
- the authenticated current-head packet is now internally aligned on the shared build-route boundary and the current bounded lifecycle inventory: the manifest still marks `phase11-build-gate` as `shared_gap_current_head` with `preexisting_phase11_build_present` false, keeps `dw_wdt_zig_present`, `dw_wdt_test_present`, and `dw_wdt_slice_note_present` explicitly false, and keeps the returned verify helper, restart summary, PM helper, survey note, validation matrix, and focused survey gate explicit.
- the roadmap still keeps this family inside Phase 11 simple-driver starter discipline: keep owner-packet truthfulness and scaffold truthfulness bounded, and leave the next substantive step on platform-backed acquisition or MMIO follow-through rather than widening into unrelated watchdog behavior.

## Why This Matters

- the current DesignWare packet is still meaningful Phase 11 product work because the bounded owner note, survey note, validation matrix, manifest, focused survey gate, registration scaffold, restart helper, returned verify helper, PM helper pair, and checker surfaces remain reviewable through authenticated contents reads.
- the honest owner-lane move is therefore to keep the readback split explicit instead of claiming that the broader direct-driver and direct replay stack is directly readable through the same bridge as the smaller owner packet.
- the surviving same-lane gap is no longer stale survey wording about `zigux/tests/phase11_build.zig` or the landed restart, verify, and PM-helper inventory; it is the broader direct-driver, driver-test, slice, and teardown-note stack together with the later platform-backed acquisition and MMIO follow-through.
- this is DesignWare-local review-noise cleanup only; it is not a reason to widen into driver code, registration scaffolding, verify-helper semantics, or shared Phase 11 churn.

## Next Bounded Step

- leave this provenance note parked unless a fresh DesignWare reread finds one more same-packet drift between this note, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, and `zigux/tests/phase11_dw_wdt_survey.zig`.
- keep the next substantive non-doc DesignWare follow-through on `P11-L10`, the platform-registration scaffold lane, rather than widening this provenance note into driver-local work.
- if a future run uses public-tree fallback to inspect the broader DesignWare driver, verify-helper-adjacent context, slice, teardown-note, or direct replay stack, record that as fallback evidence instead of promoting it to authenticated current-head readback without a matching contents reread.
- keep the broader direct-driver and direct replay stack framed as larger same-lane vocabulary until a fresh authenticated reread restores those paths through the same bridge.
- do not widen into live watchdog-core, hardware-backed MMIO, or unrelated bcm2835 or gpio watchdog behavior from this note.
