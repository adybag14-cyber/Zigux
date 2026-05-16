# Phase 11 HVC Console Survey

This note keeps the bounded Phase 11 `hvc_console` packet truthful on current `master`. It stays inside the simple-driver lane and records the shipped starter, the bounded supporting helper, the direct replay companions, the split replay surfaces, and the coupled survey route without claiming live tty or hypervisor execution. The original archival landing happened on `P11-L13`, while the currently coupled manifest, slice, and validation surfaces continue through `P11-L16`.

## Status

* `PHASE11_HVC_CONSOLE_SURVEY_STATUS=starter_packet_archived`
* archival landing lane: `P11-L13`
* current coupled packet continuity: `P11-L16`
* archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
* the Phase 11 simple-production-driver starter gap is closed at archival packet depth because current `master` now carries the bounded starter together with the coupled teardown note and validation matrix.
* the roadmap destination family `drivers/tty/hvc/*.zig` now materializes on current `master` through `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, and `drivers/tty/hvc/hvc_console_sysrq.zig`
* the roadmap-required teardown and failure-mode packet now materializes through `Documentation/zigux/phase11-hvc-console-teardown-note.md` and `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
* remaining unported work is now tty-driver registration, khvcd worker execution, live sysrq execution, notifier callback execution, and host-backed transport or teardown validation

## Surveyed Packet

The current bounded HVC archival packet on `master` is:
* `drivers/tty/hvc/hvc_console.zig`
* `drivers/tty/hvc/hvc_console_verify.zig`
* `drivers/tty/hvc/hvc_console_sysrq.zig`
* `zigux/tests/phase11_hvc_console.zig`
* `zigux/tests/phase11_hvc_cleanup.zig`
* `zigux/tests/phase11_hvc_console_survey.zig`
* `zigux/tests/phase11_hvc_console_manifest.json`
* `zigux/tests/phase11_hvc_console_modem_control_split.zig`
* `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
* `Documentation/zigux/phase11-hvc-console-survey.md`
* `Documentation/zigux/phase11-hvc-console-slice.md`
* `Documentation/zigux/phase11-hvc-console-teardown-note.md`
* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
* `scripts/zigux/check-phase11-hvc-survey-packet.py`
* `make -C zigux phase11-hvc-survey`
Current `master` also materializes direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions.

The archival packet keeps those direct replay, verify, and cleanup surfaces explicit beside the shipped starter, survey gate, split replay surfaces, and sysrq helper without presenting them as overall Phase 11 closure.

## What Landed

The shipped `drivers/tty/hvc/hvc_console.zig` starter is the direct anchor for the current HVC archival packet.

It keeps these host-free cues reviewable without claiming live tty-driver registration, notifier callback execution, or host-backed teardown:
* final-close teardown summary
* tiny notifier-add open handoff summary
* khvcd polling-contract summary
* khvcd worker-entry summary
* khvcd sleep-and-reschedule handoff summary
* `__hvc_poll` drain-order summary
* `hvc_hangup()` disconnect summary
* `hvc_remove()` handoff summary
* `hvc_cleanup()` tty-port release handoff summary
* `hvc_kick()` wakeup cue
* notifier-IRQ helper surface through `notifier_add_irq()` and `notifier_hangup_irq()`
* targetless notifier no-unregister edge through `summarizeTargetlessNotifierEdge()`

The shipped `drivers/tty/hvc/hvc_console_sysrq.zig` helper is a bounded supporting helper for the current HVC packet.

It keeps sysrq toggle handoff, pending-dispatch separation, literal-byte fallback on non-kernel `^O`, and post-teardown unavailability explicit without claiming live sysrq execution. The current archival packet also keeps the direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions explicit.

Those companions keep direct `hvc_console` replay, verify-side helper boundaries, bounded cleanup-time teardown checks, and the targetless notifier no-unregister edge visible beside the archival survey gate without promoting the lane to live tty-driver registration, notifier callback execution, khvcd execution, live sysrq dispatch, or host-backed teardown parity.

The paired archival survey gate in `zigux/tests/phase11_hvc_console_survey.zig` keeps the manifest-backed `struct winsize` `layout_assert` proof at size `8`, alignment `2`, and offsets `0`, `2`, `4`, and `6`; the bounded `struct hv_ops` `layout_assert` proof at size `72`, alignment `8`, and callback-table offsets `0` through `64`; the bounded `hv_ops` callback-signature proof; the `MAX_NR_HVC_CONSOLES` and `HVC_ALLOC_TTY_ADAPTERS` header constant proofs; the exported-helper signature proof through `notifier_hangup_irq`; the targetless notifier no-unregister edge; the modem-control fallback split; the poll-retry split; the teardown-summary wording; and the direct companion surfaces reviewable beside this survey note, the slice note, the teardown note, and the validation matrix.

## Bounded Meaning

This archival note records the landed starter, the direct verify, replay, and cleanup companions, the helper-facing survey, the targetless notifier no-unregister edge, the split tests, the sysrq helper, and the directly coupled teardown-and-validation packet only. It does not claim tty-driver registration, notifier callback execution, khvcd polling execution, live sysrq dispatch, host-backed cleanup, or hardware-validated teardown parity.

The roadmap destination family and the bounded simple-driver support packet are now materially present on current `master`, so the remaining same-lane work is execution-facing follow-through rather than a missing simple-driver starter or missing survey-backed validation packet. Those follow-through steps still belong to later same-lane HVC work rather than the already-landed archival packet.