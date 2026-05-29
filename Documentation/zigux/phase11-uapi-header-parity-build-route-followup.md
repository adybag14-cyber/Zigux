# Phase 11 UAPI Header Parity Build Route Follow-up

## Status

- `PHASE11_UAPI_HEADER_BUILD_ROUTE_FOLLOWUP_STATUS=phase11_build_present_simple_driver_only`
- lane: `P11-L12`
- reviewed against current `master` on `2026-05-29`
- scope: record the narrow current-head correction after the header-parity current-behavior evidence proved that `zigux/tests/phase11_build.zig` has returned as a simple-driver verification build, not as the retired shared UAPI/header parity replay route

## Roadmap And Ledger Fit

- Phase 11 still centers bounded watchdog and HVC simple production drivers, with hardware validation matrix discipline plus teardown or failure-mode parity.
- The bootstrap ledger's older Phase 3 ABI and UAPI substrate remains relevant background, but it does not by itself prove that the former Phase 11 cross-driver header replay family exists on current `master`.
- This note is therefore a roadmap-truthfulness follow-up only: it updates the evidence story around the build route that actually exists today without claiming a restored shared header-parity replay packet.

## Current-Head Readback

The current-behavior evidence note at `Documentation/zigux/phase11-uapi-header-parity-current-behavior-evidence.md` now records `zigux/tests/phase11_build.zig` at blob `4a7fd056f2e246bc5c81c108ce3a304543441e02`.

Direct readback of that build file shows it wires these simple-driver verification replays:

- `phase11-gpio-wdt-verify-tests`
- `phase11-hvc-console-verify-tests`
- `phase11-simple-drivers`

That means `zigux/tests/phase11_build.zig` should no longer be described as absent in future header-parity notes. The accurate statement is narrower: the path is present again, but it is a gpio/HVC simple-driver verification build and does not rematerialize the retired shared UAPI/header parity manifest, survey source, or cross-driver replay route.

The still-retired shared header-parity anchors remain:

- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`

## Follow-up Rule

When the shared header-parity survey or validation matrix is next refreshed, keep the build-route wording in this shape:

- present: `zigux/tests/phase11_build.zig` as a simple-driver verification build
- not restored: the former cross-driver UAPI/header parity replay family
- still required for a restored shared replay claim: a directly readable shared manifest, shared survey source, and explicit shared replay route

This keeps the P11 header-parity evidence aligned with current repo reality while leaving checker exactness, HVC exported-surface proof behavior, and broader shared-validator ownership with their existing lanes.
