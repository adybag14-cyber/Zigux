# Phase 11 DesignWare Watchdog Validation Matrix

This document records the bounded validation matrix for the Zigux `dw_wdt` lane.

## Status

- `PHASE11_DW_WDT_STATUS=validation_matrix_landed`
- reviewed against live `master` `907e65f13e0035306d4106dec0ca3b3eb2fc7179`
- continuity: this matrix tracks the live DesignWare watchdog packet on `P11-L10`; the parked bcm2835 archival wording under `P11-L10` is separate watchdog-family continuity and not part of this matrix
- scope: keep the current `dw_wdt` starter honest about what is already validated, name the existing lifecycle, remove-time, failure-mode, and bounded suspend-resume evidence clearly, and avoid overclaiming platform registration, live PM callbacks, IRQ wiring, debugfs, or hardware-backed behavior before those surfaces exist in Zigux
- current repo reality:
  - `drivers/watchdog/dw_wdt.zig`
  - `zigux/tests/phase11_dw_wdt.zig`
  - `zigux/tests/phase11_dw_wdt_suspend_resume.zig`
  - `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`
  - `zigux/tests/phase11_dw_wdt_manifest.json`
  - `zigux/tests/phase11_dw_wdt_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers fixed TOP timeout selection, custom TOP ordering, reset-mode versus IRQ-mode timeout bookkeeping, imported running-state snapshots, registration-facing watchdog-info and parent handoff details, platform-resource preflight and live resource-order sequencing, a bounded suspend-resume state-preservation helper, restart intent, non-stoppable stop semantics, an explicit `summarizeTeardownLifecycle()` helper for the stop-and-restart failure-mode packet, an explicit `summarizeRemoveHandoff()` helper for the remove-time teardown packet, and a dedicated remove-idle split replay for pending-interrupt teardown drift. The live repo still needed one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which lifecycle, remove-time, failure-mode, and bounded suspend-resume checkpoints are already reviewable in bounded form
- which areas must remain out of scope until a later platform-driver or hardware-validation handoff lands

Without this matrix, the slice and survey named the right boundaries but did not yet preserve the validation posture in one place.

## Watchdog Validation Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| fixed TOP timeout evidence | `DwWdtLab.initFixedTops()`, `timeoutWindows()`, and `setTimeout()` keep the fixed TOP timeout evidence reviewable, including nearest-match timeout selection and bounded max-heartbeat reporting without claiming live clock or MMIO work | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the fixed-top and timeout-window checks in `zigux/tests/phase11_dw_wdt.zig` | keep the same timeout evidence aligned with any later platform-backed clock acquisition or devicetree TOP-array work | live clock acquisition, devicetree parsing, and hardware-backed timeout programming |
| IRQ pretimeout bookkeeping | reset-mode versus IRQ-mode timeout bookkeeping, pretimeout seconds, interrupt-pending state, and second-stage time-left accounting stay reviewable through `setResponseMode()`, `setInterruptPending()`, and `runtimeSnapshot()` without claiming a live IRQ line or handler | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the IRQ-mode bookkeeping checks in `zigux/tests/phase11_dw_wdt.zig` | keep the IRQ pretimeout bookkeeping stable unless a later lane writes a small hardware-validation plan for real IRQ registration | live pretimeout IRQ registration, ISR execution, and hardware-backed interrupt delivery |
| imported running-state handoff evidence | `loadRegisters()`, `probeSummary()`, and `registrationHandoffSummary()` keep imported running-state handoff evidence explicit, including already-running watchdog state, watchdog-info selection, parent linkage, driver-data setup, timeout-init intent, and register-device intent before any live registration | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the imported-running-state and registration-handoff checks in `zigux/tests/phase11_dw_wdt.zig` | keep the handoff summary honest while any later lane decides whether to model real platform registration or watchdog-core execution | live platform-driver registration, watchdog-core registration, and backend state handoff |
| platform-resource ordering surface | `platformResourcePreflightSummary()` plus `liveResourceOrderSummary()` keep timer-clock choice, optional APB clock presence, reset-control availability, optional pretimeout-IRQ wiring, and the bounded tclk, optional pclk, reset, irq, and registration sequencing reviewable before any live devm calls | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the platform-resource preflight and live resource-order checks in `zigux/tests/phase11_dw_wdt.zig` | keep the ordering surface stable until a later lane writes the first real platform-driver call packet and its hardware-validation plan | live `devm_clk_get()`, reset-control acquisition, IRQ requests, PM callbacks, and hardware-backed registration |
| bounded suspend-resume state preservation | `summarizeSuspendResume()` keeps timer-clock or optional-APB save-and-restore ordering, restart-kick replay, imported running-state preservation, interrupt-pending preservation, response-mode preservation, and timeout-programming preservation reviewable without claiming live suspend or resume callbacks | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the dedicated suspend-resume replay in `zigux/tests/phase11_dw_wdt_suspend_resume.zig` | keep the bounded suspend-resume helper aligned with any later PM-facing scaffold packet before widening platform behavior | live suspend or resume callbacks, hardware-backed clock gating, and PM notifier execution |
| stop and restart failure-mode boundary | `stop()`, `armRestart()`, and `summarizeTeardownLifecycle()` keep the non-stoppable stop failure-mode boundary explicit when reset control is unavailable while still recording the stoppable path, interrupt-status clearing, restart arming, reset-mode restart forcing, and restart-from-stopped enablement without claiming reboot-side effects | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the stop, restart, and teardown-summary checks in `zigux/tests/phase11_dw_wdt.zig` | keep the failure-mode evidence tied to the same bounded starter until a later lane adds real platform-teardown or restart-plumbing work | live reboot ordering, reset pulses, suspend or resume callbacks, and hardware-backed failure injection |
| remove-time teardown handoff boundary | `summarizeRemoveHandoff()` keeps the unconditional debugfs clear call site, unregister-device ordering, reset-control-backed disable, and non-reset remove fallout explicit without claiming a live remove callback, PM teardown, or debugfs implementation | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the remove-handoff checks in `zigux/tests/phase11_dw_wdt.zig` | leave this handoff parked unless a later lane can isolate one equally small platform-remove or PM-teardown clarification directly adjacent to the current helper | live remove callbacks, PM teardown ordering, debugfs implementation, and hardware-backed remove validation |
| idle remove-time pending-interrupt split | `zigux/tests/phase11_dw_wdt_remove_idle_split.zig` keeps idle remove-time pending interrupts distinct when reset control is present or absent, so reset-backed interrupt clearing and non-reset preserved pending state stay reviewable even when remove happens before the watchdog is running | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the dedicated `phase11-dw-wdt-remove-idle-split-tests` replay | keep the split aligned with any later live remove callback or PM-teardown packet before widening other teardown behavior | live remove callbacks, PM teardown ordering, debugfs implementation, and hardware-backed remove validation |

## Shared Replay Surface

- current shared replay wiring on `master` includes `phase11-dw-wdt-tests`, `phase11-dw-wdt-suspend-resume-tests`, and `phase11-dw-wdt-survey-tests`
- current shared replay wiring on `master` also includes `phase11-dw-wdt-remove-idle-split-tests`, so the shared packet now keeps the dedicated idle remove-time pending-interrupt split aligned with the main driver and survey replays
- exact shared command:
  - `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- focused driver replay command:
  - `zig test --dep dw_wdt -Mroot=zigux/tests/phase11_dw_wdt.zig -Mdw_wdt=drivers/watchdog/dw_wdt.zig`
- focused suspend-resume replay command:
  - `zig test --dep dw_wdt -Mroot=zigux/tests/phase11_dw_wdt_suspend_resume.zig -Mdw_wdt=drivers/watchdog/dw_wdt.zig`
- focused remove-idle split replay command:
  - `zig test --dep dw_wdt -Mroot=zigux/tests/phase11_dw_wdt_remove_idle_split.zig -Mdw_wdt=drivers/watchdog/dw_wdt.zig`
- focused survey replay command:
  - `zig test zigux/tests/phase11_dw_wdt_survey.zig`
- focused validation script command:
  - `python3 scripts/zigux/validate-phase11.py`

## Review Rules

- treat this lane as a bounded starter plus validation-note lane even after the validation matrix lands
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not claim platform-driver registration, live clock or reset acquisition, IRQ registration, live PM callbacks, debugfs coverage, or hardware-backed execution until the Zig surface and tests for those behaviors exist
- if a later lane chooses a real platform-driver or hardware-validation step, update this matrix, the slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step
