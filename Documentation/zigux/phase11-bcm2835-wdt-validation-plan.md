# Phase 11 BCM2835 Watchdog Validation Plan
This note records the bounded validation plan that must exist before the current Zigux `bcm2835_wdt` starter widens into live platform-registration, PM-base, watchdog-core, or shared poweroff-handler behavior. It keeps the archival `P11-L08` packet honest by turning the already-documented blocked step into a directly reviewable reminder surface on current `master`.

## Status
- `PHASE11_BCM2835_WDT_VALIDATION_PLAN_STATUS=plan_landed`
- archival packet identity remains `P11-L08`
- roadmap phase: `Phase 11`
- scope: keep live platform registration, PM-base plumbing, watchdog-core lifecycle wiring, shared poweroff-handler coordination, and hardware-backed execution blocked behind explicit evidence
- current directly readable bcm2835 packet for this plan:
  - `drivers/watchdog/bcm2835_wdt.zig`
  - `drivers/watchdog/bcm2835_wdt_verify.zig`
  - `zigux/tests/phase11_bcm2835_wdt.zig`
  - `zigux/tests/phase11_bcm2835_wdt_survey.zig`
  - `zigux/tests/phase11_bcm2835_wdt_manifest.json`
  - `Documentation/zigux/phase11-bcm2835-wdt-slice.md`
  - `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
  - `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
  - `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

## Why This Exists
The current survey note, slice note, and validation matrix already say the next honest bcm2835-only follow-through is one explicit validation plan. This file makes that blocked step concrete so future same-lane work can widen only after the repo names the exact proof surfaces up front instead of implying platform-backed closure from the current starter packet.

## Required Evidence Before Widening
| wider surface | minimum new proof before landing | must stay blocked until |
| --- | --- | --- |
| live platform registration | direct driver helpers plus replay coverage for parent attachment, `pm_base` handoff, and `devm_watchdog_register_device` success-versus-failure outcomes | a dedicated bcm2835-only replay and verify packet proves the same registration states without widening into other Phase 11 drivers |
| PM-base plumbing | direct proof for the `pm_base` read or write boundary and the bounded prerequisites that feed `restart()` or `poweroff()` intent | the same packet shows how PM-base readiness changes behavior without claiming live MMIO execution |
| watchdog-core lifecycle wiring | direct proof for timeout init, `nowayout`, stop-on-reboot, and restart-priority bookkeeping once the starter goes beyond summary-only behavior | the widened driver packet keeps watchdog-core bookkeeping reviewable beside the bcm2835-only tests and verify helper |
| shared poweroff-handler coordination | direct proof for claim, conflict, install, release, and remove-side ownership transitions around `pm_power_off` | the widened packet names the callback installation and release rules explicitly instead of inferring them from the current ownership summaries |
| hardware-backed execution | direct hardware-validation evidence or an explicitly bounded lab substitute that is stronger than the current register-image summaries | the lane records the exact execution substitute and keeps platform-backed claims out of the survey note and validation matrix until that evidence lands |

## Review Guardrails
- Treat this plan as a blocker note for future bcm2835 widening, not as proof that live platform registration, PM-base plumbing, watchdog-core lifecycle wiring, shared poweroff-handler coordination, or hardware-backed execution are already implemented.
- Keep this plan aligned with `zigux/tests/phase11_bcm2835_wdt_manifest.json`, especially the `phase11-bcm2835-wdt-live-platform-registration` blocked gap, whenever the same blocked platform-registration story changes.
- Refresh this plan together with `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`, and `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` if a later lane widens the bcm2835 packet past the current starter-plus-replay-plus-verify-plus-survey surface.

## Next Bounded Step
The next honest bcm2835-only follow-through is to land one future widening step only after the new driver or replay surface satisfies the matching row in this plan. Until then, keep the current packet bounded to the directly readable starter, dedicated replay, compile-local verify helper, dedicated survey gate, manifest-backed reminder packet, and the blocker surfaces documented here.
