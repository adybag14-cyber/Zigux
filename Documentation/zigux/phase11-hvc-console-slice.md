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
* `drivers/tty/hvc/hvc_console_verify.zig`
* `drivers/tty/hvc/hvc_console_sysrq.zig`
* `zigux/tests/phase11_hvc_console.zig`
* `zigux/tests/phase11_hvc_cleanup.zig`
* `zigux/tests/phase11_hvc_console_manifest.json`
* `zigux/tests/phase11_hvc_console_modem_control_split.zig`
* `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
* `zigux/tests/phase11_hvc_console_survey.zig`
* `Documentation/zigux/phase11-hvc-console-survey.md`
* `Documentation/zigux/phase11-hvc-console-slice.md`
* `Documentation/zigux/phase11-hvc-console-teardown-note.md`
* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`

Current `master` also materializes direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions.
The archival packet keeps those direct replay, verify, and cleanup surfaces explicit instead of presenting them as a repo-reality gap or as proof of broader runtime closure.

## Teardown And Failure-Mode Cues

The parked starter keeps these bounded summaries explicit:

* `hvc_cleanup()` tty-port release handoff summary
* port-reference drop timing
* cleanup-time tty-port ownership
* tiny notifier-add open handoff summary
* khvcd polling-contract summary
* `hvc_hangup()` disconnect summary
* `hvc_kick()` wakeup cue
* notifier-IRQ helper surface
* the direct verify, replay, and cleanup companion surfaces that current `master` now materializes beside the archival survey gate

Those cues stay limited to the host-free archival packet.
They do not claim runtime callback delivery or live hypervisor transport execution.
