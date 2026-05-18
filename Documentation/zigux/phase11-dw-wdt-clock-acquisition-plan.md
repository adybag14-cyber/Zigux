# Phase 11 DesignWare Watchdog Clock-Acquisition Plan

This note keeps the next `drivers/watchdog/dw_wdt.zig` follow-through honest
against the current directly readable Phase 11 DesignWare packet on `master`.

## Current Packet Boundary

- current direct contents rereads still materialize `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- current direct contents rereads do not rematerialize `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, or `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so keep them framed as last-known packet members or repo-reality gaps instead of current-head evidence
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` keeps named-`tclk`, shared-clock fallback, blocked-no-clock preflight, optional APB clock handling, optional reset-control absence, and registration-order intent explicit without claiming live platform execution
- optional reset-control absence can still remain a ready-to-register scaffold branch while `reset_control_deassert` stays visible as an unrequested outcome rather than an implicit blocker

## Chosen Next Slice

- before reopening driver-backed code, keep the clock-acquisition story parked on the registration scaffold and this note's fail-closed owner map
- when `drivers/watchdog/dw_wdt.zig` rematerializes again, land only one timer-clock acquisition helper that records named-`tclk` success, shared-clock fallback success, and blocked-no-clock failure
- keep that first helper pre-registration, pre-IRQ, pre-PM, pre-reset-acquisition, and pre-MMIO
- do not describe the direct helper pair or the direct replay as already returned until a fresh reread proves it

## Non-Goals

- no APB clock acquisition beyond the already-readable scaffold summary
- no reset-control acquisition or release implementation
- no IRQ registration
- no `watchdog_register_device` execution
- no PM, debugfs, suspend or resume, remove or shutdown, or hardware-backed validation claims
- no shared Phase 11 reminder-surface churn outside the DesignWare owner packet

## Validation Gate

- keep `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py` aligned with the narrower current-head packet before reopening driver-backed follow-through
- preserve the registration-scaffold proof that model reset-control availability and reset-release intent as explicit outcome-bearing steps while preserving the already-readable ready-to-register branch when reset control is absent
- keep optional reset-control absence explicit as a ready-to-register scaffold branch so the bounded packet does not overstate reset wiring as mandatory before host-free registration review
- when the direct driver pair and replay return, add focused Zig validation on the exact `dw_wdt.zig` surface before publication

## Exit Criteria

- this note no longer treats `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, or the missing validation matrix as current-head evidence
- the next substantive same-lane code step remains one timer-clock acquisition helper only
- the packet still refuses to claim reset ownership, IRQ ownership, watchdog-core registration, PM, debugfs, or live MMIO execution
