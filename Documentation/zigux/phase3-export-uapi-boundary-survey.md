# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export-shim and UAPI boundary for the bounded Phase 3 ABI substrate.

## Status

- `PHASE3_SURVEYED_COMMIT=99eb24971cc35a0baa7fb071ecd01d42e22fb73d`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header`
- `PHASE3_EXPORT_SHIM_STATUS=normalize-and-compatibility-helpers-landed`
- `PHASE3_EXPORT_SHIM_BLOB_SHA=29a56fbc1657cd20a5c9d4b9ce7fa3499edeafdb`
- `PHASE3_UAPI_ROOT=zigux/uapi`
- `PHASE3_UAPI_SCOPE=version-and-boundary-header`
- `PHASE3_UAPI_STATUS=version-header-and-compatibility-surface-landed`
- `PHASE3_UAPI_VERSION_BLOB_SHA=38df0ae0c3f1eed1445a49ab3eac557078998ba9`
- `PHASE3_LINUX_HEADER_BLOB_SHA=c8cfd9590d2d0039ad087bb020a236fdc0a2b4ff`
- `PHASE3_ABI_HEADER_BLOB_SHA=c588b6d2c81659ff8996495d001dd1ebad7df1b1`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=2aba404045daca63246680a2a33a2c0b5dcad8a9`
- `PHASE3_EXPORT_UAPI_BUILD_BLOB_SHA=17778c41309a0bfb1c2c026622938059c2dd41f9`
- `PHASE3_EXPORT_UAPI_TEST_BLOB_SHA=fe3eaa894573e3a1313b46a16ee4bdf92e3694b5`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=a1a7938f6121ff6208d83dba8a46449bf615346a`
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

This survey is pinned to verified `master` head `99eb24971cc35a0baa7fb071ecd01d42e22fb73d` for the directly coupled export/UAPI packet, and it now also records the packet-local blob IDs for the curated header, helper, build, test, and manifest files so shallow history alone does not turn a reviewable packet into a false validation failure.

The current tree already carries the first bounded export and UAPI boundary surface:

- `zigux/kernel/export_shim.zig` exposes explicit `ok`, `errno`, `isOk`, `normalize`, `header`, `isCompatibleHeader`, and `isCanonicalHeader` helpers around the curated `ExportStatus` and `BoundaryHeader` ABI types
- the export shim and `zigux/uapi/version.zig` now carry the same shared boundary-header construction and compatibility contract without widening the packet beyond the existing ABI types
- the export shim and `zigux/uapi/version.zig` now also keep canonical-size header checks separate from broader future-compatible header acceptance, so the packet distinguishes exact current-shape replay from forward-compatible boundary tolerance without widening the UAPI surface
- the same surveyed head now also includes the landed policy-and-unsafe substrate tightening in `Documentation/zigux/phase3-abi-slice.md` and `zigux/tests/fixtures/phase3_abi_manifest.json`, so this export/UAPI survey pin stays aligned with the broader ABI packet instead of aging against a pre-policy snapshot
- `zigux/uapi/version.zig` now exports `abi_version`, `header_size`, `Header`, `boundaryHeader`, `isCurrentAbiVersion`, `isCompatibleSize`, `isCanonicalSize`, `isCompatible`, and `isCanonical`
- `zigux/tests/phase3_export_uapi.zig` now keeps the narrow kernel-side export shim aligned with the UAPI packet's named current-version and current-size predicates, so the shared boundary rule stays reviewable without widening the kernel shim itself
- `Documentation/zigux/phase3-abi-slice.md` now describes the export shim as explicit-status-plus-boundary-header and the UAPI surface as version-and-boundary-header
- `zigux/tests/phase3_export_uapi.zig` now proves that both helpers accept the same shared boundary header, expose the same named version and size predicates, distinguish canonical headers from broader future-compatible headers, and reject undersized or version-mismatched headers identically
- `scripts/zigux/validate-phase3-export-uapi-survey.py` now rejects drift in the directly coupled export/UAPI packet by checking the recorded packet-local blob IDs first and only falling back to `PHASE3_SURVEYED_COMMIT` when older survey notes do not yet carry those fingerprints, so the survey stays anchored to boundary-local evidence even on shallow checkouts

This is real roadmap-backed progress.
It is also still a narrow starting point rather than broad UAPI closure.

## Ledger Alignment

This landed boundary step still belongs to the same bounded Phase 3 ABI substrate family recorded in
`BOOTSTRAP_COMMIT_LEDGER.md`.

More specifically, it is still evidence for commit-train entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`, so the focused export/UAPI replay should be read as tighter proof for the original boundary packet rather than as a new standalone UAPI tranche.

- the original substrate ledger entry already named `zigux/kernel/export_shim.zig` and `zigux/uapi/version.zig` as part of the permanent Phase 3 boundary
- current `master` now adds focused replay evidence for that same boundary through `zigux/tests/phase3_export_uapi_build.zig` and `zigux/tests/phase3_export_uapi.zig`
- current `master` also keeps that same ledger entry reviewable through the restored `python3 scripts/zigux/validate-phase3.py` gate and the tightened `python3 scripts/zigux/validate-phase3-export-uapi-survey.py` survey gate, so packet-local drift now fails at the survey layer before the boundary snapshot can quietly age out
- `zigux/tests/fixtures/phase3_abi_manifest.json` now carries those focused replay paths inside the same ABI substrate packet rather than presenting them as a broader UAPI tranche

## Current Boundary Gap

The current gap is no longer the absence of an export shim.
That piece exists and is reviewable.

The remaining gap for this specific boundary packet is broader curated UAPI coverage:

- `zigux/uapi/` still contains only `version.zig`
- there is no second curated public boundary helper or constant pack under `zigux/uapi/`
- the shared header support is now explicit and now includes named version and size predicates plus canonical-versus-compatible header checks, but the export shim and UAPI surface still stop well short of a broader public entrypoint or shim family

That repo reality is consistent with the bounded ABI substrate, but it is still short of the roadmap's eventual broader permanent boundary destination.

## Next Bounded Step

The next honest follow-on inside this boundary family is still narrow:

- keep the current export shim and boundary-header surface narrow until a roadmap-backed interop slice needs one more reviewable boundary helper
- keep `zigux/uapi/` at version-plus-boundary-header scope until a concrete Phase 3 slice needs one additional curated public constant, type, or helper surface
- refresh `PHASE3_SURVEYED_COMMIT` and the packet-local `*_BLOB_SHA` markers whenever the directly coupled export/UAPI packet paths are deliberately resurveyed after boundary-local changes

This lane does not justify broad UAPI expansion, generated headers, or a larger export namespace on its own.
