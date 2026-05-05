# Phase 11 HVC Console Survey

This survey note now serves as the archival checkpoint for the original Phase 11 roadmap gap around `drivers/tty/hvc/hvc_console.c`.

The live repo state is now:

- reviewed against live `master` `c9b956c155281407bf86bf56d122b08d6fc634ea`
- `drivers/tty/hvc/hvc_console.zig` and `zigux/tests/phase11_hvc_console.zig` now land the first bounded starter around setup-state slot validation, CRLF write framing, flush intent, teardown gating, final-close wait summaries, and a tiny remove-path handoff summary
- `Documentation/zigux/phase11-hvc-console-slice.md` records the active starter scope, while `Documentation/zigux/phase11-hvc-console-validation-matrix.md` now names the current shared gate, the landed remove-path handoff, and the still-pending tty-registration follow-up
- this survey note remains as the checkpoint for the original gap that the bounded starter closed
- the remaining unported work is now tty-driver registration, notifier callback execution, khvcd polling, sysrq integration, and host-backed teardown validation

This lane is no longer survey-only, but the archival survey still does not claim tty-driver registration, notifier callback execution, hvc polling kthread behavior, sysrq handling, early-console registration, or live hypervisor I/O.

The next honest bounded step inside the same Phase 11 lane is a tiny tty-registration handoff summary that keeps `setup_hvc_console()` teardown parity and khvcd-facing behavior reviewable before any host-backed I/O widens the slice.
