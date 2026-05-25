# Phase 11 HVC Console Survey

This note keeps the bounded Phase 11 `hvc_console` packet truthful on current
`master`.

## Status

- `PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`
- archival landing lane: `P11-L13`
- current coupled packet continuity: `P11-L16`
- the Phase 11 roadmap still keeps `drivers/tty/hvc/*.zig` inside bounded
  simple-production-driver work where teardown parity and failure-mode
  reviewability should deepen before any live execution claims
- current authenticated contents readback keeps the bounded HVC current-head
  packet reviewable through the direct starter, current survey, current-head
  companion, verify-helper boundary note, validation matrix, the returned
  `phase11-validate` validator surfaces, build-inventory checker,
  focused-direct-build replay checker, cleanup-current-head checker,
  targetless-unregister witness checker, shared build inventory, the
  proof-backed adjunct stack, the dedicated modem-control proof pair, and the
  standalone targetless-unregister witness pair
- current authenticated contents readback still does not rematerialize
  `drivers/tty/hvc/hvc_console_verify.zig`,
  `drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`,
  `zigux/tests/phase11_hvc_cleanup.zig`,
  `zigux/tests/phase11_hvc_console_survey.zig`,
  `zigux/tests/phase11_hvc_console_manifest.json`,
  `Documentation/zigux/phase11-hvc-console-teardown-note.md`, or
  `scripts/zigux/check-phase11-hvc-survey-packet.py`; keep those anchors framed
  as repo-reality gaps or archival vocabulary instead of returned fallback
  evidence until a future reread proves they returned
- `zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey`
  route, so keep the current route claim bounded to `make -C zigux phase11-validate`

## Current-Head Packet

Treat the current bounded HVC packet on `master` as:

- `.github/workflows/zigux-bootstrap.yml`
- `drivers/tty/hvc/hvc_console.zig`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-focused-direct-build-replays.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/validate-phase11.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase11_build_inventory.json`
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

The shared build-inventory checker, focused-direct-build replay checker, and
shared build inventory still record the three proof-backed build tests while
keeping the dedicated modem-control and standalone targetless-unregister build
routes explicit as direct-readback checks instead of promoting either pair into
that shared three-entry inventory. `scripts/zigux/validate-phase11.py`,
`zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` keep the same
validator-backed route directly readable on current `master` too. Keep the
dedicated survey route absent until `zigux/Makefile` grows it explicitly. The
dedicated modem-control proof pair likewise stays directly readable as a
focused adjunct route without promoting itself into the shared three-entry
build inventory, and the standalone targetless-unregister witness pair likewise
stays directly readable as a separate failure-mode replay without promoting
itself into the shared three-entry build inventory.

## Still-Bounded Gaps

Keep `Documentation/zigux/phase11-hvc-console-slice.md` and a dedicated
`make -C zigux phase11-hvc-survey` route framed as remaining gaps until a
future reread proves they returned.

Keep `drivers/tty/hvc/hvc_console_verify.zig`,
`drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`,
`zigux/tests/phase11_hvc_cleanup.zig`,
`zigux/tests/phase11_hvc_console_survey.zig`,
`zigux/tests/phase11_hvc_console_manifest.json`,
`Documentation/zigux/phase11-hvc-console-teardown-note.md`, and
`scripts/zigux/check-phase11-hvc-survey-packet.py` framed as repo-reality gaps
or archival vocabulary until a future reread proves they returned.

Keep the lane below live tty registration, notifier callback execution, khvcd
execution, live sysrq dispatch, and host-backed teardown parity.

## Bounded Meaning

This note records that the HVC simple-driver lane still has reviewable
current-head continuity through the direct starter, the current companion stack,
the verify-boundary reminder surface, the shared inventory-backed proof routes,
the focused-direct-build replay checker, the validator-backed
`make -C zigux phase11-validate` route, the dedicated modem-control proof pair,
and the standalone targetless-unregister witness pair.

It does not claim that the currently missing verify helper, sysrq helper,
focused survey replay, manifest, teardown note, or dedicated survey checker
have returned, nor does it claim live tty-driver registration, notifier
callback execution, khvcd polling execution, live sysrq dispatch, host-backed
cleanup, or hardware-validated teardown parity.
