# Phase 11 DesignWare Watchdog Lane Sequencing Gap

This note records the bounded reminder-surface truthfulness repair for the live Phase 11 DesignWare watchdog packet on current `master`.

## Live Readback

- the roadmap still keeps Phase 11 bounded to straightforward driver delivery with teardown and failure-mode parity under `drivers/watchdog/*.zig` and `drivers/tty/hvc/*.zig`
- current direct tree readback materializes `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, and `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
- current direct tree readback also materializes `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle remains historical context until a future reread proves it returned
- the stale reminder noise this lane carried was not missing helper coverage anymore; it was outdated wording that still described returned DesignWare helper, replay, and matrix surfaces as repo-reality gaps

## Why This Matters

- this is a DesignWare-local reminder-surface truthfulness repair, not a reason to widen into platform-backed execution
- cleaning the stale wording matters because it keeps the next same-lane review focused on the real remaining step: one acquisition-facing platform-registration scaffold
- the freeze posture still favors bounded validation and reminder-surface repairs before broader platform registration, PM, IRQ, reset, or MMIO work

## Result

- the shared lane note and the DesignWare owner note now treat the returned DesignWare helper, replay, and reminder surfaces as current-head evidence again
- the surviving repo-reality gap in this reminder family is the older packet-checker handle, not the direct DesignWare helper pair or replay pair
- the lane can now move forward without mixing stale missing-file language into the next scaffold review

## Next Bounded Step

- keep the next substantive non-doc move on one platform-backed acquisition scaffold only
- keep the manifest, the registration scaffold, the helper pair, the replay pair, the reminder packet, and the checker pair explicit
- keep the older packet-checker handle framed as historical context until a fresh reread proves it returned
- do not widen into live watchdog-core or hardware-backed behavior
