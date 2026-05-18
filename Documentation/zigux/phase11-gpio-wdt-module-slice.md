# Phase 11 GPIO Watchdog Module Slice

This bounded Phase 11 module slice keeps the archived `P11-L04` gpio watchdog review packet truthful on current `master`.
## Review Packet

The `gpio_wdt_lab` starter remains intentionally narrow and review-first:
- `descriptorPreflightSummary()` records the `devm_gpiod_get()` flag choice and the probe ordering boundary without claiming live descriptor acquisition.
- `timeoutPropertyCheckpointSummary()` keeps the required `hw_margin_ms` boundary explicit before later watchdog handoffs.
- `platformDrvdataCheckpointSummary()` keeps the early `platform_set_drvdata()` ordering explicit before GPIO lookup and later watchdog bookkeeping.
- `registerDeviceCallSummary()` keeps the first bounded `devm_watchdog_register_device()` request surface visible without claiming live watchdog-core registration.
The same review packet also keeps teardown and failure-mode parity explicit in bounded form. The current starter records teardown-facing stop outcomes, the split between watchdog-core policy and hardware `always-running` behavior, and the still-blocked `watchdog_set_drvdata()` checkpoint, reboot-glue checkpoint, live GPIO, remove-hook, reboot-backed teardown execution, and hardware-backed validation work.
## Boundaries

This module slice does not claim live GPIO descriptor acquisition, a code-backed `watchdog_set_drvdata()` checkpoint, live `watchdog_set_drvdata()` execution, live `devm_watchdog_register_device()` execution, a code-backed `watchdog_stop_on_reboot()` checkpoint, platform-driver registration, live reboot-hook registration, or hardware-backed validation yet.

The next honest bounded step remains one equally small gpio watchdog review-surface or validation-truthfulness repair inside the same packet rather than new runtime behavior.
