# Phase 11 HVC Console Survey

This survey note now serves as the archival checkpoint for the original Phase 11 roadmap gap around `drivers/tty/hvc/hvc_console.c`.

The live repo state is now:

- reviewed against live `master` `d197eb9c46920e26d7e146bdde0800b6c5b25c00`
- `drivers/tty/hvc/hvc_console.zig` and `zigux/tests/phase11_hvc_console.zig` now land the first bounded starter around setup-state slot validation, CRLF write framing, flush intent, teardown gating, and final-close wait summaries
- `Documentation/zigux/phase11-hvc-console-slice.md` records the active starter scope, while this survey note remains as the checkpoint for the gap that was just closed
- the remaining unported work is now tty-driver registration, `setup_hvc_console()` teardown parity, khvcd polling, sysrq integration, and host-backed teardown validation

This lane is no longer survey-only, but the archival survey still does not claim tty-driver registration, hvc polling kthread behavior, close-wait teardown parity, sysrq handling, early-console registration, or live hypervisor I/O.

The next honest bounded step inside the same Phase 11 lane is the first kernel-integration validation matrix for tty registration, close-wait teardown parity, and khvcd-facing behavior before any host-backed I/O widens the slice.
