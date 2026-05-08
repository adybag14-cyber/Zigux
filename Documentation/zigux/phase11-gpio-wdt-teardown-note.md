# Phase 11 GPIO Watchdog Teardown Note

This note captures the bounded teardown ownership that is already reviewable in the Zigux `gpio_wdt` starter anchored to `drivers/watchdog/gpio_wdt.c`.

The current driver-local teardown surface is intentionally small and host-free:

- `requestStop()` owns the stop-policy split by separating watchdog-core `nowayout` blocking from the hardware `always-running` branch and the normal stoppable branch without claiming live watchdog-core callbacks.
- `stop()` owns the bounded line-state transition by preserving heartbeat output for `always-running` hardware, disabling the line for stoppable toggle hardware, and keeping the level-mode disable state explicit.
- `teardownSummary()` owns the teardown-facing handoff by recording the running and line-mode state before teardown, the stop disposition selected during teardown, and the post-teardown line ownership that remains reviewable after the bounded stop path.

## Teardown Ownership

| boundary | current Zigux owner | what stays reviewable now | still out of scope |
| --- | --- | --- | --- |
| stop-policy boundary | `requestStop()` | `nowayout` blocking versus allowed stop requests, whether the driver stop path is invoked, and whether hardware stays running because of the `always-running` contract | live watchdog-core stop callbacks, module-parameter plumbing, and reboot notifier ordering |
| stop transition | `stop()` | toggle disable ownership, level-mode disable state, preserved running state for `always-running` hardware, and bounded post-stop GPIO line posture | live GPIO writes, hardware pulse timing, and platform-backed stop execution |
| teardown handoff | `teardownSummary()` | pre-teardown running state, stop disposition, post-teardown line ownership, disable-count bookkeeping, and whether teardown leaves the watchdog stopped, running, or blocked by `nowayout` | remove hooks, shutdown ordering, reboot-integrated teardown, and hardware-backed teardown behavior |

## Review Guardrails

- keep this note tied only to `drivers/watchdog/gpio_wdt.zig` and its directly coupled teardown checks in `zigux/tests/phase11_gpio_wdt.zig`
- do not treat this note as evidence of live GPIO descriptor lookup, `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution, watchdog-core registration, reboot integration, or hardware-backed validation
- when `requestStop()`, `stop()`, or `teardownSummary()` change, update this note together with `Documentation/zigux/phase11-gpio-wdt-survey.md` and `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` so the lane keeps one honest teardown story