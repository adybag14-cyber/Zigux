# Phase 11 GPIO Watchdog Validation Matrix

This document records the bounded gpio watchdog validation matrix for the current Zigux Phase 11 simple-driver packet.

## Status

- `PHASE11_GPIO_WDT_STATUS=visible_starter_with_archived_review_surface`
- lane: `P11-L04`
- reviewed against live `master`
- scope: keep the current `gpio_wdt` review packet honest about the visible starter, the visible main replay, the archived notes, the dedicated survey gate, and the focused replays that remain directly visible on current `master`, without overclaiming the missing shared build route, live GPIO descriptor acquisition, platform-driver registration, watchdog-core registration, remove hooks, reboot-backed teardown execution, or hardware-backed validation
- latest directly visible gpio-local replays recorded by the current packet: `zig test zigux/tests/phase11_gpio_wdt.zig`, `zig test zigux/tests/phase11_gpio_wdt_timeout_property.zig`, `zig test zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`, and `zig test zigux/tests/phase11_gpio_wdt_watchdog_drvdata.zig`
- dedicated archived-packet freshness gate now visible: `zig test zigux/tests/phase11_gpio_wdt_survey.zig`
- shared replay boundary: direct current-`master` contents reads still do not expose `zigux/tests/phase11_build.zig`, so this matrix keeps the older shared replay route only as archived review context rather than current shipped evidence

## Current Repo Reality

The live gpio watchdog review surfaces still directly visible on current `master` are:

- `drivers/watchdog/gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt_timeout_property.zig`
- `zigux/tests/phase11_gpio_wdt_manifest.json`
- `zigux/tests/phase11_gpio_wdt_survey.zig`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`
- `zigux/tests/phase11_gpio_wdt_watchdog_drvdata.zig`

Direct current-`master` contents reads still do not expose `zigux/tests/phase11_build.zig`.

The visible starter keeps these code-backed review surfaces explicit:

- `descriptorRequestSummary()`
- `platformDrvdataCheckpointSummary()`
- `watchdogDrvdataCheckpointSummary()`
- `nowayoutPolicySummary()`
- `probeSummary()`
- `registrationHandoffSummary()`
- `registrationPlanSummary()`
- `registerDeviceCallSummary()`
- `registerDeviceFailureSummary()`
- `summarizeTeardown()`

## Visible Replay Surface

The gpio-local evidence still directly visible on current `master` now includes the directly coupled main replay plus the focused pre-registration ordering replays:

- `zigux/tests/phase11_gpio_wdt.zig`
- `zig test zigux/tests/phase11_gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt_timeout_property.zig`
- `zig test zigux/tests/phase11_gpio_wdt_timeout_property.zig`
- `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`
- `zig test zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`
- `zigux/tests/phase11_gpio_wdt_watchdog_drvdata.zig`
- `zig test zigux/tests/phase11_gpio_wdt_watchdog_drvdata.zig`
- `zigux/tests/phase11_gpio_wdt_survey.zig`
- `zig test zigux/tests/phase11_gpio_wdt_survey.zig`

The older shared route remains archived reference only for now:

- archived-only shared-route reference: `zigux/tests/phase11_build.zig`
- archived-only shared replay command reference: `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- archived-only shared make route reference: `make -C zigux phase11`

This gpio-local matrix does not treat those archived shared-route references as proof that the shared Phase 11 build path is currently materialized on `master`.

## Kernel-Integration Matrix

- descriptor preflight boundary: the visible starter now exposes `descriptorRequestSummary()`, so the exact `devm_gpiod_get()` flag choice and the early probe-ordering boundary are code-backed again without claiming live descriptor acquisition.
- timeout-property bookkeeping: the visible starter keeps the required `hw_margin_ms` boundary explicit through `probeSummary()` and `platformDrvdataCheckpointSummary()`, and the focused `zigux/tests/phase11_gpio_wdt_timeout_property.zig` replay now keeps that pre-registration checkpoint directly reviewable without widening into the missing shared build route or live registration execution.
- platform-drvdata checkpoint: `platformDrvdataCheckpointSummary()` plus the still-visible focused `phase11_gpio_wdt_platform_drvdata.zig` replay keep the early `platform_set_drvdata()` ordering boundary explicit while staying outside the missing shared `phase11_build.zig` route.
- watchdog-drvdata checkpoint: `watchdogDrvdataCheckpointSummary()` plus the still-visible focused `phase11_gpio_wdt_watchdog_drvdata.zig` replay keep the bounded `watchdog_set_drvdata()` ordering boundary explicit without claiming live watchdog-core registration or the missing shared Phase 11 build route.
- stop-policy and failure-mode surface: the visible starter now exposes `nowayoutPolicySummary()`, `requestStop()`, and `registerDeviceFailureSummary()` so the watchdog-core stop-policy split and the bounded registration failure surface are code-backed without promoting them into live watchdog-core registration or hardware-backed execution.
- registration handoff and register-device request surface: the visible starter now exposes `registrationHandoffSummary()`, `registrationPlanSummary()`, and `registerDeviceCallSummary()` without claiming platform-driver registration or watchdog-core side effects are currently replayable.
- teardown surface: `summarizeTeardown()` plus `Documentation/zigux/phase11-gpio-wdt-teardown-note.md` keep the bounded teardown handoff explicit without claiming live reboot hooks, remove hooks, or reboot-backed shutdown execution.
- out of scope for now: the missing shared Phase 11 build route, live GPIO descriptor acquisition, `platform_set_drvdata()` execution, `watchdog_set_drvdata()` execution, watchdog-core registration, remove hooks, reboot-backed teardown execution, and hardware-backed validation.

## Review Guardrails

- Treat this matrix as a truthfulness note for the current gpio watchdog packet, not as proof that the missing shared build route is already restored on current `master`.
- Keep this matrix aligned with `drivers/watchdog/gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_timeout_property.zig`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-module-slice.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_gpio_wdt_survey.zig`, `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`, and `zigux/tests/phase11_gpio_wdt_watchdog_drvdata.zig` whenever gpio checkpoint wording moves.
- Preserve lane identity `P11-L04` so the matrix, survey note, module-slice note, teardown note, manifest, and dedicated survey gate continue to describe the same archived gpio watchdog packet.

## Next Blocked Step

The next honest gpio-only follow-up is still one bounded restore step that stays inside this packet: restore the missing shared Phase 11 build route beside the visible starter and main replay, or continue trimming gpio watchdog review notes only when the dedicated survey gate finds a fresh truthfulness drift.
