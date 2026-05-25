# Phase 11 DesignWare Watchdog Lane Sequencing Gap

This note records the bounded reminder-surface truthfulness repair for the live Phase 11 DesignWare watchdog packet on current `master`.

## Live Readback

- the roadmap still keeps Phase 11 bounded to straightforward driver delivery with teardown and failure-mode parity under `drivers/watchdog/*.zig` and `drivers/tty/hvc/*.zig`
- current authenticated contents rereads keep `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_pm.zig`, `drivers/watchdog/dw_wdt_pm_scaffold.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` directly reviewable in this smaller current-head packet
- those same authenticated contents rereads still do not rematerialize `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `drivers/watchdog/dw_wdt.zig`, or `zigux/tests/phase11_dw_wdt.zig`, so keep that broader direct-driver, direct replay, and older reminder stack framed as larger same-lane vocabulary until a future authenticated reread proves it returned through the same contents bridge
- public-tree fallback rereads may still surface some of those broader DesignWare reminder or replay paths, but this note should not mix that fallback visibility into the smaller authenticated current-head packet without naming the different read path explicitly
- the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle remains historical context until a future reread proves it returned
- the stale reminder noise this lane carried was not missing restart, verify, or PM helper coverage anymore; it was readback wording that blurred the smaller authenticated current-head packet together with the larger fallback-visible DesignWare stack

## Why This Matters

- this is a DesignWare-local reminder-surface truthfulness repair, not a reason to widen into platform-backed execution
- cleaning the readback boundary matters because it keeps the next same-lane review focused on the real remaining step: one acquisition-facing platform-registration scaffold or paired truthfulness follow-through inside the still-returned smaller packet
- the freeze posture still favors bounded validation and reminder-surface repairs before broader platform registration, PM, IRQ, reset, or MMIO work

## Result

- the DesignWare continuity packet now treats the authenticated current-head packet and any broader public-tree fallback visibility as separate readback modes instead of presenting them as the same direct-readback surface
- the surviving repo-reality gap inside the authenticated packet is still the broader direct-driver, driver-test, slice, and teardown-note stack together with the older packet-checker handle, not the returned survey note, validation matrix, survey gate, restart helper, verify helper, PM helper pair, manifest-backed scaffold, or paired truthfulness checkers
- the lane can now move forward without mixing fallback-only visibility into the smaller authenticated current-head packet

## Next Bounded Step

- keep the next substantive non-doc move on one acquisition-facing scaffold or one coupled truthfulness surface only inside the still-returned authenticated packet
- keep the manifest, the survey gate, the survey note, the validation matrix, the registration scaffold, the restart helper, the verify helper, the PM helper pair, the reminder packet, and the checker pair explicit
- if a future run uses public-tree fallback to inspect the broader DesignWare stack, record that as fallback evidence instead of promoting it to authenticated current-head readback without a matching contents reread
- keep the older packet-checker handle framed as historical context until a fresh reread proves it returned
- do not widen into live watchdog-core or hardware-backed behavior
