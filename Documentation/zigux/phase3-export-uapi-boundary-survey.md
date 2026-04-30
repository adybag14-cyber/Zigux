# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export-shim and UAPI boundary for the bounded Phase 3 ABI substrate.

## Status

- `PHASE3_SURVEYED_COMMIT=f11569d38143cfcfa204ff63c744cb9780575081`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header`
- `PHASE3_EXPORT_SHIM_STATUS=normalize-and-compatibility-helpers-landed`
- `PHASE3_UAPI_ROOT=zigux/uapi`
- `PHASE3_UAPI_SCOPE=version-and-boundary-header`
- `PHASE3_UAPI_STATUS=version-header-and-compatibility-surface-landed`
- `PHASE3_EXPORT_UAPI_GATE=zig build phase3-export-uapi-test --build-file zigux/tests/phase3_export_uapi_build.zig`
- `PHASE3_BOUNDARY_GAP=broader-curated-uapi-shims-still-deferred`
- `PHASE3_NEXT_BOUNDED_STEP=keep-boundary-header-surface-narrow-until-one-roadmap-backed-interop-slice-needs-another-curated-uapi-or-export-entry`

## Roadmap Contract

Phase 3 is supposed to define the permanent C and Zigux boundary.

For this lane, the relevant roadmap requirements are:

- explicit export shims
- curated bindings
- a narrow unsafe surface
- the long-term `zigux/uapi/` destination for reviewable public boundary helpers

That does not require broad UAPI exposure on day one.
It does require the live repo to say clearly what is already part of the permanent boundary and what is still intentionally deferred.

## Live Repo Reality

This survey is pinned to verified `master` head `f11569d38143cfcfa204ff63c744cb9780575081` so the note stays tied to one inspected boundary snapshot instead of a floating branch label.

The current tree already carries the first bounded export and UAPI boundary surface:

- `zigux/kernel/export_shim.zig` exposes explicit `ok`, `errno`, `isOk`, `normalize`, `header`, and `isCompatibleHeader` helpers around the curated `ExportStatus` and `BoundaryHeader` ABI types
- the export shim and `zigux/uapi/version.zig` now carry the same shared boundary-header construction and compatibility contract without widening the packet beyond the existing ABI types
- the export shim and `zigux/uapi/version.zig` now also keep canonical-size header checks separate from broader future-compatible header acceptance, so the packet distinguishes exact current-shape replay from forward-compatible boundary tolerance without widening the UAPI surface
- `zigux/uapi/version.zig` now exports `abi_version`, `header_size`, `Header`, `boundaryHeader`, `isCurrentAbiVersion`, `isCompatibleSize`, `isCanonicalSize`, `isCompatible`, and `isCanonical`
- `zigux/tests/phase3_export_uapi.zig` now keeps the narrow kernel-side export shim aligned with the UAPI packet's named current-version and current-size predicates, so the shared boundary rule stays reviewable without widening the kernel shim itself
- `Documentation/zigux/phase3-abi-slice.md` now describes the export shim as explicit-status-plus-boundary-header and the UAPI surface as version-and-boundary-header
- `zigux/tests/phase3_export_uapi.zig` now proves that both helpers accept the same shared boundary header, expose the same named version and size predicates, and reject undersized or version-mismatched headers identically

This is real roadmap-backed progress.
It is also still a narrow starting point rather than broad UAPI closure.

## Ledger Alignment

This landed boundary step still belongs to the same bounded Phase 3 ABI substrate family recorded in
`BOOTSTRAP_COMMIT_LEDGER.md`.

More specifically, it is still evidence for commit-train entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`, so the focused export/UAPI replay should be read as tighter proof for the original boundary packet rather than as a new standalone UAPI tranche.

- the original substrate ledger entry already named `zigux/kernel/export_shim.zig` and `zigux/uapi/version.zig` as part of the permanent Phase 3 boundary
- current `master` now adds focused replay evidence for that same boundary through `zigux/tests/phase3_export_uapi_build.zig` and `zigux/tests/phase3_export_uapi.zig`
- current `master` also keeps that same ledger entry reviewable through the restored `python3 scripts/zigux/validate-phase3.py` gate, which now checks the canonical ABI and bindings source markers before the focused export/UAPI replay runs
- `zigux/tests/fixtures/phase3_abi_manifest.json` now carries those focused replay paths inside the same ABI substrate packet rather than presenting them as a broader UAPI tranche

## Current Boundary Gap

The current gap is no longer the absence of an export shim.
That piece exists and is reviewable.

The remaining gap for this specific boundary packet is broader curated UAPI coverage:

- `zigux/uapi/` still contains only `version.zig`
- there is no second curated public boundary helper or constant pack under `zigux/uapi/`
- the shared header support is now explicit and now includes named version and size predicates, but the export shim and UAPI surface still stop well short of a broader public entrypoint or shim family

That repo reality is consistent with the bounded ABI substrate, but it is still short of the roadmap's eventual broader permanent boundary destination.

## Next Bounded Step

The next honest follow-on inside this boundary family is still narrow:

- keep the current export shim and boundary-header surface narrow until a roadmap-backed interop slice needs one more reviewable boundary helper
- keep `zigux/uapi/` at version-plus-boundary-header scope until a concrete Phase 3 slice needs one additional curated public constant, type, or helper surface
- refresh `PHASE3_SURVEYED_COMMIT` whenever this note is deliberately resurveyed against a newer verified `master` head

This lane does not justify broad UAPI expansion, generated headers, or a larger export namespace on its own.
