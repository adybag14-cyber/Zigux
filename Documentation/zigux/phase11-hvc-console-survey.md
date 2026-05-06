# Phase 11 HVC Console Survey

This survey note now serves as the archival checkpoint for the original Phase 11 roadmap gap around `drivers/tty/hvc/hvc_console.c`.

The live repo state is now:

- reviewed against live `master` `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- `drivers/tty/hvc/hvc_console.zig` and `zigux/tests/phase11_hvc_console.zig` now land the first bounded starter around setup-state slot validation, CRLF write framing, flush intent, teardown gating, final-close wait summaries, a tiny remove-path handoff summary, a tiny tty-registration handoff summary, a tiny sysrq handoff summary, and a tiny notifier-facing handoff summary
- `zigux/tests/phase11_hvc_console_survey.zig` now keeps a bounded driver-local `struct winsize` layout checkpoint for the resize boundary, asserting size `8`, alignment `2`, and offsets `0`, `2`, `4`, and `6` without widening into tty-core ownership
- `Documentation/zigux/phase11-hvc-console-slice.md` records the active starter scope, `Documentation/zigux/phase11-hvc-console-validation-matrix.md` names the current shared gate plus the landed tty-registration, sysrq, and notifier-facing handoffs, and `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `zigux/tests/README.md`, and `.github/workflows/zigux-bootstrap.yml` now keep those HVC review surfaces coupled to the wider Phase 11 replay route
- against the Phase 11 roadmap, the current packet now closes the straightforward-lifecycle simple-driver gap in bounded form and already has its first hardware validation matrix, while teardown and failure-mode parity remain intentionally host-free across the close, cleanup, remove, sysrq, and notifier handoff checkpoints
- this survey note remains as the checkpoint for the original gap that the bounded starter closed
- the remaining unported work is now live tty-driver registration, notifier callback execution, khvcd polling, live sysrq integration, and host-backed teardown validation

This lane is no longer survey-only, but the archival survey still does not claim live tty-driver registration, notifier callback execution, hvc polling kthread behavior, live sysrq handling, early-console registration, or live hypervisor I/O.

The next honest bounded step inside the same Phase 11 lane is now another small shared-review truthfulness sync or similarly small watchdog or HVC teardown and failure-mode parity repair that stays inside the shipped `scripts/zigux/check-phase11-shared-replay-contract.py` contract, instead of reopening the already-landed shared-review checker hardening or widening into live callback execution or host-backed I/O.
