# Phase 11 DesignWare Verify Alignment Gap

## Status

- lane family: `P11-L12`
- active current-head continuity note owner: `P11-Y03`
- phase: `Phase 11`
- scope: `drivers/watchdog/dw_wdt` verify-alignment and adjacent PM-truthfulness evidence
- current authenticated contents no longer keep the older returned validation-matrix story directly readable through the same bridge that serves the rest of this packet
- the directly checkable current-head packet in this environment is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `drivers/watchdog/dw_wdt_pm.zig`, and this companion note
- `zigux/tests/phase11_dw_wdt_manifest.json` now records deeper platform-registration scaffold continuity `P11-L10` at surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`
- the active routing split now keeps owner-note truthfulness on `P11-Y03`, survey-only follow-through on `P11-L09`, and deeper platform-registration scaffold follow-through on `P11-L10`; do not reserve `P11-L05` unless the packet collapses back to the older survey-era shape
- `zigux/tests/phase11_dw_wdt_manifest.json` still routes `phase11-dw-wdt-teardown-parity` to `drivers/watchdog/dw_wdt_verify.zig`, so teardown-parity ownership remains explicit even though the broader verify helper itself does not currently rematerialize through the same authenticated-contents bridge
- `drivers/watchdog/dw_wdt_pm.zig` still keeps bounded suspend, resume, and shutdown handoff summaries explicit across missing-drvdata blocks, idle suspend without teardown hooks, running-hardware suspend stop intent, missing suspend hook teardown during running stop, imported-running resume recovery, timeout-reprogram blocks, running shutdown stop intent, pretimeout-mask teardown, and idle shutdown cleanup while still keeping live PM execution out of scope
- `zigux/tests/phase11_dw_wdt_manifest.json` still keeps `phase11-dw-wdt-live-mmio-validation` parked as `ready_next` at `zigux/tests/phase11_dw_wdt.zig`, but this note does not itself own that later implementation step
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` still records that the broader direct-driver and replay-backed packet does not currently rematerialize through the same authenticated-contents bridge
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` should keep this narrower current-head packet fail-closed instead of asserting direct readability for the broader returned validation-matrix or verify-helper stack

## Why This Note Exists

The Phase 11 roadmap still keeps this watchdog family inside bounded lifecycle parity, teardown parity, and validation truthfulness around `drivers/watchdog/*.zig`. Keeping one closed-gap note for the current `P11-L12` verify-alignment family is still useful, but it has to describe the current packet honestly.

This note therefore no longer treats the manifest lane key as archived continuity. Instead it records that current manifest continuity now stays on `P11-L10` while current note-only truthfulness stays parked on `P11-Y03`, survey-only follow-through stays on `P11-L09`, and the same deeper platform-registration scaffold work remains on `P11-L10`.

This note also no longer treats the broader validation-matrix, survey, slice, teardown-note, direct verify-helper, or direct replay stack as same-bridge proof in this environment. Instead it records the smaller packet that current authenticated contents still make directly reviewable, keeps the active manifest continuity explicit, and leaves future reopening to a fail-closed checker if the manifest, platform-plan note, manifest-routed teardown-parity ownership, or PM helper drift again.

## Observed Current-Head Evidence

- `zigux/tests/phase11_dw_wdt_manifest.json` matches deeper platform-registration scaffold continuity `P11-L10` and surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`
- `zigux/tests/phase11_dw_wdt_manifest.json` still routes `phase11-dw-wdt-teardown-parity` to `drivers/watchdog/dw_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt_manifest.json` still marks `phase11-dw-wdt-live-platform-pm` as `starter_landed` at `drivers/watchdog/dw_wdt_pm.zig`
- `zigux/tests/phase11_dw_wdt_manifest.json` still keeps `phase11-dw-wdt-live-mmio-validation` parked as `ready_next` at `zigux/tests/phase11_dw_wdt.zig`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` still records that the broader direct-driver and replay-backed packet does not currently rematerialize through the same authenticated-contents bridge
- `drivers/watchdog/dw_wdt_pm.zig` keeps `test "phase11 dw_wdt pm suspend keeps missing drvdata explicit"`, `test "phase11 dw_wdt pm suspend keeps running-hardware stop handoff explicit"`, `test "phase11 dw_wdt pm suspend keeps idle path explicit without teardown hooks"`, `test "phase11 dw_wdt pm suspend keeps missing hook teardown explicit during running stop"`, `test "phase11 dw_wdt pm resume keeps imported-running handoff explicit"`, `test "phase11 dw_wdt pm resume keeps timeout reprogram block explicit before idle restore"`, `test "phase11 dw_wdt pm shutdown keeps missing drvdata explicit"`, `test "phase11 dw_wdt pm shutdown keeps running teardown stop and hook removal explicit"`, `test "phase11 dw_wdt pm shutdown keeps running pretimeout mask explicit"`, `test "phase11 dw_wdt pm shutdown keeps idle hook teardown explicit without stop"`, and `test "phase11 dw_wdt pm shutdown keeps idle no-hook teardown explicit"` reviewable on current `master`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` should keep this narrower current-head packet fail-closed instead of asserting direct readability for the broader returned validation-matrix or verify-helper stack

## Next Bounded Same-Lane Step

- leave this note, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `drivers/watchdog/dw_wdt_pm.zig`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` parked unless the smaller authenticated-contents packet drifts again
- route any next survey-only reminder repair to `P11-L09` instead of reopening the archived manifest lane key
- route any next platform-registration scaffold reminder or implementation change to `P11-L10` instead of reopening this note-only coordination lane
- keep the manifest-backed live-MMIO validation step parked as the later substantive DesignWare follow-through once the owner packet changes justify it
- do not widen this note back into survey-only fallback surfaces, broader replay claims, or unrelated Phase 11 watchdog work without fresh direct readback
- do not reserve `P11-L05` again unless a fresh reread shows current `master` has collapsed back to the older survey-era packet shape