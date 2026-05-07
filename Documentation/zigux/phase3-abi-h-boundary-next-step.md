# Phase 3 `include/zigux/abi.h` Boundary Next Step

This note keeps the current `include/zigux/abi.h` boundary honest without widening beyond the shared Phase 3 ABI header itself.

## Status

- `PHASE3_LANE=P3-Y06`
- `PHASE3_BOUNDARY_FILE=include/zigux/abi.h`
- `PHASE3_BOUNDARY_BLOB_SHA=c588b6d2c81659ff8996495d001dd1ebad7df1b1`
- `PHASE3_BOUNDARY_BINDINGS=zigux/bindings/abi.zig`
- `PHASE3_BOUNDARY_BINDINGS_BLOB_SHA=7a2d25c8ae492cbdf5a8af7097e4bdaa749b5674`
- `PHASE3_NOTE_SCOPE=one bounded next-safe-step note for the authoritative C ABI header only`

## Current Repo Evidence

- `include/zigux/abi.h` is no longer only the small Phase 3 root described by the original ABI-substrate skeleton commit train.
- The live header still owns the baseline boundary root (`zigux_boundary_header`, `zigux_export_status`, bitmap or cpumask, list, hlist, err_ptr, xarray, ida, and related starter packets), but it also now carries a very large `ZIGUX_CHRDEV_*` family with deeply nested notify, ack, budget, window, and delivery-budget-guard constants and structs.
- `zigux/bindings/abi.zig` mirrors that same large family, so this is real shared boundary surface, not a C-only stub.
- The current shipped guards around this boundary are still narrower than the live family growth:
  - `scripts/zigux/validate-phase3-abi-bindings-syntax.py` fail-closes on fused top-level declarations and verifies the shared ABI packet contract.
  - `scripts/zigux/survey-phase3-abi-constant-parity.py` currently checks only five baseline constants: facility, status flag, panic mode, allocator mode, and one unsafe scope constant.
- That means current `master` does document and syntax-guard the header, but it does not yet carry a dedicated family-growth survey for the large chrdev notify or ack ladder now living in `include/zigux/abi.h`.

## Next Safe Step

Before adding another top-level `ZIGUX_CHRDEV_*` family or another sibling family to `include/zigux/abi.h`, add one dedicated header-family survey that stays bounded to this same boundary:

- inspect only `include/zigux/abi.h` and `zigux/bindings/abi.zig`
- anchor one already-landed family prefix, starting with the current chrdev notify or ack delivery-budget guard ladder
- fail closed if the curated C header and curated Zig bindings drift on that family’s root constants or view or summary type names
- record the survey in the shared Phase 3 ABI packet instead of widening into helper, export/UAPI, or later driver lanes

## Non-Goals

This note does not claim that the chrdev family should be expanded further now.
It also does not claim a broad Phase 3 ABI rewrite, generator switch, or packet split.
The immediate goal is only to make the next bounded `abi.h` follow-up explicit before more top-level surface lands.
