# Phase 11 HVC Verify Helper Boundary

This note records the helper-facing failure-mode packet now materialized in `drivers/tty/hvc/hvc_console_verify.zig`.

It keeps the current HVC simple-driver lane honest without widening into live tty registration, notifier callback execution, khvcd worker execution, live sysrq dispatch, or host-backed transport behavior.

Current direct contents reads on `master` now rematerialize `drivers/tty/hvc/hvc_console_verify.zig`, so keep this note aligned with the helper itself and treat the helper as current-head evidence for the bounded failure-mode edges listed below.

## Verify Helper Coverage

- `drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove handoff explicit without implying live `hvc_remove()` execution.
- `drivers/tty/hvc/hvc_console_verify.zig` keeps the remove handoff explicit when tty teardown outlives console binding, preserving hangup-driven teardown without implying live `hvc_remove()` execution.
- `error.CleanupRequiresFinalCloseOrHangup` keeps cleanup-time tty-port release evidence tied to a prior final-close or hangup boundary instead of drifting into unconditional cleanup claims.
- `CleanupTrigger.hangup_only` and `CleanupTrigger.final_close_and_hangup` keep the hangup-only and combined cleanup trigger split explicit beside the earlier final-close-only path.
- `error.NotifierDispatchRequiresTtyRegistration` keeps notifier prerequisite failures explicit instead of implying sysrq-triggered notifier dispatch can occur before tty registration.
- `NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.
- `NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable without claiming that notifier teardown has become live runtime behavior.
- `targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.
- `targetless_dispatch_with_notifier_sanitized` keeps registered-but-targetless sysrq fallback visible without implying notifier callbacks can still fire after the target disappears.
- `SysrqLiteralFallbackSummary.literal_byte_retained` keeps the non-kernel sysrq literal fallback explicit instead of letting a plain byte path read like live sysrq execution.
- the literal-fallback helpers keep the targetless sysrq path without notifier, the sanitized registered-but-targetless sysrq path, and the non-kernel sysrq literal fallback explicit without promoting the lane to live sysrq execution.

## Packet Relationship

- `Documentation/zigux/phase11-hvc-console-survey.md` keeps the broader HVC packet vocabulary visible while the live current-head packet now reads through `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `scripts/zigux/check-phase11-build-inventory.py`, and the proof-backed adjunct files instead of treating the deeper verify helper as archival vocabulary.
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md` keeps cleanup prerequisite failures, the targetless notifier no-unregister edge, and targetless sysrq dispatch reviewable at the shared packet level.
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` together with `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` keeps the targetless notifier no-unregister edge, the sanitized targetless-unregister request, the registered-but-targetless sysrq fallback edge, and the targetless sysrq boundary tied to returned current-head evidence.
- current HVC current-head reads now keep those landed helper edges reviewable through both this note and `drivers/tty/hvc/hvc_console_verify.zig` itself, while deeper sysrq helpers or older manifest-side companions remain separate follow-up surfaces until they return directly.
- this note narrows one current-head reminder surface so the detached-binding remove-handoff branch, notifier prerequisite failure edge, extra verify-helper failure-mode details, and the standalone targetless-unregister witness packet stay reviewable without forcing the broader survey note or validation matrix to carry every helper-local detail.

## Guardrails

- keep this note coupled to `drivers/tty/hvc/hvc_console_verify.zig` and the already-landed survey and validation packet
- do not treat the helper as evidence of live notifier callbacks, tty registration, khvcd execution, live sysrq dispatch, or host-backed teardown
- if the verify helper adds or removes cleanup-trigger, notifier-unregister, detached-binding remove-handoff, notifier-prerequisite, or sysrq-literal-fallback edges, update this note together with any dedicated checker that guards it
