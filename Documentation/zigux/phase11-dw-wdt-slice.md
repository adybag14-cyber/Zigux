# Phase 11 DesignWare Watchdog Slice

This bounded Phase 11 slice adds the first Zigux `dw_wdt` starter anchored to `drivers/watchdog/dw_wdt.c`.

The starter stays intentionally narrow:

- derives the fixed TOP timeout windows from an injected input clock rate
- mirrors reset-mode versus IRQ-mode timeout selection and pretimeout bookkeeping
- models the register-image writes for start, ping, stop, restart, imported running-state snapshots, and time-left queries only
- keeps the DesignWare non-stoppable stop semantics explicit when reset control is unavailable
- adds a tiny probe-time summary for fixed-versus-custom TOP sourcing, nowayout and restart-priority bookkeeping, stop-on-reboot intent, and already-running watchdog state before registration
- adds a small registration-facing handoff that keeps watchdog info selection, parent linkage, driver-data setup, timeout-init intent, imported running-state bookkeeping, and register-device intent explicit before any live registration
- keeps the tiny watchdog-metadata surface from `dw_wdt_ident`, `dw_wdt_pt_ident`, and `dw_wdt_ops` explicit through that registration-facing handoff, so the identity string, the basic-versus-pretimeout option-flag split, and the bounded ops contract stay reviewable before any platform-driver widening
- adds a tiny platform-resource preflight plus live resource-order summary that keeps the timer-clock choice, optional APB clock presence, reset-control availability, and optional pretimeout-IRQ wiring, plus the bounded tclk, optional pclk, reset, irq, and registration sequencing reviewable before any live devm calls
- adds a bounded `summarizeSuspendResume()` helper so timer-clock or optional-APB save-and-restore ordering, restart-kick replay, imported running-state preservation, interrupt-pending preservation, and timeout-programming preservation stay reviewable without claiming live PM callbacks or hardware-backed clock gating
- adds an explicit `summarizeTeardownLifecycle()` helper so reset-control-backed stop pulses, non-stoppable stop fallout, reset-mode restart forcing, and restart-from-stopped enablement stay reviewable before any live platform remove or PM teardown work
- adds an explicit `summarizeRemoveHandoff()` helper so the unconditional debugfs clear call site, unregister-device ordering, reset-control-backed remove, and non-reset remove fallout stay reviewable before any live platform remove, PM, or debugfs-backed teardown work
- keeps idle remove-time pending interrupts distinct when remove happens before the watchdog is running, so reset-backed interrupt clearing and non-reset preserved pending interrupt state stay reviewable without claiming a live remove callback

This slice does not claim platform-driver registration, clock or reset acquisition, IRQ registration, live suspend or resume callbacks, debugfs support, custom devicetree TOP arrays beyond the bounded in-memory ordering helper, live MMIO access, or hardware validation coverage yet.

The next honest bounded step inside the same Phase 11 lane is to leave this starter parked unless fresh repo inspection finds another comparably small watchdog-family drift around the current metadata, lifecycle, remove-time, suspend-resume, or platform-resource summaries. Anything larger remains blocked on platform-driver scaffold work such as live clock or reset acquisition, IRQ registration, watchdog registration execution, live PM callback wiring, and a hardware-validation plan.
