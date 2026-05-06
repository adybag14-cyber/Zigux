# Phase 11 GPIO Watchdog Survey

- `PHASE11_LANE_KEY=P11-Y07`

This survey note now tracks the landed Phase 11 `gpio_wdt` starter anchored to `drivers/watchdog/gpio_wdt.c`.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig` models `hw_algo` parsing, heartbeat-margin validation, the narrow start, ping, stop, and disable transitions from the Linux GPIO watchdog driver, a small probe-time summary for startup and registration-facing bookkeeping, a tiny `descriptorPreflightSummary()` helper for the `devm_gpiod_get()` flag choice and probe ordering, a tiny `timeoutPropertyCheckpointSummary()` helper for the `hw_margin_ms` boundary and its fail-closed ordering before later handoffs, a tiny nowayout-aware stop helper that separates watchdog-core policy blocking from hardware `always-running` behavior, and a registration handoff summary
- `zigux/tests/phase11_gpio_wdt.zig` keeps the toggle and level algorithms reviewable without claiming GPIO registration or hardware-backed execution, and now checks always-running startup, descriptor preflight ordering, timeout-property checkpoint ordering, pre-registration bookkeeping, stop-request outcomes, and registration handoff reporting
- `zigux/tests/phase11_build.zig` runs the starter and survey paths together so lane-local freshness drift shows up in one place
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` now records the bounded validation posture for the landed starter and the still-deferred kernel-facing follow-up

This remains intentionally small. The lane still does not claim platform-driver registration, live GPIO descriptor lookup, watchdog core registration, reboot hooks, module parameters beyond summary bookkeeping, live GPIO execution, teardown and failure-mode parity beyond the bounded starter checks, or hardware-backed validation beyond the landed matrix.

The next honest bounded step inside the same lane is to land one registration-facing scaffold note or replay that ties `devm_gpiod_get()`, `watchdog_set_drvdata()`, and `devm_watchdog_register_device()` to the remaining teardown and failure-mode parity plus hardware-backed validation work, while still avoiding live GPIO and platform glue claims.
