# Phase 11 BCM2835 Watchdog Survey

This survey note tracks the current Phase 11 gap around `drivers/watchdog/bcm2835_wdt.c`.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig` already provides one bounded Phase 11 watchdog starter, so the tranche has a real foothold
- `zigux/tests/phase11_bcm2835_wdt_survey.zig` and `zigux/tests/phase11_bcm2835_wdt_manifest.json` now record the `bcm2835_wdt` gap against the roadmap without pretending a second watchdog starter has landed
- `zigux/tests/phase11_build.zig` runs the gpio starter checks and the bcm2835 survey check together so Phase 11 watchdog drift is visible in one place

This lane still does not claim `drivers/watchdog/bcm2835_wdt.zig`, dedicated bcm2835 driver tests, watchdog-core registration, PM base wiring, restart and poweroff integration, module-parameter parity, or hardware validation coverage.

The next honest bounded step inside the same lane is to add the first narrow `drivers/watchdog/bcm2835_wdt.zig` starter for timeout tick encoding, running-bit detection, and bounded restart or poweroff intent bookkeeping before any platform or MMIO-backed behavior.
