# Phase 11 DesignWare Verify Alignment Gap

## Status

- lane: `P11-L10`
- phase: `Phase 11`
- scope: `drivers/watchdog/dw_wdt` verify alignment and lifecycle-parity reminder packet
- current `master` no longer has a matrix-versus-manifest continuity split for the DesignWare verify packet: both `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` and `zigux/tests/phase11_dw_wdt_manifest.json` record continuity `P11-L05` with surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`
- `drivers/watchdog/dw_wdt_verify.zig` currently keeps registration-blocking failure paths, MMIO-blocked registration handoff, imported-running shared-clock fallback, and teardown and failure-mode parity explicit without claiming platform registration execution, clock or reset acquisition, IRQ ownership, PM behavior, or live MMIO validation
- bcm2835 continuity remains adjacent Phase 11 watchdog work, but this closed-gap note is DesignWare-only and should not be used to reopen bcm2835 reminder wording
- nearby continuity notes in the memory folder already treat this alignment drift as closed, so the remaining same-lane work is no longer shared-packet truthfulness and returns to the next bounded platform-backed acquisition scaffold

## Why This Note Exists

The Phase 11 roadmap still keeps this watchdog family inside bounded lifecycle parity, teardown parity, and validation truthfulness around `drivers/watchdog/*.zig`. That makes it useful to retain one reviewable note for the retired alignment gap instead of silently dropping the continuity trail.

This note now exists as a closed-gap companion: it records that the shared validation matrix and manifest agree again, and it keeps a small fail-closed checker in place so future lane or surveyed-head drift reopens immediately instead of hiding inside Phase 11 reminder surfaces.

## Observed Current-Master Evidence

- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` describes the active continuity as `P11-L05` with surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`
- `zigux/tests/phase11_dw_wdt_manifest.json` matches that same lane key and surveyed commit while still routing `phase11-dw-wdt-teardown-parity` to `drivers/watchdog/dw_wdt_verify.zig`
- `drivers/watchdog/dw_wdt_verify.zig` keeps `test "phase11 dw_wdt verify keeps registration-blocking failure paths explicit"`, `test "phase11 dw_wdt verify keeps mmio-blocked registration handoff explicit"`, `test "phase11 dw_wdt verify keeps imported-running handoff and shared-clock fallback explicit"`, `test "phase11 dw_wdt verify keeps continued-heartbeat teardown and remove failure modes explicit"`, `test "phase11 dw_wdt verify keeps reset-backed teardown and remove cleanup distinct"`, and `test "phase11 dw_wdt verify keeps idle no-op teardown and remove paths explicit"` reviewable on current `master`
- the active packet should not widen into bcm2835 archival work, platform registration execution, PM, IRQ ownership, clock or reset acquisition, or live MMIO validation during this follow-up
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` now keeps the resolved matrix-versus-manifest alignment and the current verify-helper scope fail-closed

## Next Bounded Same-Lane Step

- leave `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `drivers/watchdog/dw_wdt_verify.zig`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` parked unless the shared DesignWare packet drifts again
- keep bcm2835 follow-through on its own same-family packet instead of mixing it into this closed DesignWare note
- the next substantive non-doc move should remain one platform-backed acquisition scaffold only