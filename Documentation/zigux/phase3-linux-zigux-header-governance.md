# Phase 3 Linux `zigux.h` Header Governance

This note closes the dedicated ownership and boundary-note gap for `include/linux/zigux.h` inside the shared Phase 3 ABI packet.

## Scope

- `PHASE3_ZIGUX_H_PATH=include/linux/zigux.h`
- `PHASE3_ZIGUX_H_PACKET=shared Phase 3 ABI substrate packet only`
- this note governs how the Linux-facing aggregation header may grow without turning header churn into fake Phase 3 progress

## Ownership

- canonical struct layout ownership stays in `include/zigux/abi.h` and `include/zigux/dev_t.h`
- curated Zig mirror ownership stays in `zigux/bindings/abi.zig`, `zigux/bindings/dev_t.zig`, and `zigux/bindings/notifier_abi.zig`
- packet-local export and UAPI starter wording stays in `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- policy, unsafe, atomic, barrier, and MMIO helper wording stays in the existing Phase 3 policy and low-level-wrapper survey notes
- `include/linux/zigux.h` remains the Linux-facing relay and aggregation header for already-landed helper views, summaries, and narrow boundary adapters only

## Growth Rule

- `PHASE3_ZIGUX_H_GROWTH_RULE=new top-level helper families may land in include/linux/zigux.h only when the same bounded change also lands packet-local proof and updates this note.`
- packet-local proof means either the shared ABI dump route or a focused replay already carried by the Phase 3 packet for that exact surface
- header-only naming growth does not count as Phase 3 closure by itself
- repetitive wrapper, summary, or suffix-chain expansion without new bounded proof should be treated as churn, not progress

## Boundary

- `include/linux/zigux.h` may aggregate already-approved helper entry points, but it should not become a second source of truth for canonical struct layout, policy enums, or UAPI version ownership
- if a helper surface needs new ownership wording before it can be reviewed safely, add that wording here first instead of burying it in a dump-only or wrapper-only follow-up
- export/UAPI starter work may reference this header, but the dedicated export/UAPI survey still owns the narrower starter-boundary claims it proves directly

## Non-Goals

- this note does not claim a new binding family
- this note does not claim broader UAPI exposure
- this note does not claim runtime allocator, scheduler, or driver-port progress
- this note does not justify adding more `include/linux/zigux.h` surface without matching Phase 3 evidence
