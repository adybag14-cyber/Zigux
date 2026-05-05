# Phase 11 BCM2835 Watchdog Validation Matrix

This document records the first bounded hardware-validation matrix for the Zigux `bcm2835_wdt` lane.

## Status

- `PHASE11_BCM2835_WDT_STATUS=hardware_validation_matrix_landed`
- scope: keep the current `bcm2835_wdt` starter honest about what is already validated, name the next kernel-facing checkpoints, and avoid overclaiming platform registration or poweroff plumbing before those behaviors exist in Zigux
- current repo reality:
  - `drivers/watchdog/bcm2835_wdt.zig`
  - `zigux/tests/phase11_bcm2835_wdt.zig`
  - `zigux/tests/phase11_bcm2835_wdt_manifest.json`
  - `zigux/tests/phase11_bcm2835_wdt_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-bcm2835-wdt-slice.md`
  - `Documentation/zigux/phase11-bcm2835-wdt-survey.md`

## Why This Exists

The bounded starter now covers timeout-window validation, running-bit detection, start and stop register-image transitions, restart intent, halt-partition bookkeeping, a tiny probe-time summary, a registration-facing handoff summary, an explicit get-timeleft helper, and a remove-time ownership summary. The live shared Phase 11 packet already couples this watchdog starter to `Documentation/zigux/phase11-shared-replay-contract.md`, which keeps the wider shared replay route explicit beside the dedicated HVC archival surfaces. This matrix keeps one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which poweroff-facing and watchdog-core-facing behaviors are already reviewable in bounded form versus still deferred
- which shared replay surfaces on `master` keep this lane aligned with the rest of the shipped simple-driver packet
- which areas must remain out of scope until a later platform-facing handoff lands

This matrix keeps the current validation posture in one place while the next driver-local step stays below live platform registration.

## Kernel-Integration Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| timeout window and running-state bookkeeping | `drivers/watchdog/bcm2835_wdt.zig` validates timeout bounds, tick conversion, running-bit detection, start and stop register writes, and time-left snapshots through `Bcm2835WatchdogLab.init()`, `loadRegisters()`, `getTimeleft()`, `start()`, `stop()`, and `runtimeSnapshot()` | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the timeout, start, stop, and running-state checks in `zigux/tests/phase11_bcm2835_wdt.zig` inside the shared Phase 11 replay packet recorded by `Documentation/zigux/phase11-shared-replay-contract.md` | keep the same register-image evidence stable while the lane stays parked for another comparably small hardware-validation or handoff note | MMIO-backed register access, platform probe wiring, and live watchdog-core registration |
| restart and halt-partition intent | `armRestart()` and the restart-path coverage in `zigux/tests/phase11_bcm2835_wdt.zig` keep the short reset timeout, full-reset request, and Raspberry Pi halt-partition state reviewable without claiming live restart execution | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the restart-intent checks in `zigux/tests/phase11_bcm2835_wdt.zig` inside the shared Phase 11 replay packet | leave the restart boundary parked unless another similarly small host-free bookkeeping summary is needed | hardware-backed restart timing, PM base plumbing, and board-level reboot behavior |
| probe-time watchdog-core bookkeeping | `probeSummary()` records bootloader-carried running state, nowayout posture, watchdog-core heartbeat-init intent, stop-on-reboot setup, parent linkage, restart priority, and system-power-controller eligibility | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the probe-summary checks in `zigux/tests/phase11_bcm2835_wdt.zig` inside the shared Phase 11 replay packet | keep the same probe-time evidence wired into any future platform-registration handoff summary | live probe ordering, PM base discovery, watchdog parent registration, and watchdog-core side effects |
| registration-facing handoff and poweroff ownership | `registrationSummary()` keeps watchdog registration intent plus poweroff-handler claim-versus-conflict outcomes reviewable without claiming live watchdog-core or poweroff registration | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the registration-summary checks in `zigux/tests/phase11_bcm2835_wdt.zig` inside the shared Phase 11 replay packet | use this bounded handoff as the base for any later platform-registration summary rather than widening straight into poweroff plumbing | live watchdog registration, system poweroff handler installation, and conflicting owner arbitration across real devices |
| explicit get-timeleft parity | `getTimeleft()` now mirrors the C driver's `WDOG_TICKS_TO_SECS` readback over the bounded register image so the lane exposes time-left behavior directly instead of only through the larger runtime snapshot | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the direct `getTimeleft()` checks in `zigux/tests/phase11_bcm2835_wdt.zig` inside the shared Phase 11 replay packet | keep the same helper stable and reuse it if a later platform-facing handoff needs direct time-left wording | live MMIO reads, watchdog-core callback plumbing, and hardware-backed countdown sampling |
| platform registration and PM-base behavior | no live Zigux implementation yet; the current repo only records these as the next kernel-facing checkpoint in the slice, survey, manifest, and shared replay contract | none beyond the survey or manifest guard that keeps the missing work explicit | land one tiny platform-facing handoff note that names registration intent, PM-base ownership, and poweroff boundary rules without claiming hardware-backed execution | platform-driver registration, PM base mapping, hardware-backed timeout programming, watchdog-core device lifetime, and full poweroff integration |

## Review Rules

- treat this lane as a bounded driver-starter plus validation-note lane until a platform-facing handoff actually lands
- keep `Documentation/zigux/phase11-shared-replay-contract.md`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from the shipped shared Phase 11 replay route
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not claim platform-driver registration, PM base wiring, watchdog-core registration, hardware-backed timeout programming, or live poweroff-handler coordination until the Zig surface and tests for those behaviors exist
- when the next platform-facing handoff lands, update this matrix, the slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step
