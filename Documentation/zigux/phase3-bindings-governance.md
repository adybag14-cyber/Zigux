# Phase 3 Bindings Governance

This note records the bounded governance and review-owner split for the current `zigux/bindings` packet so shared Phase 3 ABI reminders describe the curated bindings surface that current `master` actually ships.

## Scope

This note is for the bindings side of the active Phase 3 substrate only.

Current `master` materializes this bounded bindings trio:
- `zigux/bindings/abi.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/notifier_abi.zig`

Keep these neighboring surfaces distinct:
- `Documentation/zigux/phase3-abi-header-family-survey.md` for the header-family boundary
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md` for the export and starter-UAPI packet
- `Documentation/zigux/phase3-abi-slice.md` for the shared Phase 3 packet inventory
- `Documentation/zigux/phase13-notifier-list-survey.md` for the later notifier-facing adjacent evidence that already reuses `zigux/bindings/notifier_abi.zig`

## Owned Review Surface

When contributors touch the bindings packet, keep this note aligned with:
- `Documentation/zigux/phase3-bindings-governance.md`
- `Documentation/zigux/phase3-abi-slice.md`
- `include/zigux/abi.h`
- `include/zigux/dev_t.h`
- `zigux/bindings/abi.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `scripts/zigux/validate-phase3-abi-bindings-syntax.py`

The direct lane-local proof on current `master` is still the curated bindings trio plus the shared ABI packet that already tracks those files. Treat broader reminder surfaces as routing aids, not as replacement evidence for this bindings-local packet.

## Governance Boundaries

Use this note to keep these boundaries explicit:
- bindings-owned wording, curated field names, and interop disclaimers belong here
- `zigux/bindings/abi.zig` mirrors the exported ABI constants and layout-tracked structs that already ship through `include/zigux/abi.h`; changes here should stay coupled to `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`, and `zigux/tests/fixtures/phase3_abi/expected.json`
- `zigux/bindings/dev_t.zig` stays the canonical Zig-side companion for `include/zigux/dev_t.h` and the starter `zigux/uapi/dev_t.zig` packet; keep same-lane follow-through here inside range, encoding, or reminder-surface truthfulness rather than broad UAPI expansion
- `zigux/bindings/notifier_abi.zig` remains curated adjacent ABI evidence for later notifier-facing work; it may mirror the shipped notifier result codes, block layout, and bounded priority-order review helpers from `include/zigux/abi.h`, but should not claim callback execution, registration, SRCU, or blocking-notifier semantics while the broader notifier packet remains bounded elsewhere
- broad Phase 3 summaries should keep this note explicit whenever they name the bindings trio so `zigux/bindings/notifier_abi.zig` does not disappear behind only the header-family or later notifier reminder packets

## Review Prompts

If a change updates the bindings packet, verify that:
- the bindings trio listed above still matches current `master`
- `zigux/bindings/notifier_abi.zig` stays framed as adjacent notifier ABI evidence with bounded priority-order review helpers, not full notifier parity
- `zigux/bindings/abi.zig` and `zigux/bindings/dev_t.zig` stay coupled to their current C header companions
- the shared ABI reminder packet keeps this note explicit beside the manifest-backed file inventory instead of leaving the bindings slice readable only through broader Phase 3 or Phase 13 notes

## Non-goals

- no new exported header-family claims
- no helper, unsafe, or kernel packet growth
- no Phase 13 notifier survey rewrite or runtime parity claim
