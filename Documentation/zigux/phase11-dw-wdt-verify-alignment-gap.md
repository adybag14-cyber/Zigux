# Phase 11 DesignWare Verify Alignment Gap

## Status

- lane family: `P11-L12`
- active current-head continuity note owner: `P11-Y03`
- phase: `Phase 11`
- scope: `drivers/watchdog/dw_wdt` verify-alignment and adjacent PM-truthfulness evidence
- current authenticated contents now keep the returned validation matrix directly readable through the same bridge that serves the rest of this narrower packet
- the directly checkable current-head packet in this environment is `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/watchdog/dw_wdt_pm.zig`, and this companion note
- `zigux/tests/phase11_dw_wdt_manifest.json` now records deeper platform-registration scaffold continuity `P11-L10` at surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`
- the active routing split now keeps owner-note truthfulness on `P11-Y03`, survey-only follow-through on `P11-L09`, and deeper platform-registration scaffold follow-through on `P11-L10`; do not reserve `P11-L05` unless the packet collapses back to the older survey-era shape
- `zigux/tests/phase11_dw_wdt_manifest.json` still routes `phase11-dw-wdt-teardown-parity` to `drivers/watchdog/dw_wdt_verify.zig`, and the returned verify helper now remains directly readable on the same authenticated bridge, so teardown-parity ownership and evidence both stay explicit without reopening the broader reminder stack
- `drivers/watchdog/dw_wdt_pm.zig` still keeps bounded suspend, resume, and shutdown handoff summaries explicit across missing-drvdata blocks, idle suspend without teardown hooks, running-hardware suspend stop intent, missing suspend hook teardown during running stop, imported-running resume recovery, timeout-reprogram blocks, running shutdown stop intent, pretimeout-mask teardown, and idle shutdown cleanup while still keeping live PM execution out of scope
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` now keeps the returned DesignWare matrix readable on current `master` while still parking hardware-backed MMIO validation as the next bounded same-lane step
- `zigux/tests/phase11_dw_wdt_manifest.json` still keeps `phase11-dw-wdt-live-mmio-validation` parked as `ready_next` at `zigux/tests/phase11_dw_wdt.zig`, but this note does not itself own that later implementation step
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` now records that the direct driver-and-test pair has returned on the authenticated contents bridge while the slice note, teardown note, and older packet checker still remain outside the same narrower packet
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` should keep this narrower current-head packet fail-closed around the returned validation matrix, the manifest-routed teardown-parity ownership, the returned verify helper, the platform-plan boundary, and the bounded PM helper instead of asserting direct readability for reminder surfaces that still have not returned

## Why This Note Exists

The Phase 11 roadmap still keeps this watchdog family inside bounded lifecycle parity, teardown parity, and validation truthfulness around `drivers/watchdog/*.zig`. Keeping one closed-gap note for the current `P11-L12` verify-alignment family is still useful, but it has to describe the current packet honestly.

This note therefore no longer treats the returned validation matrix as absent from the current contents bridge. It records that the current bridge now keeps the DesignWare matrix readable together with the manifest, the owner note, the returned verify helper, the PM helper, and the note-only continuity packet, while the slice note, teardown note, and older packet checker still remain outside that narrower direct-read packet.

## Observed Current-Head Evidence

- `zigux/tests/phase11_dw_wdt_manifest.json` matches deeper platform-registration scaffold continuity `P11-L10` and surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`
- `zigux/tests/phase11_dw_wdt_manifest.json` still routes `phase11-dw-wdt-teardown-parity` to `drivers/watchdog/dw_wdt_verify.zig`
- `drivers/watchdog/dw_wdt_verify.zig` remains directly readable on current `master` for teardown-parity review inside the smaller packet
- `zigux/tests/phase11_dw_wdt_manifest.json` still marks `phase11-dw-wdt-live-platform-pm` as `starter_landed` at `drivers/watchdog/dw_wdt_pm.zig`
- `zigux/tests/phase11_dw_wdt_manifest.json` still keeps `phase11-dw-wdt-live-mmio-validation` parked as `ready_next` at `zigux/tests/phase11_dw_wdt.zig`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` keeps `PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed` explicit, keeps current surveyed packet pin `75f8336c4305beed127d7abfae37d3999b7cc57c` explicit, keeps `P11-L10` continuity explicit, and still parks hardware-backed MMIO validation as the next bounded same-lane step
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` now records that the direct driver-and-test pair has returned while the slice note, teardown note, and older packet checker still do not rematerialize through the same authenticated-contents bridge
- `drivers/watchdog/dw_wdt_pm.zig` keeps `test "phase11 dw_wdt pm suspend keeps missing drvdata explicit"`, `test "phase11 dw_wdt pm suspend keeps running-hardware stop handoff explicit"`, `test "phase11 dw_wdt pm suspend keeps idle path explicit without teardown hooks"`, `test "phase11 dw_wdt pm suspend keeps missing hook teardown explicit during running stop"`, `test "phase11 dw_wdt pm resume keeps imported-running handoff explicit"`, `test "phase11 dw_wdt pm resume keeps timeout reprogram block explicit before idle restore"`, `test "phase11 dw_wdt pm shutdown keeps missing drvdata explicit"`, `test "phase11 dw_wdt pm shutdown keeps running teardown stop and hook removal explicit"`, `test "phase11 dw_wdt pm shutdown keeps running pretimeout mask explicit"`, `test "phase11 dw_wdt pm shutdown keeps idle hook teardown explicit without stop"`, and `test "phase11 dw_wdt pm shutdown keeps idle no-hook teardown explicit"` reviewable on current `master`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` should keep this narrower current-head packet fail-closed around the returned validation matrix, verify helper, and PM helper rather than asserting direct readability for reminder surfaces that still have not returned

## Next Bounded Same-Lane Step

- leave this note, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/watchdog/dw_wdt_pm.zig`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` parked unless the narrower authenticated-contents packet drifts again
- route any next survey-only reminder repair to `P11-L09` instead of reopening the archived manifest lane key
- route any next platform-registration scaffold reminder or implementation change to `P11-L10` instead of reopening this note-only coordination lane
- keep the manifest-backed live-MMIO validation step parked as the later substantive DesignWare follow-through once the owner packet changes justify it
- do not widen this note back into survey-only fallback surfaces, broader replay claims, or unrelated Phase 11 watchdog work without fresh direct readback
- do not reserve `P11-L05` again unless a fresh reread shows current `master` has collapsed back to the older survey-era packet shape
