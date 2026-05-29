# Phase 11 ABI Layout Assertion Evidence

## Status

- `PHASE11_ABI_LAYOUT_ASSERTION_EVIDENCE_STATUS=current_hvc_layout_packet_verified`
- lane: `P11-L15`
- reviewed against current `master` on `2026-05-29`
- scope: verify the current ABI layout assertions that remain live for Phase 11 without broadening into driver behavior, cleanup ownership, watchdog proof ownership, or the retired shared header-parity replay family

## Roadmap And Ledger Fit

- Phase 11 still uses bounded HVC and watchdog simple-driver surfaces as the production-driver anchors.
- The ABI/layout assertion substrate comes from the earlier Phase 3 tranche, especially the `zigux/helpers/layout_assert.zig` helper and curated boundary discipline.
- This evidence note records the live Phase 11 HVC-centered layout assertion packet as current repo fact; it does not claim whole-Phase-11 closure or a restored cross-driver UAPI replay.

## Current Readback Evidence

Current authenticated readback of `master` showed these exact evidence paths and blob IDs:

- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` blob `1c6c6c667e79cb06578e786071ab35c009750503`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig` blob `1036e2aecc99c8e1b7497c0ba106a9e8ba6a6d3b`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig` blob `b8a780989f1eb27740a7790d2c5a6f438768fa46`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig` blob `3caa4744295cb6ba68166e58a6307825a6798c33`
- `zigux/tests/fixtures/phase11_build_inventory.json` blob `3704ef70cc3e5adfb962ce3b3219f91be6674d37`
- `scripts/zigux/check-phase11-build-inventory.py` blob `7476032db87e781131a06068b9e4e75830f18e62`
- `drivers/tty/hvc/hvc_console.zig` blob `69e534ffc0d183ee8e335f56142075f26ae375fc`
- `drivers/tty/hvc/hvc_console.h` blob `57f1542b3e6f1901f444bc2d94b5e438f14eb9b3`
- `zigux/tests/phase11_build.zig` blob `4a7fd056f2e246bc5c81c108ce3a304543441e02`
- `zigux/Makefile` blob `f49b44b6f70ce70b8f0c7b04b8fb88c805ba40c9`
- `.github/workflows/zigux-bootstrap.yml` blob `5bdb136b8b6710c08c19566879d5a9da42b63445`

The retired shared header-parity replay anchors still return `404 Not Found` on current `master`:

- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`

`zigux/tests/phase11_build.zig` is present again, but the current file is a simple-driver verification build for `phase11-gpio-wdt-verify-tests`, `phase11-hvc-console-verify-tests`, and `phase11-simple-drivers`; it is not the restored cross-driver ABI/header-parity replay route.

## Exact Assertions Verified

### `struct hv_ops`

The current HVC callback-table proof keeps `struct hv_ops` explicit in `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` and repeats the imported-module checks in `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`:

- size `72`
- alignment `8`
- field offsets: `get_chars=0`, `put_chars=8`, `flush=16`, `notifier_add=24`, `notifier_del=32`, `notifier_hangup=40`, `tiocmget=48`, `tiocmset=56`, `dtr_rts=64`
- callback signatures exact-checked against C ABI types, including `c_char`, `c_int`, `c_uint`, and `callconv(.c)`
- imported `drivers/tty/hvc/hvc_console.zig` `HvOps` layout and callback signatures tied back to the same expected C ABI shape

### `struct winsize`

The current exported-surface proof keeps the HVC `winsize` shape explicit:

- size `8`
- alignment `2`
- field offsets: `ws_row=0`, `ws_col=2`, `ws_xpixel=4`, `ws_ypixel=6`
- imported `drivers/tty/hvc/hvc_console.zig` `Winsize` field types exact-checked as `u16`
- exported C header text still exposes the four `uint16_t` fields in `drivers/tty/hvc/hvc_console.h`

### Exported HVC Helper Surface

The current exported-helper proof models the exported HVC helper table as `HvcExportSurface` and keeps it explicit:

- size `72`
- alignment `8`
- field offsets: `hvc_instantiate=0`, `hvc_alloc=8`, `hvc_remove=16`, `hvc_poll=24`, `hvc_kick=32`, `__hvc_resize=40`, `notifier_add_irq=48`, `notifier_del_irq=56`, `notifier_hangup_irq=64`
- exported helper signatures exact-checked in Zig against the C ABI shape
- imported declarations from `drivers/tty/hvc/hvc_console.zig` exact-checked against those exported helper signatures

### Exported Header Constants

The current exported-surface proof also keeps these constants exact against both the Zig module and `drivers/tty/hvc/hvc_console.h` text:

- `MAX_NR_HVC_CONSOLES = 16`
- `HVC_ALLOC_TTY_ADAPTERS = 1`

## Build And Validator Routing

The current build and validator evidence remains narrower than the retired shared replay family:

- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig` runs `phase11-hvc-hv-ops-layout-proof-tests` and also includes `phase11-hvc-export-surface-layout-proof-tests` through the same focused exported-header proof build.
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig` runs the standalone `phase11-hvc-export-surface-layout-proof` route.
- `zigux/tests/fixtures/phase11_build_inventory.json` still lists the HVC `hv_ops`, exported-surface, and cleanup proof shards as shared adjunct replay evidence and keeps the modem-control plus targetless-unregister builds as focused direct-build companions.
- `zigux/Makefile` still exposes `phase11-validate`.
- `.github/workflows/zigux-bootstrap.yml` still runs `make -C zigux phase11-validate` as `Validate current Phase 11 support bundle`.

## Conclusion

The current Phase 11 ABI layout assertion suite is live and concrete, but it is HVC-centered. The exact current assertions cover `struct hv_ops`, `struct winsize`, exported HVC helper declarations, and the two exported HVC constants. Current `master` does not restore the older shared manifest or shared survey source, and the returned `zigux/tests/phase11_build.zig` is a simple-driver verification route rather than a restored ABI/header-parity replay route.

The next bounded `P11-L15` step is to leave the proof shards parked unless one of the exact assertions above drifts, or a future Phase 11 public surface adds another struct layout proof that needs the same evidence treatment.
