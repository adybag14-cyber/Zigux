# Phase 11 GPIO Watchdog Validation Matrix

This document records the first bounded hardware-validation matrix for the Zigux `gpio_wdt` lane.

## Status

- `PHASE11_GPIO_WDT_STATUS=metadata_teardown_and_register_device_surface_landed`
- reviewed against live `master` `0bd402fd6ca83ba2ace6b21e9e57459401b631cd`
- active continuity owner for this review packet: `P11-Y01`
- archived manifest lane key for this packet remains `P11-L04` for traceability, even though later scheduled continuity revisited the same landed review packet under `P11-L03` for teardown-facing verification and `P11-L05` for wording-only matrix cleanup without widening into descriptor-backed preflight or live registration work
- scope: keep the current `gpio_wdt` starter honest about what is already validated, name the explicit teardown evidence plus the first bounded register-device call evidence, and avoid overclaiming live GPIO, platform registration, or reboot integration before those behaviors exist in Zigux
- current repo reality:
  - `drivers/watchdog/gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt_manifest.json`
  - `zigux/tests/phase11_gpio_wdt_survey.zig`
  - `Documentation/zigux/phase11-gpio-wdt-slice.md`
  - `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  - `zigux/tests/phase11_build.zig`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers `hw_algo` parsing, heartbeat-margin validation, an explicit watchdog metadata summary, starter-local `nowayout` policy bookkeeping, start or ping or stop transitions, a small probe-time summary, a nowayout-aware stop helper, an explicit `summarizeTeardown()` helper, a metadata-only registration plan, and the first bounded register-device call summary. The live repo still needed one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which direct watchdog-info identity and option flags are already preserved as starter-local evidence
- which starter-local `nowayout` policy checkpoints are already explicit in the driver surface even before descriptor-backed registration work lands
- which teardown-facing stop outcomes are already preserved as test-backed evidence
- which disable-order and failure-mode checkpoints are now explicit in one helper instead of implied by end-state assertions alone
- which module-facing checkpoints stay aligned with the shared replay, the slice note, and the focused survey gate
- which registration-facing checkpoints are now explicit call-surface evidence rather than live behavior
- which areas must remain out of scope after that first bounded `devm_watchdog_register_device()` request summary lands

Without this matrix, the slice and survey named the right next step but did not yet preserve the validation posture in one place.

## Hardware-Validation Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| property parsing and bounded timeout window | `drivers/watchdog/gpio_wdt.zig` validates `toggle` versus `level` mode selection plus the same bounded heartbeat-margin window used by `drivers/watchdog/gpio_wdt.c` through `init()` and `initFromPropertyString()` | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via `zigux/tests/phase11_gpio_wdt.zig` in `.github/workflows/zigux-bootstrap.yml` | keep the same property and timeout evidence wired into any later registration-facing surface | live GPIO descriptor lookup, module parameter wiring, and platform-driver execution |
| direct watchdog metadata surface | `watchdogMetadataSummary()` now keeps the `GPIO Watchdog` identity, `WDIOF_SETTIMEOUT`, `WDIOF_MAGICCLOSE`, and `WDIOF_KEEPALIVEPING` contract explicit alongside the starter-local start or stop or ping readiness before the lane widens into descriptor-backed registration work | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the metadata assertions in `zigux/tests/phase11_gpio_wdt.zig` | keep the same watchdog-info evidence stable while later lane work decides whether descriptor-backed preflight or registration execution is the next honest widening | live watchdog-core registration, descriptor acquisition, and hardware-backed metadata wiring |
| direct nowayout policy surface | `nowayoutPolicySummary()` now keeps the `nowayout` module parameter name, the `watchdog_nowayout` default source, and the bounded `watchdog_set_nowayout()` application boundary explicit as starter-local policy bookkeeping before descriptor-backed registration work lands | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the direct `nowayoutPolicySummary()` assertions in `zigux/tests/phase11_gpio_wdt.zig` | keep this policy summary and its focused assertion stable while a later lane decides whether descriptor-backed preflight or registration execution is the next honest widening | live module parameter wiring, watchdog-core registration, and hardware-backed policy enforcement |
| in-memory start, ping, and bounded runtime transitions | `GpioWatchdogLab.start()`, `ping()`, and `stop()` keep toggle-state, pulse-count, disable-count, and always-running outcomes reviewable without claiming hardware-backed toggling | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the transition checks in `zigux/tests/phase11_gpio_wdt.zig` | keep the same runtime transition evidence stable while later lane work decides whether descriptor acquisition or probe ordering is the next bounded widening after the call surface | live GPIO value changes, reboot hooks, and watchdog-core side effects |
| teardown-facing stop and failure-mode evidence | `requestStop()` keeps nowayout blocking, non-`always_running` disable, and `always_running` keepalive outcomes reviewable as teardown-facing metadata immediately adjacent to the current register-device planning boundary | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the stop-policy checks in `zigux/tests/phase11_gpio_wdt.zig` | keep the same teardown-facing stop evidence and nowayout failure-mode evidence stable while a later lane decides whether descriptor-backed preflight or richer unregister planning is the next honest boundary | real unregister paths, reboot glue, `devm_watchdog_register_device()`, and hardware-backed teardown |
| explicit disable-order teardown summary | `summarizeTeardown()` now keeps `gpio_wdt_disable()`-style eternal-ping ordering, toggle-mode return-to-input behavior, level-mode asserted-output behavior, and `always-running` versus `nowayout` stop fallout reviewable without claiming a live unregister path | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the teardown-summary checks in `zigux/tests/phase11_gpio_wdt.zig` | leave this helper parked unless a later lane can isolate another comparably small teardown or failure-mode split beside it | real unregister callbacks, descriptor release ordering, reboot glue, and hardware-backed teardown |
| probe-time startup bookkeeping | `probeSummary()` records requested line mode, `always-running` startup behavior, parent linkage, timeout-init intent, `stop_on_reboot`, and pre-registration running state without claiming real GPIO or watchdog-core calls | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the probe-summary checks in `zigux/tests/phase11_gpio_wdt.zig` | keep the probe bookkeeping explicit while a later lane decides whether descriptor acquisition or registration intent is the first real boundary to widen | live probe callbacks, devm-managed GPIO acquisition, and watchdog-core registration |
| registration-facing handoff summary | `registrationHandoffSummary()` keeps startup state, line mode, timeout-init intent, stop policy, and reboot bookkeeping reviewable as metadata that would reach `devm_watchdog_register_device()` without claiming the registration call itself | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the registration handoff assertions in `zigux/tests/phase11_gpio_wdt.zig` | keep this handoff stable as the lane names the exact watchdog metadata and request boundary that reach the first bounded register-device call summary | real platform registration, `devm_gpiod_get()`, `devm_watchdog_register_device()`, and hardware-backed execution |
| register-device call surface | `registerDeviceCallSummary()` now records the exact watchdog metadata, timeout bounds, driver-data ownership, parent linkage, `nowayout`, stop-on-reboot, startup state, and explicit `register_device_requested` marker that would reach the first bounded `devm_watchdog_register_device()` request without claiming the live call or descriptor path | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the register-device call assertions in `zigux/tests/phase11_gpio_wdt.zig` | if this lane reopens, keep the next step on one tiny descriptor-backed or probe-order preflight that stays immediately adjacent to the new request summary | live GPIO descriptor acquisition, real platform registration, reboot glue, and hardware-backed execution |

## Shared Replay Surface

- current shared replay wiring on `master` includes both `phase11-gpio-wdt-tests` and `phase11-gpio-wdt-survey-tests`
- exact shared command:
  - `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- included gpio artifacts:
  - `phase11-gpio-wdt-tests`
  - `phase11-gpio-wdt-survey-tests`
- focused survey replay command:
  - `zig test zigux/tests/phase11_gpio_wdt_survey.zig`

## Latest Verification Snapshot

- lane key: `P11-L04`
- active continuity owner: `P11-Y01`
- later continuity note: the same landed review packet was revisited under `P11-L03` for teardown-facing verification and `P11-L05` for wording-only matrix cleanup while the archived manifest identity stayed fixed
- inspected `master` head: `0bd402fd6ca83ba2ace6b21e9e57459401b631cd`
- focused head-refresh compile check performed in this pass:
  - `zig fmt --check zigux/tests/phase11_gpio_wdt_survey.zig`
  - `zig test --test-no-exec zigux/tests/phase11_gpio_wdt_survey.zig`
  - result: the refreshed survey file stayed format-clean and compiled without errors after the inspected-head pin moved to `0bd402fd6ca83ba2ace6b21e9e57459401b631cd`
- carried-forward last full repo-local replay for the unchanged driver and test packet:
  - `zig test --dep gpio_wdt -Mroot=zigux/tests/phase11_gpio_wdt.zig -Mgpio_wdt=drivers/watchdog/gpio_wdt.zig`
  - result: `14/14` focused gpio watchdog tests passed before this review-only head refresh
  - `zig test zigux/tests/phase11_gpio_wdt_survey.zig`
  - result: `1/1` survey tests passed before this review-only head refresh
- bounded conclusion:
  - current compile, teardown, and register-device review surfaces still pass as landed; this refresh only moves the machine-checkable verification head forward to the latest inspected `master` while keeping the helper surface unchanged

## Review Rules

- treat this lane as a bounded starter plus validation-matrix lane even after the register-device call summary lands
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- keep teardown-facing stop evidence and the explicit disable-order teardown helper tied to the current starter until a real unregister or registration-execution path exists
- do not claim GPIO descriptor lookup, watchdog-core registration, reboot glue, or live hardware validation until the Zig surface and tests for those behaviors exist
- if a later lane advances beyond the current teardown or register-device summaries, update this matrix, the slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step
