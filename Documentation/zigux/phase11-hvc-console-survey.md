# Phase 11 HVC Console Survey

This survey note now serves as the archival checkpoint for the original Phase 11 roadmap gap around `drivers/tty/hvc/hvc_console.c`.

The live repo state is now:

- reviewed against live `master` `6bc5aab94fd86534959bf9197c904fa5145f23e2`
- `drivers/tty/hvc/hvc_console.zig` and `zigux/tests/phase11_hvc_console.zig` now land the first bounded starter around setup-state slot validation, a tiny `drivers/tty/hvc/hvc_console.h` parity snapshot for console limits plus `hv_ops` and exported `hvc_*` surface metadata, CRLF write framing, flush intent, teardown gating, and final-close wait summaries
- `Documentation/zigux/phase11-hvc-console-slice.md` records the active starter scope, while `Documentation/zigux/phase11-hvc-console-validation-matrix.md` now names the current shared gate, records that the dedicated hvc survey replay is still separate from `zigux/tests/phase11_build.zig`, and keeps the close-wait teardown evidence plus the still-pending tty-registration follow-up explicit
- this survey note remains as the checkpoint for the original gap that the bounded starter closed
- the remaining unported work is now tty-driver registration, `setup_hvc_console()` teardown parity, khvcd polling, sysrq integration, and host-backed teardown validation

This lane is no longer survey-only, but the archival survey still does not claim tty-driver registration, hvc polling kthread behavior, close-wait teardown parity, sysrq handling, early-console registration, or live hypervisor I/O.

The next honest bounded step inside the same Phase 11 lane is a tiny tty-registration handoff summary that keeps `setup_hvc_console()` teardown parity and khvcd-facing behavior reviewable before any host-backed I/O widens the slice.
