# Phase 11 UAPI Header Parity Survey
## Status

- `PHASE11_HEADER_BOUNDARY_STATUS=shared_header_packet_restored`
- lane: `P11-L18`
- reviewed against `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839` on current `master`
- scope: keep the shared `phase11-uapi-header-parity-surface` truthful around the bounded `watchdog_info`, `winsize`, and `hvc_console.h` header boundary without widening into tty-core or watchdog-core ownership

## Current Repo Reality
- shared packet still shipped on current `master`:
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `zigux/tests/phase11_uapi_header_parity_manifest.json`
  - `zigux/tests/phase11_uapi_header_parity_survey.zig`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `zigux/tests/phase11_build.zig`
- adjacent dedicated HVC proof shards still reinforce the same public surface without replacing the shared packet:
  - `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
  - `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
  - `zigux/tests/fixtures/phase11_build_inventory.json`
  - `drivers/tty/hvc/hvc_console.h`

## Roadmap Fit
- Phase 11 still treats bounded watchdog and HVC surfaces as the simple-production-driver anchors.
- Phase 11 still requires reviewable validation, matrix evidence, and failure-mode discipline before expansion.
- This survey stays useful only if it reflects the restored shared header packet and the adjacent proof shards together rather than relabeling the shared survey, manifest, checker, or build route as missing.

## Current-Head Boundary
- `phase11-build-gate`: `zigux/tests/phase11_build.zig` keeps the shared header-boundary replay visible beside the watchdog starters and the dedicated HVC packet.
- `phase11-uapi-header-parity-survey-gate`: `zigux/tests/phase11_uapi_header_parity_survey.zig` replays the bounded `watchdog_info` and `winsize` layout checkpoints, the shared replay contract markers, the `hv_ops` callback-table layout proof, the HVC header constants, and the exported helper declarations without widening into tty-core ownership.
- `phase11-uapi-header-parity-note`: this note records the restored shared packet, the current inspected commit, and the shared-versus-dedicated replay split that keeps the HVC survey separate.
- `phase11-dw-wdt-watchdog-info-layout-assert`: the shared packet keeps `struct watchdog_info` explicit at size 40, alignment 4, with offsets 0, 4, and 8 so the public watchdog boundary stays reviewable without claiming `watchdog_device` ownership.
- `phase11-hvc-console-winsize-layout-assert`: the shared packet keeps `struct winsize` explicit at size 8, alignment 2, with offsets 0, 2, 4, and 6 so the resize boundary stays anchored in public UAPI rather than tty-core internals.
- `phase11-hvc-console-hv-ops-layout-assert`: the shared packet keeps `struct hv_ops` explicit at size 72, alignment 8, with callback-table offsets 0 through 64 so the exported HVC callback surface stays reviewable without claiming tty-core callback execution parity.
- `phase11-hvc-console-header-constant-assert`: the shared packet keeps `MAX_NR_HVC_CONSOLES` and `HVC_ALLOC_TTY_ADAPTERS` machine-checked so the bounded public HVC header constants stay reviewable beside the callback and export surfaces.
- `phase11-hvc-console-export-signature-assert`: the shared packet keeps the exact exported `hvc_instantiate`, `hvc_alloc`, `hvc_remove`, `hvc_poll`, `hvc_kick`, `__hvc_resize`, `notifier_add_irq`, `notifier_del_irq`, and `notifier_hangup_irq` declarations in `drivers/tty/hvc/hvc_console.h` machine-checked as the bounded public driver-header boundary.

## Shared Versus Dedicated Replay
- shared replay route: `zig build phase11-uapi-header-parity-survey --build-file zigux/tests/phase11_build.zig --summary all`
- dedicated `zig build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all` step continues to carry the broader HVC archival packet rather than the shared `test` step.
- `Documentation/zigux/phase11-shared-replay-contract.md` still records the shared packet route and the explicit split from the dedicated HVC survey.
- `zigux/tests/fixtures/phase11_build_inventory.json` should still be read as adjacent HVC continuity evidence, not as a replacement for the restored shared packet.

## Why This Stays Bounded

- The current packet proves the restored shared header-boundary survey plus the adjacent proof shards that reinforce the same public HVC surface.
- It does not claim tty registration parity, notifier execution parity, watchdog-core integration, or whole-Phase-11 closure.
- Any future driver-local handoff still belongs in the smallest same-family follow-up that keeps the shared packet truthful before widening into broader driver or contributor-note ownership.
