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
  companion, verify-helper boundary note, validation matrix, build-inventory
  checker, cleanup-current-head checker, targetless-unregister witness checker,
  shared build inventory, and the proof-backed adjunct stack
- public raw fallback readback also restores `drivers/tty/hvc/hvc_console_verify.zig`,
  `drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`,
  `zigux/tests/phase11_hvc_cleanup.zig`,
  `zigux/tests/phase11_hvc_console_survey.zig`,
  `zigux/tests/phase11_hvc_console_manifest.json`,
  `Documentation/zigux/phase11-hvc-console-teardown-note.md`, and
  `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey`
  route, so keep the current route claim bounded to `make -C zigux phase11-validate`

## Current-Head Packet

Treat the current bounded HVC packet on `master` as:

- `drivers/tty/hvc/hvc_console.zig`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `drivers/tty/hvc/hvc_console_sysrq.zig`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_console.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`

The shared build-inventory checker plus shared build inventory still record
three proof-backed build tests, the coupled `exact_current_checks` list, and
the `workflow_phase11_steps` entry that routes this packet through
`make -C zigux phase11-validate`. Keep the dedicated survey route absent unless
`zigux/Makefile` grows it explicitly.

## Still-Bounded Gaps

Keep `Documentation/zigux/phase11-hvc-console-slice.md` and a dedicated
`make -C zigux phase11-hvc-survey` route framed as remaining gaps until a
future reread proves they returned.

Keep the lane below live tty registration, notifier callback execution, khvcd
execution, live sysrq dispatch, and host-backed teardown parity.

## Bounded Meaning

This note records that the HVC simple-driver lane still has reviewable
current-head continuity through the direct starter, the raw-fallback verify and
sysrq helpers, the returned teardown note and manifest, the focused console and
cleanup replays, the survey checker, the proof-backed adjunct replays, and the
standalone targetless-unregister witness pair.

It does not claim live tty-driver registration, notifier callback execution,
khvcd polling execution, live sysrq dispatch, host-backed cleanup, or
hardware-validated teardown parity.
