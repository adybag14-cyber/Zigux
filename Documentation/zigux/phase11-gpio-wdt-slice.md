# Phase 11 GPIO Watchdog Slice

This bounded Phase 11 slice adds the first Zigux `gpio_wdt` starter anchored to `drivers/watchdog/gpio_wdt.c`.

The starter stays intentionally narrow:

- parses the Linux driver's `hw_algo` property surface for the `toggle` and `level` modes
- enforces the same bounded hardware heartbeat margin window used by the C driver
- models the in-memory start, ping, stop, and disable transitions for both hardware algorithms
- preserves the `always-running` stop behavior so the lab model does not pretend the watchdog can be disabled when the platform contract forbids it
- reports a probe-time summary for requested GPIO line mode, `always-running` startup behavior, `nowayout`, timeout init, parent linkage, and stop-on-reboot bookkeeping before watchdog registration
- adds a tiny `descriptorPreflightSummary()` helper so the starter records the exact `devm_gpiod_get()` flag choice and the fact that descriptor lookup still sits before timeout parsing, `always-running` bookkeeping, and the later registration handoff without claiming live GPIO acquisition
- adds a tiny `timeoutPropertyCheckpointSummary()` helper so the starter records that `hw_margin_ms` stays required and bounds-checked after descriptor lookup but before `always-running` bookkeeping, `watchdog_set_drvdata()`, and the registration-facing handoff without claiming a live property read
- distinguishes watchdog-core `nowayout` stop blocking from the driver's own `always-running` hardware behavior so stop-path review does not blur policy gating with hardware gating
- adds a tiny registration-facing handoff summary so the starter records what startup state, stop policy, timeout init, and reboot bookkeeping reach `devm_watchdog_register_device()` without claiming the registration call itself
- adds a tiny `registerDeviceCallSummary()` helper so the starter records the first bounded `devm_watchdog_register_device()` request surface, including descriptor readiness, `watchdog_set_drvdata()` completion, timeout propagation, and the still-blocked live GPIO, platform-registration, and reboot-glue boundaries without claiming execution
- stays under the shared `zigux/tests/phase11_build.zig` review gate so the starter and survey lane remain aligned

This slice does not claim platform-driver registration, live GPIO descriptor lookup, watchdog-core registration, reboot integration beyond summary bookkeeping, module parameter wiring beyond `nowayout` bookkeeping, teardown and failure-mode parity beyond the bounded starter checks, or hardware validation coverage yet.

The next honest bounded step for this archived review packet is to keep the landed descriptor, timeout-property, handoff, and register-device request summaries traceable while later same-family lanes decide whether teardown-facing parity or hardware-backed validation can move forward without claiming live GPIO or broader platform glue.
