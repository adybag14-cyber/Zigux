# Phase 11 HVC Console Validation Matrix

This document records the bounded current-head validation matrix for the Zigux
`hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=current_head_companion_packet_truthful`
- lane: `P11-L16`
- reviewed against live `master`
- scope: keep the current HVC console validation and teardown packet truthful
  without widening into live tty registration, notifier callback execution,
  khvcd worker execution, live sysrq dispatch, or host-backed teardown
- the current matrix packet now stays aligned with the smaller
  authenticated-readback companion stack while the raw fallback readback keeps
  the returned teardown and replay anchors explicit

## Current-Head Matrix Packet

Treat the current matrix packet as:

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

Authenticated contents reads may still flap on the deeper helper and replay
paths, but public raw fallback readback re-materializes them. Treat those files
as fallback-backed current-head evidence, and keep route claims bounded to
`make -C zigux phase11-validate` until `zigux/Makefile` exposes a dedicated
`make -C zigux phase11-hvc-survey` step.

## Failure-Mode Evidence

- `drivers/tty/hvc/hvc_console.zig` keeps flush intent, final-close teardown,
  tty-registration handoff, `hvc_install()` ownership, `hvc_alloc()` slot
  selection, early console setup and device selection, `__hvc_resize()`
  handoff, notifier-add open handoff, khvcd polling-contract, khvcd worker-entry,
  khvcd sleep-and-reschedule handoff, `__hvc_poll` drain-order,
  `hvc_hangup()` disconnect, `hvc_remove()` handoff, `hvc_cleanup()` tty-port
  release, targetless notifier, `hvc_kick()` wakeup-cue, notifier-irq, and
  modem-control helper summaries reviewable on current `master`.
- `Documentation/zigux/phase11-hvc-console-teardown-note.md` and
  `zigux/tests/phase11_hvc_console_manifest.json` have returned on current
  `master`, so teardown-parity evidence no longer needs to describe them as
  absent.
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md` keeps helper-local
  failure-mode edges reviewable through the verify helper boundary note.
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` and
  `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` keep the
  targetless-unregister witness explicit as standalone direct-readback coverage.

## Replay Posture

- keep `make -C zigux phase11-validate` as the returned shared route
- keep the dedicated survey route absent until `zigux/Makefile` grows it
- keep helper-local failure-mode edges reviewable through the verify boundary
  note and the returned teardown note
- keep public raw fallback readback explicit when current contents reads still
  flap on the deeper HVC helper and replay files
