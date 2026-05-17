# Phase 11 GPIO Watchdog Survey

`PHASE11_LANE_KEY=P11-L04`

This survey note tracks the current `gpio_wdt` simple-driver gap against the Phase 11 roadmap anchor `drivers/watchdog/gpio_wdt.c` on current `master`.
## Live Repo State
  * Current `master` exposes the bounded gpio watchdog starter and review packet surfaces `drivers/watchdog/gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_survey.zig`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-module-slice.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, and the focused replay `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`.
  * The landed packet is still bounded: the dedicated survey gate, the shared Phase 11 build route, and the main gpio watchdog replay are now visible on `master`, while the focused `platform_set_drvdata()` replay continues to cover one early ordering checkpoint alongside them.
  * The visible packet is enough to keep the starter, the directly coupled main replay, the dedicated survey gate, and the shared Phase 11 build route reviewable on current `master` without overclaiming later registration, reboot, remove-hook, teardown, or hardware-backed validation work.
  * The focused `platform_set_drvdata()` replay remains a bounded proof of one early ordering checkpoint only. It strengthens the visible starter packet, but it does not close the broader Phase 11 follow-through around live GPIO descriptor lookup, watchdog-core registration, remove hooks, reboot hooks, teardown execution, or hardware-backed validation.
## Roadmap Gap

Phase 11 still calls for direct-port or dual-implementation driver templates under `drivers/watchdog/*.zig` together with hardware validation discipline and teardown or failure-mode parity.

For `gpio_wdt` on current `master`, the remaining honest simple-driver gap is:
  * keep the visible `drivers/watchdog/gpio_wdt.zig` starter, `zigux/tests/phase11_gpio_wdt.zig` replay, `zigux/tests/phase11_gpio_wdt_survey.zig` gate, and `zigux/tests/phase11_build.zig` route aligned with the archived manifest, survey note, module-slice note, teardown note, and validation matrix
  * complete live GPIO descriptor lookup and the remaining registration path around `devm_gpiod_get()`, `devm_add_action_or_reset()`, and `devm_watchdog_register_device()`
  * add broader teardown or failure-mode parity and hardware-backed validation once the registration path is reviewable
## Boundaries

This survey note does not claim that current `master` already ships live GPIO descriptor lookup, `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution, watchdog core registration, reboot hooks, remove hooks, broader teardown or failure-mode parity, or hardware-backed validation.

It treats the visible starter packet and the focused platform-drvdata replay as bounded reviewable evidence on `master`, not as proof that the later registration and hardware-backed follow-through are already closed.
