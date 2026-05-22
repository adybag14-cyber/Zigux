# Phase 11 UAPI Header Parity Checker Coverage Note

## Status

- `PHASE11_UAPI_HEADER_CHECKER_COVERAGE_STATUS=adjacent_current_head_packet_truthful`
- lane: `P11-L07`
- reviewed against current `master` on `2026-05-22`
- scope: record one bounded survey-side truthfulness step inside the shared Phase 11 header-boundary packet without reopening driver-local HVC or watchdog ownership

## Current Packet Evidence

The current shared header-boundary packet on `master` is narrower than the older
shared replay family tracked by earlier continuity.

Current directly readable packet surfaces:
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `zigux/helpers/layout_assert.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/validate-phase11.py`
- `drivers/tty/hvc/hvc_console.h`

Current direct reads still do not rematerialize the older shared replay anchors:
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `zigux/tests/phase11_build.zig`

That means the truthful current-head packet is the smaller HVC-centered proof
stack plus the shared reminder notes, inventory, and validator route rather than
an older cross-driver shared replay family.

## Checker Coverage Posture

There is no longer a same-lane gap to describe as "the dedicated shared
header-boundary checker proves too little," because the dedicated shared checker
itself does not read back on current `master`.

What current `master` does still machine-check is the adjacent current-head
packet:
- `scripts/zigux/check-phase11-build-inventory.py` fail-closes on the exact
  current build inventory, the HVC proof-build roster, the returned
  `phase11-validate` route, and required marker text inside
  `Documentation/zigux/phase11-uapi-header-parity-survey.md` and
  `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `scripts/zigux/validate-phase11.py` reruns that inventory checker together
  with the shared matrix-gap checks and the focused HVC proof builds
- the surviving proof shards keep `struct hv_ops`, `struct winsize`, exported
  `hvc_console.h` helper declarations, and the header constants reviewable as
  bounded current-head evidence

So the active checker-coverage truth on current `master` is indirect and
adjacent: the survey and matrix are kept honest by the shared build-inventory
checker and validator route, not by a returned dedicated
`check-phase11-header-boundary-packet.py` surface.

## Roadmap-Facing Gap

The Phase 11 roadmap still wants honest public-surface validation around simple
watchdog and HVC drivers.
Current `master` only materializes the HVC-centered proof stack directly, so the
remaining same-family gap is broader than a checker-subset mismatch:
- the older cross-driver shared replay family is still absent
- the current packet should not imply that shared `watchdog_info` replay,
  manifest-backed cross-driver coverage, or a dedicated shared header-boundary
  checker have already returned

This note therefore stays useful only if it records that the surviving machine
checks are the adjacent HVC proof packet plus the shared inventory-backed
reminder contract, while the broader shared replay family remains a real repo
reality gap.

## Next Bounded Step

The next honest same-lane follow-up is another survey-side truthfulness reread
only if one of these changes on current `master`:
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/validate-phase11.py`
- the retired shared replay anchors listed above rematerialize

Until then, treat the missing shared manifest, survey source, checker, and build
route as the real header-parity gap rather than inventing a checker-local gap
inside files that no longer ship on `master`.
