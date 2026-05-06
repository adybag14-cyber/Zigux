# Phase 11 DesignWare Watchdog Survey

This survey note tracks the Phase 11 gap around `drivers/watchdog/dw_wdt.c` after re-reading `master` `0ddb982b08ffa3f1a34bddc0520f50af0b3e346f`.

The live repo state is now:
  * `drivers/watchdog/gpio_wdt.zig` and `drivers/watchdog/bcm2835_wdt.zig` already give the simple-driver watchdog tranche two landed Phase 11 footholds
  * `drivers/watchdog/dw_wdt.zig` now ships the bounded DesignWare starter for fixed TOP timeout windows, reset-mode versus IRQ-mode timeout selection, pretimeout bookkeeping, register-image transitions, non-stoppable stop semantics, a tiny probe-time summary for fixed-versus-custom TOP sourcing plus already-running watchdog metadata, and a small registration-facing handoff around watchdog info selection, parent linkage, timeout-programming intent, and `watchdog_register_device`
  * `zigux/tests/phase11_dw_wdt.zig` and `Documentation/zigux/phase11-dw-wdt-slice.md` keep that starter reviewable without claiming platform registration, live MMIO, IRQ wiring, PM behavior, or hardware-backed execution
  * `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` now records the bounded hardware-validation posture for the current starter so the shared replay path and deferred ownership boundaries stay reviewable in one place
  * `zigux/tests/phase11_build.zig` now runs the gpio starter checks, bcm2835 starter and survey checks, the dw_wdt starter checks, and the dw_wdt survey check together so watchdog-lane drift is visible in one place
This cleanup packet now carries lane identity `P11-L05` so the live manifest, focused survey gate, and survey note all point at the same DesignWare watchdog review record.
This lane still does not claim platform-driver registration, clock or reset acquisition, IRQ registration, suspend or resume handling, debugfs support, or live MMIO access. Hardware-validation coverage remains bounded to the review matrix already recorded for the current starter rather than any hardware-backed validation beyond the bounded matrix evidence already recorded for the current starter.
