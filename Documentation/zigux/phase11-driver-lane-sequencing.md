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
- bcm2835 continuity stays separate from the shared sequencing lane, but fresh
  raw `master` fallback rereads in this run do rematerialize
  `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, so shared-note
  truthfulness work can keep that returned driver-local matrix explicit without
  widening into bcm2835-only reminder wording, replay claims, or platform-backed
  execution
- gpio continuity stays separate from the shared sequencing lane; current
  shared-note work should not reopen gpio reminder wording unless the gpio lane
  itself changes
- DesignWare lane `P11-L10` stays separate from the shared sequencing lane, but
  raw `master` fallback rereads in this run do rematerialize
  `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so current
  shared-note work can keep that returned DesignWare matrix explicit while the
  wider helper-backed owner packet and the older
  `scripts/zigux/check-phase11-dw-wdt-packet.py` handle stay framed as
  separate-lane or historical vocabulary
- HVC continuity lane `P11-L16` currently keeps the directly readable
  `Documentation/zigux/phase11-hvc-console-survey.md`,
  `drivers/tty/hvc/hvc_console.zig`,
  `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`,
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md`,
  `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`,
  `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`,
  `zigux/tests/fixtures/phase11_build_inventory.json`,
  `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`,
  `zigux/tests/phase11_hvc_export_surface_layout_build.zig`,
  `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`,
  `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,
  `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, and
  `zigux/tests/phase11_hvc_cleanup_packet_build.zig` authoritative for the
  current-head continuity packet and helper-local teardown or failure-mode
  evidence while the broader starter-depth archival landing remains `P11-L13`;
  keep the deeper verify helper, sysrq helper, focused survey replay, manifest,
  dedicated survey-checker, and teardown-note anchors framed as archival or
  repo-reality-gap vocabulary until a fresh reread proves they returned
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

Treat the current shared Phase 11 packet as the reminder and continuity
surfaces that were reread in this run:

- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`

Current rereads in this run rematerialized the gpio watchdog and HVC
driver-local validation matrices named by the roadmap together with the
narrower HVC current-head continuity packet plus its cleanup companion,
current-head checker, build inventory, and proof-backed adjunct stack.
Authenticated contents reads still clip
`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` and
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, but raw `master`
fallback rereads rematerialized both driver-local matrix notes, so keep all
four driver-local validation matrices explicit in the shared current-head packet
while leaving bcm2835 and DesignWare reminder follow-through in their own lanes.

Keep the returned gpio, bcm2835, and DesignWare validation matrices explicit as
shared matrix-boundary evidence while preserving bcm2835 and DesignWare deeper
owner-packet follow-through as separate continuity lanes.

HVC still has the smaller current-head continuity packet rather than the deeper
starter-depth replay or manifest stack. bcm2835, gpio, and DesignWare reminder
follow-through still belong to their own lanes.

## Sequencing Rules

Use this note to keep the bounded work order honest:

1. Prefer one Phase 11 lane at a time instead of batching bcm2835, gpio,
   DesignWare, HVC, header-boundary, and contributor-note work into one mixed
   change.
2. Keep the shared-versus-dedicated split explicit: the shared sequencing lane
   owns reminder-surface truthfulness, not driver-local execution claims.
3. Keep the current reread boundary honest: today that means the shared
   validation-matrix packet for
   `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`,
   `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`,
   `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and
   `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, plus the adjacent
   `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`,
   `scripts/zigux/check-phase11-matrix-gap-survey.py`,
   `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`,
   `scripts/zigux/check-phase11-build-inventory.py`, and the HVC current-head
   continuity packet with its cleanup companion,
   `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, shared build
   inventory anchor, and proof-backed adjunct stack; keep it explicit that the
   bcm2835 and DesignWare matrix notes currently return through raw `master`
   fallback rather than this runtime's authenticated contents bridge.
4. Keep bcm2835 and DesignWare follow-through parked in their own lanes; do not
   widen either lane into live watchdog-core execution, PM plumbing, reset
   execution, IRQ execution, live MMIO validation, or claims of hardware-backed
   closure just because the shared packet can now name the returned driver-local
   matrix notes again.
5. Keep HVC current-head continuity and helper-local teardown or failure-mode
   evidence routed through `Documentation/zigux/phase11-hvc-console-survey.md`,
   `drivers/tty/hvc/hvc_console.zig`,
   `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`,
   `Documentation/zigux/phase11-hvc-console-validation-matrix.md`,
   `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`,
   `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`,
   `zigux/tests/fixtures/phase11_build_inventory.json`,
   `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`,
   `zigux/tests/phase11_hvc_export_surface_layout_build.zig`,
   `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`,
   `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,
   `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, and
   `zigux/tests/phase11_hvc_cleanup_packet_build.zig`; do not widen that packet
   into tty registration, notifier execution, khvcd execution, sysrq dispatch,
   or host-backed teardown.
6. Do not imply broader platform registration, PM plumbing, reset execution,
   IRQ execution, MMIO validation, notifier execution, sysrq execution, khvcd
   execution, or hardware-backed closure beyond the helper, proof, note, and
   checker surfaces that were reread in this run.
7. When contributor-facing summaries reopen, keep them aligned with the
   returned four-matrix shared packet, the narrower HVC current-head continuity
   packet plus its cleanup companion, current-head checker, shared build
   inventory, and proof-backed adjunct stack instead of reviving broader bcm2835
   or DesignWare owner-packet claims, shared-contract surfaces, or overstating
   the HVC archival stack.
8. Keep the next bounded shared follow-through inside the smallest
   reminder-surface truthfulness repair unless a later reread restores or
   removes another Phase 11 packet surface.

## Non-Goals

This note does not widen Phase 11 into:

- a claim that the overall simple-driver tranche is closed
- a claim that the missing shared-validator surface `scripts/zigux/validate-phase11.py`
  or the broader absent `make -C zigux phase11` and
  `make -C zigux phase11-contract` routes are already present on current
  `master` beyond the now-returned `make -C zigux phase11-validate` path
- a claim that bcm2835 or DesignWare broader reminder packets, helper stacks, or
  replay routes have all returned just because the driver-local validation
  matrices now reread through raw `master` fallback
- a claim that bcm2835 or gpio reminder packets have been broadly reread beyond
  the watchdog-local surfaces touched in their own lanes
- a claim that the older DesignWare packet-checker handle is already directly
  readable again
- broader hardware-backed watchdog validation, tty registration parity,
  notifier execution, sysrq dispatch, khvcd execution, or host-backed teardown
  closure
- a migration of driver-local reminder ownership into the shared packet
