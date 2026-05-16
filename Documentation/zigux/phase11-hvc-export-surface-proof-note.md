# Phase 11 HVC Exported-Helper Proof Note

This note records the dedicated exported-helper ABI proof companion that now sits beside the bounded Phase 11 `hvc_console` archival packet.

It exists to keep the newer exported-helper layout proof explicit without pretending that the archival survey gate or shared Phase 11 build route already absorbed that focused replay.

## Status

* `PHASE11_HVC_EXPORT_SURFACE_PROOF_STATUS=companion_proof_landed`
* lane continuity: `P11-L16`
* proof source: `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
* focused build route: `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
* relationship to the archival survey packet: this proof stays a direct HVC companion and does not replace `zigux/tests/phase11_hvc_console_survey.zig`

## What This Companion Proves

* the exported `hvc_*` surface keeps `HvcExportSurface` at size `72` with alignment `8`
* field offsets stay pinned for `hvc_instantiate`, `hvc_alloc`, `hvc_remove`, `hvc_poll`, `hvc_kick`, `__hvc_resize`, `notifier_add_irq`, `notifier_del_irq`, and `notifier_hangup_irq`
* the focused proof also keeps the exported helper signatures exact through `notifier_hangup_irq`

## Boundaries

* this note does not claim that the dedicated proof already runs through `make -C zigux phase11-hvc-survey`
* this note does not claim tty-driver registration, notifier callback execution, khvcd worker execution, live sysrq dispatch, or host-backed teardown parity
* if the exported-helper proof broadens later, keep the next repair inside this proof companion, the directly coupled HVC governance notes, or a checker-local refresh instead of widening into new console behavior
