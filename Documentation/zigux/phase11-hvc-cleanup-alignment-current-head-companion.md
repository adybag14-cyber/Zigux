# Phase 11 HVC Cleanup Alignment Current-Head Companion

This note records the bounded current-head readback for the Phase 11 HVC
cleanup-alignment packet.

## Status

- `PHASE11_STATUS=current_head_companion_landed`
- surveyed against current `master` readback
- scope: keep the current HVC cleanup-alignment reminder truthful without
  widening into notifier callback execution, khvcd execution, tty registration,
  sysrq execution, or host-backed teardown

## Current Repo Reality

Current `master` keeps the bounded HVC continuity packet reviewable through the
direct starter, current survey note, current companion, verify-helper boundary
note, validation matrix, build-inventory checker, focused-direct-build replay
checker, cleanup-current-head checker, targetless-unregister witness checker,
shared build inventory, and the current proof-backed adjunct stack.

Current authenticated contents readback still does not rematerialize
`drivers/tty/hvc/hvc_console_verify.zig`,
`drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`,
`zigux/tests/phase11_hvc_cleanup.zig`,
`zigux/tests/phase11_hvc_console_survey.zig`,
`zigux/tests/phase11_hvc_console_manifest.json`,
`Documentation/zigux/phase11-hvc-console-teardown-note.md`, or
`scripts/zigux/check-phase11-hvc-survey-packet.py`; keep those older helper,
replay, manifest, note, and checker anchors framed as repo-reality gaps or archival vocabulary
instead of returned fallback evidence.

The returned HVC validation matrix, focused-direct-build replay checker, and
build-inventory checker stay explicit inside that smaller current-head packet.
The standalone targetless-unregister witness likewise stays directly readable
through `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` and
`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` as a separate failure-mode replay,
while the dedicated modem-control proof pair and the targetless-unregister
witness build routes stay jointly fail-closed by
`scripts/zigux/check-phase11-focused-direct-build-replays.py` without
promoting either pair into the shared three-entry build inventory, and the
smaller proof-backed HVC continuity packet remains reviewable through the
shared inventory-backed proof routes.

That same smaller proof-backed packet also keeps cleanup-prerequisite trigger
parity explicit through `error.CleanupRequiresFinalCloseOrHangup` together with
`CleanupTrigger.final_close_only`, `CleanupTrigger.hangup_only`, and
`CleanupTrigger.final_close_and_hangup`, so teardown evidence stays bounded to
preconditions instead of drifting into unconditional `hvc_cleanup()` claims.

## Drift Kept Explicit

This companion exists so nearby reminders do not keep describing the currently
missing manifest and teardown note as returned, and do not reintroduce
stale returned-file claims for the missing verify helper, sysrq helper, focused
replay, or dedicated survey-checker anchors that current `master` still does
not expose.

Keep `scripts/zigux/check-phase11-hvc-survey-packet.py` explicit as a current
repo-reality gap, but keep the dedicated `make -C zigux phase11-hvc-survey`
route absent until `zigux/Makefile` grows it.

## Boundary Kept Honest

This companion does not claim:

- notifier callback execution
- khvcd worker execution
- tty-driver registration
- live sysrq dispatch
- host-backed teardown or transport parity

It only records that current `master` keeps the direct starter, the verify
boundary reminder, the standalone targetless-unregister witness pair, the
focused-direct-build replay checker, the dedicated modem-control proof pair,
and the smaller proof-backed continuity packet reviewable while the older
helper, survey-replay, manifest,
teardown-note, and survey-checker anchors remain absent on current head.
