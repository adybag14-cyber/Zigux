# Phase 11 DesignWare Watchdog Lane Sequencing Gap

This note records one bounded truthfulness gap in the live Phase 11 DesignWare
watchdog packet on current `master`.

## Live Readback

- the roadmap still keeps Phase 11 bounded to straightforward driver delivery with teardown and failure-mode parity under `drivers/watchdog/*.zig` and `drivers/tty/hvc/*.zig`
- current direct tree readback still materializes `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, and `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- current direct tree readback still materializes `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- current direct tree readback did not rematerialize `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, or `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `Documentation/zigux/phase11-driver-lane-sequencing.md` already keeps those missing helper, matrix, survey, slice, teardown, replay, and packet-checker surfaces framed as repo-reality gaps, but `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md` still narrates the next slice as if the direct helper pair and direct replay are current-head evidence

## Why This Matters

- this is a DesignWare-local reminder-surface truthfulness miss, not a reason to widen into platform-backed execution
- leaving the lane map overstated makes the next same-lane review noisy because it blurs the smaller current-head docs-and-scaffold packet together with older same-family helper and replay surfaces that the live tree does not currently materialize
- the freeze posture still favors bounded validation and reminder-surface repairs before broader platform registration, PM, IRQ, reset, or MMIO work

## Next Bounded Step

- sync `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md` and the coupled `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py` guard to the narrower current-head DesignWare packet that the live tree actually rematerializes
- keep the manifest, the registration scaffold, the checker pair, and the four directly readable DesignWare continuity notes explicit
- keep the missing validation-matrix, survey, slice, teardown-note, direct helper, direct replay, survey-replay, and dedicated packet-checker surfaces framed as same-lane repo-reality gaps until a fresh reread proves they returned
- keep the next substantive non-doc same-lane step parked on platform-registration scaffolding rather than widening into live watchdog-core or hardware-backed behavior
