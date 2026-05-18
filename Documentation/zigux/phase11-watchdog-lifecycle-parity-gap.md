# Phase 11 Watchdog Lifecycle Parity Gap

## Status

- lane: `P11-L07`
- phase: `Phase 11`
- scope: `drivers/watchdog/bcm2835_wdt` and `drivers/watchdog/dw_wdt` straightforward watchdog lifecycle parity
- the Phase 11 roadmap still keeps simple production drivers on straightforward lifecycles together with teardown and failure-mode parity around `drivers/watchdog/*.zig`
- current `master` keeps `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig` directly readable as the bcm2835 lifecycle-backed packet survey
- current `master` keeps `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` directly readable as the narrower DesignWare owner packet

## Observed Current-Master Evidence

- `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig` still requires `drivers/watchdog/bcm2835_wdt.zig` to expose `maxTimeoutSeconds(...)`, `secondsToWatchdogTicks(...)`, `summarizeProbe(...)`, `summarizePlatformHandoff(...)`, `Bcm2835WdtLab.importBootloaderRunning(...)`, and `Bcm2835WdtLab.poweroff(...)`
- that same bcm2835 manifest-packet survey still requires the direct replay `zigux/tests/phase11_bcm2835_wdt.zig` and the verify helper `drivers/watchdog/bcm2835_wdt_verify.zig`, so current repo reality still keeps bcm2835 on a lifecycle-backed review packet rather than a note-only reminder
- `zigux/tests/phase11_dw_wdt_manifest.json` still keeps `phase11-dw-wdt-platform-registration-scaffold` at `starter_landed` and keeps `phase11-dw-wdt-live-platform-pm` at `ready_next`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` still keeps named-`tclk` acquisition, shared-clock fallback, optional APB clock, optional reset-control absence, imported-running registration handoff, and blocked-missing-timer-clock outcomes explicit before live platform registration
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` still says the next bounded follow-up is one acquisition-facing platform-registration scaffold without widening into live MMIO, IRQ, PM, or broader hardware-backed behavior
- `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md` still keeps DesignWare teardown and restart failure-mode coverage distinct from the narrower platform-registration scaffold packet

## Gap Statement

Current repo reality therefore does not yet show straightforward cross-driver lifecycle parity between `bcm2835_wdt` and `dw_wdt`.

The bcm2835 packet still proves direct watchdog lifecycle surfaces through helper, replay, and verify coverage, while the directly readable DesignWare packet still stops at acquisition-facing platform-registration scaffolding plus separate teardown and restart-failure notes.

That difference is acceptable inside Phase 11, but it must stay explicit so reminder surfaces do not overclaim that `dw_wdt` has already caught up to the bcm2835 lifecycle-backed packet.

## Next Bounded Same-Lane Step

- keep `bcm2835_wdt` parked unless its lifecycle-backed packet drifts
- keep `dw_wdt` on one acquisition-facing platform-registration scaffold or summary extension only
- do not claim cross-driver lifecycle parity is closed until the live DesignWare packet grows beyond the current registration-scaffold boundary
