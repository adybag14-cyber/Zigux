# Phase 11 DesignWare Watchdog Platform Registration Plan

This note records the next bounded follow-up for the live Phase 11 DesignWare watchdog packet on current `master`.

## Why this step belongs next

Current direct contents reads on `master` now keep this owner note,
`Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`,
`Documentation/zigux/phase11-dw-wdt-provenance-readback.md`,
`Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`,
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-dw-wdt-survey.md`,
`Documentation/zigux/phase11-dw-wdt-slice.md`,
`Documentation/zigux/phase11-dw-wdt-teardown-note.md`,
`zigux/tests/phase11_dw_wdt_manifest.json`,
`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`,
`zigux/tests/phase11_dw_wdt.zig`,
`zigux/tests/phase11_dw_wdt_survey.zig`,
`drivers/watchdog/dw_wdt.zig`,
`drivers/watchdog/dw_wdt_verify.zig`,
`scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and
`scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` directly readable for
the bounded DesignWare packet.

Keep the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle framed as
historical context until a future reread proves it returned. The live DesignWare
packet is no longer just a docs-and-scaffold owner stack: the direct helper,
verify helper, replay, survey replay, validation matrix, slice, survey, and
teardown note are all current-head evidence again.

The directly readable owner packet now keeps the bounded lane reviewable through:
- the current starter-laned gap inventory in `zigux/tests/phase11_dw_wdt_manifest.json`
- the acquisition-facing scaffold in `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, including timer-clock, optional APB clock, reset-release posture, optional pretimeout-IRQ acquisition, imported-running handoff, and the missing timer-clock failure path
- the direct helper pair `drivers/watchdog/dw_wdt.zig` and `drivers/watchdog/dw_wdt_verify.zig`
- the direct replay pair `zigux/tests/phase11_dw_wdt.zig` and `zigux/tests/phase11_dw_wdt_survey.zig`
- the directly readable reminder packet in `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, and `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- the dedicated fail-closed companions `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py` and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- this owner note together with `Documentation/zigux/phase11-driver-lane-sequencing.md` as the continuity packet that keeps the surviving DesignWare platform-registration follow-through explicit without widening it into live platform-driver execution or broader hardware-backed closure

The roadmap still keeps this family inside straightforward driver delivery with teardown and failure-mode parity under `drivers/watchdog/*.zig`. That means the honest next step is still to attach the existing registration-facing handoff to one acquisition-facing platform-registration scaffold without widening into live clock, reset, IRQ, PM, or MMIO behavior.

Current scaffold readback also already proves one bounded reset-side truthfulness point that this note should preserve: when timeout programming is present and the rest of the acquisition-facing handoff is ready, optional reset-control absence can still remain a ready-to-register scaffold branch while `reset_control_deassert` stays visible as an unrequested outcome rather than an implicit blocker.

## Scope for the first platform-backed step

Keep the next implementation bounded to one acquisition-facing scaffold inside
the surviving DesignWare packet without claiming a full probe path.

The preferred first packet is:
1. model timer-clock acquisition and optional APB clock acquisition as explicit outcome-bearing steps
2. model reset-control availability and reset-release intent as explicit outcome-bearing steps while preserving the already-readable ready-to-register branch when reset control is absent
3. reuse the existing ordering around `platform_set_drvdata`, timeout-programming intent, stop-on-reboot intent, restart-priority sequencing, and `watchdog_register_device`
4. keep imported-running-state handoff reviewable when the timer starts hot

## Explicit non-goals

Do not widen this first scaffold into:
- live MMIO reads or writes
- devm-managed resource ownership claims
- IRQ request or handler execution
- suspend or resume behavior
- debugfs support
- devicetree TOP parsing beyond a bounded preflight summary
- shared Phase 11 reminder-surface churn outside the DesignWare owner packet
- bcm2835 watchdog work, gpio watchdog work, or unrelated Phase 11 console work

## Validation target

The first scaffold packet should stay publishable with bounded proof only:
- keep missing timer-clock acquisition blocked as a distinct scaffold state so the bounded packet does not imply registration is ready before timer-clock acquisition succeeds
- keep optional reset-control absence explicit as a ready-to-register scaffold branch so the bounded packet does not overstate reset wiring as mandatory before host-free registration review
- update this plan note together with `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py` and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` when the live DesignWare packet meaning changes
- keep proof bounded to the checker self-test plus the narrowest truthful Zig-side review available for the next scaffold change
- refresh the shared lane-sequencing note only when a future DesignWare owner-packet change materially changes the shared owner map, not just because the live manifest-backed scaffold packet is being restated
- Phase 11 shared build replay only as a truthfulness check, not as a claim that hardware-backed behavior is complete

## Recommended file targets

- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`
- `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`
- `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-slice.md`
- `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
- `drivers/watchdog/dw_wdt.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`

## Handoff

If a future run picks up this packet, keep it to one acquisition-facing helper
or summary family only.
If clock acquisition lands first, leave reset wiring for the next bounded step.
If reset acquisition lands first, leave clock-path execution for the next
bounded step. When reset control is absent, keep the ready-to-register branch
explicit instead of treating reset wiring as a blocked prerequisite. Keep the
missing timer-clock failure path explicit until live acquisition exists.
Keep the directly readable registration scaffold, helper pair, replay pair,
and reminder packet explicit while the next implementation step stays inside one
platform-registration helper family. Keep the older packet-checker handle framed
as historical context until current `master` rematerializes it again.