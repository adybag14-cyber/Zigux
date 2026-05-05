# Phase 11 BCM2835 Watchdog Slice

This bounded Phase 11 slice adds the first Zigux `bcm2835_wdt` starter anchored to `drivers/watchdog/bcm2835_wdt.c`.

The starter stays intentionally narrow:

- validates the watchdog timeout window exposed by the Linux driver
- models the in-memory register image for `PM_RSTC`, `PM_RSTS`, and `PM_WDOG`
- mirrors the bounded `is_running`, `start`, `stop`, `get_timeleft`, and restart behavior through register-image transitions only
- adds a tiny probe-time summary for bootloader-carried running status, watchdog-core timeout and nowayout initialization, restart priority, stop-on-reboot setup, watchdog parent linkage, and system-power-controller eligibility
- adds a tiny registration-facing handoff summary for watchdog registration intent plus poweroff-handler claim-vs-conflict outcomes
- adds a tiny remove-time ownership summary for clearing the shared poweroff handler only when the bcm2835 lane currently owns it
- preserves the Raspberry Pi halt-partition state in the lab snapshot without claiming full poweroff plumbing

This slice does not claim platform-driver registration, watchdog-core registration, MMIO access, delayed restart behavior, module parameter wiring beyond bookkeeping, live remove-time poweroff-handler release logic, or live poweroff integration yet.

The current hardware-validation matrix now records that bounded validation posture in one place.

The next honest bounded step inside the same Phase 11 lane is to add a tiny platform-facing handoff note that builds on the landed hardware-validation matrix before any platform registration, PM base plumbing, or live poweroff-handler work.
