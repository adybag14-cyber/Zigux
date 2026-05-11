# Phase 11 BCM2835 Watchdog Teardown Note

This note records the bounded teardown and poweroff-ownership surface already present in the Zigux `bcm2835_wdt` packet.

## Status

- `PHASE11_BCM2835_WDT_TEARDOWN_STATUS=teardown_note_landed`
- archival packet identity remains `P11-L08` for traceability while the current bcm2835-only continuity note is tracked through `P11-Y02`
- lane scope: keep the current bcm2835 watchdog teardown story reviewable without widening into live platform remove, PM base plumbing, watchdog-core deregistration, or hardware-backed poweroff execution
- paired driver-local packet:
  - `drivers/watchdog/bcm2835_wdt.zig`
  - `drivers/watchdog/bcm2835_wdt_verify.zig`
  - `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
  - `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
  - `Documentation/zigux/phase11-driver-lane-sequencing.md`

## Teardown Ownership

The current bcm2835 watchdog packet already keeps one small teardown boundary explicit:

- `poweroffSummary()` is the bounded poweroff-path surface. It records the shared system-poweroff callback preconditions, the Raspberry Pi halt-partition request bits, and the short watchdog restart arming sequence without claiming a live callback install or board-backed shutdown path.
- `removeSummary()` is the bounded remove-time surface. It keeps watchdog teardown devm-managed and only clears the shared poweroff callback when `pm_power_off` still points at `bcm2835_power_off`.
- when the callback is absent, owned by another path, or the bcm2835 lane is not the active system-power-controller owner, the teardown packet leaves the shared callback in place instead of overclaiming cleanup authority.

## Review Rules

- treat this note as an ownership boundary, not as proof of live platform remove execution
- do not claim PM base release, watchdog-core deregistration, platform-driver remove ordering, or hardware-backed poweroff coverage from this note alone
- do not claim that the older bcm2835 survey note, manifest-backed survey packet, or packet-checker scaffolds are currently present on `master` unless those files are restored in the repo
- keep the current teardown packet tied to the same bounded evidence already tracked in the focused driver replay, the driver-local verifier, the validation matrix, and the driver-lane sequencing note
- if a later Phase 11 lane widens into live platform registration or PM base plumbing, update this note together with the bcm2835 validation matrix so the teardown story stays truthful

## Next Blocked Step

The next honest bcm2835 follow-up remains blocked on an explicit hardware-validation plan for any wider platform-registration, PM-base, or shared poweroff-handler coordination work. This teardown note does not change that blocker.
