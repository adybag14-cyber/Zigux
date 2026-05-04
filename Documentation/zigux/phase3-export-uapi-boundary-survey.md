# Phase 3 Export Shim and UAPI Boundary Survey

This note records the current export-shim and UAPI boundary for the bounded Phase 3 ABI substrate.

## Status

- `PHASE3_SURVEYED_COMMIT=784b64d82982923ab4d1bec751cfbf26b49dfee4`
- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-with-legacy-head-anchor`
- `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
- `PHASE3_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header`
- `PHASE3_EXPORT_SHIM_STATUS=normalize-and-compatibility-helpers-landed`
- `PHASE3_EXPORT_SHIM_BLOB_SHA=c435e5a5ddc7c298908be43e9744f465103f61b0`
- `PHASE3_C_HEADER_PATH=include/linux/zigux.h`
- `PHASE3_C_HEADER_STATUS=shared-abi-relay-status-and-interop-helper-aggregation-landed`
- `PHASE3_C_HEADER_BOUNDARY_OWNERSHIP=export-uapi-packet-owns-boundary-wording-helper-slices-own-semantic-growth`
- `PHASE3_C_HEADER_GROWTH_RULE=explicit-resurvey-required-before-new-c-header-entry-points`
- `PHASE3_UAPI_ROOT=zigux/uapi`
- `PHASE3_UAPI_SCOPE=version-and-boundary-header`
- `PHASE3_UAPI_STATUS=version-header-and-compatibility-surface-landed`
- `PHASE3_UAPI_VERSION_BLOB_SHA=9cf90840a62ff3571e869860ea5ec2809be7415f`
- `PHASE3_LINUX_HEADER_BLOB_SHA=c8cfd9590d2d0039ad087bb020a236fdc0a2b4ff`
- `PHASE3_ABI_HEADER_BLOB_SHA=c588b6d2c81659ff8996495d001dd1ebad7df1b1`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=6bb6839964179a4f0d818c40412233f8a718de51`
- `PHASE3_EXPORT_UAPI_BUILD_BLOB_SHA=17778c41309a0bfb1c2c026622938059c2dd41f9`
- `PHASE3_EXPORT_UAPI_TEST_BLOB_SHA=8ea50cfe314806f81ea8ab05cef9ceb5ef9db3a8`
- `PHASE3_EXPORT_UAPI_LAYOUT_BUILD_BLOB_SHA=081b0624641588ea987a6562ac32781cfe93013f`
- `PHASE3_EXPORT_UAPI_LAYOUT_TEST_BLOB_SHA=3b8cb112602ff250f62ef68275a049a11c3a13d4`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=3b6103a6ef4162b0969c78a48681923cb622402a`
- `PHASE3_EXPORT_UAPI_GATE=zig build phase3-export-uapi-test --build-file zigux/tests/phase3_export_uapi_build.zig`
- `PHASE3_EXPORT_UAPI_LAYOUT_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`
- `PHASE3_ABI_BUILD_SMOKE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi --check-build-smoke`
- `PHASE3_ABI_BUILD_SMOKE_STATUS=shared-validator-replays-export-uapi-boundary-and-layout`
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

This survey keeps `PHASE3_SURVEYED_COMMIT=784b64d82982923ab4d1bec751cfbf26b49dfee4` as the last fully resurveyed shared-head anchor for the directly coupled export/UAPI packet, but packet-local blob IDs are now the authoritative current boundary evidence for those files, so shallow history alone does not turn a reviewable packet into a false validation failure.

The current tree already carries the first bounded export and UAPI boundary surface:

- `zigux/kernel/export_shim.zig` exposes explicit `canonicalHeader`, `compatibleHeader`, `versionedHeader`, `header`, `headerCompatibility`, `canonicalizeHeader`, `ok`, `errno`, `isOk`, `normalize`, `isCompatibleHeader`, and `isCanonicalHeader` helpers around the curated `ExportStatus` and `BoundaryHeader` ABI types, with `HeaderCompatibility` keeping canonical-versus-future-compatible classification named at the same boundary
- `include/linux/zigux.h` now sits inside the same bounded packet as the C-facing relay for those shared ABI types: the C-facing helper header still relays the shared `BoundaryHeader` and `ExportStatus` ABI types through `#include <zigux/abi.h>` while broader named C-side boundary-header helpers stay intentionally deferred, but current `master` no longer leaves that file as only a narrow relay-and-status shim because the same header also carries multiple already-landed Phase 3 interop helper families beyond the export/UAPI starter; this packet now explicitly owns the boundary wording and growth rule for `include/linux/zigux.h`, while slice-local validators still own semantic proof for the already-landed helper families collected there
- the export shim and `zigux/uapi/version.zig` now carry the same shared boundary-header construction and compatibility contract without widening the packet beyond the existing ABI types
- the export shim and `zigux/uapi/version.zig` now also keep canonical-size header checks separate from broader future-compatible header acceptance, so the packet distinguishes exact current-shape replay from forward-compatible boundary tolerance without widening the UAPI surface
- packet-local blob evidence now also records the broadened shared ABI slice reality in `Documentation/zigux/phase3-abi-slice.md`, including the current interop-family catalog, the landed shared `rbtree` root-view lift, and the remaining survey-and-validator wording gap around that shared lift, so this export/UAPI survey packet stays aligned with the broader ABI packet instead of aging against an older shared-boundary snapshot
- `zigux/uapi/version.zig` now exports `abi_version`, `header_size`, `Header`, `versionedHeader`, `canonicalHeader`, `boundaryHeader`, `compatibleHeader`, `Compatibility`, `compatibility`, `isCurrentAbiVersion`, `isCompatibleSize`, `isCanonicalSize`, `isCompatible`, and `isCanonical`
- `zigux/kernel/export_shim.zig` now re-exports that same named future-compatible boundary replay helper through `compatibleHeader(size, flags)` alongside the exact current-shape `canonicalHeader(flags)` relay and the arbitrary-version `versionedHeader(size, version, flags)` relay, so kernel-side callers can keep same-ABI future-size probes reviewable without reaching around the boundary packet into `zigux/uapi/version.zig` directly
- `zigux/kernel/export_shim.zig` now also re-exports that same named boundary-header classification through `HeaderCompatibility` and `headerCompatibility`, so callers can distinguish canonical and broader future-compatible headers without recombining multiple boolean checks by hand
- `zigux/tests/phase3_export_uapi.zig` now keeps the narrow kernel-side export shim aligned with the UAPI packet's named current-version and current-size predicates, the explicit named canonical constructor, the kernel-side compatible-header relay, the explicit arbitrary-version replay constructor, and the named compatibility classifier, so the shared boundary rule stays reviewable without widening the kernel shim itself
- `zigux/tests/phase3_export_uapi.zig` now proves that both helpers accept the same shared boundary header, expose the same named version and size predicates, distinguish canonical headers from broader future-compatible headers, reject canonical, future-compatible, undersized, and version-mismatched headers through the same explicit review packet, and classify the same header shapes through the same named compatibility helper instead of rebuilding version-mismatch cases with raw struct literals
- `zigux/tests/phase3_export_uapi_layout.zig` now keeps the canonical boundary-header and export-status size and field-offset contract on its own focused layout replay, and `zigux/tests/phase3_export_uapi_layout_build.zig` keeps that check callable as `phase3-export-uapi-layout-test` beside the broader export/UAPI smoke gate
- `zigux/uapi/version.zig` now also keeps the forward-compatible constructor explicit through `compatibleHeader(size, flags)`, the exact current-shape constructor equally explicit through `canonicalHeader(flags)`, the arbitrary-version replay path equally explicit through `versionedHeader(size, version, flags)`, and the exact header-shape decision equally explicit through `compatibility(header)`, so future-size and version-mismatch replay no longer have to fall back to ad hoc struct literals or recombined boolean checks when the boundary packet wants to stay narrow but still reviewable
- `scripts/zigux/validate_phase3_core.py` now routes `python3 scripts/zigux/validate-phase3.py --slug abi --check-build-smoke` through the shared `phase3-dump`, `phase3-low-level-wrappers-test`, `phase3-export-uapi-test`, `phase3-export-uapi-layout-test`, and `phase3-policy-unsafe-test` replays, so the export/UAPI boundary is part of the shared ABI build-smoke proof rather than only a boundary-local survey gate
- `zigux/tests/fixtures/phase3_abi_manifest.json` and `zigux/Makefile` already keep that same focused layout replay named beside the broader export/UAPI smoke gate, so the canonical boundary layout contract does not disappear into the larger Phase 3 bundle
- `scripts/zigux/validate-phase3-export-uapi-survey.py` now rejects drift in the directly coupled export/UAPI packet by checking the recorded packet-local blob IDs first and only falling back to `PHASE3_SURVEYED_COMMIT` when older survey notes do not yet carry those fingerprints, so the survey stays anchored to boundary-local evidence even on shallow checkouts
- that same survey validator now also compiles and runs a tiny C relay check against `include/linux/zigux.h`, so the C-facing `zigux_status_ok()` and `zigux_status_err()` helpers plus raw `zigux_boundary_header` field values still agree with the same constants the Zig-side starter uses instead of relying only on source markers
- that same survey validator still fails if the C-facing helper header stops carrying the shared ABI include or the local `zigux_status_ok()` and `zigux_status_err()` relay helpers, so the export/UAPI packet no longer leaves its C-side relay implicit even while the broader helper growth in that header remains a review concern for this lane
- current repo reality is therefore asymmetric in a reviewable way: the Zig-side packet around `zigux/kernel/export_shim.zig` and `zigux/uapi/version.zig` is still intentionally narrow, while the paired C-side helper header has already grown into a much broader aggregation surface for Phase 3 interop helpers

This is real roadmap-backed progress.
It is also still a narrow starting point rather than broad UAPI closure.

## Ledger Alignment

This landed boundary step still belongs to the same bounded Phase 3 ABI substrate family recorded in
`BOOTSTRAP_COMMIT_LEDGER.md`.

More specifically, it is still evidence for commit-train entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`, so the focused export/UAPI replay should be read as tighter proof for the original boundary packet rather than as a new standalone UAPI tranche.

- the original substrate ledger entry already named `zigux/kernel/export_shim.zig` and `zigux/uapi/version.zig` as part of the permanent Phase 3 boundary
- current `master` now adds focused replay evidence for that same boundary through `zigux/tests/phase3_export_uapi_build.zig`, `zigux/tests/phase3_export_uapi.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, and `zigux/tests/phase3_export_uapi_layout.zig`
- current `master` now also keeps the exact boundary-header shape decision reviewable inside that same bounded packet through `zigux/uapi/version.zig` and `zigux/kernel/export_shim.zig`, where one named compatibility classifier distinguishes canonical headers from broader future-compatible headers, one named `compatibleHeader(size, flags)` helper keeps same-ABI future-size replay explicit, and one named `versionedHeader(size, version, flags)` helper keeps arbitrary version replay explicit without widening into a broader UAPI family
- the same ledger packet also includes `include/linux/zigux.h`, and the dedicated export/UAPI survey now treats that helper header as first-class packet evidence instead of a side reference outside the reviewable boundary note
- current `master` now also keeps that same ledger entry reviewable through the ABI-only build-smoke replay at `python3 scripts/zigux/validate-phase3.py --slug abi --check-build-smoke`, where `scripts/zigux/validate_phase3_core.py` compiles the shared dump plus the focused export/UAPI, export/UAPI-layout, low-level-wrapper, and policy/unsafe build steps inside one bounded substrate packet
- current `master` also keeps that same ledger entry reviewable through the restored `python3 scripts/zigux/validate-phase3.py` gate and the tightened `python3 scripts/zigux/validate-phase3-export-uapi-survey.py` survey gate, so packet-local drift now fails at the survey layer before the boundary snapshot can quietly age out
- `zigux/tests/fixtures/phase3_abi_manifest.json` now carries those focused replay paths inside the same ABI substrate packet rather than presenting them as a broader UAPI tranche

## Current Boundary Gap

The current gap is no longer the absence of an export shim.
That piece exists and is reviewable.

The remaining gap for this specific boundary packet is narrower than a missing public boundary altogether.
The live repo already carries the C-facing boundary headers in `include/zigux/abi.h` and `include/linux/zigux.h`.

The sharper repo-reality gap is that the Zig-side starter and the C-side helper header are no longer growing at the same size or review level.
`zigux/kernel/export_shim.zig` and `zigux/uapi/version.zig` still form a small, explicit, reviewable Zig-side boundary starter, but `include/linux/zigux.h` has already accumulated a much broader C-side helper surface around bitmap, cpumask, list, hlist, err-ptr, xarray, IDR, IDA, dev-region, cdev, and chrdev-adjacent interop helpers.
That means the permanent boundary is still segmented unevenly even though the narrow export/UAPI starter itself is real.

What is still missing is a broader curated Zig-side UAPI helper family beyond the current boundary-header starter:

- `zigux/uapi/` still contains only `version.zig`
- there is still no second curated Zig-side UAPI module or broader constant pack under `zigux/uapi/`
- the shared header support is now explicit and now includes named version and size predicates, canonical-versus-compatible header checks, explicit `canonicalHeader()`, `compatibleHeader()`, and `versionedHeader()` constructors, and one named compatibility classifier, but the Zig-side UAPI surface still stops well short of a broader helper family
- the C-facing helper header is now an explicit part of the same surveyed packet, but current repo reality has moved past a relay-plus-status-only role, so the main boundary-management risk is now the mismatch between the still-narrow Zig-side starter and the already-broader C-side aggregation header rather than the complete absence of C-facing entry points

That repo reality is consistent with the bounded ABI substrate, but it is still short of the roadmap's eventual broader permanent boundary destination.

## Next Bounded Step

The next honest follow-on inside this boundary family is still narrow:

- keep the current export shim, boundary-header, and compatibility-classification surface narrow until a roadmap-backed interop slice needs one more reviewable boundary helper
- keep `zigux/uapi/` at version-plus-boundary-header scope until a concrete Phase 3 slice needs one additional curated Zig-side public constant, type, or helper surface
- do not treat this lane as permission to add more unrelated helper growth to `include/linux/zigux.h`; if another Phase 3 slice needs new C-side boundary entry points, resurvey this packet explicitly so the broader header growth stays visible instead of being mistaken for export/UAPI closure
- keep the ownership split explicit: this survey owns boundary wording and resurvey rules for `include/linux/zigux.h`, while slice-local helper packets own behavioral validation for the already-landed helper families gathered there
- refresh the packet-local `*_BLOB_SHA` markers whenever the directly coupled export/UAPI packet paths are deliberately resurveyed after boundary-local changes
- refresh `PHASE3_SURVEYED_COMMIT` only when the whole export/UAPI packet is deliberately resurveyed against a confirmed shared head

This lane does not justify broad UAPI expansion, generated headers, or a larger export namespace on its own.
