# Phase 11 HVC Console Survey

This survey note now serves as the archival checkpoint for the original Phase 11 roadmap gap around `drivers/tty/hvc/hvc_console.c`.

The live repo state is now:

- reviewed against live `master` `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- `drivers/tty/hvc/hvc_console.zig` and `zigux/tests/phase11_hvc_console.zig` now land the first bounded starter around setup-state slot validation, CRLF write framing, flush intent, teardown gating, final-close wait summaries, a tiny remove-path handoff summary, a tiny tty-registration handoff summary, a tiny sysrq handoff summary, and a tiny notifier-facing handoff summary
- `Documentation/zigux/phase11-hvc-console-slice.md` records the active starter scope, `Documentation/zigux/phase11-hvc-console-validation-matrix.md` names the current shared gate plus the landed tty-registration, sysrq, and notifier-facing handoffs, and `Documentation/zigux/phase11-shared-replay-contract.md` now records the shared contributor packet that keeps those HVC review surfaces coupled to the wider Phase 11 replay route
- this survey note remains as the checkpoint for the original gap that the bounded starter closed
- the remaining unported work is now live tty-driver registration, notifier callback execution, khvcd polling, live sysrq integration, and host-backed teardown validation

This lane is no longer survey-only, but the archival survey still does not claim live tty-driver registration, notifier callback execution, hvc polling kthread behavior, live sysrq handling, early-console registration, or live hypervisor I/O.

The next honest bounded step inside the same Phase 11 lane is now the next small shared-review or hardware-validation sync that keeps the landed notifier-facing handoff explicit without widening into live callback execution or host-backed I/O.
