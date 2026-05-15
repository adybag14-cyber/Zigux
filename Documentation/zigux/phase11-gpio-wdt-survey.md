# Phase 11 GPIO Watchdog Survey

`PHASE11_LANE_KEY=P11-L04`

This survey note tracks the current `gpio_wdt` simple-driver gap against the Phase 11 roadmap anchor `drivers/watchdog/gpio_wdt.c` on current `master`.

## Live Repo State

- Current `master` now exposes the visible starter `drivers/watchdog/gpio_wdt.zig` together with the directly coupled main replay `zigux/tests/phase11_gpio_wdt.zig`, the archived gpio watchdog review surfaces `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_gpio_wdt_survey.zig`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-module-slice.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, and the focused replays `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig` plus `zigux/tests/phase11_gpio_wdt_watchdog_drvdata.zig`.
- Direct current-`master` contents reads still do not expose `zigux/tests/phase11_build.zig`, so the shared Phase 11 build route is still missing from the current visible repo surface.
- The visible starter, the visible main replay, the archived review notes, the focused platform-drvdata replay, the focused watchdog-drvdata replay, and the dedicated survey gate are therefore useful as current review memory and code-backed checkpoints for the bounded packet. They are still not enough to claim that the shared Phase 11 build route is presently shipped on current `master`.
- The focused `platform_set_drvdata()` and `watchdog_set_drvdata()` replays that remain visible on `master` are still bounded proofs of early ordering checkpoints only. The dedicated survey gate now keeps the surrounding archived packet honest, but without the shared build route beside the visible starter and main replay, the broader simple-driver gap that Phase 11 still schedules for `gpio_wdt` remains open.

## Roadmap Gap

Phase 11 still calls for direct-port or dual-implementation driver templates under `drivers/watchdog/*.zig` together with hardware validation discipline and teardown or failure-mode parity.

For `gpio_wdt` on current `master`, the remaining honest simple-driver gap is:

- keep the visible `drivers/watchdog/gpio_wdt.zig` starter aligned with the visible main replay, the archived manifest, survey note, module-slice note, teardown note, validation matrix, and dedicated survey gate
- keep the focused `platform_set_drvdata()` and `watchdog_set_drvdata()` ordering replays aligned with that archived packet while the shared build route stays absent
- restore or publish the shared Phase 11 build route at `zigux/tests/phase11_build.zig`
- then expand only from that visible packet into later live GPIO, watchdog-core registration, reboot-hook, teardown, failure-mode, or hardware-backed follow-through

## Boundaries

This survey note does not claim that current `master` already ships live GPIO descriptor lookup, `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution, watchdog-core registration, reboot hooks, remove hooks, broader teardown or failure-mode parity, or hardware-backed validation.

It also does not treat the visible starter, the visible main replay, the archived review notes, the dedicated survey gate, and the two focused drvdata replays as proof that the missing shared Phase 11 build route is already landed on `master`.

The next honest bounded step for this survey lane is one same-family follow-through that keeps the current-master record aligned with the roadmap: restore the missing shared build route, or continue tightening the archived survey gate and notes only when they drift from the packet that current `master` actually exposes.
