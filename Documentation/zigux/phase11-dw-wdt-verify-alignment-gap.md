# Phase 11 DesignWare Verify Alignment Gap

## Status

- lane: `P11-L11`
- phase: `Phase 11`
- scope: `drivers/watchdog/dw_wdt` deterministic evidence for the surviving DesignWare owner packet
- the surviving directly readable DesignWare owner packet on current `master` is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- current contents reads in this lane still return missing for `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, and `scripts/zigux/check-phase11-dw-wdt-packet.py`
- the current `zigux/tests/phase11_dw_wdt_manifest.json` keeps lane key `P11-L05` pinned to surveyed commit `75f8336c4305beed127d7abfae37d3999b7cc57c`
- the manifest still routes `phase11-dw-wdt-teardown-parity` to `drivers/watchdog/dw_wdt_verify.zig`, so the compile-local verify packet remains part of the DesignWare continuity story even while direct contents reads for that file stay missing in this environment
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` now fails closed on that smaller directly readable owner packet instead of the older matrix-versus-manifest mismatch story

## Why This Note Exists

The Phase 11 roadmap and bootstrap ledger still keep DesignWare inside bounded lifecycle-parity and validation-truthfulness work under `drivers/watchdog/*.zig`. That means the right same-lane follow-up is still tooling that describes the current evidence honestly, not a speculative new driver slice.

Earlier same-lane work assumed the validation matrix, survey note, dedicated replay, and verify helper were all directly readable together. Current `master` no longer supports that story through direct contents reads in this runtime. The packet that remains directly readable is smaller: the platform-registration plan, the manifest-backed gap inventory, and the registration scaffold. The deterministic guard for this lane should therefore fail closed on that smaller packet and keep the compile-local verify destination explicit through the manifest instead of insisting on a stale matrix-versus-manifest mismatch.

## Observed Current-Master Evidence

- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` explicitly records that the driver, verify helper, direct replay, survey note, validation matrix, slice note, teardown note, and dedicated packet checker still read as missing in this runtime and should stay last-known packet members until a future reread confirms them again
- `zigux/tests/phase11_dw_wdt_manifest.json` remains directly readable and still pins the DesignWare packet to lane `P11-L05` with surveyed commit `75f8336c4305beed127d7abfae37d3999b7cc57c`
- the same manifest still records `phase11-dw-wdt-teardown-parity` with Zigux destination `drivers/watchdog/dw_wdt_verify.zig`
- `Documentation/zigux/phase11-driver-lane-sequencing.md` already narrows the shared Phase 11 packet away from the older contract-stack wording and describes the current DesignWare continuity packet as the platform-registration plan plus manifest-backed scaffold
- the active packet should still avoid widening into bcm2835 or gpio work, live platform registration execution, PM or IRQ ownership, clock or reset acquisition behavior, or broader contributor-note churn during this follow-up

## Next Bounded Same-Lane Step

Keep the dedicated verify-alignment guard tied to the current directly readable DesignWare owner packet:

- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`

If future direct rereads rematerialize `drivers/watchdog/dw_wdt_verify.zig`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, or `scripts/zigux/check-phase11-dw-wdt-packet.py`, refresh this note and the checker together before claiming that larger DesignWare packet is directly readable again. Until then, the next substantive non-doc move should remain one platform-registration scaffold step only.
