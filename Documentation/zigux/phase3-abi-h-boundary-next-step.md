# Phase 3 `include/zigux/abi.h` Boundary Next Step

This note keeps the current `include/zigux/abi.h` boundary honest without widening beyond the shared Phase 3 ABI header itself.

## Status

- `PHASE3_LANE=P3-Y06`
- `PHASE3_BOUNDARY_FILE=include/zigux/abi.h`
- `PHASE3_BOUNDARY_BLOB_SHA=c588b6d2c81659ff8996495d001dd1ebad7df1b1`
- `PHASE3_BOUNDARY_BINDINGS=zigux/bindings/abi.zig`
- `PHASE3_BOUNDARY_BINDINGS_BLOB_SHA=d8df5a2a888ed29c71d2c75e7f6cd0bd18d37771`
- `PHASE3_NOTE_SCOPE=one bounded next-safe-step note for the authoritative C ABI header only`

## Current Repo Evidence

- `include/zigux/abi.h` is no longer only the small Phase 3 root described by the original ABI-substrate skeleton commit train.
- the live header still owns the baseline boundary root (`zigux_boundary_header`, `zigux_export_status`, bitmap or cpumask, list, hlist, err_ptr, xarray, ida, and related starter packets), but it also now carries a very large `ZIGUX_CHRDEV_*` family with deeply nested notify, ack, budget, window, and delivery-budget-guard constants and structs.
- `zigux/bindings/abi.zig` mirrors that same large family, so this is real shared boundary surface, not a C-only stub.
- the current shipped guards around this boundary are still intentionally bounded:
  - `scripts/zigux/validate-phase3-abi-bindings-syntax.py` fail-closes on fused top-level declarations and verifies the shared ABI packet contract.
  - `scripts/zigux/survey-phase3-abi-constant-parity.py` checks the baseline facility, status, panic, allocator, and unsafe constants, two landed chrdev delivery-window family constants, and one exact delivery-window view-plus-summary type pair across both `include/zigux/abi.h` and `zigux/bindings/abi.zig`.
  - `scripts/zigux/validate-phase3-abi-header-family-survey.py` plus `Documentation/zigux/phase3-abi-header-family-survey.md` now keep two directly adjacent footholds explicit: the original `chrdev_notify_ack_window_policy_budget_window_delivery_window` family and the adjacent `chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery` family. The survey fail-closes on each family's exact status constant pair, exact budget-applied constant pair, and landed view-plus-summary type pair across the authoritative C header and curated Zig bindings.
- the manifest-backed Phase 3 ABI packet is now the 58-file surface recorded in `zigux/tests/fixtures/phase3_abi_manifest.json`, and that packet already includes `zigux/uapi/dev_t.zig`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `Documentation/zigux/phase3-abi-header-family-survey.md`, and `scripts/zigux/validate-phase3-abi-header-family-survey.py` alongside the authoritative header, curated bindings, and shared validator routes.
- `scripts/zigux/validate-phase3.py` already requires that same landed packet, so the current gap is not missing packet membership or another fresh `abi.h` foothold inside the live chrdev ladder.
- the remaining drift is in the broad shared review summaries only: `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` still summarize the shared Phase 3 ABI packet without keeping the landed header-family survey and this boundary note equally explicit, and the scripts-root summary still omits `scripts/zigux/validate-phase3-abi-header-family-survey.py` from its Phase 3 helper inventory.
- compared against the roadmap-backed ABI substrate packet and the bootstrap ledger's Phase 3 skeleton scope, the smallest same-lane truthfulness gap is therefore no longer another adjacent `abi.h` family foothold. The smaller live gap is shared-surface accounting drift around the already-landed `include/zigux/abi.h` review packet.

## Next Safe Step

Before adding another top-level `ZIGUX_CHRDEV_*` family or another sibling family to `include/zigux/abi.h`, stay inside the same bounded review packet:

- refresh only the shared review surfaces that summarize the shipped ABI validator-support packet: `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`
- make those four shared summaries explicitly carry `Documentation/zigux/phase3-abi-header-family-survey.md`, `scripts/zigux/validate-phase3-abi-header-family-survey.py`, and `Documentation/zigux/phase3-abi-h-boundary-next-step.md` as part of the current Phase 3 ABI packet instead of leaving them implicit behind the baseline constant-parity survey alone
- keep `zigux/uapi/dev_t.zig` explicit wherever those same summaries still compress the UAPI side down to version-only shorthand
- leave `include/zigux/abi.h`, `zigux/bindings/abi.zig`, the landed header-family survey checker, and the shared Phase 3 validator logic untouched until those broad summaries stop understating the already-landed packet
- only return to another exact constant or exact view or summary foothold inside `include/zigux/abi.h` when those shared review surfaces are truthful again and a new landed adjacent family actually exists to justify a fresh bounded proof
- keep the proof in the shared Phase 3 ABI packet instead of widening into helper, export/UAPI, or later driver lanes

## Non-Goals

This note does not claim that the chrdev family should be expanded further now.
It also does not claim a broad Phase 3 ABI rewrite, generator switch, or packet split.
The immediate goal is only to keep the next bounded `abi.h` follow-up explicit before more top-level surface lands.
