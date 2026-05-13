# Phase 11 HVC Console Survey

This note restores the compact archival survey for the bounded Phase 11 `hvc_console` packet on current `master`.
It stays inside the simple-drivers lane and records only the shipped starter, the bounded supporting helper, and the still-blocked follow-through that the surrounding shared packet already names.

## Status

* `PHASE11_HVC_CONSOLE_SURVEY_STATUS=starter_packet_archived`
* archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
* Phase 11 simple-production-driver gap has been closed by the bounded starter.
* remaining unported work is now tty-driver registration, khvcd worker execution, live sysrq execution, notifier callback execution, and host-backed transport or teardown validation

## Surveyed Packet

The current bounded HVC archival packet on `master` is:

* `drivers/tty/hvc/hvc_console.zig`
* `zigux/tests/phase11_hvc_console_survey.zig`
* `zigux/tests/phase11_hvc_console_manifest.json`
* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
* `Documentation/zigux/phase11-hvc-console-teardown-note.md`
* `zigux/tests/phase11_hvc_console_modem_control_split.zig`
* `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
* `scripts/zigux/check-phase11-hvc-survey-packet.py`
* `make -C zigux phase11-hvc-survey`
* `drivers/tty/hvc/hvc_console_sysrq.zig`

The survey note exists to keep those surfaces, the direct `drivers/tty/hvc/hvc_console.zig` starter, the paired validation matrix, and the paired teardown checkpoint readable together without overstating runtime parity or widening the Phase 11 claim beyond the landed starter.

The current archival packet does not yet ship direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, or `zigux/tests/phase11_hvc_cleanup.zig` companions on current `master`, so keep those paths framed as later same-lane follow-through rather than as already-landed replay evidence.

## What Landed

The shipped `drivers/tty/hvc/hvc_console.zig` starter is the direct anchor for the current HVC archival packet.
It keeps the host-free close, notifier-add, khvcd, poll, hangup, remove, and cleanup summaries reviewable without claiming live tty-driver registration, notifier execution, or host-backed teardown.

The shipped `drivers/tty/hvc/hvc_console_sysrq.zig` helper is a bounded supporting helper for the current HVC packet.
It keeps the tiny sysrq handoff explicit without claiming live sysrq execution, and it leaves the direct transport, tty registration, and callback-driving work outside the archived survey.

The paired archival survey gate in `zigux/tests/phase11_hvc_console_survey.zig` keeps the manifest-backed header-layout, exported-helper, modem-control fallback, and poll-retry failure-mode packet reviewable beside that archived survey, the paired teardown checkpoint, and the validation matrix without widening into live notifier callbacks, khvcd execution, or host-backed cleanup.

The bounded HVC survey keeps direct verify-only and cleanup follow-through explicitly deferred.
Those paths remain same-lane follow-up work and should not be described as landed replay evidence while the archival packet stays host-free.

The bounded starter and its archival replay now keep these focused cues explicit:

* final-close teardown summary
* tiny notifier-add open handoff summary
* khvcd worker-entry summary
* khvcd sleep-and-reschedule handoff summary
* `__hvc_poll` drain-order summary
* `hvc_hangup()` disconnect summary
* `hvc_remove()` handoff summary
* `hvc_cleanup()` tty-port release handoff summary
* `hvc_kick()` wakeup cue
* notifier-IRQ helper surface through `notifier_add_irq()` and `notifier_hangup_irq()`
* exported-helper signature proof for the bounded helper-facing HVC surface
* `tiocmget` and `tiocmset` fallback coverage when `hv_ops` modem-control callbacks are absent
* `tiocmset` mask handling stays distinct even when `tiocmget` falls back
* sysrq toggle handoff stays distinct from literal fallback on the primary console
* pending sysrq dispatch stays separate from ordinary poll bytes
* non-kernel `^O` input stays a literal byte without toggling sysrq state
* sysrq handoff stays unavailable after teardown

## Bounded Meaning

This archival note records the landed starter and the helper-facing survey only.
It does not claim tty-driver registration, notifier callback execution, khvcd polling execution, live sysrq dispatch, host-backed cleanup, or hardware-validated teardown parity.
Those follow-through steps still belong to later same-lane HVC work rather than the shared Phase 11 closure packet.
