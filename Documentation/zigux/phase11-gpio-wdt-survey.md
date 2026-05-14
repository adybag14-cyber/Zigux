# Phase 11 GPIO Watchdog Survey

`PHASE11_LANE_KEY=P11-L04`

This survey note tracks the current `gpio_wdt` simple-driver gap against the Phase 11 roadmap anchor `drivers/watchdog/gpio_wdt.c` on current `master`.

## Live Repo State

- Current `master` still exposes the archived gpio watchdog review surfaces `zigux/tests/phase11_gpio_wdt_manifest.json`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-module-slice.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, and the focused replay `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`.
- Direct current-`master` contents reads no longer expose `drivers/watchdog/gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_survey.zig`, or `zigux/tests/phase11_build.zig`, so the roadmap destination under `drivers/watchdog/*.zig` is still not visibly landed on `master`.
- The archived review surfaces therefore remain useful only as review memory for the earlier gpio watchdog packet. They are not enough to claim that the simple-driver scaffold, the main gpio watchdog replay, the dedicated survey gate, or the shared Phase 11 build route are presently shipped on current `master`.
- The focused `platform_set_drvdata()` replay that remains visible on `master` is still a bounded proof of one early ordering checkpoint only. Without the driver file and the directly coupled main replay beside it, it does not close the broader simple-driver gap that Phase 11 still schedules for `gpio_wdt`.

## Roadmap Gap

Phase 11 still calls for direct-port or dual-implementation driver templates under `drivers/watchdog/*.zig` together with hardware validation discipline and teardown or failure-mode parity.

For `gpio_wdt` on current `master`, the remaining honest simple-driver gap is:

- restore or publish the visible `drivers/watchdog/gpio_wdt.zig` starter itself
- restore or publish the directly coupled main replay at `zigux/tests/phase11_gpio_wdt.zig`
- restore or publish the dedicated survey gate at `zigux/tests/phase11_gpio_wdt_survey.zig`
- restore or publish the shared Phase 11 build route at `zigux/tests/phase11_build.zig`
- then realign the archived manifest, survey note, module-slice note, teardown note, and validation matrix around the newly visible packet instead of treating the archived notes as proof on their own

## Boundaries

This survey note does not claim that current `master` already ships live GPIO descriptor lookup, `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution, watchdog core registration, reboot hooks, remove hooks, broader teardown or failure-mode parity, or hardware-backed validation.

It also no longer treats the archived review notes and the single focused platform-drvdata replay as proof that the main `gpio_wdt` starter packet is already landed on `master`.

The next honest bounded step for this survey lane is one truthfulness follow-through that keeps the current-master record aligned with the roadmap: either restore the missing visible driver packet onto `master` or continue trimming gpio watchdog review surfaces so they stop overstating what current `master` actually ships.
