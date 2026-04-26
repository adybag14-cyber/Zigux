# Phase 11 GPIO Watchdog Survey

This survey note now tracks the landed Phase 11 `gpio_wdt` starter anchored to `drivers/watchdog/gpio_wdt.c`.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig` models `hw_algo` parsing, heartbeat-margin validation, the narrow start, ping, stop, and disable transitions from the Linux GPIO watchdog driver, a small probe-time summary for startup and registration-facing bookkeeping, a tiny nowayout-aware stop helper that separates watchdog-core policy blocking from hardware `always-running` behavior, and a registration handoff summary
- `zigux/tests/phase11_gpio_wdt.zig` keeps the toggle and level algorithms reviewable without claiming GPIO registration or hardware-backed execution, and now checks always-running startup, pre-registration bookkeeping, stop-request outcomes, and registration handoff reporting
- `zigux/tests/phase11_build.zig` runs the starter and survey paths together so lane-local freshness drift shows up in one place

This remains intentionally small. The lane still does not claim platform-driver registration, GPIO descriptor acquisition, watchdog core registration, reboot hooks, module parameters beyond summary bookkeeping, or hardware validation coverage.

The next honest bounded step inside the same lane is to pick the first real registration surface and the minimum validation plan around it, while still avoiding live GPIO and platform glue until the handoff bookkeeping is no longer the blocker.
