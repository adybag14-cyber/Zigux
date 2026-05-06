# Phase 11 DesignWare Watchdog Validation Matrix

This document records the first bounded hardware-validation matrix for the Zigux `dw_wdt` lane.

## Status

- `PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`
- scope: keep the current `dw_wdt` starter honest about what is already validated, name the next kernel-facing checkpoints, and avoid overclaiming platform registration, clock or reset wiring, IRQ handling, or live MMIO behavior before those surfaces exist in Zigux
- current repo reality:
  - `drivers/watchdog/dw_wdt.zig`
  - `zigux/tests/phase11_dw_wdt.zig`
  - `zigux/tests/phase11_dw_wdt_manifest.json`
  - `zigux/tests/phase11_dw_wdt_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-dw-wdt-slice.md`
  - `Documentation/zigux/phase11-dw-wdt-survey.md`
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `scripts/zigux/README.md`
  - `scripts/zigux/check-phase11-shared-replay-contract.py`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`
  - `zigux/tests/README.md`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers fixed TOP timeout derivation, custom TOP ordering, reset-mode versus IRQ-mode timeout selection, pretimeout bookkeeping, imported running-state snapshots, register-image transitions for start, ping, stop, and restart, the non-stoppable stop boundary when reset control is unavailable, and a registration-facing handoff that keeps `watchdog_register_device` intent reviewable. The live shared Phase 11 packet already couples those `dw_wdt`-specific replays to `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, which keep the focused shared header-boundary packet and the wider shared build route explicit beside this watchdog-local matrix. This matrix keeps one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which watchdog-core-facing behaviors are already reviewable in bounded form versus still deferred
- which shared replay surfaces on `master` keep this lane aligned with the other shipped Phase 11 starters
- which areas must remain out of scope until a later platform-backed registration and hardware-validation step lands

Without this matrix, the slice, survey, manifest, and shared review surfaces would not agree on how far the current starter goes before real platform-backed work begins.

## Kernel-Integration Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| fixed and custom TOP timeout windows | `drivers/watchdog/dw_wdt.zig` derives fixed TOP timeout windows from the input clock, sorts bounded custom TOP arrays, and exposes the ordered timeout table through `initFixedTops()`, `initCustomTops()`, and `timeoutWindows()` | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the fixed-top limit and custom-ordering checks in `zigux/tests/phase11_dw_wdt.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | keep the same timeout-window evidence stable while the lane chooses the first platform-backed registration follow-up | devicetree TOP parsing, clock acquisition, and hardware-backed timeout programming |
| reset versus IRQ mode timeout selection | `setTimeout()` and `setResponseMode()` keep the reset-mode versus IRQ-mode timeout choice, nearest-TOP selection, and pretimeout bookkeeping reviewable without claiming live interrupt handling | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the reset-mode and IRQ-mode timeout checks in `zigux/tests/phase11_dw_wdt.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | preserve this timeout-selection split when the lane grows platform-backed registration instead of widening into IRQ execution | live IRQ registration, interrupt delivery, and watchdog-core callback execution |
| imported running-state snapshots | `loadRegisters()`, `syncStateFromRegisters()`, and `runtimeSnapshot()` re-derive running state, response mode, timeout bookkeeping, and time-left snapshots from the bounded register image | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the imported running-state and probe-summary checks in `zigux/tests/phase11_dw_wdt.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | keep the imported-state evidence wired into any later registration-facing handoff summary | live MMIO reads, watchdog-core state import, and suspend or resume recovery |
| start, ping, stop, and restart register images | `start()`, `ping()`, `stop()`, and `armRestart()` keep restart kicks, control-bit transitions, timeout-range programming, and restart intent reviewable without claiming live hardware access | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the start, ping, stop, and restart checks in `zigux/tests/phase11_dw_wdt.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | leave the same register-image evidence parked unless another comparably small handoff summary is needed | live MMIO writes, restart timing, and hardware-backed reboot behavior |
| non-stoppable stop semantics | `stop()` keeps the reset-control split explicit by preserving hardware-running state when the lane has no reset control and clearing runtime state only when stopping is actually supported | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the stoppable versus non-stoppable stop checks in `zigux/tests/phase11_dw_wdt.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | keep this stop boundary stable while the lane stays host-free and registration-first | reset-controller acquisition, reboot notifier ordering, and hardware-backed shutdown behavior |
| probe-time watchdog-core bookkeeping | `probeSummary()` records fixed-versus-custom TOP sourcing, requested timeout origin, nowayout posture, restart priority, stop-on-reboot intent, and already-running watchdog state before registration | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the probe-summary checks in `zigux/tests/phase11_dw_wdt.zig` and the manifest-backed survey assertions in `zigux/tests/phase11_dw_wdt_survey.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | keep the same bookkeeping stable while the lane stays bounded to the current registration-facing handoff | watchdog registration, parent-device lifetime, clock and reset ownership, and IRQ wiring |
| registration-facing handoff | `registrationSummary()` now keeps watchdog info selection, parent linkage, timeout-programming intent, and the bounded `watchdog_register_device` call reviewable before any live platform-backed driver work | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the new registration-summary checks in `zigux/tests/phase11_dw_wdt.zig` and the manifest-backed survey assertions in `zigux/tests/phase11_dw_wdt_survey.zig`, kept on the shared Phase 11 route by `Documentation/zigux/phase11-shared-replay-contract.md` | attach this handoff to platform-backed registration scaffolding plus a hardware-validation plan | actual `platform_device` lifetime, watchdog-core registration side effects, clock and reset acquisition, and IRQ ownership |
| platform registration and PM behavior | no live Zigux implementation yet; the current repo only records these as the next kernel-facing checkpoint in the slice, survey, manifest, and shared replay contract | none beyond the survey or manifest guard that keeps the missing work explicit | keep the next step narrowed to one platform-backed registration and hardware-validation plan before any PM or MMIO scaffold | platform-driver registration, clock and reset acquisition, IRQ registration, debugfs support, suspend or resume handling, and live MMIO validation |

## Shared Replay Surface

- current shared replay wiring on `master` includes both `phase11-dw-wdt-tests` and `phase11-dw-wdt-survey-tests`
- exact shared commands:
  - `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
  - `make -C zigux phase11`
- shared replay posture for this watchdog lane:
  - `phase11-dw-wdt-tests` and `phase11-dw-wdt-survey-tests` remain the shared Phase 11 artifacts that cover this DesignWare packet
  - the focused shared header-boundary packet from `Documentation/zigux/phase11-uapi-header-parity-survey.md` plus `scripts/zigux/check-phase11-header-boundary-packet.py` stays explicit beside those watchdog-local replays inside the same shipped Phase 11 route
  - full-bundle green status for the wider current Phase 11 replay is intentionally tracked outside this watchdog-local matrix because unrelated non-watchdog drift can reopen elsewhere on `master`
- included DesignWare artifacts:
  - `phase11-dw-wdt-tests`
  - `phase11-dw-wdt-survey-tests`
- focused survey replay command:
  - `zig test zigux/tests/phase11_dw_wdt_survey.zig`

## Review Rules

- treat this lane as a bounded driver-starter plus validation-note lane until platform-backed registration scaffolding actually lands
- keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from the shipped shared Phase 11 replay route or the focused shared header-boundary packet
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not claim platform-driver registration, watchdog-core registration side effects, clock or reset ownership, IRQ registration, suspend or resume handling, debugfs support, or live MMIO execution until the Zig surface and tests for those behaviors exist
- when the next platform-backed registration step lands, update this matrix, the slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step
