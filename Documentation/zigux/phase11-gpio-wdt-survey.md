# Phase 11 GPIO Watchdog Survey

- `PHASE11_LANE_KEY=P11-L04`

This survey note now tracks the landed Phase 11 `gpio_wdt` starter anchored to `drivers/watchdog/gpio_wdt.c`.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig` models `hw_algo` parsing, heartbeat-margin validation, the narrow start, ping, stop, and disable transitions from the Linux GPIO watchdog driver, a small probe-time summary for startup and registration-facing bookkeeping, a tiny `descriptorPreflightSummary()` helper for the `devm_gpiod_get()` flag choice and probe ordering, a tiny `timeoutPropertyCheckpointSummary()` helper for the `hw_margin_ms` boundary and its fail-closed ordering before later handoffs, a tiny `platformDrvdataCheckpointSummary()` helper for the early `platform_set_drvdata()` ordering boundary before later GPIO and watchdog handoffs, a tiny `drvdataCheckpointSummary()` helper for the `watchdog_set_drvdata()` ordering boundary between timeout validation, registration handoff, and the first register-device request surface, a tiny nowayout-aware stop helper that separates watchdog-core policy blocking from hardware `always-running` behavior, a registration handoff summary, and a tiny `registerDeviceCallSummary()` helper for the first bounded `devm_watchdog_register_device()` request surface
- `zigux/tests/phase11_gpio_wdt.zig` keeps the toggle and level algorithms reviewable without claiming GPIO registration or hardware-backed execution, and now checks always-running startup, descriptor preflight ordering, timeout-property checkpoint ordering, `platform_set_drvdata()` ordering, `watchdog_set_drvdata()` checkpoint ordering, pre-registration bookkeeping, stop-request outcomes, registration handoff reporting, and the first bounded register-device request bookkeeping
- `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig` keeps the early `platform_set_drvdata()` ordering checkpoint honest as a focused local replay beside, not inside, the shared `phase11_build.zig` route
- `zigux/tests/phase11_build.zig` runs the starter and survey paths together so lane-local freshness drift shows up in one place while the focused platform-drvdata replay stays explicitly outside the shared Phase 11 route
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` now records the bounded validation posture for the landed starter, the platform drvdata checkpoint, the drvdata checkpoint, the register-device request surface, and the still-deferred kernel-facing follow-up

This cleanup packet now carries lane identity `P11-L04` so the live manifest, focused survey gate, and survey note all point at the same gpio watchdog review record.

This remains intentionally small. The lane still does not claim platform-driver registration, live GPIO descriptor lookup, `watchdog_set_drvdata()` execution, watchdog core registration, reboot hooks, module parameters beyond summary bookkeeping, live GPIO execution, teardown and failure-mode parity beyond the landed bounded starter checks, or hardware-backed validation beyond the landed matrix.

The next honest bounded step for this archived review packet is to keep the landed descriptor, timeout-property, platform-drvdata, drvdata, handoff, and register-device request summaries traceable while later same-family lanes decide whether teardown-facing parity or hardware-backed validation can move forward without claiming live GPIO or broader platform glue.
