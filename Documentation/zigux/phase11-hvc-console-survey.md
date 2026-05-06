# Phase 11 HVC Console Survey

This survey note now serves as the archival checkpoint for the original Phase 11 roadmap gap around `drivers/tty/hvc/hvc_console.c`.

The live archival packet now belongs to lane `P11-L16`.

The archived lane checkpoint is now:

- reviewed against archival `master` checkpoint `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- lane `P11-L16` keeps `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, and `zigux/tests/phase11_hvc_console.zig` aligned around the bounded starter, compile-local teardown truthfulness, setup-state slot validation, CRLF write framing, flush intent, teardown gating, final-close wait summaries, a tiny remove-path handoff summary, a tiny tty-registration handoff summary, a tiny sysrq handoff summary, and a tiny notifier-facing handoff summary
- `zigux/tests/phase11_hvc_console_survey.zig` now keeps a bounded driver-local `struct winsize` layout checkpoint for the resize boundary, asserting size `8`, alignment `2`, and offsets `0`, `2`, `4`, and `6`, and a bounded `struct hv_ops` callback-table layout checkpoint for size `72`, alignment `8`, and callback-pointer offsets `0` through `64`, without widening into tty-core or `struct hvc_struct` ownership
- `Documentation/zigux/phase11-hvc-console-slice.md` records the active starter scope, `Documentation/zigux/phase11-hvc-console-validation-matrix.md` names the current shared gate plus the compile-local verifier, the landed tty-registration, sysrq, and notifier-facing handoffs, `Documentation/zigux/phase11-hvc-console-teardown-note.md` keeps the close, cleanup, and remove ownership split explicit in one driver-local note, and `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` now keep those HVC review surfaces coupled to the wider Phase 11 replay route while preserving the focused shared header-boundary packet beside the broader HVC note
- against the Phase 11 roadmap, the current packet closed the straightforward-lifecycle simple-driver gap in bounded form and already had its first hardware validation matrix at that archival checkpoint, while teardown and failure-mode parity remain intentionally host-free across the close, cleanup, remove, sysrq, and notifier handoff checkpoints
- current `master` may move independently after this checkpoint; the live truthfulness source for the lane is the current driver, verifier, tests, validation matrix, and shared replay contract rather than this archived commit pin alone
- this survey note remains as the checkpoint for the original gap that the bounded starter closed
- the remaining unported work is now live tty-driver registration, notifier callback execution, khvcd polling, live sysrq integration, and host-backed teardown validation

This lane is no longer survey-only, but the archival survey still does not claim live tty-driver registration, notifier callback execution, hvc polling kthread behavior, live sysrq handling, early-console registration, or live hypervisor I/O.

The next honest bounded step inside the same Phase 11 lane is now another small shared-review truthfulness sync or similarly small watchdog or HVC teardown and failure-mode parity repair that stays inside the shipped `scripts/zigux/check-phase11-shared-replay-contract.py` contract, the focused `scripts/zigux/check-phase11-header-boundary-packet.py` route, and the shared-versus-dedicated replay packet, instead of reopening the already-landed shared-review checker hardening or widening into live callback execution or host-backed I/O.
