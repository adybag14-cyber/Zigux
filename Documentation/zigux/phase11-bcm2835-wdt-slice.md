# Phase 11 BCM2835 Watchdog Slice

This bounded Phase 11 slice adds the first Zigux `bcm2835_wdt` starter anchored to `drivers/watchdog/bcm2835_wdt.c`.

The starter stays intentionally narrow:

- validates the watchdog timeout window exposed by the Linux driver
- models the in-memory register image for `PM_RSTC`, `PM_RSTS`, and `PM_WDOG`
- mirrors the bounded `is_running`, `start`, `stop`, `get_timeleft`, and restart behavior through register-image transitions only
- preserves the Raspberry Pi halt-partition state in the lab snapshot without claiming full poweroff plumbing

This slice does not claim platform-driver registration, watchdog-core registration, MMIO access, delayed restart behavior, module parameter wiring, or live poweroff integration yet.

The next honest bounded step inside the same Phase 11 lane is to add a tiny probe-time summary and registration-facing bookkeeping helper before any platform registration or poweroff-handler work.
