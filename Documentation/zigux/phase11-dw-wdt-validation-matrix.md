# Phase 11 DesignWare Watchdog Validation Matrix

This matrix keeps the current bounded validation packet for the Zigux `dw_wdt` lane explicit.

## Status

- `PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`
- current surveyed packet pin: `75f8336c4305beed127d7abfae37d3999b7cc57c`
- active watchdog continuity for this matrix and its coupled survey packet is `P11-L10`
- scope: keep the current DesignWare owner packet honest, name the next kernel-facing checkpoint, and avoid overclaiming live platform registration, clock or reset execution, IRQ delivery, or hardware-backed MMIO behavior before those surfaces are directly readable on current `master`

## Current Evidence

- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, and `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md` keep the smaller authenticated current-head packet and its readback boundary explicit.
- `zigux/tests/phase11_dw_wdt_manifest.json` and `zigux/tests/phase11_dw_wdt_survey.zig` keep the lane-local packet fail closed on current-head truth.
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` keeps timer-clock choice, optional APB clock presence, reset-release posture, imported-running handoff, optional pretimeout IRQ acquisition, and the missing-timer-clock block reviewable before live platform execution lands.
- `drivers/watchdog/dw_wdt.zig` and `zigux/tests/phase11_dw_wdt.zig` now rematerialize on current `master` and keep timer-clock choice, registration-order intent, imported-running handoff, timeout-programming readiness, restart intent, and replay alignment reviewable alongside the smaller owner packet without claiming live platform execution.
- `drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/watchdog/dw_wdt_pm.zig`, and `drivers/watchdog/dw_wdt_pm_scaffold.zig` keep restart, teardown-parity, and bounded PM-helper handoff coverage reviewable inside the same smaller packet.
- `Documentation/zigux/phase11-dw-wdt-survey.md` keeps the same packet summary readable for reviewers.

## Current Readback Boundary

- Authenticated current-head rereads in this environment still do not rematerialize `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, or the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle.
- Treat that broader reminder stack as larger same-lane vocabulary or fallback-visible evidence until a future authenticated reread proves it returned through the same bridge.
- Keep the direct driver-and-test pair explicit inside the authenticated packet rather than repeating older missing-file wording after those paths have already returned.

## Shared Gap And Next Step

- `zigux/tests/phase11_build.zig` is still a shared current-head gap rather than live lane evidence here.
- The next bounded same-lane follow-up remains the manifest-marked ready-next step: hardware-backed MMIO validation around suspend, resume, and platform-backed probe or remove execution, without widening into unrelated driver behavior.

## Non-Goals

- no claim that live platform registration side effects are already executing
- no claim that clock or reset execution, IRQ delivery, or hardware-backed MMIO validation has already landed
- no promotion of the still-missing slice-note, teardown-note, or older packet-checker reminder stack to authenticated current-head evidence without a fresh reread
- no migration of this driver-local packet into a broader shared Phase 11 reminder surface
