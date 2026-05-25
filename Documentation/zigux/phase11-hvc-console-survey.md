# Phase 11 HVC Console Survey

This note keeps the bounded Phase 11 `hvc_console` packet truthful on current
`master`.

## Status

- `PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`
- archival landing lane: `P11-L13`
- current coupled packet continuity: `P11-L16`
- the Phase 11 roadmap still keeps `drivers/tty/hvc/*.zig` inside bounded
  simple-production-driver work where teardown parity and failure-mode
  reviewability should deepen before any live execution claims
- current authenticated contents readback keeps the bounded HVC current-head
  packet reviewable through the direct starter, current survey, current-head
  companion, verify-helper boundary note, validation matrix, the returned
  `phase11-validate` validator surfaces, the shared manifest-roster guard, the
  validate-check roster guard, the validate-route alignment guard, the
  dedicated validate-check fixture roster, the build-inventory checker,
  focused-direct-build replay checker, cleanup-current-head checker,
  targetless-unregister witness checker, shared build inventory, the
  proof-backed adjunct stack, the dedicated modem-control proof pair, and the
  standalone targetless-unregister witness pair
- current authenticated contents readback still does not rematerialize
  `drivers/tty/hvc/hvc_console_verify.zig`,
  `drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`,
  `zigux/tests/phase11_hvc_cleanup.zig`,
  `zigux/tests/phase11_hvc_console_survey.zig`,
  `zigux/tests/phase11_hvc_console_manifest.json`,
  `Documentation/zigux/phase11-hvc-console-teardown-note.md`, or
  `scripts/zigux/check-phase11-hvc-survey-packet.py`; keep those anchors framed
  as repo-reality gaps or archival vocabulary instead of returned fallback
  evidence until a future reread proves they returned
- `zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey`
  route, so keep the current route claim bounded to `make -C zigux phase11-validate`

## Current-Head Packet

Treat the current bounded HVC packet on `master` as:

- `.github/workflows/zigux-bootstrap.yml`
- `drivers/tty/hvc/hvc_console.h`
- `drivers/tty/hvc/hvc_console.zig`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-validate-manifest-roster.py`
- `scripts/zigux/check-phase11-validate-check-roster.py`
- `scripts/zigux/check-phase11-validate-route-alignment.py`
- `scripts/zigux/check-phase11-focused-direct-build-replays.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/validate-phase11.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/fixtures/phase11_validate_checks.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- `zigux/tests/phase11_hvc_modem_control_proof.zig`
- `zigux/tests/phase11_hvc_modem_control_proof_build.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`

The shared validator route now rereads the dedicated
`zigux/tests/fixtures/phase11_validate_checks.json` roster through the
manifest-roster, validate-check-roster, and validate-route-alignment guards
before the same proof-backed build fan-out runs, so keep those validator-side
surfaces explicit beside the HVC starter and companion packet. The shared
build-inventory checker, focused-direct-build replay checker, and shared build
inventory still record the three proof-backed build tests while keeping the
dedicated modem-control and standalone targetless-unregister build routes
explicit as direct-readback checks instead of promoting either pair into that
shared three-entry inventory. `drivers/tty/hvc/hvc_console.h` now stays
explicit in the current packet too, keeping the exported `struct hvc_struct`
forward declaration, `struct hv_ops` tag, `struct winsize` layout, and helper
prototypes directly readable beside the starter Zig module and the focused
export-surface proofs. `scripts/zigux/validate-phase11.py`, `zigux/Makefile`,
and `.github/workflows/zigux-bootstrap.yml` keep the same validator-backed
route directly readable on current `master` too. Keep the dedicated survey
route absent until `zigux/Makefile` grows it explicitly. The dedicated
modem-control proof pair likewise stays directly readable as a focused adjunct
route without promoting itself into the shared three-entry build inventory, and
the standalone targetless-unregister witness pair likewise stays directly
readable as a separate failure-mode replay without promoting itself into the
shared three-entry build inventory.

## Exact Current Checks

Keep the live HVC delivery-tooling commands explicit too:

- shared validator route: `python3 scripts/zigux/validate-phase11.py --self-test`, `python3 scripts/zigux/validate-phase11.py`, and `make -C zigux phase11-validate`
- HVC adjunct proof builds: `zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig`, and `zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- focused failure-mode builds: `zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig` and `zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
- coupled checker routes: `python3 scripts/zigux/check-phase11-build-inventory.py --self-test`, `python3 scripts/zigux/check-phase11-build-inventory.py`, `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py --self-test`, `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py`, `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test`, `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test`, and `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- the machine-readable command roster stays pinned in `zigux/tests/fixtures/phase11_validate_checks.json`, while `zigux/tests/fixtures/phase11_build_inventory.json` keeps the shared three-entry adjunct build packet separate from the focused modem-control and targetless-unregister failure-mode routes
- no dedicated `make -C zigux phase11-hvc-survey` wrapper is currently shipped on `master`, so keep that route absent until `zigux/Makefile` grows it explicitly instead of treating the focused adjunct and failure-mode builds as a returned dedicated survey path

## Still-Bounded Gaps

Keep `Documentation/zigux/phase11-hvc-console-slice.md` and a dedicated
`make -C zigux phase11-hvc-survey` route framed as remaining gaps until a
future reread proves they returned.

Keep `drivers/tty/hvc/hvc_console_verify.zig`,
`drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`,
`zigux/tests/phase11_hvc_cleanup.zig`,
`zigux/tests/phase11_hvc_console_survey.zig`,
`zigux/tests/phase11_hvc_console_manifest.json`,
`Documentation/zigux/phase11-hvc-console-teardown-note.md`, and
`scripts/zigux/check-phase11-hvc-survey-packet.py` framed as repo-reality gaps
or archival vocabulary until a future reread proves they returned.

Keep the lane below live tty registration, notifier callback execution, khvcd
execution, live sysrq dispatch, and host-backed teardown parity.

## Bounded Meaning

This note records that the HVC simple-driver lane still has reviewable
current-head continuity through the direct starter, the current companion stack,
the verify-boundary reminder surface, the shared inventory-backed proof routes,
the validator-side manifest-roster, validate-check-roster, and
validate-route-alignment guards, the dedicated validate-check fixture roster,
the focused-direct-build replay checker, the validator-backed
`make -C zigux phase11-validate` route, the dedicated modem-control proof pair,
and the standalone targetless-unregister witness pair.

It does not claim that the currently missing verify helper, sysrq helper,
focused survey replay, manifest, teardown note, or dedicated survey checker
have returned, nor does it claim live tty-driver registration, notifier
callback execution, khvcd polling execution, live sysrq dispatch, host-backed
cleanup, or hardware-validated teardown parity.
