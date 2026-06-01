# Phase 3 Shared Reminder Gap

This note records the bounded Phase 3 shared-reminder status on current `master`.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, the dedicated ABI header-family survey follow-through, the focused abi.h next-step note, the shared ABI catalog helper plus manifest-backed inventory companion, the bounded bitmap/cpumask and list/hlist helper slices, the shared tests-root export/UAPI layout route, the named Linux-side boundary-header helper family plus validation relay, and the direct C smoke proof; the docs-root reminder, shared review checklist, tests-root reminder, and scripts-root reminder are now aligned on those already-returned helper-local slices, and no same-lane shared-summary drift remains on current master`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=keep this note parked unless a fresh current-master reread shows a smaller one-file shared-summary drift around the returned export/UAPI, bitmap/cpumask, list/hlist, shared tests-root layout, named boundary-header helper, or direct C smoke packet`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the helper-local bitmap/cpumask packet through Documentation/zigux/phase3-bitmap-cpumask-slice.md, zigux/helpers/bitmap_view.zig, zigux/helpers/cpumask_view.zig, zigux/tests/phase3_bitmap_cpumask_starter_packet.zig, zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig, the phase3_bitmap_cpumask fixture packet, and scripts/zigux/check-phase3-bitmap-cpumask.py; it confirms the helper-local list/hlist packet through Documentation/zigux/phase3-list-hlist-slice.md, zigux/helpers/list_view.zig, zigux/helpers/hlist_view.zig, zigux/bindings/notifier_list_shape.zig, zigux/tests/phase3_list_hlist_starter_packet.zig, zigux/tests/phase3_list_hlist_starter_packet_build.zig, zigux/tests/phase3_list_hlist_dump.zig, the phase3_list_hlist fixture packet, scripts/zigux/check-phase3-list-hlist-starter-packet.py, and scripts/zigux/check-phase3-list-hlist.py; it also confirms the shared ABI/binding survey family through the packet-local export/UAPI survey note, header-family survey, header-family binding relay, focused abi.h next-step note, shared ABI catalog helper, manifest-backed ABI inventory, direct C smoke proof, and restored docs-root, review-checklist, tests-root, and scripts-root reminders`

## Grounding

Roadmap comparison: Phase 3 is the ABI and interop substrate phase. Its product goal is the permanent C/Zigux boundary, with required features including export shims, curated bindings, layout assertions, explicit panic and allocator policy, approved low-level wrappers, and a narrow unsafe surface. The current repo has multiple bounded pieces of that substrate, but the roadmap still treats the wider boundary as staged work rather than complete product parity.

Ledger comparison: the bootstrap ledger records the initial Phase 3 ABI substrate skeleton and later bounded helper-local interop slices. The current bitmap/cpumask and list/hlist packets are therefore real progress, not wrapper churn, but they remain helper-local slices rather than proof that broader exported ABI structs, scheduler-facing cpumask behavior, intrusive list mutation, or subsystem ownership semantics are complete.

Repo reality: current `master` still contains the dedicated Phase 3 slice notes and replay files for bitmap/cpumask and list/hlist, plus the export/UAPI, header-family, catalog, ABI, and binding survey files. The shared reminder drift is now closed across `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md`; future changes should reopen this note only after a fresh current-master reread finds a smaller same-lane summary drift.

## Shared Reminder Surfaces

- `Documentation/zigux/phase3-bitmap-cpumask-slice.md` keeps the returned bitmap/cpumask helper-local packet explicit and limits its scope to bounded word and CPU-mask walking semantics.
- `Documentation/zigux/phase3-list-hlist-slice.md` keeps the returned list/hlist helper-local packet explicit and limits its scope to bounded shape, backlink, dump, and parity witnesses.
- `Documentation/zigux/phase3-policy-slice.md` keeps the focused policy helper packet explicit beside the policy dump and policy-unsafe survey replay.
- `Documentation/zigux/phase3-validator-support-surface.md` keeps the packet-local validator-support map aligned with this shared reminder note.
- `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `zigux/bindings/header_family.zig`, `scripts/zigux/phase3_catalog.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json` keep the ABI and binding survey family reviewable.
- `Documentation/zigux/README.md` now stays aligned on the returned bitmap/cpumask, list/hlist, xarray-slot, validator-support, shared catalog, policy, low-level-wrapper, and bounded export/UAPI plus header-family reminder surfaces.
- `Documentation/zigux/review-checklist.md` now keeps the returned bitmap/cpumask and list/hlist helper-slice wording explicit beside the bounded export/UAPI, xarray-slot, policy, low-level-wrapper, and shared-catalog packet, so the checklist no longer carries an open same-lane summary gap.
- `zigux/tests/README.md` now keeps the returned bitmap/cpumask and list/hlist helper slices explicit beside the packet-local export/UAPI survey note, validator, focused export/UAPI layout replay, and direct C smoke companion family, so the tests-root reminder no longer carries a same-lane summary gap.
- `scripts/zigux/README.md` now carries a compact Phase 3 section for the export/UAPI, header-family, catalog, shared ABI manifest, bitmap/cpumask, and list/hlist checker packet from the scripts root.
- `scripts/zigux/README.md` now keeps the returned bitmap/cpumask and list/hlist helper slices explicit beside the shared ABI manifest companion, export/UAPI layout replay pair, named Linux-side boundary-header helper family, and direct C smoke proof, so the scripts-root reminder no longer carries a same-lane summary gap.

## Current Gap

The earlier shared-reminder drift is now closed for the packet-local export/UAPI survey, the dedicated header-family and abi.h follow-through, the manifest-backed catalog packet, the landed helper-local interop slices themselves, and the shared docs-root, review-checklist, tests-root, and scripts-root reminder surfaces. No smaller same-lane shared-summary drift is visible on current `master` right now.

## Scope

This note is limited to the Phase 3 shared reminder packet. It records current survey and summary alignment only. It does not claim that exported ABI structs, scheduler-affinity policy, intrusive list mutation helpers, container-of recovery, broader subsystem ownership behavior, or full interop parity have returned beyond the bounded helper-local, export/UAPI, header-family, catalog, manifest, binding-relay, and replay surfaces named above.
