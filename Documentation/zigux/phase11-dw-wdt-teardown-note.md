# Phase 11 DesignWare Watchdog Teardown Note

This note captures the bounded teardown ownership that is already reviewable in the Zigux `dw_wdt` starter anchored to `drivers/watchdog/dw_wdt.c`.

The current driver-local teardown surface is intentionally small and host-free:
- `stop()` owns the reset-control split by clearing the enable bit, current count, and pending interrupt state only when reset control exists, while preserving continued-heartbeat semantics when the hardware is non-stoppable.
- `teardownSummary()` owns the stop-backed handoff by separating the idle no-op, reset-controlled stop, and continued-heartbeat outcomes while keeping timeout and response-mode context reviewable.
- `removeSummary()` owns the unregister-side cleanup by recording debugfs-clear intent, unregister-device intent, idle remove-time no-fabricated-heartbeat readback, reset-assert intent, reset-backed quiesce when reset control exists, and whether hardware remains running after remove when reset control is unavailable.
- `platformRegistrationScaffoldSummary()` owns the non-executing shutdown-side scaffold by keeping `module_platform_driver`, `dw_wdt_drv_remove`, and `dw_wdt_drv_shutdown` explicit beside the existing register-device ordering proof while the lane still blocks on live platform registration.

## Teardown Ownership

| boundary | current Zigux owner | what stays reviewable now | still out of scope |
| --- | --- | --- | --- |
| stop boundary | `stop()` | reset-control-backed disable, current-count clear, interrupt clear, and preserved running state when the DesignWare instance is non-stoppable | reset-controller acquisition, live MMIO writes, and watchdog-core stop side effects |
| teardown handoff | `teardownSummary()` | idle no-op versus active-stop outcome selection, stop-invocation bookkeeping, enable-bit clear state, interrupt-clear state, and hardware-running-after-teardown reporting | reboot notifier ordering, hardware-backed shutdown timing, and interrupt delivery |
| remove handoff | `removeSummary()` | debugfs-clear intent, unregister-device intent, idle remove-time no-fabricated-heartbeat readback, reset-assert request, reset-backed quiesce when reset control exists, and running-versus-quiesced remove outcomes | actual platform remove callbacks, debugfs teardown execution, and hardware-backed reset-line behavior |
| shutdown scaffold handoff | `platformRegistrationScaffoldSummary()` | `module_platform_driver`, `dw_wdt_drv_remove`, and `dw_wdt_drv_shutdown` stay reviewable beside the existing stop-on-reboot and register-device ordering packet before live callbacks exist | actual platform shutdown callbacks, reboot notifier ordering, and hardware-backed reset-line timing |

## Review Guardrails

- keep this note tied only to `drivers/watchdog/dw_wdt.zig` and its directly coupled teardown or scaffold checks in `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, and `drivers/watchdog/dw_wdt_verify.zig`
- do not treat this note as evidence of live platform-driver registration, clock or reset acquisition, IRQ registration, live MMIO execution, suspend or resume behavior, or hardware-backed shutdown
- when `stop()`, `teardownSummary()`, `removeSummary()`, or `platformRegistrationScaffoldSummary()` change, update this note together with `Documentation/zigux/phase11-dw-wdt-slice.md` and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` so the lane keeps one honest teardown story
