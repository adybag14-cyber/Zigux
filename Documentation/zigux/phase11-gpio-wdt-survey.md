# Phase 11 GPIO Watchdog Survey

The Phase 11 `gpio_wdt` lane now has a first bounded Zigux starter anchored to `drivers/watchdog/gpio_wdt.c`.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig` models `hw_algo` parsing, heartbeat-margin validation, and the narrow start, ping, stop, and disable transitions from the Linux GPIO watchdog driver
- `zigux/tests/phase11_gpio_wdt.zig` keeps the toggle and level algorithms reviewable without claiming GPIO registration or hardware-backed execution
- `zigux/tests/phase11_build.zig` can run both the survey and the starter test path together

This remains intentionally small. The lane still does not claim platform-driver registration, GPIO descriptor acquisition, watchdog core registration, reboot hooks, module parameters, or hardware validation coverage.

The next honest bounded step inside the same lane is to widen the starter from pure state transitions into a slightly richer probe-time summary around `always-running` startup behavior and watchdog registration-facing bookkeeping, while still avoiding live GPIO and platform glue.
