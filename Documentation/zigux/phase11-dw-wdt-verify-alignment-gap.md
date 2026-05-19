# Phase 11 DesignWare Verify Alignment Gap

## Status

- lane: `P11-L10`
- phase: `Phase 11`
- scope: `drivers/watchdog/dw_wdt` verify alignment and adjacent PM-truthfulness reminder packet
- current `master` no longer has a matrix-versus-manifest continuity split for the DesignWare verify packet: both `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` and `zigux/tests/phase11_dw_wdt_manifest.json` record continuity `P11-L05` with surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`
- `drivers/watchdog/dw_wdt_verify.zig` currently keeps registration-blocking failure paths, MMIO-blocked registration handoff, imported-running shared-clock fallback, and teardown and failure-mode parity explicit without claiming platform registration execution, clock or reset acquisition, IRQ ownership, live PM execution, or live MMIO validation
- `drivers/watchdog/dw_wdt_pm.zig` now also keeps bounded suspend and resume handoff summaries explicit across missing-drvdata blocks, running-hardware suspend stop intent, imported-running resume recovery, and timeout-reprogram blocks while still keeping live PM execution out of scope
- bcm2835 continuity remains adjacent Phase 11 watchdog work, but this closed-gap note is DesignWare-only and should not be used to reopen bcm2835 reminder wording
- nearby continuity notes in the memory folder already treat this alignment drift as closed, so the remaining same-lane work is no longer shared-packet truthfulness and now narrows to the next live-MMIO validation step already parked in the manifest

## Why This Note Exists

The Phase 11 roadmap still keeps this watchdog family inside bounded lifecycle parity, teardown parity, and validation truthfulness around `drivers/watchdog/*.zig`. That makes it useful to retain one reviewable note for the retired alignment gap instead of silently dropping the continuity trail.

This note now exists as a closed-gap companion: it records that the shared validation matrix and manifest agree again, it records that the adjacent bounded PM helper is now landed, and it keeps a small fail-closed checker in place so future lane or surveyed-head drift reopens immediately instead of hiding inside Phase 11 reminder surfaces.

## Observed Current-Master Evidence

- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` describes the active continuity as `P11-L05` with surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`
- `zigux/tests/phase11_dw_wdt_manifest.json` matches that same lane key and surveyed commit while still routing `phase11-dw-wdt-teardown-parity` to `drivers/watchdog/dw_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt_manifest.json` also marks `phase11-dw-wdt-live-platform-pm` as `starter_landed` at `drivers/watchdog/dw_wdt_pm.zig` and keeps `phase11-dw-wdt-live-mmio-validation` parked as `ready_next` at `zigux/tests/phase11_dw_wdt.zig`
- `drivers/watchdog/dw_wdt_verify.zig` keeps `test "phase11 dw_wdt verify keeps registration-blocking failure paths explicit"`, `test "phase11 dw_wdt verify keeps mmio-blocked registration handoff explicit"`, `test "phase11 dw_wdt verify keeps imported-running handoff and shared-clock fallback explicit"`, `test "phase11 dw_wdt verify keeps continued-heartbeat teardown and remove failure modes explicit"`, `test "phase11 dw_wdt verify keeps reset-backed teardown and remove cleanup distinct"`, and `test "phase11 dw_wdt verify keeps idle no-op teardown and remove paths explicit"` reviewable on current `master`
- `drivers/watchdog/dw_wdt_pm.zig` keeps `test "phase11 dw_wdt pm suspend keeps missing drvdata explicit"`, `test "phase11 dw_wdt pm suspend keeps running-hardware stop handoff explicit"`, `test "phase11 dw_wdt pm resume keeps imported-running handoff explicit"`, and `test "phase11 dw_wdt pm resume keeps timeout reprogram block explicit before idle restore"` reviewable on current `master`
- the active packet should not widen into bcm2835 archival work, platform registration execution, IRQ ownership, clock or reset acquisition, live PM execution, or live MMIO validation during this follow-up
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` now keeps the resolved matrix-versus-manifest alignment, the adjacent bounded PM-helper landing, and the current next-step scope fail-closed

## Next Bounded Same-Lane Step

- leave `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/watchdog/dw_wdt_pm.zig`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` parked unless the shared DesignWare packet drifts again
- keep bcm2835 follow-through on its own same-family packet instead of mixing it into this closed DesignWare note
- the next substantive non-doc move should now remain the manifest-backed live-MMIO validation step, still without widening beyond the bounded platform-backed probe, remove, suspend, and resume edges already named by the current packet
