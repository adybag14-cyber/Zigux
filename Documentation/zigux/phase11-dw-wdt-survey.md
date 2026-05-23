# Phase 11 DesignWare Watchdog Survey

This survey note tracks the bounded Phase 11 DesignWare watchdog packet around
`drivers/watchdog/dw_wdt.c` after rereading current `master` against the
roadmap-backed simple-driver lane.

The current lane-local packet is `P11-L10`: the manifest-backed survey gate,
this note, and the validation matrix all describe the same DesignWare watchdog
continuity surface. Current repo reality keeps the bounded starter reviewable
through `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`,
`drivers/watchdog/dw_wdt_pm.zig`,
`zigux/tests/phase11_dw_wdt_manifest.json`,
`zigux/tests/phase11_dw_wdt_survey.zig`, and
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`.

The packet now carries reviewable fixed TOP timeout handling, reset-versus-IRQ
timeout selection, registration-order scaffolding, teardown and failure-mode
parity, restart summary coverage, and PM-helper handoff coverage without
claiming live platform execution, clock or reset acquisition, IRQ delivery, or
hardware-backed MMIO behavior.

The shared `zigux/tests/phase11_build.zig` route remains a shared current-head
gap rather than landed evidence in this lane. The next bounded same-lane step
is still the ready-next manifest gap: hardware-backed MMIO validation around
suspend, resume, and platform-backed probe or remove execution, kept separate
from unrelated driver behavior.
