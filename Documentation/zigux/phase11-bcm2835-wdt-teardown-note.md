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
  - `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
  - `zigux/tests/phase11_bcm2835_wdt_manifest.json`
  - `zigux/tests/phase11_bcm2835_wdt_survey.zig`
  - `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
  - `Documentation/zigux/phase11-driver-lane-sequencing.md`

## Teardown Ownership

The current bcm2835 watchdog packet already keeps one small teardown boundary explicit:

- `registrationOutcomeSummary()` owns the success-versus-failure split around `devm_watchdog_register_device()` intent, probe-error return intent, and whether the shared `pm_power_off` callback can be claimed or must stay untouched.
- `ownershipMatrixSummary()` keeps the four current callback-ownership paths aligned in one packet by replaying `claimed_poweroff_handler`, `conflicting_poweroff_handler`, `failed_registration`, and `not_system_power_controller` through `registrationOutcomeSummary()`, `poweroffSummary()`, and `removeSummary()`.
- `poweroffSummary()` is the bounded poweroff-path surface. It records the shared system-poweroff callback preconditions, the Raspberry Pi halt-partition request bits, and the short watchdog restart arming sequence without claiming a live callback install or board-backed shutdown path.
- `removeSummary()` and `removeAfterRegistrationSummary()` own the remove-side cleanup by recording that watchdog teardown stays devm-managed while the explicit remove path clears the shared poweroff callback only when `pm_power_off` still belongs to `bcm2835_power_off`, leaving conflicting or unrelated ownership in place.

| boundary | current Zigux owner | what stays reviewable now | still out of scope |
| --- | --- | --- | --- |
| registration outcome boundary | `registrationOutcomeSummary()` | register-device intent, success-versus-failure bookkeeping, probe-error return intent, claimed-versus-conflicting `pm_power_off` ownership, and whether the callback remains present after probe | live watchdog-core registration, platform probe return wiring, and hardware-backed rollback |
| ownership matrix paths | `ownershipMatrixSummary()` | the `claimed_poweroff_handler`, `conflicting_poweroff_handler`, `failed_registration`, and `not_system_power_controller` paths tied across registration outcome, poweroff readiness, halt-partition intent, restart arming, and remove-side callback cleanup | live callback installation, platform remove ordering, and hardware-backed rollback |
| poweroff handoff | `poweroffSummary()` | callback ownership preconditions, ready-versus-blocked path selection, halt-partition request bits, and short restart-arming intent | live poweroff callback installation, PM base wiring, and hardware-backed shutdown execution |
| remove handoff | `removeSummary()` and `removeAfterRegistrationSummary()` | devm-managed teardown posture, callback-clear request selection, and preserve-versus-clear ownership outcomes after registration | live platform remove callbacks, reboot-time ordering, and hardware-backed poweroff release |

## Review Rules

- treat this note as an ownership boundary, not as proof of live platform remove execution
- do not claim PM base release, watchdog-core deregistration, platform-driver remove ordering, or hardware-backed poweroff coverage from this note alone
- keep this note aligned with `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, and `scripts/zigux/check-phase11-bcm2835-wdt-packet.py` so the teardown story matches the live bcm2835 review packet on `master`
- when `registrationOutcomeSummary()`, `ownershipMatrixSummary()`, `poweroffSummary()`, `removeSummary()`, or `removeAfterRegistrationSummary()` change, update this note together with `Documentation/zigux/phase11-bcm2835-wdt-slice.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, and `zigux/tests/phase11_bcm2835_wdt_survey.zig` so the lane keeps one honest teardown story
- if a later Phase 11 lane widens into live platform registration or PM base plumbing, update this note together with the bcm2835 validation matrix so the teardown story stays truthful

## Next Blocked Step

The next honest bcm2835 follow-up remains blocked on an explicit hardware-validation plan for any wider platform-registration, PM-base, or shared poweroff-handler coordination work. This teardown note does not change that blocker.
