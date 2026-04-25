# Phase 11 BCM2835 Watchdog Survey

This survey note tracks the Phase 11 gap around `drivers/watchdog/bcm2835_wdt.c` after re-reading `master` `b6c2dc8bb6869db064b14df4f94b7326eb95b9eb`.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig` already provides one bounded Phase 11 watchdog starter, so the tranche has a real foothold
- `drivers/watchdog/bcm2835_wdt.zig` already ships the bounded bcm2835 starter for timeout tick encoding, running-bit detection, bounded start and stop register transitions, restart intent, and halt-partition bookkeeping
- `zigux/tests/phase11_bcm2835_wdt.zig` and `Documentation/zigux/phase11-bcm2835-wdt-slice.md` keep that starter reviewable without claiming platform registration or hardware-backed execution
- `zigux/tests/phase11_bcm2835_wdt_survey.zig` and `zigux/tests/phase11_bcm2835_wdt_manifest.json` still track the remaining bcm2835_wdt gap against the roadmap so the lane does not overclaim progress
- `zigux/tests/phase11_build.zig` runs the gpio starter checks, the bcm2835 starter checks, and the bcm2835 survey check together so Phase 11 watchdog drift is visible in one place

This lane still does not claim watchdog-core registration, PM base wiring, restart-priority setup, poweroff-handler coordination, module-parameter parity, or hardware validation coverage.

The next honest bounded step inside the same lane is to add a tiny probe-time summary and registration-facing bookkeeping helper before any platform or MMIO-backed behavior.
