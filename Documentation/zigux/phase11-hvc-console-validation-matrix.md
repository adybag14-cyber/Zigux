# Phase 11 HVC Console Validation Matrix

This document records the bounded current-head validation matrix for the Zigux
`hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=current_head_companion_packet_truthful`
- lane: `P11-L16`
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
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`

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
| helper-local failure-mode edges | `drivers/tty/hvc/hvc_console.zig` keeps starter-backed targetless notifier, sanitized targetless-unregister, wakeup-cue, notifier-irq, and modem-control helper surfaces reviewable, while `Documentation/zigux/phase11-hvc-verify-helper-boundary.md` keeps the deeper cleanup-trigger, targeted notifier-unregister timing, targetless-dispatch, and detached remove-handoff history explicit without treating `drivers/tty/hvc/hvc_console_verify.zig` as a returned direct-readback anchor; the standalone `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` plus `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` witness shard now rereads the live starter and the boundary note together so the current targetless-unregister sanitizer alignment stays directly reviewable without widening the shared packet | preserve the starter-backed targetless notifier and sanitized targetless-unregister cues in `hvc_console.zig`, the deeper helper-local cleanup, targeted notifier-unregister, targetless-dispatch, and remove-handoff wording in the boundary note, and the standalone witness shard that exact-rereads the current targetless-unregister sanitizer alignment without treating the absent verify helper as a current-head file | if `drivers/tty/hvc/hvc_console_verify.zig` returns on a future reread, refresh this matrix, the coupled note, and the standalone witness together before deciding whether that witness still needs to stay separate from the smaller shared packet | treating helper-local review history as proof of live notifier or sysrq execution |
| proof-backed adjuncts | `zigux/tests/fixtures/phase11_build_inventory.json` still records exactly three proof-backed build tests and no dedicated survey replay entries, while the exported-surface proof/build pair, the `hv_ops` proof/build pair, and the cleanup-packet proof/build pair remain directly readable; the targetless-unregister witness stays a separate direct-readback replay rather than part of that shared three-proof inventory | keep the shared build inventory exact and keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet unless the inventory, checker, and workflow expand together in a later bounded pass | if a future reread promotes the witness into the shared packet or restores dedicated survey or cleanup replay files, land that expansion together with an inventory refresh | reconstructing a larger replay family from older wording alone |
| route and checker boundary | `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, and `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` remain directly readable, while `scripts/zigux/check-phase11-hvc-survey-packet.py` and a dedicated `make -C zigux phase11-hvc-survey` route do not; the standalone targetless-unregister witness build shard is directly readable, its focused route is still exercised by both `.github/workflows/zigux-bootstrap.yml` and `zigux/Makefile` `phase11-validate`, and the dedicated targetless-unregister witness checker now keeps the survey, validation matrix, shared build inventory, shared validator, and returned `phase11-validate` route aligned while intentionally remaining outside the shared build-inventory route set for now | keep the build-inventory checker, the current-head cleanup checker, and the dedicated targetless-unregister witness checker explicit, keep the bootstrap workflow self-testing and running the shared build-inventory guard before the shared proof replay set, and keep the separate targetless-unregister witness exercised as a standalone route rather than promoting it into a shared route claim | if the dedicated survey checker or route returns, refresh the matrix and survey together; if the shared build-inventory packet expands again, refresh the checker and inventory in one bounded pass | reviving route or checker claims from historical wording alone |

## Failure-Mode Evidence

- `drivers/tty/hvc/hvc_console.zig` remains present and keeps CRLF framing,
  flush intent, final-close teardown, tty-registration handoff,
  `hvc_install()` ownership, `hvc_alloc()` slot selection, early console setup
  and device selection, `__hvc_resize()` handoff, notifier-add open handoff,
  khvcd polling-contract, khvcd worker-entry, khvcd sleep-and-reschedule
  handoff, `__hvc_poll` drain-order, `hvc_hangup()` disconnect,
  `hvc_remove()` handoff, `hvc_cleanup()` tty-port release, targetless
  notifier and sanitized targetless-unregister handling, `hvc_kick()`
  wakeup-cue, notifier-irq, and modem-control helper summaries reviewable on
  current `master`.
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md` keeps the helper
  history for cleanup prerequisite failures, detached-binding remove handoff,
  targeted notifier-unregister timing, and targetless sysrq fallback explicit
  without treating `drivers/tty/hvc/hvc_console_verify.zig` as a returned
  current-head anchor.
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` and
  `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` now keep the
  live targetless-unregister witness explicit as a standalone direct-readback
  replay that rereads the current starter and the boundary note together
  without widening the shared build-inventory packet, and the same witness route
  is still exercised through both `.github/workflows/zigux-bootstrap.yml` and
  `make -C zigux phase11-validate`.
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` now keeps
  that standalone witness aligned across the validation matrix, survey, shared
  build inventory, shared validator, and returned `phase11-validate` route
  without promoting the witness into the shared proof inventory.
- `scripts/zigux/check-phase11-build-inventory.py` now stays part of the
  directly reviewable packet together with the shared build inventory JSON,
  keeping the workflow-backed proof inventory fail-closed before the current-head
  cleanup proof replay.
- the proof-backed adjuncts keep the exported-surface proof/build pair, the
  `hv_ops` proof/build pair, and the current-head cleanup proof/build pair
  explicit without implying a broader replay roster.

## Replay Posture

- treat the current matrix packet as the smaller authenticated-readback
  companion stack listed above, including the live build-inventory checker and
  its shared JSON companion
- keep the targetless-unregister witness explicit as a standalone direct-readback
  replay that keeps the current notifier-edge alignment explicit without
  promoting it to the shared proof inventory or a dedicated survey route claim
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
- keep the standalone targetless-unregister witness aligned with the driver and
  boundary note until either the shared packet expands or the missing verify
  helper returns on current-head reread
- keep helper-local failure-mode edges reviewable through the boundary note
  until direct current-head readback restores the missing helper file