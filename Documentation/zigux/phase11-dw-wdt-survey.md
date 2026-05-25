# Phase 11 DesignWare Watchdog Survey

This survey note tracks the bounded Phase 11 DesignWare watchdog packet around
`drivers/watchdog/dw_wdt.c` after rereading current `master` against the
roadmap-backed simple-driver lane.

The current lane-local packet is `P11-L10`. Authenticated current-head rereads
now keep the bounded DesignWare continuity packet explicit through
`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`,
`Documentation/zigux/phase11-dw-wdt-provenance-readback.md`,
`Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`,
`Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`,
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-dw-wdt-survey.md`,
`zigux/tests/phase11_dw_wdt_manifest.json`,
`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`,
`zigux/tests/phase11_dw_wdt_survey.zig`,
`drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_pm.zig`,
`drivers/watchdog/dw_wdt_pm_scaffold.zig`,
`drivers/watchdog/dw_wdt_verify.zig`,
`scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and
`scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`.

Those same authenticated contents rereads do not rematerialize
`Documentation/zigux/phase11-dw-wdt-slice.md`,
`Documentation/zigux/phase11-dw-wdt-teardown-note.md`,
`drivers/watchdog/dw_wdt.zig`, or `zigux/tests/phase11_dw_wdt.zig`, so keep
that broader direct-driver, direct replay, and older reminder stack framed as
larger same-lane vocabulary and fallback-visible evidence rather than as part of
the same direct current-head packet.

The returned smaller packet now keeps the platform-registration owner note, the
current-head gap inventory, the registration scaffold outcomes, the restart
summary helper, the returned verify helper, and the bounded PM-helper pair
reviewable without claiming live platform execution, clock or reset acquisition
execution, IRQ delivery, or hardware-backed MMIO behavior.

The shared `zigux/tests/phase11_build.zig` route remains a shared current-head
gap rather than landed evidence in this lane. The next bounded same-lane step
is still the ready-next manifest gap: hardware-backed MMIO validation around
suspend, resume, and platform-backed probe or remove execution, kept separate
from unrelated driver behavior and from promoting the broader direct-driver
stack without a fresh authenticated reread.
