# Phase 11 UAPI Header Parity Checker Coverage Note

## Status

- `PHASE11_UAPI_HEADER_CHECKER_COVERAGE_STATUS=returned_note_side_checker_and_adjacent_packet_truthful`
- lane: `P11-L05`
- reviewed against current `master` on `2026-05-27`
- scope: record one bounded validation-truthfulness step inside the shared Phase 11 header-boundary packet without reopening driver-local HVC or watchdog ownership

## Current Packet Evidence

The current shared header-boundary packet on `master` is still narrower than the
older shared replay family tracked by earlier continuity, but it now includes a
returned dedicated note-side checker alongside the adjacent HVC proof packet.

Current directly readable packet surfaces:
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-checker-coverage-note.md`
- `Documentation/zigux/phase11-uapi-header-parity-hv-ops-followup.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `zigux/helpers/layout_assert.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- `zigux/tests/phase11_hvc_modem_control_proof.zig`
- `zigux/tests/phase11_hvc_modem_control_proof_build.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `scripts/zigux/check-phase11-focused-direct-build-replays.py`
- `scripts/zigux/validate-phase11.py`
- `drivers/tty/hvc/hvc_console.h`
- `drivers/tty/hvc/hvc_console.zig`

Current direct reads still do not rematerialize the older shared replay anchors:
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `zigux/tests/phase11_build.zig`

That means the truthful current-head packet is the smaller HVC-centered proof
stack plus the shared reminder notes, the returned dedicated note-side checker,
the build-inventory guard, and the focused direct-build checker rather than an
older cross-driver shared replay family.

## Checker Coverage Posture

The returned dedicated shared checker now exists, but it is still note-side
evidence only.

What current `master` machine-checks today is:
- `scripts/zigux/check-phase11-header-boundary-packet.py` fail-closes on the
  survey, validation matrix, this checker-coverage note, and the `hv_ops`
  follow-up note through
  `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`
  and `python3 scripts/zigux/check-phase11-header-boundary-packet.py`
- `scripts/zigux/check-phase11-build-inventory.py` fail-closes on the exact
  current build inventory and the returned `phase11-validate` route
- `scripts/zigux/check-phase11-focused-direct-build-replays.py` fail-closes on
  the current modem-control and targetless-unregister direct build replays
- `scripts/zigux/validate-phase11.py` reruns those checker routes together with
  the shared matrix-gap checks and the focused proof-build fan-out

So the active checker-coverage truth on current `master` is layered:
- the returned header-boundary checker keeps the four-note packet truthful
- the build-inventory checker keeps the narrower shared packet fail-closed
- the focused direct-build checker keeps the current modem-control and
  targetless-unregister proof routes machine-checked

None of those routes rematerializes the missing shared manifest, survey source,
or build route by itself.

## Roadmap-Facing Gap

The Phase 11 roadmap still wants honest public-surface validation around simple
watchdog and HVC drivers. Current `master` only materializes the HVC-centered
proof stack directly, so the remaining same-family gap is broader than checker
coverage alone:

- the older cross-driver shared replay family is still absent
- the returned note-side checker does not convert reminder notes into a restored
  shared replay
- the current packet should not imply that shared `watchdog_info` replay or
  manifest-backed cross-driver coverage has already returned
- the shared reminder surfaces outside this note stack still lag the roadmap:
  `scripts/zigux/README.md` and `zigux/tests/README.md` currently skip Phase 11
  between their Phase 10 and Phase 12 packets even though
  `Documentation/zigux/phase11-uapi-header-parity-survey.md`,
  `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`,
  `scripts/zigux/validate-phase11.py`, `zigux/Makefile`, and
  `make -C zigux phase11-validate` are directly readable on current `master`

This note therefore stays useful only if it records that the surviving machine
checks are the returned four-note checker packet, the adjacent HVC proof packet,
the shared inventory-backed reminder contract, and the focused direct-build
checker while the broader shared replay family remains a real repo-reality gap.

## Next Bounded Step

The next honest same-lane follow-up is another survey-side truthfulness reread
only if one of these changes on current `master`:
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-checker-coverage-note.md`
- `Documentation/zigux/phase11-uapi-header-parity-hv-ops-followup.md`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `scripts/zigux/check-phase11-focused-direct-build-replays.py`
- `scripts/zigux/validate-phase11.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- the retired shared replay anchors listed above rematerialize

Until then, treat the missing shared manifest, survey source, and build route as
the real header-parity gap, and treat the missing Phase 11 reminder entries in
`scripts/zigux/README.md` and `zigux/tests/README.md` as the adjacent roadmap-
truthfulness gap rather than inventing a checker-local closure that the current
repo state does not support.
