# Phase 11 Driver Lane Sequencing

This note keeps the active Phase 11 simple-driver packet split into bounded owner
lanes while reflecting only the current-head surfaces that were reread in this
run.

## Scope

Use this note when a Phase 11 change touches the shared reminder packet under
`Documentation/zigux/phase11-*.md`, the coupled
`scripts/zigux/check-phase11-*.py` review surfaces, the proof-backed or
scaffold-backed Phase 11 files under `zigux/tests/`, or the broad
contributor-facing summaries.

## Lane Split

Keep the current lane split explicit:

- shared sequencing lane `P11-Y06` owns the shared reminder wording in
  `Documentation/zigux/phase11-driver-lane-sequencing.md` and
  `Documentation/zigux/phase11-validation-matrix-gap-survey.md` together with
  the smallest coupled checker updates needed to keep that shared packet honest
- bcm2835 continuity stays separate from the shared sequencing lane; this run
  reread the bcm2835 survey packet but did not reopen a broader bcm2835 reminder
  sweep, so keep bcm2835 follow-through bounded to its own same-family surfaces
- gpio continuity stays separate from the shared sequencing lane; current
  shared-note work should not reopen gpio reminder wording unless the gpio lane
  itself changes
- DesignWare lane `P11-L10` currently owns the returned watchdog-local packet
  through `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`,
  `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`,
  `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`,
  `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`,
  `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`,
  `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`,
  `Documentation/zigux/phase11-dw-wdt-survey.md`,
  `Documentation/zigux/phase11-dw-wdt-slice.md`,
  `Documentation/zigux/phase11-dw-wdt-teardown-note.md`,
  `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`,
  `zigux/tests/phase11_dw_wdt_manifest.json`,
  `zigux/tests/phase11_dw_wdt.zig`,
  `zigux/tests/phase11_dw_wdt_survey.zig`,
  `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`,
  `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and
  `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`; keep the older
  `scripts/zigux/check-phase11-dw-wdt-packet.py` handle framed as historical or
  repo-reality-gap vocabulary until a future reread proves it returned on
  current `master`
- HVC archival lane `P11-L16` currently keeps the directly readable
  `Documentation/zigux/phase11-hvc-console-survey.md`,
  `drivers/tty/hvc/hvc_console.zig`,
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and
  `Documentation/zigux/phase11-hvc-verify-helper-boundary.md` authoritative for
  the current-head continuity packet and helper-local teardown or failure-mode
  evidence; keep the deeper replay, manifest, dedicated survey-checker, and
  teardown-note anchors framed as archival or repo-reality-gap vocabulary until
  a fresh reread proves they returned
- contributor-note lane `P11-L18` owns broad cross-phase reminder wording in
  `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`,
  `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`,
  `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`,
  `scripts/zigux/README.md`, and `zigux/tests/README.md`
- shared header-boundary follow-through stays adjacent to
  `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`; do not
  fold that public-surface packet into the HVC archival lane or into
  driver-local watchdog packets

## Shared Packet Boundaries

Treat the current shared Phase 11 packet as the reminder surfaces that were
 directly reread in this run:

- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`
- `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`
- `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-slice.md`
- `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
- `drivers/watchdog/dw_wdt.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `drivers/tty/hvc/hvc_console.zig`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`

Current rereads in this run rematerialized the returned DesignWare helper,
replay, reminder-note, validation-matrix, and checker packet alongside the
narrower HVC current-head continuity packet. Keep only the older DesignWare
packet-checker handle `scripts/zigux/check-phase11-dw-wdt-packet.py` framed as
historical or repo-reality-gap vocabulary until a future reread proves it
returned.

HVC still has the smaller current-head continuity packet rather than the deeper
starter-depth replay or manifest stack. bcm2835 and gpio reminder follow-through
still belong to their own lanes.

## Sequencing Rules

Use this note to keep the bounded work order honest:

1. Prefer one Phase 11 lane at a time instead of batching bcm2835, gpio,
   DesignWare, HVC, header-boundary, and contributor-note work into one mixed
   change.
2. Keep the shared-versus-dedicated split explicit: the shared sequencing lane
   owns reminder-surface truthfulness, not driver-local execution claims.
3. Keep the current readback boundary honest: today that means the HVC
   current-head continuity packet plus the returned DesignWare helper-backed
   owner stack of notes, helpers, replays, manifest, registration scaffold,
   validation matrix, and paired teardown and verify checkers.
4. Keep the DesignWare follow-through parked on bounded starter, scaffold, and
   reminder-surface truthfulness; do not widen that returned owner stack into
   live watchdog-core execution, PM plumbing, reset execution, IRQ execution,
   live MMIO validation, or claims of hardware-backed closure.
5. Keep HVC current-head continuity and helper-local teardown or failure-mode
   evidence routed through `Documentation/zigux/phase11-hvc-console-survey.md`,
   `drivers/tty/hvc/hvc_console.zig`,
   `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and
   `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`; do not widen
   that packet into tty registration, notifier execution, khvcd execution, sysrq
   dispatch, or host-backed teardown.
6. Do not imply broader platform registration, PM plumbing, reset execution, IRQ
   execution, MMIO validation, notifier execution, sysrq execution, khvcd
   execution, or hardware-backed closure beyond the helper, replay, manifest,
   scaffold, note, and checker surfaces that were directly reread in this run.
7. When contributor-facing summaries reopen, keep them aligned with the returned
   DesignWare helper-backed packet and the narrower HVC current-head continuity
   packet instead of reviving missing shared-contract surfaces or overstating the
   HVC archival stack.
8. Keep the next bounded shared follow-through inside the smallest
   reminder-surface truthfulness repair unless a later reread restores or
   removes another directly readable Phase 11 packet surface.

## Non-Goals

This note does not widen Phase 11 into:

- a claim that the overall simple-driver tranche is closed
- a claim that the missing shared-validator surfaces `scripts/zigux/validate-phase11.py`
  or `make -C zigux phase11-validate` are already present on current `master`
- a claim that bcm2835 or gpio reminder packets have been broadly reread beyond
  the specific watchdog-local surfaces touched in their own lanes
- a claim that the older DesignWare packet-checker handle is already directly
  readable again
- broader hardware-backed watchdog validation, tty registration parity, notifier
  execution, sysrq dispatch, khvcd execution, or host-backed teardown closure
- a migration of driver-local reminder ownership into the shared packet