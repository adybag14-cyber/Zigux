# Phase 11 GPIO Watchdog Validation Matrix

This document records the bounded gpio watchdog validation matrix for the current Zigux Phase 11 simple-driver packet.

## Status

- `PHASE11_GPIO_WDT_STATUS=starter_matrix_archived_review_surface`
- lane: `P11-L04`
- reviewed against live `master`
- scope: keep the current `gpio_wdt` review packet honest about which archived notes and focused replays remain directly visible on current `master`, without overclaiming a landed main starter, shared build route, live GPIO descriptor acquisition, platform-driver registration, watchdog-core registration, remove hooks, reboot-backed teardown execution, or hardware-backed validation
- latest directly visible focused replay recorded by the current packet: `zig test zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`
- shared replay boundary: current direct contents reads no longer expose `zigux/tests/phase11_build.zig`, so this matrix keeps the older shared replay route only as archived review context rather than current shipped evidence

## Current Repo Reality

The live gpio watchdog review surfaces still directly visible on current `master` are:

- `zigux/tests/phase11_gpio_wdt_manifest.json`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`

Direct current-`master` contents reads no longer expose `drivers/watchdog/gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_survey.zig`, or `zigux/tests/phase11_build.zig`.

The archived gpio watchdog packet still records these bounded review surfaces without turning them into current shipped proof:

- `descriptorPreflightSummary()` for the `devm_gpiod_get()` flag choice and the early probe-ordering boundary
- `timeoutPropertyCheckpointSummary()` for the required `hw_margin_ms` property and its fail-closed ordering before later handoffs
- `platformDrvdataCheckpointSummary()` for the early `platform_set_drvdata()` ordering boundary before later GPIO and watchdog handoffs
- `drvdataCheckpointSummary()` for the `watchdog_set_drvdata()` ordering boundary before the registration handoff and the first register-device request surface
- the nowayout-aware stop helper that separates watchdog-core stop policy from hardware `always-running` behavior
- the registration handoff summary and register-device call summary
- the teardown summary plus reboot-glue checkpoint tracked beside the dedicated teardown note

## Visible Replay Surface

The gpio-local evidence still directly visible on current `master` is narrower than the older starter packet:

- `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`
- `zig test zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`

The older main replay and shared route remain archived references only for now:

- archived-only main replay reference: `zigux/tests/phase11_gpio_wdt.zig`
- archived-only survey-gate reference: `zigux/tests/phase11_gpio_wdt_survey.zig`
- archived-only shared-route reference: `zigux/tests/phase11_build.zig`
- archived-only shared replay command reference: `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- archived-only shared make route reference: `make -C zigux phase11`

This gpio-local matrix does not treat those archived references as proof that the main starter packet is currently materialized on `master`.

## Kernel-Integration Matrix

- descriptor preflight boundary: the archived module-slice and survey notes still record the exact `devm_gpiod_get()` flag choice and the early probe-ordering boundary, but current direct repo reads do not expose the main starter or replay that originally carried that checkpoint.
- timeout-property checkpoint: the archived module-slice and survey notes still keep the required `hw_margin_ms` property, its accepted range, and the fail-closed ordering before later handoffs reviewable as documentation, not as a directly readable current replay.
- platform-drvdata checkpoint: `platformDrvdataCheckpointSummary()` plus the still-visible focused `phase11_gpio_wdt_platform_drvdata.zig` replay keep the early `platform_set_drvdata()` ordering boundary explicit while staying outside the missing shared `phase11_build.zig` route.
- drvdata checkpoint: the archived module-slice and survey notes still record the `watchdog_set_drvdata()` ordering boundary before registration handoff and register-device request surfaces, but current direct repo reads do not expose the paired main replay.
- runtime and stop-policy surface: the archived review packet still documents the bounded start, ping, stop, disable, and nowayout-aware stop outcomes without promoting them into live GPIO or reboot-backed behavior on current `master`.
- registration handoff and register-device request surface: the archived module-slice and survey notes still record the pre-registration bookkeeping, registration handoff summary, and first bounded `devm_watchdog_register_device()` request surface without claiming platform-driver registration or watchdog-core side effects are currently replayable.
- teardown and reboot-glue surface: `Documentation/zigux/phase11-gpio-wdt-teardown-note.md` still keeps the stop-policy split, bounded teardown handoff, and reboot-glue checkpoint explicit without claiming remove hooks or live shutdown execution.
- out of scope for now: visible main driver scaffolding on current `master`, live GPIO descriptor acquisition, `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution, watchdog-core registration, remove hooks, reboot-backed teardown execution, failure-mode parity beyond the archived bounded starter notes, and hardware-backed validation.

## Review Guardrails

- Treat this matrix as a truthfulness note for the current gpio watchdog review memory, not as proof of a directly materialized main starter packet on current `master`.
- Keep this matrix aligned with `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-module-slice.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, `zigux/tests/phase11_gpio_wdt_manifest.json`, and the still-visible `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig` replay whenever gpio checkpoint wording moves.
- Preserve lane identity `P11-L04` so the matrix, survey note, module-slice note, teardown note, and manifest continue to describe the same archived gpio watchdog packet.

## Next Blocked Step

The next honest gpio-only follow-up is still one truthfulness step that stays inside this archived review packet: either restore the missing visible main driver packet and replay surfaces onto current `master`, or continue trimming gpio watchdog review notes so they do not overstate what current `master` directly exposes.
