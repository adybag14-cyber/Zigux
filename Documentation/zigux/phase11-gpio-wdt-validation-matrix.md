# Phase 11 GPIO Watchdog Validation Matrix

This document records the bounded gpio watchdog validation matrix for the current Zigux Phase 11 simple-driver packet.
## Status
- `PHASE11_GPIO_WDT_STATUS=starter_matrix_landed`
- lane: `P11-L04`
- reviewed against live `master`
- scope: keep the current `gpio_wdt` packet honest about what is already reviewable in the landed starter, the bounded survey note, the manifest-backed replay route, and the teardown note without overclaiming live GPIO descriptor acquisition, platform-driver registration, watchdog-core registration, remove hooks, reboot-backed teardown execution, or hardware-backed validation
- latest focused replays recorded by the current packet: `zig test zigux/tests/phase11_gpio_wdt.zig`, `zig test zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`, and `zig test zigux/tests/phase11_gpio_wdt_survey.zig`
- shared replay boundary: `zig build test --build-file zigux/tests/phase11_build.zig --summary all` still keeps the starter and survey paths together, while the dedicated focused `phase11_gpio_wdt_platform_drvdata.zig` replay still stays outside the shared `phase11_build.zig` route
## Current Repo Reality

The live gpio watchdog packet visible on `master` is:
- `drivers/watchdog/gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig`
- `zigux/tests/phase11_gpio_wdt_manifest.json`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `zigux/tests/phase11_build.zig`
The current packet already keeps these reviewable without claiming live platform behavior:
- `hw_algo` parsing plus heartbeat-margin validation and bounded `start`, `ping`, `stop`, and `disable` transitions
- `descriptorPreflightSummary()` for the `devm_gpiod_get()` flag choice and the early probe-ordering boundary
- `platformDrvdataCheckpointSummary()` for the early `platform_set_drvdata()` ordering boundary before later GPIO and watchdog handoffs
- `registerDeviceFailureSummary()` for the bounded register-device failure cues that stay reviewable before live watchdog-core registration
- `summarizeTeardown()` for the host-free teardown summary that stays bounded beside the teardown note
- the nowayout-aware stop helper that separates watchdog-core stop policy from hardware `always-running` behavior
- the registration handoff summary, registration plan summary, and register-device call summary
## Shared Replay Surface

The active gpio watchdog validation packet stays explicit inside the shared Phase 11 route:

- `zigux/tests/phase11_gpio_wdt.zig`
- `zigux/tests/phase11_gpio_wdt_survey.zig`
- `zigux/tests/phase11_build.zig`
- `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- `make -C zigux phase11`
This gpio-local matrix does not claim that the whole current shared Phase 11 replay is green when unrelated HVC, header-boundary, or bcm2835 drift can reopen elsewhere on `master`.
## Kernel-Integration Matrix
- descriptor preflight boundary: `descriptorPreflightSummary()` plus the landed gpio tests keep the exact `devm_gpiod_get()` flag choice, the probe-ordering boundary, and the still-blocked live descriptor lookup explicit.
- platform-drvdata checkpoint: `platformDrvdataCheckpointSummary()` plus the dedicated focused `phase11_gpio_wdt_platform_drvdata.zig` replay keep the early `platform_set_drvdata()` ordering boundary explicit while still staying outside the shared `phase11_build.zig` route.
- runtime and stop-policy surface: the landed starter and gpio tests keep the bounded start, ping, stop, disable, and nowayout-aware stop outcomes explicit without promoting them into live GPIO or reboot-backed behavior.
- registration handoff and register-device request surface: the landed starter and gpio tests keep the pre-registration bookkeeping, registration handoff summary, registration plan summary, `registerDeviceCallSummary()`, and `registerDeviceFailureSummary()` reviewable without claiming platform-driver registration or watchdog-core side effects.
- teardown surface: `Documentation/zigux/phase11-gpio-wdt-teardown-note.md` keeps `summarizeTeardown()`, `requestStop()`, and the bounded teardown handoff explicit without claiming a `watchdog_set_drvdata()` checkpoint, reboot-glue checkpoint, remove hooks, or live shutdown execution.
- dedicated focused replay boundary: `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig` is now present on `master`, but it remains intentionally dedicated rather than part of the shared Phase 11 replay route so the packet can keep one extra local proof without widening the archive packet.
- out of scope for now: live GPIO descriptor acquisition, `platform_set_drvdata()` execution, a code-backed timeout-property checkpoint, a code-backed `watchdog_set_drvdata()` checkpoint, `watchdog_set_drvdata()` execution, watchdog-core registration, a code-backed reboot-glue checkpoint around `watchdog_stop_on_reboot()`, remove hooks, reboot-backed teardown execution, failure-mode parity beyond the landed bounded starter checks, and hardware-backed validation.
## Review Guardrails
- Treat this matrix as a truthfulness note for the current gpio watchdog packet, not as proof of live platform registration or hardware execution.
- Keep this matrix aligned with `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_build.zig`, and `Documentation/zigux/phase11-shared-replay-contract.md` whenever gpio checkpoint wording moves.
- Preserve lane identity `P11-L04` so the matrix, survey note, and manifest continue to describe the same archived gpio watchdog packet.
## Next Blocked Step

The next honest gpio-only follow-up is still one focused failure-mode parity or broader hardware-backed validation step that stays adjacent to the landed descriptor, platform-drvdata, teardown, handoff, and register-device request surfaces without widening into live GPIO or platform registration.
