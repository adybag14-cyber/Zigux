# Phase 11 BCM2835 Watchdog Teardown Note

This note records the bounded teardown and poweroff-ownership surface already present in the Zigux `bcm2835_wdt` packet.

## Status

- `PHASE11_BCM2835_WDT_TEARDOWN_STATUS=teardown_note_landed`
- lane scope: keep the current bcm2835 watchdog teardown story reviewable without widening into live platform remove, PM base plumbing, watchdog-core deregistration, or hardware-backed poweroff execution
- paired driver-local packet:
  - `drivers/watchdog/bcm2835_wdt.zig`
  - `zigux/tests/phase11_bcm2835_wdt.zig`
  - `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
  - `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
  - `zigux/tests/phase11_bcm2835_wdt_manifest.json`

## Teardown Ownership

The current bcm2835 watchdog packet already keeps one small teardown boundary explicit:

- `poweroffSummary()` is the bounded poweroff-path surface. It records the shared system-poweroff callback preconditions, the Raspberry Pi halt-partition request bits, and the short watchdog restart arming sequence without claiming a live callback install or board-backed shutdown path.
- `removeSummary()` is the bounded remove-time surface. It keeps watchdog teardown devm-managed and only clears the shared poweroff callback when `pm_power_off` still points at `bcm2835_power_off`.
- when the callback is absent, owned by another path, or the bcm2835 lane is not the active system-power-controller owner, the teardown packet leaves the shared callback in place instead of overclaiming cleanup authority.

## Review Rules

- treat this note as an ownership boundary, not as proof of live platform remove execution
- do not claim PM base release, watchdog-core deregistration, platform-driver remove ordering, or hardware-backed poweroff coverage from this note alone
- keep the current teardown packet tied to the same bounded evidence already tracked in the focused driver replay, survey note, validation matrix, and manifest
- if a later Phase 11 lane widens into live platform registration or PM base plumbing, update this note together with the bcm2835 survey and validation matrix so the teardown story stays truthful

## Next Blocked Step

The next honest bcm2835 follow-up remains blocked on an explicit hardware-validation plan for any wider platform-registration, PM-base, or shared poweroff-handler coordination work. This teardown note does not change that blocker.
