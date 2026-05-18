# Phase 11 HVC Verify Helper Boundary

This note records the helper-facing failure-mode packet previously landed in `drivers/tty/hvc/hvc_console_verify.zig`.

It keeps the current HVC simple-driver lane honest without widening into live tty registration, notifier callback execution, khvcd worker execution, live sysrq dispatch, or host-backed transport behavior.

Current direct contents reads on `master` still do not rematerialize `drivers/tty/hvc/hvc_console_verify.zig`, so keep this note as the current-head reminder surface for those landed helper edges rather than treating the helper file itself as returned direct-readback evidence.

## Verify Helper Coverage

- `drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove handoff explicit without implying live `hvc_remove()` execution.
- `drivers/tty/hvc/hvc_console_verify.zig` keeps the remove handoff explicit when tty teardown outlives console binding, preserving hangup-driven teardown without implying live `hvc_remove()` execution.
- `error.CleanupRequiresFinalCloseOrHangup` keeps cleanup-time tty-port release evidence tied to a prior final-close or hangup boundary instead of drifting into unconditional cleanup claims.
- `CleanupTrigger.hangup_only` and `CleanupTrigger.final_close_and_hangup` keep the hangup-only and combined cleanup trigger split explicit beside the earlier final-close-only path.
- `error.NotifierDispatchRequiresTtyRegistration` keeps notifier prerequisite failures explicit instead of implying sysrq-triggered notifier dispatch can occur before tty registration.
- `NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.
- `NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable without claiming that notifier teardown has become live runtime behavior.
- `targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.
- the literal-fallback helpers keep both the sanitized targetless sysrq path and the non-kernel sysrq literal fallback explicit without promoting the lane to live sysrq execution.

## Packet Relationship

- `Documentation/zigux/phase11-hvc-console-survey.md` keeps the archived HVC packet and its direct verify companion explicit beside the starter, split replays, and sysrq helper.
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md` keeps cleanup prerequisite failures, the targetless notifier no-unregister edge, and targetless sysrq dispatch reviewable at the shared packet level.
- current HVC current-head reads keep those landed helper edges reviewable through this note and the coupled survey and validation packet, while `drivers/tty/hvc/hvc_console_verify.zig` itself remains survey-recorded archival vocabulary until a future reread proves the helper returned.
- this note narrows one direct companion surface so the detached-binding remove-handoff branch, notifier prerequisite failure edge, and extra verify-helper failure-mode details stay reviewable without forcing the broader survey note or validation matrix to carry every helper-local detail.

## Guardrails

- keep this note coupled only to the landed `drivers/tty/hvc/hvc_console_verify.zig` helper history and the already-landed survey and validation packet
- do not treat this note as proof that `drivers/tty/hvc/hvc_console_verify.zig` has returned to direct current-head readback
- do not treat this note as evidence of live notifier callbacks, tty registration, khvcd execution, live sysrq dispatch, or host-backed teardown
- if the verify helper adds or removes cleanup-trigger, notifier-unregister, detached-binding remove-handoff, notifier-prerequisite, or sysrq-literal-fallback edges, update this note together with any dedicated checker that guards it
