# Phase 11 HVC Cleanup Prerequisite Parity Gap

This note keeps one narrow HVC teardown-parity edge explicit on current
`master`: the helper-local cleanup-prerequisite trigger split that gates
`hvc_cleanup()` reviewability without claiming live host-backed teardown
execution.

## Status

- `PHASE11_HVC_CLEANUP_PREREQUISITE_STATUS=current_head_trigger_split_reviewable`
- lane: `P11-L16`
- scope: keep the `summarizeCleanupPrerequisite()` trigger split and its
  failure mode explicit beside the current HVC cleanup packet
- this note stays below live tty-port release execution, notifier callback
  execution, khvcd execution, sysrq execution, or a claim that
  `Documentation/zigux/phase11-hvc-console-teardown-note.md` has returned

## Current Evidence

- `drivers/tty/hvc/hvc_console.zig` keeps `CleanupTrigger.final_close_only`,
  `CleanupTrigger.hangup_only`, and `CleanupTrigger.final_close_and_hangup`
  explicit through `summarizeCleanupPrerequisite()`
- the same helper keeps `error.CleanupRequiresFinalCloseOrHangup` explicit when
  neither final-close nor hangup evidence is present
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig` already rereads the
  cleanup-prerequisite trigger split through the final-close-only, hangup-only,
  combined-trigger, and missing-prerequisite cases
- `Documentation/zigux/phase11-hvc-console-survey.md` and
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md` keep this note
  and its checker explicit as a helper-local teardown-parity companion instead
  of widening the HVC packet into live cleanup claims

## Route Posture

- keep `make -C zigux phase11-validate` as the shared returned Phase 11 route
- keep `python3 scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py --self-test`
  and `python3 scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py`
  explicit as this note's fail-closed companion checker
- keep `Documentation/zigux/phase11-hvc-console-teardown-note.md` framed as a
  repo-reality gap until a future reread proves it returned

## Non-Goals

- this note does not claim that live `hvc_cleanup()` execution is replayed on
  current `master`
- this note does not promote the helper-local trigger split into a dedicated
  `make -C zigux phase11-hvc-survey` route
- this note does not claim host-backed teardown parity, live tty registration
  parity, or deeper HVC closure