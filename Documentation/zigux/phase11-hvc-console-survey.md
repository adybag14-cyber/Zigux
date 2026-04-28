# Phase 11 HVC Console Survey

This survey note now serves as the archival checkpoint for the original Phase 11 roadmap gap around `drivers/tty/hvc/hvc_console.c`.

The live repo state is now:

- reviewed against live `master` `97c9a41d834873da3c45a187bdf888a46d8b18ba`
- `drivers/tty/hvc/hvc_console.zig` and `zigux/tests/phase11_hvc_console.zig` now land the first bounded starter around setup-state slot validation, a tiny `drivers/tty/hvc/hvc_console.h` parity snapshot for console limits plus `hv_ops` and exported `hvc_*` surface metadata, CRLF write framing, flush intent, teardown gating, final-close wait summaries, a tiny tty-registration handoff summary, a khvcd polling-contract summary, and a khvcd worker-entry summary
- `Documentation/zigux/phase11-hvc-console-slice.md` records the active starter scope, while `Documentation/zigux/phase11-hvc-console-validation-matrix.md` now names the current shared gate, records that the dedicated hvc survey replay is still separate from `zigux/tests/phase11_build.zig`, and keeps the landed tty-registration handoff, khvcd polling-contract, and khvcd worker-entry evidence explicit
- this survey note remains as the checkpoint for the original gap that the bounded starter closed
- the remaining unported work is now tty-driver registration, `__hvc_poll()` drain ordering, khvcd worker execution, sysrq integration, and host-backed teardown validation

This lane is no longer survey-only, but the archival survey still does not claim tty-driver registration, hvc polling kthread worker execution, notifier callback execution, sysrq handling, early-console registration, or live hypervisor I/O.

The next honest bounded step inside the same Phase 11 lane is a tiny `__hvc_poll()` drain-order summary that keeps poll-mask handoff and tty wakeup drain boundaries reviewable before any host-backed I/O widens the slice.
