# Phase 11 DesignWare Verify Alignment Gap

## Status

- lane: `P11-L11`
- phase: `Phase 11`
- scope: `drivers/watchdog/bcm2835_wdt` and `drivers/watchdog/dw_wdt` watchdog lifecycle parity
- current `master` now ships a driver-backed `drivers/watchdog/dw_wdt_verify.zig` packet that imports `dw_wdt.zig` directly and keeps registration-blocking paths, imported-running handoff, continued-heartbeat teardown and remove outcomes, reset-backed teardown and remove cleanup, and idle no-op lifecycle behavior reviewable
- the shared `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` still names continuity `P11-L05` with surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`
- the current `zigux/tests/phase11_dw_wdt_manifest.json` instead records lane key `P11-L10` with surveyed commit `6726fdd9da4eef55498fb06c38815317a684bcbf`
- nearby continuity notes in the memory folder already treat the driver-backed verify helper as the latest same-lane substantive step, so the remaining gap is truthfulness across the DesignWare shared packet rather than missing watchdog behavior

## Why This Note Exists

The Phase 11 roadmap and bootstrap ledger still keep this watchdog family inside bounded lifecycle parity, teardown parity, and validation truthfulness around `drivers/watchdog/*.zig`. That makes the current same-lane gap smaller than another helper or platform-backed scaffold step.

The live DesignWare packet now has stronger failure-mode evidence than the shared note stack consistently records. The verify helper moved from the older standalone model to a driver-backed proof surface, but the coupled validation matrix and manifest still disagree on lane identity and reviewed head. That mismatch makes future review work noisy and risks reopening stale provenance arguments instead of keeping the next step on a real platform-backed acquisition scaffold.

## Observed Current-Master Evidence

- `drivers/watchdog/dw_wdt_verify.zig` now covers registration-blocking `drvdata` and timer-clock failure paths, imported-running handoff, reset-backed teardown and remove cleanup, continued-heartbeat teardown and remove behavior when reset control is absent, and idle no-op stop or teardown or remove behavior
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` still describes the active continuity as `P11-L05`
- `zigux/tests/phase11_dw_wdt_manifest.json` still describes the active packet as lane `P11-L10`
- the active packet should not widen into bcm2835 archival work, platform registration execution, PM, IRQ ownership, clock or reset acquisition, or live MMIO validation during this follow-up
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` now keeps the documented matrix-versus-manifest mismatch fail-closed until the shared DesignWare packet is refreshed together

## Next Bounded Same-Lane Step

Refresh the coupled DesignWare review packet together so it records one truthful continuity story around the landed driver-backed verify helper:

- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`

That follow-up should stay doc-and-checker-local unless a focused replay path for the survey packet is available on the resulting head. The next substantive non-doc move after this truthfulness refresh should remain one platform-backed acquisition scaffold only.
