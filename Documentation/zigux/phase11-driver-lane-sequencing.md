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
- bcm2835 continuity stays separate from the shared sequencing lane; current
  shared-note work should not reopen bcm2835 reminder wording unless a fresh
  reread proves a directly readable bcm2835 driver-local validation matrix or a
  smaller same-family packet returned on current `master`
- gpio continuity stays separate from the shared sequencing lane; current
  shared-note work should not reopen gpio reminder wording unless the gpio lane
  itself changes
- DesignWare lane `P11-L10` stays separate from the shared sequencing lane;
  current shared-note work should not promote a returned DesignWare validation
  matrix or helper-backed owner packet while direct contents reads in this run
  still do not rematerialize
  `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, and the older
  `scripts/zigux/check-phase11-dw-wdt-packet.py` handle should stay framed as
  historical or repo-reality-gap vocabulary until a future reread proves it
  returned on current `master`
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
surfaces that were directly reread in this run:

- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
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

Current direct contents reads in this run do not rematerialize
`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` or
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so keep bcm2835 and
DesignWare matrix follow-through out of the shared current-head packet until a
future reread returns those driver-local notes.

Keep the returned gpio validation matrix explicit as shared matrix boundary
evidence while preserving bcm2835 and DesignWare follow-through as separate
continuity lanes.

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
3. Keep the current readback boundary honest: today that means the shared
   validation-matrix packet for
   `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` and
   `Documentation/zigux/phase11-hvc-console-validation-matrix.md` plus the
   adjacent `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`,
   `scripts/zigux/check-phase11-matrix-gap-survey.py`,
   `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`,
   `scripts/zigux/check-phase11-build-inventory.py`, and the HVC current-head
   continuity packet with its cleanup companion,
   `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, shared build
   inventory anchor, and proof-backed adjunct stack.
4. Keep bcm2835 and DesignWare follow-through parked in their own lanes; do not
   promote missing bcm2835 or DesignWare validation-matrix surfaces into the
   shared current-head packet until a future reread proves they returned, and
   do not widen either lane into live watchdog-core execution, PM plumbing,
   reset execution, IRQ execution, live MMIO validation, or claims of
   hardware-backed closure.
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
   checker surfaces that were directly reread in this run.
7. When contributor-facing summaries reopen, keep them aligned with the
   returned gpio and HVC validation-matrix packet, the narrower HVC current-head
   continuity packet plus its cleanup companion, current-head checker, shared
   build inventory, and proof-backed adjunct stack instead of reviving missing
   bcm2835 or DesignWare matrix surfaces, shared-contract surfaces, or
   overstating the HVC archival stack.
8. Keep the next bounded shared follow-through inside the smallest
   reminder-surface truthfulness repair unless a later reread restores or
   removes another directly readable Phase 11 packet surface.

## Non-Goals

This note does not widen Phase 11 into:

- a claim that the overall simple-driver tranche is closed
- a claim that the missing shared-validator surfaces `scripts/zigux/validate-phase11.py`
  or `make -C zigux phase11-validate` are already present on current `master`
- a claim that bcm2835 or DesignWare validation-matrix notes are already
  directly readable again on current `master`
- a claim that bcm2835 or gpio reminder packets have been broadly reread beyond
  the watchdog-local surfaces touched in their own lanes
- a claim that the older DesignWare packet-checker handle is already directly
  readable again
- broader hardware-backed watchdog validation, tty registration parity,
  notifier execution, sysrq dispatch, khvcd execution, or host-backed teardown
  closure
- a migration of driver-local reminder ownership into the shared packet
