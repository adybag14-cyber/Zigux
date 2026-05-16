# Phase 11 HVC Verify Helper Boundary

This note records the direct helper-facing failure-mode packet already landed in `drivers/tty/hvc/hvc_console_verify.zig`.

It keeps the current HVC simple-driver lane honest without widening into live tty registration, notifier callback execution, khvcd worker execution, live sysrq dispatch, or host-backed transport behavior.

## Verify Helper Coverage

- `drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove handoff explicit without implying live `hvc_remove()` execution.
- `error.CleanupRequiresFinalCloseOrHangup` keeps cleanup-time tty-port release evidence tied to a prior final-close or hangup boundary instead of drifting into unconditional cleanup claims.
- `CleanupTrigger.hangup_only` and `CleanupTrigger.final_close_and_hangup` keep the hangup-only and combined cleanup trigger split explicit beside the earlier final-close-only path.
- `NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.
- `NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable without claiming that notifier teardown has become live runtime behavior.
- `targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.
- the literal-fallback helpers keep both the sanitized targetless sysrq path and the non-kernel sysrq literal fallback explicit without promoting the lane to live sysrq execution.

## Packet Relationship

- `Documentation/zigux/phase11-hvc-console-survey.md` keeps the archived HVC packet and its direct verify companion explicit beside the starter, split replays, and sysrq helper.
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md` keeps cleanup prerequisite failures, the targetless notifier no-unregister edge, and targetless sysrq dispatch reviewable at the shared packet level.
- this note narrows one direct companion surface so the extra verify-helper failure-mode edges stay reviewable without forcing the broader survey note or validation matrix to carry every helper-local detail.

## Guardrails

- keep this note coupled only to `drivers/tty/hvc/hvc_console_verify.zig` and the already-landed survey and validation packet
- do not treat this note as evidence of live notifier callbacks, tty registration, khvcd execution, live sysrq dispatch, or host-backed teardown
- if the verify helper adds or removes cleanup-trigger, notifier-unregister, or sysrq-literal-fallback edges, update this note together with any dedicated checker that guards it
