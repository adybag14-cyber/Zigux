# Phase 11 DesignWare Watchdog Validation Matrix

This document records the first bounded hardware-validation matrix for the Zigux `dw_wdt` lane.

## Status

- `PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`
- current surveyed packet pin: `75f8336c4305beed127d7abfae37d3999b7cc57c`
- current validation-matrix continuity for this DesignWare packet is `P11-L11`; the older dedicated survey packet and explicit packet pin still reflect archived `P11-L05` provenance until the next full same-packet resurvey
- scope: keep the current `dw_wdt` starter honest about what is already validated, name the next kernel-facing checkpoints, and avoid overclaiming platform registration, clock or reset wiring, IRQ handling, or live MMIO behavior before those surfaces exist in Zigux
- current repo reality:
  - `drivers/watchdog/dw_wdt.zig`
  - `drivers/watchdog/dw_wdt_verify.zig`
  - `zigux/tests/phase11_dw_wdt.zig`
  - `zigux/tests/phase11_dw_wdt_manifest.json`
  - `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
  - `zigux/tests/phase11_dw_wdt_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-closure-note.md`
  - `Documentation/zigux/phase11-dw-wdt-slice.md`
  - `Documentation/zigux/phase11-dw-wdt-survey.md`
  - `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `scripts/zigux/README.md`
  - `scripts/zigux/check-phase11-shared-replay-contract.py`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`
  - `scripts/zigux/check-phase11-dw-wdt-packet.py`
  - `zigux/tests/README.md`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers fixed TOP timeout derivation, custom TOP ordering, reset-mode versus IRQ-mode timeout selection, pretimeout bookkeeping, imported running-state snapshots, register-image transitions for start, ping, stop, and restart, the reset-controlled versus continued-heartbeat teardown split, idle remove-time heartbeat preservation versus reset-backed quiesce, a registration-facing handoff that keeps both `watchdog_register_device` intent and the pre-registration `platform_set_drvdata`, reset-control, IRQ-readiness, and imported-running-state split reviewable, a bounded platform-resource preflight summary that keeps named `tclk` versus shared-clock fallback, optional APB clock presence, optional reset-control availability, optional pretimeout-IRQ wiring, and the explicit no-timer-clock block reviewable before any live `devm_*` acquisition, and a dedicated platform-registration scaffold summary that names `module_platform_driver` plus the bounded `dw_wdt_drv_probe`, `dw_wdt_drv_remove`, and `dw_wdt_drv_shutdown` anchors without claiming live platform execution. The live shared Phase 11 packet already couples those `dw_wdt`-specific replays to `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, which keep the focused shared header-boundary packet, the wider shared build route, the parked shared closure checkpoint, and the dedicated DesignWare teardown companion explicit beside this watchdog-local matrix. The dedicated `scripts/zigux/check-phase11-dw-wdt-packet.py` guard now keeps this matrix, the survey note, the manifest-backed survey gate, the registration-scaffold replay, the verify replay, and the shared Phase 11 build wiring fail-closed together instead of relying on prose alone. That teardown companion keeps the stop, teardown, and remove ownership split reviewable from the same packet instead of leaving this matrix to imply it indirectly. This matrix keeps one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which watchdog-core-facing behaviors are already reviewable in bounded form versus still deferred
- which shared replay surfaces on `master` keep this lane aligned with the other shipped Phase 11 starters
- which areas must remain out of scope until a later platform-backed execution and hardware-validation step lands

Without this matrix, the slice, survey, manifest, shared review surfaces, dedicated teardown companion, platform-resource preflight proof, and new platform scaffold summary would not agree on how far the current starter goes before real clock, reset, IRQ, and MMIO work begins.

## Kernel-Integration Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| fixed and custom TOP timeout windows | `drivers/watchdog/dw_wdt.zig` derives fixed TOP timeout windows from the input clock, sorts bounded custom TOP arrays, and exposes the ordered timeout table through `initFixedTops()`, `initCustomTops()`, and `timeoutWindows()` | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the fixed-top limit and custom-ordering checks in `zigux/tests/phase11_dw_wdt.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | keep the same timeout-window evidence stable while the lane chooses the first platform-backed execution follow-up | devicetree TOP parsing, clock acquisition, and hardware-backed timeout programming |
| reset versus IRQ mode timeout selection | `setTimeout()` and `setResponseMode()` keep the reset-mode versus IRQ-mode timeout choice, nearest-TOP selection, and pretimeout bookkeeping reviewable without claiming live interrupt handling | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the reset-mode and IRQ-mode timeout checks in `zigux/tests/phase11_dw_wdt.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | preserve this timeout-selection split when the lane grows platform-backed execution instead of widening into IRQ delivery | live IRQ registration, interrupt delivery, and watchdog-core callback execution |
| imported running-state snapshots | `loadRegisters()`, `syncStateFromRegisters()`, and `runtimeSnapshot()` re-derive running state, response mode, timeout bookkeeping, and time-left snapshots from the bounded register image | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the imported running-state and probe-summary checks in `zigux/tests/phase11_dw_wdt.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | keep the imported-state evidence wired into any later registration-facing handoff or probe execution slice | live MMIO reads, watchdog-core state import, and suspend or resume recovery |
| start, ping, stop, and restart register images | `start()`, `ping()`, `stop()`, and `armRestart()` keep restart kicks, control-bit transitions, timeout-range programming, and restart intent reviewable without claiming live hardware access | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the start, ping, stop, and restart checks in `zigux/tests/phase11_dw_wdt.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | leave the same register-image evidence parked unless another comparably small platform-backed execution slice is needed | live MMIO writes, restart timing, and hardware-backed reboot behavior |
| remove and teardown failure-mode split | `stop()`, `removeSummary()`, and `teardownSummary()` keep the reset-control split explicit by preserving continued-heartbeat behavior when the lane has no reset control, clearing runtime state only when stopping is actually supported, and keeping idle remove-time no-fabricated-heartbeat paths separate from reset-backed quiesce | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the stoppable versus non-stoppable stop checks in `zigux/tests/phase11_dw_wdt.zig` plus the reset-controlled remove, idle-remove, and IRQ-mode teardown-outcome replays in `drivers/watchdog/dw_wdt_verify.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md`; the paired ownership boundaries remain documented in `Documentation/zigux/phase11-dw-wdt-teardown-note.md` | keep this remove-and-teardown boundary stable while the lane stays host-free and execution-light | reset-controller acquisition, reboot notifier ordering, and hardware-backed shutdown behavior |
| probe-time watchdog-core bookkeeping | `probeSummary()` records fixed-versus-custom TOP sourcing, requested timeout origin, nowayout posture, restart priority, stop-on-reboot intent, and already-running watchdog state before registration | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the probe-summary checks in `zigux/tests/phase11_dw_wdt.zig` and the manifest-backed survey assertions in `zigux/tests/phase11_dw_wdt_survey.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | keep the same bookkeeping stable while the lane stays bounded to the current registration-facing handoff | watchdog registration, parent-device lifetime, clock and reset ownership, and IRQ wiring |
| platform resource preflight | `platformResourcePreflightSummary()` keeps named `tclk` versus shared-clock fallback, optional APB clock presence, optional reset-control availability, optional pretimeout-IRQ wiring, and the explicit blocked-no-timer-clock posture reviewable before any live `devm_*` resource acquisition | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the named-`tclk`, shared-fallback, and blocked-no-clock checks in `zigux/tests/phase11_dw_wdt.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | keep this resource-choice evidence stable until one real platform-backed probe step can reuse it without widening past the current starter | live `devm_clk_get_*` calls, reset-controller acquisition, platform IRQ ownership, and MMIO-backed resource programming |
| registration-facing and pre-registration platform handoff | `registrationSummary()` and `platformHandoffSummary()` keep watchdog info selection, parent linkage, timeout-programming intent, the bounded `watchdog_register_device` call, and the pre-registration `platform_set_drvdata`, reset-control, IRQ-readiness, and imported-running-state split reviewable before any live platform-backed driver work | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the registration-summary checks in `zigux/tests/phase11_dw_wdt.zig`, the manifest-backed survey assertions in `zigux/tests/phase11_dw_wdt_survey.zig`, the focused registration-scaffold replay in `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, and the verify-backed no-IRQ pretimeout-flattening, missing-`drvdata`, and blocked-but-reviewable no-IRQ plus no-`drvdata` platform-handoff replays in `drivers/watchdog/dw_wdt_verify.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | keep this handoff truthful while the next step stays limited to one real probe or remove execution slice that reuses this matrix as the hardware-validation plan | actual `platform_device` lifetime, watchdog-core registration side effects, clock and reset acquisition, IRQ ownership, and live MMIO validation |
| platform registration scaffold | `platformRegistrationScaffoldSummary()` now attaches the existing registration-facing handoff and registration-order proof to a bounded `module_platform_driver` scaffold with explicit `dw_wdt_drv_probe`, `dw_wdt_drv_remove`, and `dw_wdt_drv_shutdown` anchors while still deferring any live probe execution | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the internal `drivers/watchdog/dw_wdt.zig` scaffold tests plus the focused platform-registration scaffold replay in `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | keep the named scaffold stable until the lane can land one real probe or remove execution slice with matching clock, reset, IRQ, and validation evidence | platform-driver registration side effects, probe-time resource acquisition, shutdown ordering, and live MMIO validation |
| platform registration and PM behavior | no live Zigux probe or remove execution yet; the current repo now names the bounded platform-registration anchors and keeps the missing execution step explicit in the slice, survey, manifest, and shared replay contract | none beyond the survey or manifest guard that keeps the missing execution work explicit | keep the next step narrowed to one real probe or remove execution slice that reuses this matrix as the hardware-validation plan before any PM or wider MMIO scaffold | platform-driver registration side effects, clock and reset acquisition, IRQ registration, debugfs support, suspend or resume handling, and live MMIO validation |

## Shared Replay Surface

- current shared replay wiring on `master` includes `phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`
- exact shared commands:
  - `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
  - `make -C zigux phase11`
- shared replay posture for this watchdog lane:
  - `phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests` remain the shared Phase 11 artifacts that cover this DesignWare packet
  - the focused shared header-boundary packet from `Documentation/zigux/phase11-uapi-header-parity-survey.md` plus `scripts/zigux/check-phase11-header-boundary-packet.py` stays explicit beside those watchdog-local replays inside the same shipped Phase 11 route
  - full-bundle green status for the wider current Phase 11 replay is intentionally tracked outside this watchdog-local matrix because unrelated non-watchdog drift can reopen elsewhere on `master`
- included DesignWare artifacts:
  - `phase11-dw-wdt-tests`
  - `phase11-dw-wdt-registration-scaffold-tests`
  - `phase11-dw-wdt-verify-tests`
  - `phase11-dw-wdt-survey-tests`
- focused survey replay command:
  - `zig test zigux/tests/phase11_dw_wdt_survey.zig`
- dedicated packet-checker commands:
  - `python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test`
  - `python3 scripts/zigux/check-phase11-dw-wdt-packet.py`

## Review Rules

- treat this lane as a bounded driver-starter plus validation-note lane until platform-backed execution actually lands
- treat this matrix as the current `P11-L11` watchdog-family follow-up until the next full DesignWare same-packet resurvey refreshes the coupled survey note, manifest, survey gate, and packet checker together
- keep `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_build.zig`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` aligned so the DesignWare-local packet checker stays fail-closed around the current starter without reopening broader shared Phase 11 contract surfaces
- keep the dedicated teardown companion aligned with the remove-and-teardown matrix row whenever `stop()`, `teardownSummary()`, or `removeSummary()` change
- keep the platform resource preflight row aligned with `platformResourcePreflightSummary()` whenever timer-clock selection or optional resource-availability proof changes
- keep the platform scaffold row aligned with `platformRegistrationScaffoldSummary()` whenever the probe or remove or shutdown anchor packet changes
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not claim platform-driver registration side effects, watchdog-core registration side effects, clock or reset ownership, IRQ registration, suspend or resume handling, debugfs support, or live MMIO execution until the Zig surface and tests for those behaviors exist
- when the next platform-backed execution step lands, update this matrix, the slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step instead of rediscovering missing scaffold state
