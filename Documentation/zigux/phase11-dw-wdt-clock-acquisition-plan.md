# Phase 11 DesignWare Watchdog Clock-Acquisition Plan

This note keeps the next `drivers/watchdog/dw_wdt.zig` follow-through honest
against the current directly readable Phase 11 DesignWare packet on `master`.

## Current Packet Boundary

- current direct contents rereads now materialize `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- keep the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle framed as historical context until a future reread proves it returned
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` keeps named-`tclk`, shared-clock fallback, blocked-no-clock preflight, optional APB clock handling, optional reset-control absence, and registration-order intent explicit without claiming live platform execution
- optional reset-control absence can still remain a ready-to-register scaffold branch while `reset_control_deassert` stays visible as an unrequested outcome rather than an implicit blocker

## Chosen Next Slice

- keep the next code move bounded to one timer-clock acquisition helper inside the returned `drivers/watchdog/dw_wdt.zig` packet
- when that helper lands, record named-`tclk` success, shared-clock fallback success, and blocked-no-clock failure without widening into registration, IRQ, PM, reset execution, or MMIO behavior
- keep the returned direct helper pair, replay pair, validation matrix, teardown note, and checker pair explicit while the next helper stays pre-registration and host-free
- preserve the registration-scaffold proof that optional reset-control absence remains a ready-to-register branch rather than a fabricated blocker

## Non-Goals

- no APB clock acquisition beyond the already-readable scaffold summary
- no reset-control acquisition or release implementation
- no IRQ registration
- no `watchdog_register_device` execution
- no PM, debugfs, suspend or resume, remove or shutdown, or hardware-backed validation claims
- no shared Phase 11 reminder-surface churn outside the DesignWare owner packet

## Validation Gate

- keep `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py` aligned with the returned helper, replay, reminder, scaffold, and checker packet before reopening driver-backed follow-through
- preserve the registration-scaffold proof that models reset-control availability and reset-release intent as explicit outcome-bearing steps while preserving the already-readable ready-to-register branch when reset control is absent
- keep optional reset-control absence explicit as a ready-to-register scaffold branch so the bounded packet does not overstate reset wiring as mandatory before host-free registration review
- when the next helper lands in the already-returned direct driver pair, add focused Zig validation on the exact `dw_wdt.zig` surface before publication

## Exit Criteria

- this note keeps the returned `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, and the paired DesignWare checkers explicit as current-head evidence
- the next substantive same-lane code step remains one timer-clock acquisition helper only
- the packet still refuses to claim reset ownership, IRQ ownership, watchdog-core registration, PM, debugfs, or live MMIO execution
- the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle remains historical context until a fresh reread proves it returned
