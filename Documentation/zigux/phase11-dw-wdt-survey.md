# Phase 11 DesignWare Watchdog Survey

This survey note tracks the Phase 11 gap around `drivers/watchdog/dw_wdt.c` after re-reading `master` `23d15e44622d2cedd7691c88f78709db6bf1eb7e`.

The live repo state is now:
  * `drivers/watchdog/gpio_wdt.zig` and `drivers/watchdog/bcm2835_wdt.zig` already give the simple-driver watchdog tranche two landed Phase 11 footholds
  * `drivers/watchdog/dw_wdt.zig` now ships the bounded DesignWare starter for fixed TOP timeout windows, reset-mode versus IRQ-mode timeout selection, pretimeout bookkeeping, register-image transitions, non-stoppable stop semantics, a tiny probe-time summary for fixed-versus-custom TOP sourcing plus already-running watchdog metadata, and a small registration-facing handoff around watchdog info selection, parent linkage, timeout-programming intent, and `watchdog_register_device`
  * `drivers/watchdog/dw_wdt_verify.zig` keeps the teardown and failure-mode parity packet reviewable by replaying the split between reset-controlled remove and unstoppable hardware while also keeping the custom TOP ordering and platform handoff summary bounded
  * `zigux/tests/phase11_dw_wdt.zig` and `Documentation/zigux/phase11-dw-wdt-slice.md` keep that starter reviewable without claiming platform registration, live MMIO, IRQ wiring, PM behavior, or hardware-backed execution
  * `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` now records the bounded hardware-validation posture for the current starter so the shared replay path and deferred ownership boundaries stay reviewable in one place
  * `zigux/tests/phase11_build.zig` now runs the gpio starter checks, bcm2835 starter and survey checks, the `phase11-dw-wdt-tests` starter replay, the `phase11-dw-wdt-verify-tests` verify replay, and the `phase11-dw-wdt-survey-tests` survey replay together so watchdog-lane drift is visible in one place
  * `Documentation/zigux/phase11-shared-replay-contract.md` and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` now keep those exact shared DesignWare replay names explicit beside `drivers/watchdog/dw_wdt_verify.zig` so the verify-backed handoff does not collapse back into a generic build-only claim

Against the Phase 11 simple-driver roadmap, the current packet now lands two required features in bounded form: the hardware validation matrix is present, and teardown and failure-mode parity is reviewable through the paired verify replay. The remaining simple-driver gap is the next ready step already hinted at by the starter: attach the bounded registration-facing handoff to platform-backed registration scaffolding in a direct-port or dual-implementation style without widening into PM or live MMIO work yet.

This cleanup packet now carries lane identity `P11-L10` so the live manifest, focused survey gate, and survey note all point at the same DesignWare watchdog review record.
This lane still does not claim platform-driver registration side effects, clock or reset acquisition, live IRQ registration, suspend or resume handling, debugfs support, or live MMIO access. Hardware-validation coverage remains bounded to the review matrix already recorded for the current starter rather than any hardware-backed validation beyond the bounded matrix evidence already recorded for the current starter.
