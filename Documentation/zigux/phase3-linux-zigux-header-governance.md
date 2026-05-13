# Phase 3 Linux `zigux.h` Header Governance

This note closes the dedicated ownership and boundary-note gap for `include/linux/zigux.h` inside the shared Phase 3 ABI packet.

## Scope

- `PHASE3_ZIGUX_H_PATH=include/linux/zigux.h`
- `PHASE3_ZIGUX_H_BLOB_SHA=848f61bedfb9cd19f0f8aeee6879a1e7f7421ef7`
- `PHASE3_ZIGUX_H_PACKET=shared Phase 3 ABI substrate packet only`
- `PHASE3_ZIGUX_H_SHARED_SLICE_NOTE=Documentation/zigux/phase3-abi-slice.md`
- `PHASE3_ZIGUX_H_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`
- `PHASE3_ZIGUX_H_VALIDATOR_PATH=scripts/zigux/validate-phase3-linux-zigux-header-governance.py`
- this note governs how the Linux-facing aggregation header may grow without turning header churn into fake Phase 3 progress

## Ownership

- canonical struct layout ownership stays in `include/zigux/abi.h` and `include/zigux/dev_t.h`
- curated Zig mirror ownership stays in `zigux/bindings/abi.zig`, `zigux/bindings/dev_t.zig`, and `zigux/bindings/notifier_abi.zig`
- packet-local export and UAPI starter wording stays in `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- policy, unsafe, atomic, barrier, and MMIO helper wording stays in the existing Phase 3 policy and low-level-wrapper survey notes
- `Documentation/zigux/phase3-abi-slice.md` remains the shared packet summary that must keep this governance note explicit whenever the Linux-facing header adds or rehomes a top-level review surface
- `include/linux/zigux.h` remains the Linux-facing relay and aggregation header for already-landed helper views, summaries, and narrow boundary adapters only

## Growth Rule

- `PHASE3_ZIGUX_H_GROWTH_RULE=new top-level helper families may land in include/linux/zigux.h, and already-landed top-level review surfaces may be rehomed there, only when the same bounded change also lands packet-local proof and updates this note.`
- packet-local proof means either the shared ABI dump route or a focused replay already carried by the Phase 3 packet for that exact landed or rehomed surface
- the same bounded change should also refresh `Documentation/zigux/phase3-abi-slice.md` and update `zigux/tests/fixtures/phase3_abi_manifest.json` whenever the review surface inventory changes
- header-only naming growth or rehome churn does not count as Phase 3 closure by itself
- repetitive wrapper, summary, or suffix-chain expansion without new bounded proof should be treated as churn, not progress

## Current State

- live `include/linux/zigux.h` now already carries the shipped named relay helpers `zigux_export_status_ok()`, `zigux_boundary_header_make()`, and `zigux_boundary_header_make_compatible()` beside the canonical `include/zigux/abi.h` and `include/zigux/dev_t.h` includes, so the current Phase 3 interop gap is no longer missing header-starter scaffolding
- `scripts/zigux/validate-phase3-linux-zigux-header-governance.py` now keeps this governance note aligned with the live include set, helper inventory, and blob marker for `include/linux/zigux.h`, so Linux-facing relay drift fails closed before broader Phase 3 reminder surfaces go stale
- the new `zigux_boundary_header_make_compatible()` relay keeps the C-facing constructor split aligned with the shipped `zigux/uapi/version.zig` canonical-versus-future-compatible contract without moving boundary-header ownership out of the canonical ABI header
- live `include/linux/zigux.h` no longer restates `ZIGUX_DEV_MINOR_BITS` or `ZIGUX_DEV_MINOR_MASK` locally; the C-facing packet now correctly aggregates `include/zigux/dev_t.h` as the single `dev_t` source of truth
- live `zigux/uapi/` now ships both `version.zig` and `dev_t.zig`, so the current exported boundary ownership is no longer version-only even though it remains a deliberately small starter packet beside the shared relay roots
- the remaining roadmap gap is that this growth is still concentrated in the shared `zigux.h` relay plus the same curated binding roots `zigux/bindings/abi.zig`, `zigux/bindings/dev_t.zig`, and `zigux/bindings/notifier_abi.zig`, rather than being split into additional top-level curated boundary families with their own proof surfaces
- wider exported boundary ownership beyond those two starter companions is still absent from the shipped substrate
- until a new boundary family lands with its own header, bindings, manifest-backed replay, and note refresh, more `include/linux/zigux.h` aggregation alone should be treated as reviewability risk, not interop closure

## Boundary

- `include/linux/zigux.h` may aggregate already-approved helper entry points, but it should not become a second source of truth for canonical struct layout, policy enums, or UAPI version ownership
- when the Linux-facing relay needs boundary-header helpers, keep canonical and future-compatible constructors as thin named relays over the canonical header and starter UAPI ownership rather than turning `include/linux/zigux.h` into a second semantic home
- when the Linux-facing relay needs `dev_t` minor-width aliases, it should aggregate `include/zigux/dev_t.h` rather than restating `ZIGUX_DEV_MINOR_BITS` or `ZIGUX_DEV_MINOR_MASK` locally, because those aliases already belong to the canonical `dev_t` boundary
- if a helper surface needs new ownership wording before it can be reviewed safely, add that wording here first instead of burying it in a dump-only or wrapper-only follow-up
- if an already-landed helper surface is rehomed into `include/linux/zigux.h`, refresh this note in the same bounded change so the shared ABI slice and the dedicated header-governance note continue to name the same owner map
- export/UAPI starter work may reference this header, but the dedicated export/UAPI survey still owns the narrower starter-boundary claims it proves directly
- the shared ABI slice and manifest should keep this note visible as part of the live Phase 3 packet so header growth never becomes an implied proof surface on its own

## Non-Goals

- this note does not claim a new binding family
- this note does not claim broader UAPI exposure
- this note does not claim runtime allocator, scheduler, or driver-port progress
- this note does not justify adding more `include/linux/zigux.h` surface without matching Phase 3 evidence
