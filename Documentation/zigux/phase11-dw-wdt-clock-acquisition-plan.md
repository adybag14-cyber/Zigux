# Phase 11 DesignWare Watchdog Clock-Acquisition Plan

This note keeps the next same-lane follow-through honest against the current directly readable Phase 11 DesignWare packet on `master`.

## Current Packet Boundary

- current direct contents rereads now materialize `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_pm.zig`, `drivers/watchdog/dw_wdt_pm_scaffold.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- those same direct contents rereads do not currently rematerialize `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, or the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle, so keep that broader slice-note, teardown-note, and older packet-checker reminder stack framed as larger same-lane vocabulary until a future direct reread proves it returned through the same bridge
- keep the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle framed as historical context until a future reread proves it returned
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` keeps named-`tclk`, shared-clock fallback, blocked-no-clock preflight, optional APB clock handling, optional reset-control absence, and registration-order intent explicit without claiming live platform execution
- optional reset-control absence can still remain a ready-to-register scaffold branch while `reset_control_deassert` stays visible as an unrequested outcome rather than an implicit blocker

## Chosen Next Slice

- keep the next same-lane move bounded to one acquisition-facing scaffold or one coupled truthfulness surface inside the returned smaller DesignWare packet
- keep the returned validation matrix, survey note, survey gate, registration scaffold, direct driver-and-test pair, restart helper, returned verify helper, bounded PM helper pair, and paired DesignWare checkers explicit while the slice-note, teardown-note, and older packet-checker reminder stack stays outside this direct contents bridge
- preserve the registration-scaffold proof that optional reset-control absence remains a ready-to-register branch rather than a fabricated blocker

## Non-Goals

- no live MMIO reads or writes
- no reset-control acquisition or release implementation
- no IRQ registration
- no `watchdog_register_device` execution
- no PM, debugfs, suspend or resume, remove or shutdown, or hardware-backed validation claims
- no shared Phase 11 reminder-surface churn outside the DesignWare owner packet
- no claim that the slice note, teardown note, or older packet-checker handle have returned on this direct contents bridge without a fresh reread

## Validation Gate

- keep `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py` aligned with the returned reminder, scaffold, helper, direct-driver, and checker packet before reopening any broader follow-through
- keep optional reset-control absence explicit as a ready-to-register scaffold branch so the bounded packet does not overstate reset wiring as mandatory before host-free registration review
- keep proof bounded to the checker self-test plus the narrowest truthful reminder or scaffold validation available for the next change

## Exit Criteria

- this note keeps the directly readable owner, helper, and direct-driver packet explicit as current-head evidence instead of overclaiming only the still-missing slice note, teardown note, and older packet checker
- the next substantive same-lane step remains one acquisition-facing scaffold or one coupled truthfulness surface only
- the packet still refuses to claim reset ownership, IRQ ownership, watchdog-core registration, PM, debugfs, or live MMIO execution
- the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle remains historical context until a fresh reread proves it returned