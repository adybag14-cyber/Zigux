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
note, validation matrix, build-inventory checker, cleanup-current-head checker,
targetless-unregister witness checker, shared build inventory, and the current
proof-backed adjunct stack.

Public raw fallback readback also restores `drivers/tty/hvc/hvc_console_verify.zig`,
`drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`,
`zigux/tests/phase11_hvc_cleanup.zig`,
`zigux/tests/phase11_hvc_console_survey.zig`,
`zigux/tests/phase11_hvc_console_manifest.json`,
`Documentation/zigux/phase11-hvc-console-teardown-note.md`, and
`scripts/zigux/check-phase11-hvc-survey-packet.py`.

The returned HVC validation matrix and build-inventory checker stay explicit
inside that smaller current-head packet. The standalone targetless-unregister
witness likewise stays directly readable as a separate failure-mode replay, and
the smaller proof-backed HVC continuity packet remains reviewable through the
shared inventory-backed proof routes.

## Drift Kept Explicit

This companion exists so nearby reminders do not keep describing the returned
manifest and teardown note as absent, and do not drop the fallback-backed
verify, sysrq, focused replay, or survey-checker anchors that current `master`
still exposes.

Keep `scripts/zigux/check-phase11-hvc-survey-packet.py` explicit as a returned
fallback-backed checker, but keep the dedicated `make -C zigux phase11-hvc-survey`
route absent until `zigux/Makefile` grows it.

## Boundary Kept Honest

This companion does not claim:

- notifier callback execution
- khvcd worker execution
- tty-driver registration
- live sysrq dispatch
- host-backed teardown or transport parity

It only records that current `master` keeps the returned direct starter, the
returned teardown note and manifest, the fallback-backed helper and replay
anchors, the standalone targetless-unregister witness pair, and the smaller
proof-backed continuity packet reviewable.
