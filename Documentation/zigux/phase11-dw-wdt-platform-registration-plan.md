# Phase 11 DesignWare Watchdog Platform Registration Plan

This note records the next bounded follow-up for the live Phase 11 DesignWare watchdog packet on current `master`.

## Why this step belongs next

Current authenticated contents rereads on `master` now keep this owner note, `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_pm.zig`, `drivers/watchdog/dw_wdt_pm_scaffold.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` directly readable for the bounded DesignWare packet.

Current authenticated contents rereads in this run still do not rematerialize `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, or the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle, so keep that broader reminder stack framed as larger same-lane vocabulary until a future reread proves it returned through the same contents bridge.

The live DesignWare packet is therefore no longer just a docs-only owner stack, and it is no longer missing the direct driver or direct replay. It now truthfully centers the directly readable continuity notes, the returned survey note, the returned validation matrix, the returned survey gate, the direct driver-and-test pair, the manifest-backed registration scaffold, the returned restart helper, the returned verify helper, the bounded PM helper pair, and the two current DesignWare truthfulness checkers while leaving the wider slice-note and teardown-note reminder stack unpromoted.

The directly readable owner packet now keeps the bounded lane reviewable through:
- the continuity notes in `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, and `Documentation/zigux/phase11-driver-lane-sequencing.md`
- the current starter-laned gap inventory in `zigux/tests/phase11_dw_wdt_manifest.json`
- the returned survey gate in `zigux/tests/phase11_dw_wdt_survey.zig`, which keeps the survey note and validation matrix lane markers aligned on current-head wording
- the returned direct driver-and-test pair in `drivers/watchdog/dw_wdt.zig` and `zigux/tests/phase11_dw_wdt.zig`, which keep the bounded platform-registration scaffold, timeout-programming readiness, imported-running handoff, restart intent, remove-teardown summaries, and replay alignment reviewable without claiming live platform execution
- the acquisition-facing scaffold in `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, including timer-clock, optional APB clock, reset-release posture, optional pretimeout-IRQ acquisition, imported-running handoff, and the missing timer-clock failure path
- the returned restart helper `drivers/watchdog/dw_wdt_restart.zig`, which keeps missing-drvdata and missing-timeout-image restart blocks explicit beside restart-priority registration, timeout-range and control-register writes, and reset-pulse expectations without widening into live MMIO execution
- the returned verify helper `drivers/watchdog/dw_wdt_verify.zig`, which keeps teardown and failure-mode parity reviewable through the same authenticated packet without promoting a broader reminder stack
- the bounded PM helper pair `drivers/watchdog/dw_wdt_pm.zig` and `drivers/watchdog/dw_wdt_pm_scaffold.zig`
- the dedicated fail-closed companions `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py` and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- this owner note together with `Documentation/zigux/phase11-driver-lane-sequencing.md` as the continuity packet that keeps the surviving DesignWare platform-registration follow-through explicit without widening it into live platform-driver execution or broader hardware-backed closure

The roadmap still keeps this family inside straightforward driver delivery with teardown and failure-mode parity under `drivers/watchdog/*.zig`. The current direct-readback packet is therefore strong enough to justify one bounded same-lane truthfulness or scaffold follow-through, but not strong enough to overclaim that the still-missing slice note, teardown note, or older packet checker are already back on this read path.

Current scaffold readback also already proves one bounded reset-side truthfulness point that this note should preserve: when timeout programming is present and the rest of the acquisition-facing handoff is ready, optional reset-control absence can still remain a ready-to-register scaffold branch while `reset_control_deassert` stays visible as an unrequested outcome rather than an implicit blocker.

## Scope for the next same-lane step

Keep the next implementation or reminder move bounded to one acquisition-facing scaffold or one coupled truthfulness surface inside the surviving DesignWare packet without claiming a full probe path.

The preferred next packet is:
1. keep timer-clock acquisition and optional APB clock acquisition explicit as outcome-bearing scaffold steps
2. keep reset-control availability and reset-release intent explicit as outcome-bearing scaffold steps while preserving the already-readable ready-to-register branch when reset control is absent
3. keep the current manifest, owner notes, survey gate, validation matrix, survey note, direct driver-and-test pair, scaffold, restart helper, verify helper, PM helper pair, and DesignWare checker pair aligned before reopening broader reminder claims
4. leave imported-running-state handoff reviewable inside the scaffold without widening into live platform registration, MMIO execution, or survey-only overclaiming

The scaffold export now keeps optional APB-clock acquisition outcome fields visible beside the existing timer-clock, reset-release, imported-running, and missing-timer-clock summaries so the surviving DesignWare replay stays aligned with the packet note.

## Explicit non-goals

Do not widen this packet into:
- live MMIO reads or writes
- devm-managed resource ownership claims
- IRQ request or handler execution
- suspend or resume behavior beyond the already-readable PM helper summaries
- debugfs support
- devicetree TOP parsing beyond a bounded scaffold summary
- shared Phase 11 reminder-surface churn outside the DesignWare owner packet
- bcm2835 watchdog work, gpio watchdog work, or unrelated Phase 11 console work
- claims that the slice note, teardown note, or older packet-checker handle have returned on this read path without a fresh reread

## Validation target

The next bounded packet should stay publishable with proof that matches what the current contents bridge actually returns:
- keep missing timer-clock acquisition blocked as a distinct scaffold state so the bounded packet does not imply registration is ready before timer-clock acquisition succeeds
- keep optional reset-control absence explicit as a ready-to-register scaffold branch so the bounded packet does not overstate reset wiring as mandatory before host-free registration review
- update this plan note together with `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py` and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` when the directly readable DesignWare packet meaning changes
- keep proof bounded to the checker self-test plus the narrowest truthful reminder or scaffold validation available for the next change
- refresh the shared lane-sequencing note only when a future DesignWare owner-packet change materially changes the shared owner map, not just because the manifest-backed scaffold packet is being restated
- keep the slice note, teardown note, and older packet-checker handle framed as larger same-lane vocabulary until a fresh reread restores those paths through the same authenticated contents bridge

## Recommended file targets

- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`
- `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`
- `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`
- `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `drivers/watchdog/dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt.zig`
- `drivers/watchdog/dw_wdt_restart.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `drivers/watchdog/dw_wdt_pm.zig`
- `drivers/watchdog/dw_wdt_pm_scaffold.zig`
- `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`

## Handoff

If a future run picks up this packet, keep it to one acquisition-facing scaffold, PM-truthfulness, or reminder-surface family only. If clock acquisition becomes directly readable again through the broader driver file, leave reset wiring for the next bounded step. If reset-control follow-through becomes the clearer same-lane gap first, leave broader helper-backed probe work for the next bounded step. When reset control is absent, keep the ready-to-register branch explicit instead of treating reset wiring as a blocked prerequisite. Keep the missing timer-clock failure path explicit until live acquisition exists. Keep the older packet-checker handle framed as historical context until current `master` rematerializes it again.
