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
- the live shared ABI packet also already ships `zigux/uapi/dev_t.zig`, so the manifest-backed boundary is no longer a version-only UAPI starter even though some older shared review surfaces still summarize it that way.
- that means current `master` now documents and syntax-guards the header, carries the bounded baseline constant-parity survey, carries the landed two-family header proof inside the live chrdev ladder, and already includes one dedicated `dev_t` UAPI starter without claiming broader family closure.
- compared against the roadmap-backed ABI substrate packet and the bootstrap ledger's Phase 3 skeleton scope, the smallest same-lane truthfulness gap is no longer another adjacent `abi.h` family foothold. The smaller live gap is keeping shared review surfaces honest about the already-shipped two-family survey plus the now-landed `zigux/uapi/dev_t.zig` starter before any new top-level `ZIGUX_CHRDEV_*` growth lands.

## Next Safe Step

Before adding another top-level `ZIGUX_CHRDEV_*` family or another sibling family to `include/zigux/abi.h`, stay inside the same bounded review packet:

- inspect only the shared review surfaces that summarize the shipped ABI validator-support packet, especially `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`
- refresh those shared summaries so they explicitly carry the shipped `zigux/uapi/dev_t.zig` starter and the resulting current manifest-backed ABI packet count before treating the boundary as a 57-file or version-only UAPI packet again
- keep the already-landed `phase3-abi-header-family-survey` note and checker explicit wherever those shared summaries name the current Phase 3 ABI validator-support packet, instead of treating the two-family proof as implicit behind the baseline constant-parity survey alone
- only return to another exact constant or exact view or summary foothold inside `include/zigux/abi.h` when one of those shared review surfaces is truthful again and a new landed family pair actually exists to justify a fresh bounded proof
- keep the proof in the shared Phase 3 ABI packet instead of widening into helper, export/UAPI, or later driver lanes

## Non-Goals

This note does not claim that the chrdev family should be expanded further now.
It also does not claim a broad Phase 3 ABI rewrite, generator switch, or packet split.
The immediate goal is only to keep the next bounded `abi.h` follow-up explicit before more top-level surface lands.
