# Phase 11 HVC Console Validation Matrix

This document records the bounded current-head validation matrix for the Zigux
`hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=current_head_companion_packet_truthful`
- lane: `P11-L17`
- reviewed against live `master`
- archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- scope: keep the current HVC console validation and teardown packet truthful
  without widening into live tty registration, notifier callback execution,
  khvcd worker execution, live sysrq dispatch, or host-backed teardown
- the current matrix packet now stays aligned with the smaller
  authenticated-readback companion stack rather than the older starter-depth
  public-readback packet

## Current-Head Matrix Packet

Treat the directly reviewable current-head matrix packet as:

- `drivers/tty/hvc/hvc_console.zig`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`

Current authenticated contents reads do not rematerialize
`drivers/tty/hvc/hvc_console_verify.zig`,
`drivers/tty/hvc/hvc_console_sysrq.zig`,
`zigux/tests/phase11_hvc_console.zig`,
`zigux/tests/phase11_hvc_cleanup.zig`,
`zigux/tests/phase11_hvc_console_survey.zig`,
`zigux/tests/phase11_hvc_console_manifest.json`,
`Documentation/zigux/phase11-hvc-console-slice.md`,
`Documentation/zigux/phase11-hvc-console-teardown-note.md`, or
`scripts/zigux/check-phase11-hvc-survey-packet.py`, so the matrix should keep
those deeper anchors framed as archival or repo-reality-gap vocabulary rather
than current-head direct-readback evidence.

## Current-Head Matrix

| lane surface | current evidence | bounded gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| starter and companion stack | the current starter remains directly readable through `drivers/tty/hvc/hvc_console.zig`, while the coupled survey, companion, matrix, cleanup-current-head checker, shared build inventory, and proof-backed adjuncts keep the smaller current-head packet explicit | keep the survey, matrix, checker, proof, and inventory aligned with that smaller packet instead of reviving absent deeper anchors | if a future reread restores one deeper HVC helper, replay, manifest, or checker path, refresh the whole current-head packet in one bounded pass | live tty registration, notifier callback execution, khvcd worker execution, live sysrq dispatch, and host-backed teardown |
| helper-local failure-mode edges | `drivers/tty/hvc/hvc_console.zig` keeps starter-backed targetless notifier, wakeup-cue, notifier-irq, and modem-control helper surfaces reviewable, while `Documentation/zigux/phase11-hvc-verify-helper-boundary.md` keeps the deeper cleanup-trigger, notifier-unregister, targetless-dispatch, and detached remove-handoff history explicit without treating `drivers/tty/hvc/hvc_console_verify.zig` as a returned direct-readback anchor | preserve the starter-backed helper cues in `hvc_console.zig` and the deeper helper-local cleanup, notifier-unregister, targetless-dispatch, and remove-handoff wording in the boundary note without treating the absent verify helper as a current-head file | if `drivers/tty/hvc/hvc_console_verify.zig` returns on a future reread, refresh this matrix and the coupled note together | treating helper-local review history as proof of live notifier or sysrq execution |
| proof-backed adjuncts | `zigux/tests/fixtures/phase11_build_inventory.json` still records exactly three proof-backed build tests and no dedicated survey replay entries, while the exported-surface proof/build pair, the `hv_ops` proof/build pair, and the cleanup-packet proof/build pair remain directly readable | keep the proof inventory exact and keep the proof-backed adjunct list narrow | if a future reread restores dedicated survey or cleanup replay files, land that expansion together with an inventory refresh | reconstructing a larger replay family from older wording alone |
| route and checker boundary | `scripts/zigux/check-phase11-hvc-cleanup-current-head.py` remains directly readable, but `scripts/zigux/check-phase11-hvc-survey-packet.py` and a dedicated `make -C zigux phase11-hvc-survey` route do not | keep the current-head checker explicit and keep the absent dedicated survey checker and route out of the current packet | if the dedicated checker or route returns, refresh the matrix and survey together | reviving route or checker claims from historical wording alone |

## Failure-Mode Evidence

- `drivers/tty/hvc/hvc_console.zig` remains present and keeps CRLF framing,
  flush intent, final-close teardown, tty-registration handoff, notifier-add
  open handoff, khvcd polling-contract, khvcd worker-entry, khvcd
  sleep-and-reschedule handoff, `__hvc_poll` drain-order, `hvc_hangup()`
  disconnect, `hvc_remove()` handoff, `hvc_cleanup()` tty-port release,
  targetless notifier, `hvc_kick()` wakeup-cue, notifier-irq, and
  modem-control helper summaries reviewable on current `master`.
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md` keeps the helper
  history for cleanup prerequisite failures, detached-binding remove handoff,
  notifier-unregister timing, and targetless sysrq fallback explicit without
  treating `drivers/tty/hvc/hvc_console_verify.zig` as a returned current-head
  anchor.
- the proof-backed adjuncts keep the exported-surface proof/build pair, the
  `hv_ops` proof/build pair, and the current-head cleanup proof/build pair
  explicit without implying a broader replay roster.

## Replay Posture

- treat the current matrix packet as the smaller authenticated-readback
  companion stack listed above
- do not treat the deeper verify helper, sysrq helper, manifest, teardown note,
  dedicated survey checker, or focused survey and cleanup replays as
  current-head direct-readback evidence
- keep `zigux/Makefile` explicit only as the returned file; it still does not
  prove a dedicated `phase11-hvc-survey` route

## Review Rules

- do not claim live notifier callback execution, tty registration, khvcd worker
  execution, live sysrq dispatch, or host-backed teardown from this matrix
- if the authenticated HVC packet changes, update the matrix together with the
  coupled survey, checker, proof, or inventory in one bounded pass
- keep helper-local failure-mode edges reviewable through the boundary note
  until direct current-head readback restores the missing helper file
