# Phase 11 UAPI Header Parity Current Behavior Evidence

## Status

- `PHASE11_UAPI_HEADER_CURRENT_BEHAVIOR_STATUS=hvc_centered_packet_live_shared_replay_partial_reminder_only`
- lane: `P11-L09`
- reviewed against current `master` on `2026-05-29`
- scope: verify the exact current behavior of the Phase 11 UAPI header-parity packet without widening ownership into tty-core, watchdog-core, notifier execution, driver-local teardown, or whole-phase closure

## Roadmap And Ledger Fit

- The roadmap still places public HVC and watchdog surfaces inside Phase 11 simple production drivers, so a bounded public-header truthfulness reread is valid same-phase work.
- The bootstrap ledger carries the older ABI and UAPI substrate seed in the Phase 3 tranche, but it does not promise that a broad shared Phase 11 header replay family already exists on current `master`.
- Current repo truth therefore has to be taken from live Phase 11 files, not from older continuity shorthand.

## Verified Current Readback

Current live `master` readback on `2026-05-29` showed these exact blob IDs for the header-boundary packet:

- `Documentation/zigux/phase11-uapi-header-parity-survey.md` blob `61239f27a844be63911d64910cca99842f38dcaa`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` blob `7b8f3836731a4388676f240296ebede0880fc48f`
- `Documentation/zigux/phase11-shared-replay-contract.md` blob `3c1821607cf62a2adede73791bfbb94121a0d697`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` blob `1c6c6c667e79cb06578e786071ab35c009750503`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig` blob `b8a780989f1eb27740a7790d2c5a6f438768fa46`
- `zigux/tests/fixtures/phase11_build_inventory.json` blob `86bdd83a4fc8544c09ba7f0f6cedb8685700f59c`
- `scripts/zigux/check-phase11-build-inventory.py` blob `7476032db87e781131a06068b9e4e75830f18e62`
- `scripts/zigux/check-phase11-header-boundary-packet.py` blob `a55e944f4678261951541746d6cc229dcb840929`
- `scripts/zigux/validate-phase11.py` blob `29ce468f917ef8d1b8eeb8b6dccd928eceafc323`
- `drivers/tty/hvc/hvc_console.h` blob `57f1542b3e6f1901f444bc2d94b5e438f14eb9b3`
- `zigux/Makefile` blob `f49b44b6f70ce70b8f0c7b04b8fb88c805ba40c9`
- `.github/workflows/zigux-bootstrap.yml` blob `5bdb136b8b6710c08c19566879d5a9da42b63445`

The same live readback returned `404 Not Found` for these retired shared header-parity anchors:

- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`

Current live readback also shows `zigux/tests/phase11_build.zig` is present again at blob `4a7fd056f2e246bc5c81c108ce3a304543441e02`. Its current content is a simple-driver verification build for:

- `phase11-gpio-wdt-verify-tests`
- `phase11-hvc-console-verify-tests`
- `phase11-simple-drivers`

That means `zigux/tests/phase11_build.zig` should no longer be described as absent. It also should not be treated as a restored UAPI/header parity replay route, because it does not rematerialize the retired shared manifest or retired shared survey source.

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

That confirms the returned checker fail-closes the four-note packet, but it does not read a shared manifest, a shared survey Zig source, or the current `zigux/tests/phase11_build.zig` simple-driver verification build.

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

Direct readback of `zigux/Makefile` shows `phase11-validate` is wired as a shared route on current `master`, and direct readback of `.github/workflows/zigux-bootstrap.yml` shows the bootstrap workflow runs `make -C zigux phase11-validate` as `Validate current Phase 11 support bundle`.

That means current behavior is not note-only. The live packet includes a real validator entrypoint and a real focused HVC build fan-out.

### 3. The surviving inventory explicitly narrows the shared replay family.

Direct readback of `zigux/tests/fixtures/phase11_build_inventory.json` shows:

- `dedicated_survey_replays` is `[]`
- `shared_split_replays` is `[]`
- `shared_adjunct_replays` is limited to the HVC `hv_ops`, exported-surface, and cleanup proof shards
- `shared_adjunct_build_replays` is limited to the HVC `hv_ops`, exported-surface, and cleanup build files
- `focused_direct_build_replays` is limited to the modem-control and targetless-unregister builds

The current inventory therefore does not list a shared survey source or shared split replay. It keeps the header-boundary proof anchored in the HVC adjunct proof trio plus focused direct-build companions.

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

Direct readback of `drivers/tty/hvc/hvc_console.h` confirms the header still exposes `MAX_NR_HVC_CONSOLES 16`, `HVC_ALLOC_TTY_ADAPTERS 1`, `struct winsize`, `struct hv_ops`, and exported helper declarations through `notifier_hangup_irq`.

### 5. The reminder-surface gap remains separate.

The header survey still records that broader reminder surfaces lag the live Phase 11 packet. That is a separate reminder-surface follow-up, not proof that the HVC-centered header-boundary packet itself is missing.

## Exact Current Conclusion

The truthful current-head description is:

- Phase 11 UAPI header parity is currently enforced through a narrower HVC-centered packet.
- That packet includes a returned four-note checker, a live `phase11-validate` route, a real focused HVC proof-build fan-out, and a real build inventory file.
- Current `master` does not rematerialize the retired shared manifest or retired shared survey Zig source.
- Current `master` does contain `zigux/tests/phase11_build.zig`, but the file is a simple-driver verification build, not the restored cross-driver UAPI/header parity replay route.
- Current shared reminder surfaces still lag the shipped packet even though the validator and focused proof routes are already present.

## Next Bounded Step

Refresh the survey and validation matrix wording in a narrow follow-up if they still claim `zigux/tests/phase11_build.zig` is absent. The accurate wording is that the path is present again, but it is not the restored shared UAPI/header parity replay route.