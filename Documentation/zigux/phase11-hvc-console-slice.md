# Phase 11 HVC Console Slice

This slice keeps the bounded `hvc_console` starter focused on teardown and failure-mode reviewability.
It stays inside the archival Phase 11 HVC lane and does not widen into tty registration, notifier callback execution, khvcd execution, or host-backed transport claims.

## Status

* `PHASE11_HVC_CONSOLE_SLICE_STATUS=starter_packet_archived`
* lane: `P11-L16`
* scope: keep the landed teardown and failure-mode packet readable beside the shared Phase 11 replay route

## Landed Starter Surface

The current bounded HVC archival packet is reviewed through:

* `drivers/tty/hvc/hvc_console.zig`
* `zigux/tests/phase11_hvc_console.zig`
* `drivers/tty/hvc/hvc_console_verify.zig`
* `zigux/tests/phase11_hvc_cleanup.zig`
* `zigux/tests/phase11_hvc_console_manifest.json`
* `zigux/tests/phase11_hvc_console_modem_control_split.zig`
* `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
* `zigux/tests/phase11_hvc_console_survey.zig`
* `drivers/tty/hvc/hvc_console_sysrq.zig`
* `Documentation/zigux/phase11-hvc-console-survey.md`
* `Documentation/zigux/phase11-hvc-console-teardown-note.md`
* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`

These archival packet surfaces keep the bounded starter's teardown and failure-mode story reviewable through the shipped starter, helper, split, survey, teardown, validation, direct replay, verify, and cleanup surfaces, without widening into tty registration, notifier callback execution, khvcd execution, or host-backed transport claims.

## Teardown And Failure-Mode Cues

The parked starter keeps these bounded summaries explicit:

* `hvc_cleanup()` tty-port release handoff summary
* port-reference drop timing
* tiny notifier-add open handoff summary
* `hvc_kick()` wakeup cue
* notifier-IRQ helper surface
* direct verify-only coverage beside `drivers/tty/hvc/hvc_console_verify.zig`
* direct replay-only coverage beside `zigux/tests/phase11_hvc_console.zig`
* cleanup-teardown coverage beside `zigux/tests/phase11_hvc_cleanup.zig`

Those cues stay limited to the host-free archival packet.
They do not claim runtime callback delivery or live hypervisor transport execution.
