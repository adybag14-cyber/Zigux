# Phase 11 GPIO Watchdog Survey

This survey note now tracks the landed Phase 11 `gpio_wdt` starter anchored to `drivers/watchdog/gpio_wdt.c`.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig` models `hw_algo` parsing, heartbeat-margin validation, the narrow start, ping, stop, and disable transitions from the Linux GPIO watchdog driver, a small probe-time summary for startup and registration-facing bookkeeping, a tiny nowayout-aware stop helper that separates watchdog-core policy blocking from hardware `always-running` behavior, and a registration handoff summary
- `drivers/watchdog/gpio_wdt.zig` also records the first chosen registration surface and validation focus plus a tiny `registerDeviceCallSummary()` helper, so the lane now exposes the exact watchdog metadata, timeout, parent, `nowayout`, and stop-on-reboot state that would reach the first bounded `devm_watchdog_register_device()` request without claiming a live call
- `zigux/tests/phase11_gpio_wdt.zig` keeps the toggle and level algorithms reviewable without claiming GPIO registration or hardware-backed execution, and now checks always-running startup, pre-registration bookkeeping, stop-request outcomes, registration handoff reporting, the metadata-only registration plan, and the first bounded register-device request summary
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` now records the shared replay surface and the first bounded register-device call evidence so the lane's validation posture does not hide inside the starter, the registration-plan follow-up, or the tests alone
- `zigux/tests/phase11_build.zig` runs the starter and survey paths together so lane-local freshness drift shows up in one place

This remains intentionally small. The lane still does not claim platform-driver registration, GPIO descriptor acquisition, watchdog core registration, reboot hooks, module parameters beyond summary bookkeeping, or live hardware validation coverage.

The next honest bounded step inside the same lane is now a tiny descriptor-backed or probe-order preflight that stays immediately adjacent to the new register-device request summary, while still avoiding live GPIO, reboot glue, and broader platform-driver behavior until those boundaries have their own focused validation packet.
