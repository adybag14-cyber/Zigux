# Phase 11 DesignWare Watchdog Validation Matrix

This document records the bounded validation matrix for the Zigux `dw_wdt` lane.

## Status

- `PHASE11_DW_WDT_STATUS=validation_matrix_landed`
- reviewed against live `master` `82ccfea5b769fd42a3b6926eb43aeac9ae5ea9dc`
- scope: keep the current `dw_wdt` starter honest about what is already validated, name the existing lifecycle, remove-time, and failure-mode evidence clearly, and avoid overclaiming platform registration, PM, IRQ, debugfs, or hardware-backed behavior before those surfaces exist in Zigux
- latest focused replay posture: the bounded `dw_wdt` driver, remove-idle split, survey replays, and paired teardown note remain this lane's truthful current-master evidence, while any wider shared `Phase 11` green status stays intentionally tracked outside this watchdog-local matrix because unrelated non-watchdog drift can reopen elsewhere on `master`
- current repo reality:
  - `drivers/watchdog/dw_wdt.zig`
  - `zigux/tests/phase11_dw_wdt.zig`
  - `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`
  - `zigux/tests/phase11_dw_wdt_manifest.json`
  - `zigux/tests/phase11_dw_wdt_survey.zig`
  - `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
  - `zigux/tests/phase11_build.zig`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers fixed TOP timeout selection, custom TOP ordering, reset-mode versus IRQ-mode timeout bookkeeping, imported running-state snapshots, registration-facing watchdog-info and parent handoff details, platform-resource preflight and live resource-order sequencing, restart intent, non-stoppable stop semantics, an explicit `summarizeTeardownLifecycle()` helper for the stop-and-restart failure-mode packet, an explicit `summarizeRemoveHandoff()` helper for the remove-time teardown packet, and a dedicated remove-idle split replay for pending-interrupt teardown drift. The live repo still needed one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which lifecycle, remove-time, and failure-mode checkpoints are already reviewable in bounded form
- which areas must remain out of scope until a later platform-driver or hardware-validation handoff lands

Without this matrix, the slice and survey named the right boundaries but did not yet preserve the validation posture in one place. The paired teardown note now makes the stop, restart, remove, and idle-remove ownership split explicit alongside the matrix instead of leaving teardown evidence implicit inside helper and test names only.

## Watchdog Validation Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| fixed TOP timeout evidence | `DwWdtLab.initFixedTops()`, `timeoutWindows()`, and `setTimeout()` keep the fixed TOP timeout evidence reviewable, including nearest-match timeout selection and bounded max-heartbeat reporting without claiming live clock or MMIO work | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the fixed-top and timeout-window checks in `zigux/tests/phase11_dw_wdt.zig` | keep the same timeout evidence aligned with any later platform-backed clock acquisition or devicetree TOP-array work | live clock acquisition, devicetree parsing, and hardware-backed timeout programming |
| IRQ pretimeout bookkeeping | reset-mode versus IRQ-mode timeout bookkeeping, pretimeout seconds, interrupt-pending state, and second-stage time-left accounting stay reviewable through `setResponseMode()`, `setInterruptPending()`, and `runtimeSnapshot()` without claiming a live IRQ line or handler | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the IRQ-mode bookkeeping checks in `zigux/tests/phase11_dw_wdt.zig` | keep the IRQ pretimeout bookkeeping stable unless a later lane writes a small hardware-validation plan for real IRQ registration | live pretimeout IRQ registration, ISR execution, and hardware-backed interrupt delivery |
| imported running-state handoff evidence | `loadRegisters()`, `probeSummary()`, and `registrationHandoffSummary()` keep imported running-state handoff evidence explicit, including already-running watchdog state, watchdog-info selection, parent linkage, driver-data setup, timeout-init intent, and register-device intent before any live registration | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the imported-running-state and registration-handoff checks in `zigux/tests/phase11_dw_wdt.zig` | keep the handoff summary honest while any later lane decides whether to model real platform registration or watchdog-core execution | live platform-driver registration, watchdog-core registration, and backend state handoff |
| platform-resource ordering surface | `platformResourcePreflightSummary()` plus `liveResourceOrderSummary()` keep timer-clock choice, optional APB clock presence, reset-control availability, optional pretimeout-IRQ wiring, and the bounded tclk, optional pclk, reset, irq, and registration sequencing reviewable before any live devm calls | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the platform-resource preflight and live resource-order checks in `zigux/tests/phase11_dw_wdt.zig` | keep the ordering surface stable until a later lane writes the first real platform-driver call packet and its hardware-validation plan | live `devm_clk_get()`, reset-control acquisition, IRQ requests, PM callbacks, and hardware-backed registration |
| stop and restart failure-mode boundary | `stop()`, `armRestart()`, `summarizeTeardownLifecycle()`, and `Documentation/zigux/phase11-dw-wdt-teardown-note.md` keep the non-stoppable stop failure-mode boundary explicit when reset control is unavailable while still recording the stoppable path, interrupt-status clearing, restart arming, reset-mode restart forcing, and restart-from-stopped enablement without claiming reboot-side effects | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the stop, restart, and teardown-summary checks in `zigux/tests/phase11_dw_wdt.zig` | keep the failure-mode evidence tied to the same bounded starter until a later lane adds real platform-teardown or restart-plumbing work | live reboot ordering, reset pulses, suspend or resume handling, and hardware-backed failure injection |
| remove-time teardown handoff boundary | `summarizeRemoveHandoff()` plus `Documentation/zigux/phase11-dw-wdt-teardown-note.md` keep debugfs clear, unregister-device ordering, reset-control-backed disable, non-reset remove fallout, and the note-owned ownership split explicit without claiming a live remove callback, PM teardown, or debugfs implementation | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the remove-handoff checks in `zigux/tests/phase11_dw_wdt.zig` | leave this handoff parked unless a later lane can isolate one equally small platform-remove or PM-teardown clarification directly adjacent to the current helper | live remove callbacks, PM teardown ordering, debugfs implementation, and hardware-backed remove validation |
| idle remove-time pending-interrupt split | `zigux/tests/phase11_dw_wdt_remove_idle_split.zig` plus `Documentation/zigux/phase11-dw-wdt-teardown-note.md` keep idle remove-time pending interrupts distinct when reset control is present or absent, so reset-backed interrupt clearing and non-reset preserved pending state stay reviewable even when remove happens before the watchdog is running | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the dedicated `phase11-dw-wdt-remove-idle-split-tests` replay | keep the split aligned with any later live remove callback or PM-teardown packet before widening other teardown behavior | live remove callbacks, PM teardown ordering, debugfs implementation, and hardware-backed remove validation |

## Shared Replay Surface

- current shared replay wiring on `master` includes `phase11-dw-wdt-tests`, `phase11-dw-wdt-remove-idle-split-tests`, and `phase11-dw-wdt-survey-tests`
- exact shared command:
  - `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- focused driver replay command:
  - `zig test --dep dw_wdt -Mroot=zigux/tests/phase11_dw_wdt.zig -Mdw_wdt=drivers/watchdog/dw_wdt.zig`
- focused remove-idle split replay command:
  - `zig test --dep dw_wdt -Mroot=zigux/tests/phase11_dw_wdt_remove_idle_split.zig -Mdw_wdt=drivers/watchdog/dw_wdt.zig`
- focused survey replay command:
  - `zig test zigux/tests/phase11_dw_wdt_survey.zig`
- focused validation script command:
  - `python3 scripts/zigux/validate-phase11.py`

## Review Rules

- treat this lane as a bounded starter plus validation-note lane even after the validation matrix lands
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- keep `Documentation/zigux/phase11-dw-wdt-teardown-note.md` aligned whenever stop, restart, remove, or idle-remove ownership semantics change, because that note now carries the teardown-specific review packet for this driver
- do not claim platform-driver registration, live clock or reset acquisition, IRQ registration, PM handling, debugfs coverage, or hardware-backed execution until the Zig surface and tests for those behaviors exist
- if a later lane chooses a real platform-driver or hardware-validation step, update this matrix, the slice note, the teardown note, the survey note, and the survey manifest together so the lane keeps one truthful next step
