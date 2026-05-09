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
- adds a tiny `platformDrvdataCheckpointSummary()` helper so the starter records that probe-time allocation is followed by `platform_set_drvdata()` before `hw_algo` parsing, descriptor lookup, timeout-property handling, and the later `watchdog_set_drvdata()` handoff without claiming a live platform probe
- adds a tiny `drvdataCheckpointSummary()` helper so the starter records that descriptor lookup and the required `hw_margin_ms` property still precede `watchdog_set_drvdata()`, and that the drvdata handoff itself stays required before both the registration-facing handoff and the first `devm_watchdog_register_device()` request surface without claiming execution
- adds a tiny `rebootGlueCheckpointSummary()` helper so the starter records the bounded `watchdog_stop_on_reboot()` ordering around `nowayout`, pre-registration startup, and the first `devm_watchdog_register_device()` request surface without claiming live reboot notifier registration
- adds a tiny `failureModeCheckpointSummary()` helper so the starter records invalid `hw_algo` and timeout rejection together with the bounded `nowayout` stop-preservation rules before any live GPIO, `watchdog_set_drvdata()`, or platform-registration execution
- distinguishes watchdog-core `nowayout` stop blocking from the driver's own `always-running` hardware behavior so stop-path review does not blur policy gating with hardware gating
- adds a tiny registration-facing handoff summary so the starter records what startup state, stop policy, timeout init, and reboot bookkeeping reach `devm_watchdog_register_device()` without claiming the registration call itself
- adds a tiny `registerDeviceCallSummary()` helper so the starter records the first bounded `devm_watchdog_register_device()` request surface, including descriptor readiness, `watchdog_set_drvdata()` completion, timeout propagation, and the still-blocked live GPIO, platform-registration, and reboot-glue boundaries without claiming execution
- keeps the bounded teardown handoff explicit through the landed teardown note and the starter's `teardownSummary()` surface instead of implying remove-hook or reboot-backed shutdown ownership
- stays under the shared `zigux/tests/phase11_build.zig` review gate so the starter and survey lane remain aligned

This slice does not claim platform-driver registration, live GPIO descriptor lookup, `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution, watchdog-core registration, reboot integration beyond summary bookkeeping, module parameter wiring beyond `nowayout` bookkeeping, teardown and failure-mode parity beyond the landed bounded teardown note, the bounded `failureModeCheckpointSummary()` surface, and the rest of the starter checks, or hardware validation coverage yet.

The next honest bounded step for this archived review packet is to keep the landed descriptor, timeout-property, platform-drvdata, drvdata, reboot-glue, failure-mode, handoff, register-device request, and bounded teardown summaries traceable while later same-family lanes decide whether broader failure-mode parity or hardware-backed validation can move forward without claiming live GPIO or broader platform glue.
