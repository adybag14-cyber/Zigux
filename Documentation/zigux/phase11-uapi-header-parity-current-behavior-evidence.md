# Phase 11 UAPI Header Parity Current Behavior Evidence

## Status

- `PHASE11_UAPI_HEADER_CURRENT_BEHAVIOR_STATUS=hvc_centered_packet_live_shared_replay_absent`
- lane: `P11-L09`
- reviewed against current `master` on `2026-05-27`
- scope: verify the exact current behavior of the Phase 11 UAPI header-parity packet without widening ownership into tty-core, watchdog-core, or whole-phase closure

## Roadmap And Ledger Fit

- The roadmap still places public HVC and watchdog surfaces inside Phase 11 simple production drivers, so a bounded public-header truthfulness reread is valid same-phase work.
- The bootstrap ledger carries the older ABI and UAPI substrate seed in the Phase 3 tranche, but it does not promise that a broad shared Phase 11 header replay family already exists on current `master`.
- Current repo truth therefore has to be taken from live Phase 11 files, not from older continuity shorthand.

## Verified Current Behavior

### 1. The shared header-boundary checker is present, but it is note-side only.

Direct readback of `scripts/zigux/check-phase11-header-boundary-packet.py` shows that the checker reads exactly these four note files:
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-checker-coverage-note.md`
- `Documentation/zigux/phase11-uapi-header-parity-hv-ops-followup.md`

The same checker advertises these exact success strings:
- `PHASE11_HEADER_BOUNDARY_PACKET=pass`
- `PHASE11_HEADER_BOUNDARY_PACKET_SELF_TEST=pass`

Its self-test body also hard-codes seven cases total:
- one baseline pass case
- six targeted failure cases covering missing required markers and forbidden stale wording

That confirms the returned checker fail-closes the four-note packet, but it does not read a shared manifest, a shared survey Zig source, or a shared Phase 11 build route.

### 2. The live validator route includes the header packet and the focused HVC proof routes.

Direct readback of `scripts/zigux/validate-phase11.py` shows that the live validator requires all of these Phase 11 header-boundary surfaces to exist together:
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `drivers/tty/hvc/hvc_console.h`
- `drivers/tty/hvc/hvc_console.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- `zigux/tests/phase11_hvc_modem_control_proof.zig`
- `zigux/tests/phase11_hvc_modem_control_proof_build.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
- `zigux/tests/fixtures/phase11_build_inventory.json`

The same validator's explicit check roster includes:
- the header-boundary checker in self-test and live modes
- the focused direct-build replay checker in self-test and live modes
- the HVC `hv_ops` layout build
- the HVC exported-surface layout build
- the HVC cleanup packet build
- the HVC modem-control proof build
- the HVC targetless-unregister witness build

Direct readback of `zigux/Makefile` shows `phase11-validate` is already wired as a shared route on current `master`, and that target runs:
- `python scripts/zigux/validate-phase11.py`
- fourteen explicit `zig build test --build-file ...` Phase 11 replay steps

That means current behavior is not note-only. The live packet includes a real validator entrypoint and a real focused HVC build fan-out.

### 3. The surviving inventory explicitly says the older shared replay family is still absent.

Direct readback of `zigux/tests/fixtures/phase11_build_inventory.json` shows:
- `dedicated_survey_replays` is `[]`
- `shared_split_replays` is `[]`
- `shared_adjunct_replays` is limited to the HVC `hv_ops`, exported-surface, and cleanup proof shards
- `focused_direct_build_replays` is limited to the modem-control and targetless-unregister builds

The same inventory file keeps these exact missing-family implications in place:
- no shared survey replay source is listed
- no shared split replay is listed
- no restored `zigux/tests/phase11_build.zig` route is listed

That current inventory behavior matches the survey-side wording that the older shared replay anchors are still absent:
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `zigux/tests/phase11_build.zig`

### 4. The exact shipped layout evidence is HVC-centered and concrete.

Direct readback of `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` shows the live proof packet exact-checks `struct hv_ops` at:
- size `72`
- alignment `8`
- offsets `0, 8, 16, 24, 32, 40, 48, 56, 64`

The same proof ties those offsets and callback signatures back to `drivers/tty/hvc/hvc_console.h` and to imported types from `drivers/tty/hvc/hvc_console.zig`.

Direct readback of `zigux/tests/phase11_hvc_export_surface_layout_proof.zig` shows the live exported-surface packet exact-checks:
- `struct winsize` at size `8`, alignment `2`, offsets `0, 2, 4, 6`
- `struct hv_ops` again at size `72`, alignment `8`, offsets `0, 8, 16, 24, 32, 40, 48, 56, 64`
- `HvcExportSurface` at size `72`, alignment `8`, offsets `0, 8, 16, 24, 32, 40, 48, 56, 64`

That same proof also exact-checks these exported header constants against the current Zig module and the current C header text:
- `MAX_NR_HVC_CONSOLES = 16`
- `HVC_ALLOC_TTY_ADAPTERS = 1`

### 5. The reminder-surface gap is still real.

Direct readback of `scripts/zigux/README.md` and `zigux/tests/README.md` shows that both shared reminder surfaces still jump from Phase 10 to Phase 12.

So current behavior is:
- the Phase 11 validator route is live
- the HVC-centered proof packet is live
- the returned note-side checker is live
- the broad shared replay family is still absent
- the shared reminder surfaces still under-report the live Phase 11 packet

## Exact Current Conclusion

The truthful current-head description is:
- Phase 11 UAPI header parity is currently enforced through a narrower HVC-centered packet
- that packet includes a returned four-note checker, a live `phase11-validate` route, a real focused HVC proof-build fan-out, and a real build inventory file
- current `master` does not yet rematerialize the older shared manifest, shared survey Zig source, or shared Phase 11 build route that would be needed to claim a restored cross-driver header replay family
- current shared reminder surfaces still lag the shipped packet even though the validator and focused proof routes are already present

## Next Bounded Step

Choose one of these, but do not merge them in the same pass:
- restore the missing shared replay anchors if the product really wants a broader cross-driver header-parity family again
- update `scripts/zigux/README.md` and `zigux/tests/README.md` so the shared reminder surfaces stop skipping the already-shipped Phase 11 validator-backed packet
