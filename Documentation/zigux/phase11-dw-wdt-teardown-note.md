# Phase 11 DesignWare Watchdog Teardown Note

This note keeps the bounded teardown ownership packet for `drivers/watchdog/dw_wdt.zig` explicit.

## Scope

The current Zigux `dw_wdt` starter only claims teardown-side bookkeeping that is already modeled inside:

- `DwWdtLab.stop()`
- `DwWdtLab.armRestart()`
- `DwWdtLab.remove()`
- `DwWdtLab.summarizeTeardownLifecycle()`
- `DwWdtLab.summarizeRemoveHandoff()`
- `zigux/tests/phase11_dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`

This note does not widen the lane into platform-driver registration, PM callbacks, debugfs implementation, live reset pulses, or hardware-backed remove validation.

## Current Ownership Split

- `stop()` owns the bounded stop-time state transition only. When reset control is absent, the helper keeps the running marker and any pending interrupt visible instead of pretending the hardware actually stopped.
- `summarizeTeardownLifecycle()` owns the teardown-side review packet for stop and restart. It keeps reset-backed stop, non-stoppable stop fallout, reset-mode restart forcing, restart-from-stopped enablement, and interrupt-status clearing reviewable without claiming reboot-side effects.
- `remove()` owns the bounded remove-time state transition only. With reset control available it clears the enable bit and pending interrupt state; without reset control it preserves the running marker and any pending interrupt that the helper cannot honestly clear.
- `summarizeRemoveHandoff()` owns the remove-time teardown handoff packet. It keeps debugfs clear intent, unregister-device ordering, reset-control-backed disable, and non-reset remove fallout explicit before any live remove callback or PM teardown exists.
- `zigux/tests/phase11_dw_wdt_remove_idle_split.zig` owns the special idle-remove split. That replay keeps pending interrupts distinct when remove happens before the watchdog is running, including the difference between reset-backed interrupt clearing and non-reset preserved pending state.

## Review Rules

- Treat this note as the driver-local teardown contract for the current `dw_wdt` starter.
- Keep this note aligned with the slice and validation matrix whenever stop, restart, remove, or idle-remove ownership semantics change.
- Do not claim platform remove callbacks, PM teardown ordering, debugfs implementation, or hardware-backed teardown behavior here until the driver and tests actually grow those surfaces.
