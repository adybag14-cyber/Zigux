# Phase 11 BCM2835 Watchdog Teardown Note

This note captures the bounded teardown ownership that is already reviewable in the Zigux `bcm2835_wdt` starter anchored to `drivers/watchdog/bcm2835_wdt.c`.

The current driver-local teardown surface is intentionally small and host-free:

- `registrationOutcomeSummary()` owns the success-versus-failure split around `devm_watchdog_register_device()` intent, probe-error return intent, and whether the shared `pm_power_off` callback can be claimed or must stay untouched.
- `ownershipMatrixSummary()` keeps the four current callback-ownership paths aligned in one packet by replaying `claimed_poweroff_handler`, `conflicting_poweroff_handler`, `failed_registration`, and `not_system_power_controller` through `registrationOutcomeSummary()`, `poweroffSummary()`, and `removeSummary()`.
- `poweroffSummary()` owns the callback-backed poweroff handoff by separating the ready path from the blocked and conflicting paths while keeping the Raspberry Pi halt-partition request bits and short restart-arming sequence reviewable only when the driver still owns the callback.
- `removeSummary()` and `removeAfterRegistrationSummary()` own the remove-side cleanup by recording that watchdog teardown stays devm-managed while the explicit remove path clears the shared poweroff callback only when `pm_power_off` still belongs to `bcm2835_power_off`, leaving conflicting or unrelated ownership in place.

## Teardown Ownership

| boundary | current Zigux owner | what stays reviewable now | still out of scope |
| --- | --- | --- | --- |
| registration outcome boundary | `registrationOutcomeSummary()` | register-device intent, success-versus-failure bookkeeping, probe-error return intent, claimed-versus-conflicting `pm_power_off` ownership, and whether the callback remains present after probe | live watchdog-core registration, platform probe return wiring, and hardware-backed rollback |
| ownership matrix paths | `ownershipMatrixSummary()` | the `claimed_poweroff_handler`, `conflicting_poweroff_handler`, `failed_registration`, and `not_system_power_controller` paths tied across registration outcome, poweroff readiness, halt-partition intent, restart arming, and remove-side callback cleanup | live callback installation, platform remove ordering, and hardware-backed rollback |
| poweroff handoff | `poweroffSummary()` | callback ownership preconditions, ready-versus-blocked path selection, halt-partition request bits, and short restart-arming intent | live poweroff callback installation, PM base wiring, and hardware-backed shutdown execution |
| remove handoff | `removeSummary()` and `removeAfterRegistrationSummary()` | devm-managed teardown posture, callback-clear request selection, and preserve-versus-clear ownership outcomes after registration | live platform remove callbacks, reboot-time ordering, and hardware-backed poweroff release |

## Review Guardrails

- keep this note tied only to `drivers/watchdog/bcm2835_wdt.zig` and its directly coupled teardown and poweroff ownership checks in `zigux/tests/phase11_bcm2835_wdt.zig`
- do not treat this note as evidence of live platform registration, PM base acquisition, shared poweroff callback installation, or hardware-backed poweroff execution
- when `registrationOutcomeSummary()`, `ownershipMatrixSummary()`, `poweroffSummary()`, `removeSummary()`, or `removeAfterRegistrationSummary()` change, update this note together with `Documentation/zigux/phase11-bcm2835-wdt-slice.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, and `zigux/tests/phase11_bcm2835_wdt_survey.zig` so the lane keeps one honest teardown story
