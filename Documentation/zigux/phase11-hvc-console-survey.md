# Phase 11 HVC Console Survey

This survey note records the Phase 11 roadmap gap around `drivers/tty/hvc/hvc_console.c`.

The live repo state is now:

- `drivers/tty/hvc/hvc_console.c` is a real Phase 11 anchor in the roadmap, but Zigux still has no `drivers/tty/hvc/hvc_console.zig` starter
- `zigux/tests/phase11_hvc_console_survey.zig` and `zigux/tests/phase11_hvc_console_manifest.json` now keep that missing lane explicit beside the existing watchdog starters
- `zigux/tests/phase11_build.zig` now runs the hvc survey path together with the existing Phase 11 watchdog coverage so the tty gap does not disappear from tranche review

This lane is still intentionally survey-only. It does not claim tty-driver registration, hvc polling kthread behavior, close-wait teardown parity, sysrq handling, early-console registration, or live hypervisor I/O.

The next honest bounded step inside the same lane is a tiny `drivers/tty/hvc/hvc_console.zig` starter that stays in memory only and models descriptor-level console-slot validation, CRLF console write framing, flush retry intent, and adapter-presence gating before any tty core or hypervisor-backed behavior.
