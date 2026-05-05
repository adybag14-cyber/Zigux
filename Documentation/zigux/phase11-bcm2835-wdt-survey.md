# Phase 11 BCM2835 Watchdog Survey

This survey note keeps the archived `P11-L08` bcm2835 watchdog packet traceable after re-reading the live bcm2835 watchdog packet on `master`. Current scheduled bcm2835 watchdog continuity for this archived packet stays with `P11-L08`, which keeps it separate from the unrelated `P11-L10` DesignWare watchdog lane.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig` already provides one bounded Phase 11 watchdog starter, so the tranche has a real foothold
- `drivers/watchdog/bcm2835_wdt.zig` already ships the bounded bcm2835 starter for timeout tick encoding, running-bit detection, bounded start and stop register transitions, restart intent, halt-partition bookkeeping, a tiny probe-time summary, a small registration-facing handoff or poweroff ownership summary, an explicit get-timeleft helper, and a tiny remove-time ownership summary
- `zigux/tests/phase11_bcm2835_wdt.zig` and `Documentation/zigux/phase11-bcm2835-wdt-slice.md` keep that starter reviewable without claiming platform registration or hardware-backed execution
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` now records the bounded validation posture and keeps the still-blocked platform-registration and PM-base work explicit
- the bounded starter now includes an explicit get-timeleft helper so the `WDOG_TICKS_TO_SECS` parity is reviewable as its own driver-local surface
- `zigux/tests/phase11_bcm2835_wdt_survey.zig` and `zigux/tests/phase11_bcm2835_wdt_manifest.json` still track the remaining bcm2835_wdt gap against the roadmap so the lane does not overclaim progress, and the focused survey gate now reads the live driver, dedicated test, and shared Phase 11 build packet directly so stale manifest booleans cannot overclaim review coverage
- `zigux/tests/phase11_build.zig` runs the gpio starter checks, the bcm2835 starter checks, and the bcm2835 survey check together so Phase 11 watchdog drift is visible in one place

This lane still does not claim watchdog-core registration, PM base wiring, live remove-time poweroff-handler release behavior, or hardware validation coverage beyond the bounded matrix.

The next honest bounded step inside current `P11-L08` continuity is to add a tiny platform-facing handoff note that builds on the landed hardware-validation matrix before any platform registration, PM base plumbing, or live poweroff-handler coordination.
