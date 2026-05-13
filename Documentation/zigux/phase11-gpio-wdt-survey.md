# Phase 11 GPIO Watchdog Survey

`PHASE11_LANE_KEY=P11-L04`

This survey note tracks the landed Phase 11 `gpio_wdt` starter anchored to `drivers/watchdog/gpio_wdt.c` on current `master`.

## Live Repo State

- `drivers/watchdog/gpio_wdt.zig` models `hw_algo` parsing, heartbeat-margin validation, the narrow start, ping, stop, and disable transitions from the Linux GPIO watchdog driver, a small probe-time summary for startup and registration-facing bookkeeping, a tiny `descriptorPreflightSummary()` helper for the `devm_gpiod_get()` flag choice and probe ordering, a tiny `timeoutPropertyCheckpointSummary()` helper for the `hw_margin_ms` boundary and its fail-closed ordering before later handoffs, a tiny `platformDrvdataCheckpointSummary()` helper for the early `platform_set_drvdata()` ordering boundary before later GPIO and watchdog handoffs, a tiny `drvdataCheckpointSummary()` helper for the `watchdog_set_drvdata()` ordering boundary between timeout validation, registration handoff, and the first register-device request surface, a tiny nowayout-aware stop helper that separates watchdog-core policy blocking from hardware `always-running` behavior, a registration handoff summary, a tiny `registerDeviceCallSummary()` helper for the first bounded `devm_watchdog_register_device()` request surface, and a bounded `teardownSummary()` surface that keeps teardown-facing stop outcomes explicit without claiming remove hooks or live shutdown glue.
- `zigux/tests/phase11_gpio_wdt.zig` keeps the toggle and level algorithms reviewable without claiming GPIO registration or hardware-backed execution, and checks always-running startup, descriptor preflight ordering, timeout-property checkpoint ordering, `platform_set_drvdata()` ordering, `watchdog_set_drvdata()` checkpoint ordering, pre-registration bookkeeping, stop-request outcomes, teardown outcomes, registration handoff reporting, and the first bounded register-device request bookkeeping.
- `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig` is the dedicated focused `platform_set_drvdata()` replay for this packet. It keeps the early platform-drvdata checkpoint honest beside the shared starter and survey route instead of leaving that ordering surface implied only by the driver summary and matrix notes.
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md` keeps the bounded teardown story explicit by separating stop-policy ownership, stop-transition ownership, and teardown handoff ownership without overclaiming live GPIO, remove hooks, or reboot-backed teardown.
- `zigux/tests/phase11_build.zig` still runs the starter and survey paths together so lane-local freshness drift shows up in one place, while the dedicated `phase11_gpio_wdt_platform_drvdata.zig` replay remains a focused local checkpoint rather than part of the shared Phase 11 route.
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` records the bounded validation posture for the landed starter, the dedicated platform-drvdata replay, the drvdata checkpoint, the register-device request surface, the bounded teardown note, and the still-deferred kernel-facing follow-up.

This review packet now carries lane identity `P11-L04` so the live manifest, focused survey gate, and survey note all point at the same gpio watchdog record.

## Boundaries

This remains intentionally small. The lane still does not claim platform-driver registration, live GPIO descriptor lookup, `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution, watchdog core registration, reboot hooks, module parameters beyond summary bookkeeping, live GPIO execution, teardown and failure-mode parity beyond the landed bounded starter checks and teardown note, or hardware-backed validation beyond the landed matrix.

The next honest bounded step for this archived review packet is to keep the landed descriptor, timeout-property, platform-drvdata, drvdata, teardown, handoff, and register-device request surfaces traceable while later same-family lanes decide whether failure-mode parity or broader hardware-backed validation can move forward without claiming live GPIO or wider platform glue.
