# Phase 11 DesignWare Verify Alignment Gap

## Status

- lane family: `P11-L10`
- active current-head continuity: `P11-L05`
- phase: `Phase 11`
- scope: `drivers/watchdog/dw_wdt` verify-alignment and adjacent PM-truthfulness evidence
- current authenticated contents no longer keep the older returned validation-matrix story directly readable through the same bridge that serves the rest of this packet
- the directly checkable current-head packet in this environment is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/watchdog/dw_wdt_pm.zig`, and this companion note
- `zigux/tests/phase11_dw_wdt_manifest.json` still records continuity `P11-L05` at surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`
- `drivers/watchdog/dw_wdt_verify.zig` still keeps registration-blocking failure paths, MMIO-blocked registration handoff, imported-running shared-clock fallback, and teardown and failure-mode parity explicit without claiming platform registration execution, clock or reset acquisition, IRQ ownership, live PM execution, or live MMIO validation
- `drivers/watchdog/dw_wdt_pm.zig` still keeps bounded suspend, resume, and shutdown handoff summaries explicit across missing-drvdata blocks, idle suspend without teardown hooks, running-hardware suspend stop intent, missing suspend hook teardown during running stop, imported-running resume recovery, timeout-reprogram blocks, running shutdown stop intent, pretimeout-mask teardown, and idle shutdown cleanup while still keeping live PM execution out of scope

## Why This Note Exists

The Phase 11 roadmap still keeps this watchdog family inside bounded lifecycle parity, teardown parity, and validation truthfulness around `drivers/watchdog/*.zig`. Keeping one closed-gap note for the historical `P11-L10` verify-alignment family is still useful, but it has to describe the current packet honestly.

This note therefore no longer treats the broader validation-matrix, survey, slice, teardown-note, or direct replay stack as same-bridge proof in this environment. Instead it records the smaller packet that current authenticated contents still make directly reviewable, keeps the active manifest continuity explicit, and leaves future reopening to a fail-closed checker if the manifest, platform-plan note, verify helper, or PM helper drift again.

## Observed Current-Head Evidence

- `zigux/tests/phase11_dw_wdt_manifest.json` matches active continuity `P11-L05` and surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`
- `zigux/tests/phase11_dw_wdt_manifest.json` still routes `phase11-dw-wdt-teardown-parity` to `drivers/watchdog/dw_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt_manifest.json` still marks `phase11-dw-wdt-live-platform-pm` as `starter_landed` at `drivers/watchdog/dw_wdt_pm.zig`
- `zigux/tests/phase11_dw_wdt_manifest.json` still keeps `phase11-dw-wdt-live-mmio-validation` parked as `ready_next` at `zigux/tests/phase11_dw_wdt.zig`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` still records that the broader direct-driver and replay-backed packet does not currently rematerialize through the same authenticated-contents bridge
- `drivers/watchdog/dw_wdt_verify.zig` keeps `test "phase11 dw_wdt verify keeps registration-blocking failure paths explicit"`, `test "phase11 dw_wdt verify keeps mmio-blocked registration handoff explicit"`, `test "phase11 dw_wdt verify keeps imported-running handoff and shared-clock fallback explicit"`, `test "phase11 dw_wdt verify keeps continued-heartbeat teardown and remove failure modes explicit"`, `test "phase11 dw_wdt verify keeps reset-backed teardown and remove cleanup distinct"`, and `test "phase11 dw_wdt verify keeps idle no-op teardown and remove paths explicit"` reviewable on current `master`
- `drivers/watchdog/dw_wdt_pm.zig` keeps `test "phase11 dw_wdt pm suspend keeps missing drvdata explicit"`, `test "phase11 dw_wdt pm suspend keeps running-hardware stop handoff explicit"`, `test "phase11 dw_wdt pm suspend keeps idle path explicit without teardown hooks"`, `test "phase11 dw_wdt pm suspend keeps missing hook teardown explicit during running stop"`, `test "phase11 dw_wdt pm resume keeps imported-running handoff explicit"`, `test "phase11 dw_wdt pm resume keeps timeout reprogram block explicit before idle restore"`, `test "phase11 dw_wdt pm shutdown keeps missing drvdata explicit"`, `test "phase11 dw_wdt pm shutdown keeps running teardown stop and hook removal explicit"`, `test "phase11 dw_wdt pm shutdown keeps running pretimeout mask explicit"`, `test "phase11 dw_wdt pm shutdown keeps idle hook teardown explicit without stop"`, and `test "phase11 dw_wdt pm shutdown keeps idle no-hook teardown explicit"` reviewable on current `master`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` should keep this narrower current-head packet fail-closed instead of asserting the older returned validation-matrix stack

## Next Bounded Same-Lane Step

- leave this note, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/watchdog/dw_wdt_pm.zig`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` parked unless the smaller authenticated-contents packet drifts again
- keep the next substantive non-doc move on the manifest-backed live-MMIO validation step already parked in the current DesignWare packet
- do not widen this note back into survey-only fallback surfaces, broader replay claims, or unrelated Phase 11 watchdog work without fresh direct readback