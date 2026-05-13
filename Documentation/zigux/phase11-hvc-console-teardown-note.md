# Phase 11 HVC Console Teardown Note

This note restores the missing teardown-parity checkpoint for the bounded Phase 11 `hvc_console` packet on current `master`.
It stays inside the simple-driver lane and records only the host-free teardown and failure-mode surfaces that the shipped HVC survey packet already replays.

## Status

* `PHASE11_HVC_CONSOLE_TEARDOWN_STATUS=cleanup_handoff_archived`
* teardown evidence remains bounded to the landed HVC starter packet
* remaining follow-through is still live tty-driver registration, notifier callback execution, khvcd execution, live sysrq dispatch, and host-backed transport or teardown validation

## Teardown Packet

The current teardown-facing HVC packet on `master` is:

* `drivers/tty/hvc/hvc_console.zig`
* `drivers/tty/hvc/hvc_console_verify.zig`
* `zigux/tests/phase11_hvc_cleanup.zig`
* `Documentation/zigux/phase11-hvc-console-survey.md`
* `zigux/tests/phase11_hvc_console_survey.zig`
* `zigux/tests/phase11_hvc_console_manifest.json`
* `zigux/tests/phase11_hvc_console_modem_control_split.zig`
* `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
* `drivers/tty/hvc/hvc_console_sysrq.zig`
* `scripts/zigux/check-phase11-hvc-survey-packet.py`
* `make -C zigux phase11-hvc-survey`

These surfaces keep the teardown packet readable beside the shared Phase 11 replay route without promoting it into a broader runtime-parity claim, and the direct `drivers/tty/hvc/hvc_console_verify.zig` replay boundary plus the direct `zigux/tests/phase11_hvc_cleanup.zig` cleanup companion keep the host-free disconnect and cleanup evidence explicit beside the shipped starter. The direct `drivers/tty/hvc/hvc_console.zig` starter remains the anchor for the shipped close, hangup, remove, and cleanup summaries.

## What The Landed Teardown Packet Covers

The current host-free teardown replay keeps these handoffs explicit:

* final-close teardown boundaries and close-wait ownership
* `hvc_cleanup()` tty-port release handoff and cleanup-time tty-port ownership
* `hvc_hangup()` disconnect cleanup
* `hvc_remove()` slot-release and handoff ordering
* notifier-facing teardown edges beside `summarizeNotifierAddOutcome()`
* bounded sysrq-handling support through `drivers/tty/hvc/hvc_console_sysrq.zig` without claiming live sysrq execution
* poll-retry and drain-order split
* modem-control fallback split

The landed survey-backed packet also keeps the close-path and cleanup-path failure-mode cues explicit around tty detachment, HUPCL-gated modem-line shutdown, close-wait ownership, notifier ownership, resize-work cancellation, wait-until-sent intent, buffered-write clearing, stale hangup short-circuit behavior, cleanup-time tty-port ownership, and keep-IRQ-until-hangup teardown boundaries.

## Bounded Meaning

This note records the shipped teardown summaries only.
It does not claim live notifier callback execution, khvcd polling behavior, tty-driver registration, host-backed cleanup, or hardware-validated teardown parity.
Those remain later same-lane follow-through steps rather than part of the already-landed archival packet.
