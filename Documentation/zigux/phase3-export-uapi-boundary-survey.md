# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export-shim and UAPI boundary for the bounded Phase 3 ABI substrate.

## Status

- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_EXPORT_SHIM_STATUS=explicit-status-helper-landed`
- `PHASE3_EXPORT_SHIM_BOUNDARY=test-local-header-construction-no-broader-export-entries`
- `PHASE3_UAPI_ROOT=zigux/uapi`
- `PHASE3_UAPI_STATUS=version-only-surface-landed`
- `PHASE3_UAPI_BOUNDARY=zigux/uapi/version.zig-only`
- `PHASE3_BOUNDARY_GAP=broader-curated-uapi-shims-still-deferred`
- `PHASE3_NEXT_BOUNDED_STEP=keep-boundary-narrow-until-one-roadmap-backed-interop-slice-needs-a-new-curated-uapi-or-export-entry`

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

The current tree already carries the first bounded export and UAPI boundary surface:

- `zigux/kernel/export_shim.zig` exposes explicit `ok`, `errno`, and `isOk` helpers around the curated `ExportStatus` ABI type
- that shim still keeps `BoundaryHeader` construction private to the module instead of widening the public export surface
- `zigux/uapi/version.zig` currently exports only `abi_version`
- `Documentation/zigux/phase3-abi-slice.md` already says that the export shim is explicit-status-only and that `zigux/uapi/` is version-only

This is real roadmap-backed progress.
It is also still a narrow starting point rather than broad UAPI closure.

## Current Boundary Gap

The current gap is no longer the absence of an export shim.
That piece exists and is reviewable.

The remaining gap for this specific boundary packet is broader curated UAPI coverage:

- `zigux/uapi/` currently contains only `version.zig`
- there is no second curated public boundary helper or constant pack under `zigux/uapi/`
- the export shim also remains intentionally narrow and does not yet expose a broader header or entrypoint family beyond explicit status handling

That repo reality is consistent with the bounded ABI substrate, but it is still short of the roadmap's eventual broader permanent boundary destination.

## Next Bounded Step

The next honest follow-on inside this boundary family is still narrow:

- keep the current export shim explicit-status-only until a roadmap-backed interop slice needs one more reviewable boundary helper
- keep `zigux/uapi/` version-only until a concrete Phase 3 slice needs one additional curated public constant or type surface

This lane does not justify broad UAPI expansion, generated headers, or a larger export namespace on its own.
