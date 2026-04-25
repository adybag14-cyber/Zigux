# Phase 11 HVC Console Survey

This survey note now serves as the archival checkpoint for the original Phase 11 roadmap gap around `drivers/tty/hvc/hvc_console.c`.

The live repo state is now:

- reviewed against live `master` `5e9f574d2dd6af384db83f8c1dc98be14f28e832`
- `drivers/tty/hvc/hvc_console.zig` and `zigux/tests/phase11_hvc_console.zig` now land the first bounded starter around setup-state slot validation, CRLF write framing, flush intent, and teardown gating
- `Documentation/zigux/phase11-hvc-console-slice.md` records the active starter scope, while this survey note remains as the checkpoint for the gap that was just closed
- the remaining unported work is now tty-driver registration, `setup_hvc_console()` close-wait behavior, khvcd polling, sysrq integration, and host-backed teardown parity

This lane is no longer survey-only, but the archival survey still does not claim tty-driver registration, hvc polling kthread behavior, close-wait teardown parity, sysrq handling, early-console registration, or live hypervisor I/O.

The next honest bounded step inside the same lane is one tiny probe-facing note or helper around setup-state and close-wait boundaries before any tty core or host-backed behavior widens the slice.
