# Phase 11 GPIO Watchdog Slice

This bounded Phase 11 slice adds the first Zigux `gpio_wdt` starter anchored to `drivers/watchdog/gpio_wdt.c`.

The starter stays intentionally narrow:

- parses the Linux driver's `hw_algo` property surface for the `toggle` and `level` modes
- enforces the same bounded hardware heartbeat margin window used by the C driver
- models the in-memory start, ping, stop, and disable transitions for both hardware algorithms
- preserves the `always-running` stop behavior so the lab model does not pretend the watchdog can be disabled when the platform contract forbids it

This slice does not claim platform-driver registration, GPIO descriptor lookup, watchdog-core registration, reboot integration, module parameter wiring, or real hardware validation yet.

The next honest bounded step inside the same Phase 11 lane is to add a tiny probe-time summary around startup state and registration-facing bookkeeping before any live GPIO or broader watchdog integration work.
