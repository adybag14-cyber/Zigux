# Phase 3 Policy and Unsafe Boundary Survey

This note records the current policy and narrow-unsafe boundary for the bounded Phase 3 ABI substrate.

## Status

- `PHASE3_SURVEYED_COMMIT=de9ce0d08cc56cf962acc2ab36c0cb202a7b6a1c`
- `PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig`
- `PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings`
- `PHASE3_LAYOUT_ASSERT_STATUS=canonical-layout-assertions-landed`
- `PHASE3_LAYOUT_ASSERT_BLOB_SHA=c7dc4580175d5927a926b09d9baae7cb327b71b0`
- `PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig`
- `PHASE3_PANIC_POLICY=explicit-modes-only`
- `PHASE3_PANIC_POLICY_STATUS=interop-byte-decode-landed`
- `PHASE3_PANIC_POLICY_BLOB_SHA=3eb14283de9a4229deae0ec546dca90942c563c5`
- `PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig`
- `PHASE3_ALLOCATOR_POLICY=explicit-modes-only`
- `PHASE3_ALLOCATOR_POLICY_STATUS=interop-byte-decode-and-init-flow-landed`
- `PHASE3_ALLOCATOR_POLICY_BLOB_SHA=61355af4c5498283ca9e235634c3e0a56d2caca6`
- `PHASE3_INTEROP_POLICY_PATH=zigux/helpers/interop_policy.zig`
- `PHASE3_INTEROP_POLICY_SCOPE=whole-record-decode-explicit-mode-and-scope-validation`
- `PHASE3_INTEROP_POLICY_BLOB_SHA=55d02b54a95e45c9ad1f5ca8b829f3023ca4531d`
- `PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig`
- `PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge`
- `PHASE3_UNSAFE_BLOB_SHA=543239eec61a02701f14622cacf39f6bf104621e`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_BLOB_SHA=f89427a1d2d9a3738575e70b4303a791cce8a3cd`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=c9676f9697cbe34dd75809a4dae6a53b24030059`
- `PHASE3_POLICY_UNSAFE_BUILD_BLOB_SHA=4613c79a8d082b2dd3fe9502b7dcdb03ef181bb2`
- `PHASE3_POLICY_UNSAFE_TEST_BLOB_SHA=33db1f474ec888915b9db038cac637f775687ee3`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=d40d25f96ddbda5c44aaf76ae8dcc3796936a041`
- `PHASE3_POLICY_UNSAFE_GATE=zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig`
- `PHASE3_BOUNDARY_GAP=no-second-boundary-helper-consumes-decoded-policy-beyond-focused-replay`
- `PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-boundary-helper-needs-a-typed-interop-policy-consumer`

## Roadmap Contract

Phase 3 is where Zigux starts defining permanent C and Zig boundary rules rather than only helper scaffolding.

For this lane, the roadmap requirements are:

- canonical layout assertions on the curated ABI bindings
- explicit panic and allocator policy modes
- one typed interop-policy decode path instead of hidden byte checks
- one narrow unsafe surface that keeps raw pointers and volatile MMIO reviewable

That does not require broad runtime integration yet.
It does require the current tree to say clearly which policy rules are already landed and which boundary-facing use is still deferred.

## Live Repo Reality

This survey is pinned to verified `master` head `de9ce0d08cc56cf962acc2ab36c0cb202a7b6a1c` for the directly coupled policy-and-unsafe packet, and it now also records packet-local blob IDs for the curated helper, build, test, manifest, and slice-note files so shallow history alone does not turn a reviewable packet into a false validation failure.

The current tree already carries a real bounded policy-and-unsafe substrate:

- `zigux/helpers/layout_assert.zig` now owns the canonical `BoundaryHeader`, `ExportStatus`, `InteropPolicy`, and `MmioRange` size, alignment, and offset assertions instead of spreading those checks across ad hoc call sites
- `zigux/helpers/panic_policy.zig` keeps the panic boundary explicit through `abort`, `bug`, and `warn`, and it now decodes raw `InteropPolicy.panic_mode` bytes before boundary code decides whether return is allowed
- `zigux/helpers/allocator_policy.zig` keeps allocator ownership explicit through `caller_provided`, `kernel_heap`, and `arena`, and it now decodes raw `InteropPolicy.allocator_mode` bytes before boundary code decides caller ownership, fallback, and reset behavior
- `zigux/helpers/interop_policy.zig` now treats `abi.InteropPolicy` as one typed boundary record, so reserved bits, panic mode, allocator mode, and unsafe scope fail together through one decode path instead of three unrelated byte checks, the decoded view keeps allocator-owned initialization and reset requirements reviewable alongside caller-ownership and fallback policy, the current head also keeps canonical record encoding explicit through the paired `init`, `encode`, and round-trip replay helpers, and the same decoded packet now exposes direct `action()`, `permitsVolatileMmio()`, and `permitsRawPointerBridge()` accessors so panic action and unsafe-permission review stay attached to the typed policy record instead of being re-derived ad hoc at call sites
- `zigux/unsafe/narrow.zig` now keeps `none`, `volatile_mmio`, and `raw_pointer_bridge` explicit, provides permit helpers for those declared scopes, rejects misaligned scoped accesses before pointer formation, and now fails overflowed address math before a scoped pointer or slice can be formed
- `zigux/helpers/mmio.zig` routes scoped MMIO helpers back through that same narrow unsafe layer, so volatile pointer formation stays attached to the declared unsafe scope instead of widening into a generic raw-pointer helper family
- `zigux/tests/phase3_policy_unsafe_build.zig` and `zigux/tests/phase3_policy_unsafe.zig` now keep `layout_assert`, panic, allocator, typed `InteropPolicy` decoding, unsafe-byte decoding, and declared-scope enforcement on their own focused replay path rather than leaving that packet visible only through the broader `phase3_abi.zig` bundle
- `zigux/tests/fixtures/phase3_abi_manifest.json`, `Documentation/zigux/phase3-abi-slice.md`, and `scripts/zigux/validate-phase3.py` already treat that focused replay as part of the bounded ABI substrate packet
- current `master` also extends that same focused replay to pin the newer allocator-init/reset expectations, decoded panic-action and unsafe-permission accessors in `zigux/helpers/interop_policy.zig`, and the new overflow-guard behavior in `zigux/unsafe/narrow.zig`, so this note can no longer stay pinned to the older pre-accessor packet

This is real roadmap-backed progress.
It is also still a narrow boundary packet rather than a full runtime policy substrate.

## Ledger Alignment

This landed policy-and-unsafe boundary step still belongs to the same bounded Phase 3 ABI substrate family recorded in `BOOTSTRAP_COMMIT_LEDGER.md`.

More specifically, it is still evidence for commit-train entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`, so the focused policy-and-unsafe replay should be read as stronger proof for the original ABI substrate packet rather than as a new standalone tranche.

- the original substrate ledger entry already named `zigux/helpers/layout_assert.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, and `zigux/unsafe/narrow.zig` as part of the permanent Phase 3 boundary
- current `master` now also keeps the typed interop-policy and scoped MMIO policy evidence inside that same packet through `zigux/helpers/interop_policy.zig`, `zigux/helpers/mmio.zig`, and the focused `zigux/tests/phase3_policy_unsafe.zig` replay
- the new dedicated survey gate `scripts/zigux/validate-phase3-policy-unsafe-survey.py` now keeps that boundary packet reviewable at the survey layer through packet-local blob IDs first and `PHASE3_SURVEYED_COMMIT` fallback second, so packet-local drift can fail before the broader ABI validator is asked to explain it even on shallow checkouts

## Current Boundary Gap

The current gap is no longer the absence of explicit policy helpers.
Those helpers exist and are reviewable.

The remaining gap for this boundary packet is boundary-facing consumption:

- `zigux/helpers/interop_policy.zig` currently proves typed decoding inside focused replay only
- the current tree does not yet ship a second Phase 3 boundary helper that consumes `DecodedInteropPolicy` directly outside the focused `phase3_policy_unsafe` test packet
- the narrow unsafe surface is explicit and reviewable, but it still stops at scoped MMIO and raw-pointer bridging helpers rather than a broader runtime caller surface

That repo reality matches the roadmap's wrapper-first posture.
It also means this lane should stay survey-and-validation heavy until one concrete boundary helper needs the next typed policy consumer.

## Next Bounded Step

The next honest follow-on inside this family is still narrow:

- keep the current `layout_assert`, panic, allocator, typed `InteropPolicy`, narrow unsafe, and scoped MMIO packet stable until one roadmap-backed boundary helper needs direct `DecodedInteropPolicy` consumption
- if that helper lands later, keep the change inside the same bounded ABI substrate packet rather than widening into global runtime policy machinery
- refresh `PHASE3_SURVEYED_COMMIT` and the packet-local `*_BLOB_SHA` markers whenever the directly coupled policy-and-unsafe packet paths are deliberately resurveyed after boundary-local changes

This lane does not justify broad runtime allocator integration, broader raw-pointer helpers, or a generic unsafe substrate expansion on its own.
