# Phase 3 Shared Reminder Gap

This note records the bounded Phase 3 shared-reminder status on current `master`.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master serves the packet-local export/UAPI survey note and validator, the dedicated ABI header-family survey follow-through, the landed shared header-family binding relay, the focused abi.h next-step note, the shared ABI catalog helper plus manifest-backed inventory companion, the bounded bitmap/cpumask and list/hlist helper slices, the shared tests-root export/UAPI layout route, the named Linux-side boundary-header helper family plus validation relay, the direct C smoke proof, and the restored scripts-root Phase 3 reminder; the remaining same-lane reminder drift is that the tests-root README summary no longer carries a Phase 3 section for the returned helper-local slices or shared ABI/binding survey packet`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the helper-local bitmap/cpumask packet through Documentation/zigux/phase3-bitmap-cpumask-slice.md, zigux/helpers/bitmap_view.zig, zigux/helpers/cpumask_view.zig, zigux/tests/phase3_bitmap_cpumask_starter_packet.zig, zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig, the phase3_bitmap_cpumask fixture packet, and scripts/zigux/check-phase3-bitmap-cpumask.py; it confirms the helper-local list/hlist packet through Documentation/zigux/phase3-list-hlist-slice.md, zigux/helpers/list_view.zig, zigux/helpers/hlist_view.zig, zigux/bindings/notifier_list_shape.zig, zigux/tests/phase3_list_hlist_starter_packet.zig, zigux/tests/phase3_list_hlist_starter_packet_build.zig, zigux/tests/phase3_list_hlist_dump.zig, the phase3_list_hlist fixture packet, scripts/zigux/check-phase3-list-hlist-starter-packet.py, and scripts/zigux/check-phase3-list-hlist.py; it also confirms the shared ABI/binding survey family through the packet-local export/UAPI survey note, header-family survey, header-family binding relay, focused abi.h next-step note, shared ABI catalog helper, manifest-backed ABI inventory, and restored scripts-root Phase 3 reminder; live readback of zigux/tests/README.md now jumps from Phase 2 to Phase 4, so that shared reminder surface is not aligned with the Phase 3 packet even though the underlying helper-local, ABI/binding survey, and scripts-root reminder files remain present`

## Grounding

Roadmap comparison: Phase 3 is the ABI and interop substrate phase. Its product goal is the permanent C/Zigux boundary, with required features including export shims, curated bindings, layout assertions, explicit panic and allocator policy, approved low-level wrappers, and a narrow unsafe surface. The current repo has multiple bounded pieces of that substrate, but the roadmap still treats the wider boundary as staged work rather than complete product parity.

Ledger comparison: the bootstrap ledger records the initial Phase 3 ABI substrate skeleton and later bounded helper-local interop slices. The current bitmap/cpumask and list/hlist packets are therefore real progress, not wrapper churn, but they remain helper-local slices rather than proof that broader exported ABI structs, scheduler-facing cpumask behavior, intrusive list mutation, or subsystem ownership semantics are complete.

Repo reality: current `master` still contains the dedicated Phase 3 slice notes and replay files for bitmap/cpumask and list/hlist, plus the export/UAPI, header-family, catalog, ABI, and binding survey files. The live shared reminder drift is now narrower: `scripts/zigux/README.md` again carries a Phase 3 scripts-root reminder, while `zigux/tests/README.md` still does not keep a Phase 3 reminder section for those returned packets.

## Shared Reminder Surfaces

- `Documentation/zigux/phase3-bitmap-cpumask-slice.md` keeps the returned bitmap/cpumask helper-local packet explicit and limits its scope to bounded word and CPU-mask walking semantics.
- `Documentation/zigux/phase3-list-hlist-slice.md` keeps the returned list/hlist helper-local packet explicit and limits its scope to bounded shape, backlink, dump, and parity witnesses.
- `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `zigux/bindings/header_family.zig`, `scripts/zigux/phase3_catalog.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json` keep the ABI and binding survey family reviewable.
- `scripts/zigux/README.md` now carries a compact Phase 3 section for the export/UAPI, header-family, catalog, shared ABI manifest, bitmap/cpumask, and list/hlist checker packet from the scripts root.
- `zigux/tests/README.md` currently carries Phase 1, Phase 2, then Phase 4 and later reminder sections, so it no longer exposes the Phase 3 helper-local and ABI/binding packet from the tests root.

## Current Gap

The current same-lane gap is not missing helper code and not a reason to expand ABI bodies. It is a shared-summary truthfulness gap: the tests-root README reminder should regain a compact Phase 3 section that names the returned bitmap/cpumask, list/hlist, export/UAPI, header-family, catalog, ABI manifest, direct C smoke, and binding relay surfaces without claiming broader Phase 3 parity.

## Scope

This note is limited to the Phase 3 shared reminder packet. It records current survey and summary alignment only. It does not claim that exported ABI structs, scheduler-affinity policy, intrusive list mutation helpers, container-of recovery, broader subsystem ownership behavior, or full interop parity have returned beyond the bounded helper-local, export/UAPI, header-family, catalog, manifest, binding-relay, and replay surfaces named above.