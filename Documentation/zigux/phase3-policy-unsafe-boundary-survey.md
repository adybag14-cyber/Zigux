# Phase 3 Policy and Unsafe Boundary Survey

This note records the current policy and narrow-unsafe boundary for the bounded Phase 3 ABI substrate.

## Status

- `PHASE3_SURVEYED_COMMIT=11ce68dddd5ecc31de988f3d8bf6e4c680be04b0`
- `PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig`
- `PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings`
- `PHASE3_LAYOUT_ASSERT_STATUS=canonical-layout-assertions-landed`
- `PHASE3_LAYOUT_ASSERT_BLOB_SHA=95d3dccd72bdf70d035e5d1ca0704bcc661502f1`
- `PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig`
- `PHASE3_PANIC_POLICY=explicit-modes-only`
- `PHASE3_PANIC_POLICY_STATUS=interop-byte-decode-landed`
- `PHASE3_PANIC_POLICY_BLOB_SHA=b620b09f3c5a5d3d59989a09ee7ead83a548bc16`
- `PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig`
- `PHASE3_ALLOCATOR_POLICY=explicit-modes-only`
- `PHASE3_ALLOCATOR_POLICY_STATUS=interop-byte-decode-and-init-flow-landed`
- `PHASE3_ALLOCATOR_POLICY_BLOB_SHA=b1186d5047e116539592786de273ebbca104b838`
- `PHASE3_INTEROP_POLICY_PATH=zigux/helpers/interop_policy.zig`
- `PHASE3_INTEROP_POLICY_SCOPE=whole-record-decode-explicit-mode-and-scope-validation`
- `PHASE3_INTEROP_POLICY_BLOB_SHA=c5216dd6737f83222f85f1c5e6f5fb3dd6b037e4`
- `PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig`
- `PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge`
- `PHASE3_UNSAFE_BLOB_SHA=2d95a5bca00d9e8c2ebfcddf340b7777bdcc523a`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_BLOB_SHA=218e68eb18f91b6df31e686fb7f121234d49fb24`
- `PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=6bb6839964179a4f0d818c40412233f8a718de51`
- `PHASE3_POLICY_UNSAFE_BUILD_BLOB_SHA=b8b22a949673c47f3512aac54bfa643cd593600c`
- `PHASE3_POLICY_UNSAFE_TEST_BLOB_SHA=12c752cdc3c83f1575402fd1523ed42229c0a47b`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=3b6103a6ef4162b0969c78a48681923cb622402a`
- `PHASE3_POLICY_UNSAFE_GATE=zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig`
- `PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay`
- `PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-helper-beyond-mmio-needs-a-typed-interop-policy-consumer`

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

This survey now treats `PHASE3_SURVEYED_COMMIT=11ce68dddd5ecc31de988f3d8bf6e4c680be04b0` as the last fully resurveyed shared-head anchor for the directly coupled policy-and-unsafe packet, not as a claim that the current `master` head still equals that commit. For current-truth checks, the packet-local blob IDs above are the authoritative evidence for those helper, build, test, manifest, and slice-note paths whenever later `master` movement leaves the packet unchanged.

The current tree already carries a real bounded policy-and-unsafe substrate:

- `zigux/helpers/layout_assert.zig` now owns the canonical `BoundaryHeader`, `ExportStatus`, `InteropPolicy`, and `MmioRange` size, alignment, field-type, and offset assertions instead of spreading those checks across ad hoc call sites, and the current head also keeps the `panic_mode`, `allocator_mode`, and `unsafe_scope` enum-byte contract compile-time through `assertInteropPolicyModeValues()` instead of leaving those values only in runtime assertions
- `zigux/helpers/layout_assert.zig` now also keeps `rbtree.RootView` on the same canonical compile-time layout surface through `assertRbtreeRootViewLayout()`, while `zigux/tests/phase3_policy_unsafe_build.zig` wires `zigux/bindings/rbtree.zig` into `layout_assert_module` so the focused policy/unsafe build cannot silently drop that dedicated root-view proof
- `zigux/helpers/panic_policy.zig` keeps the panic boundary explicit through `abort`, `bug`, and `warn`, and it now decodes raw `InteropPolicy.panic_mode` bytes before boundary code decides whether return is allowed
- `zigux/helpers/allocator_policy.zig` keeps allocator ownership explicit through `caller_provided`, `kernel_heap`, and `arena`, and it now decodes raw `InteropPolicy.allocator_mode` bytes before boundary code decides caller ownership, fallback, and reset behavior
- `zigux/helpers/interop_policy.zig` now treats `abi.InteropPolicy` as one typed boundary record, so reserved bits, panic mode, allocator mode, and unsafe scope fail together through one decode path instead of three unrelated byte checks, the decoded view keeps allocator-owned initialization and reset requirements reviewable alongside caller-ownership and fallback policy, the current head also keeps canonical record encoding explicit through the paired `init`, `encode`, and round-trip replay helpers, the same decoded packet now exposes direct `action()`, `permitsVolatileMmio()`, and `permitsRawPointerBridge()` accessors so panic action and unsafe-permission review stay attached to the typed policy record instead of being re-derived ad hoc at call sites, and it now also exposes direct raw-pointer bridge readers through `constSliceAt()` and `constPointerAt()` without widening the packet into a broader runtime caller surface
- `zigux/unsafe/narrow.zig` now keeps `none`, `volatile_mmio`, and `raw_pointer_bridge` explicit, provides permit helpers for those declared scopes, rejects misaligned scoped accesses before pointer formation, and now fails overflowed address math before a scoped pointer or slice can be formed
- `zigux/helpers/mmio.zig` routes scoped MMIO helpers back through that same narrow unsafe layer. `zigux/helpers/mmio.zig` is now the shipped second boundary helper that consumes `DecodedInteropPolicy` directly outside the focused `phase3_policy_unsafe` test packet. The focused replay reaches the typed-policy MMIO surface through direct `readScopedWithPolicy()` and `writeScopedWithPolicy()` replay plus the existing `mmio.write32Policy()` and `mmio.read32Policy()` anchors, so the generic decoded-policy bridge stays attached to the same narrow boundary packet instead of widening into a generic raw-pointer helper family. That same focused replay now also reaches the typed-policy MMIO surface through `read8Policy()`, `write8Policy()`, `read16Policy()`, `write16Policy()`, `read32Policy()`, `write32Policy()`, `read64Policy()`, and `write64Policy()` so the whole width-specific decoded-policy MMIO family stays attached to the same narrow boundary packet instead of leaving 8-bit, 16-bit, or 64-bit governance implicit.
- `zigux/tests/phase3_policy_unsafe_build.zig` and `zigux/tests/phase3_policy_unsafe.zig` now keep `layout_assert`, panic, allocator, typed `InteropPolicy` decoding, unsafe-byte decoding, declared-scope enforcement, decoded-policy MMIO bridging, decoded-policy raw-pointer bridge reads, and the dedicated `rbtree.RootView` compile-time layout wiring on their own focused replay path rather than leaving that packet visible only through the broader `phase3_abi.zig` bundle, and the focused replay now also keeps `phase3 policy layout stays explicit at the ABI boundary` attached to the shared compile-time `InteropPolicy` contract instead of leaving the enum-byte ABI proof only in the broader ABI bundle
- `zigux/tests/fixtures/phase3_abi_manifest.json`, `Documentation/zigux/phase3-abi-slice.md`, and `scripts/zigux/validate-phase3.py` already treat that focused replay as part of the bounded ABI substrate packet
- current `master` also extends that same focused replay to pin the newer allocator-init/reset expectations, decoded panic-action and unsafe-permission accessors in `zigux/helpers/interop_policy.zig`, the stronger canonical field-type and enum-byte assertions in `zigux/helpers/layout_assert.zig`, the typed-policy MMIO consumer in `zigux/helpers/mmio.zig`, the new typed-policy raw-pointer bridge readers in `zigux/helpers/interop_policy.zig`, the overflow-guard behavior in `zigux/unsafe/narrow.zig`, and the focused `rbtree.RootView` layout-build wiring in `zigux/tests/phase3_policy_unsafe_build.zig`, so this note can no longer stay pinned to the older pre-root-view-proof packet

This is real roadmap-backed progress.
It is also still a narrow boundary packet rather than a full runtime policy substrate.

## Ledger Alignment

This landed policy-and-unsafe boundary step still belongs to the same bounded Phase 3 ABI substrate family recorded in `BOOTSTRAP_COMMIT_LEDGER.md`.

More specifically, it is still evidence for commit-train entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`, so the focused policy-and-unsafe replay should be read as stronger proof for the original ABI substrate packet rather than as a new standalone tranche.

- the original substrate ledger entry already named `zigux/helpers/layout_assert.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, and `zigux/unsafe/narrow.zig` as part of the permanent Phase 3 boundary
- current `master` now also keeps the typed interop-policy, raw-pointer bridge readers, scoped MMIO policy evidence, and the focused `rbtree.RootView` compile-time layout proof inside that same packet through `zigux/helpers/interop_policy.zig`, `zigux/helpers/mmio.zig`, `zigux/tests/phase3_policy_unsafe_build.zig`, and the focused `zigux/tests/phase3_policy_unsafe.zig` replay
- the dedicated survey gate `scripts/zigux/validate-phase3-policy-unsafe-survey.py` still keeps that boundary packet reviewable at the survey layer through packet-local blob IDs first and `PHASE3_SURVEYED_COMMIT` fallback second, so packet-local drift can fail before the broader ABI validator is asked to explain it even on shallow checkouts

## Current Boundary Gap

The current gap is no longer the absence of explicit policy helpers or the absence of a compile-time ABI proof for the panic, allocator, and unsafe enum bytes.
Those helpers and that canonical layout contract now exist and are reviewable.

The remaining gap for this boundary packet is still the next consumer boundary:

- `zigux/helpers/layout_assert.zig` now keeps the `panic_mode`, `allocator_mode`, and `unsafe_scope` byte contract compile-time through `assertInteropPolicyModeValues()`, and the focused policy/unsafe build now also keeps `assertRbtreeRootViewLayout()` wired through `zigux/bindings/rbtree.zig`, so this survey no longer needs to treat either the enum-byte ABI proof or the dedicated root-view layout proof as a missing helper step
- `zigux/helpers/interop_policy.zig` now proves typed decoding through the focused replay, keeps direct raw-pointer bridge reads reviewable through `constSliceAt()` and `constPointerAt()`, and still stays inside the same bounded policy record rather than widening into a broader runtime surface
- `zigux/helpers/mmio.zig` is now the shipped second boundary helper that consumes `DecodedInteropPolicy` directly outside the focused `phase3_policy_unsafe` test packet
- the current tree does not yet ship a third Phase 3 boundary helper that consumes `DecodedInteropPolicy` directly beyond the focused replay and the scoped MMIO helper
- the narrow unsafe surface is explicit and reviewable, but it still stops at scoped MMIO and raw-pointer bridging helpers rather than a broader runtime caller surface

That repo reality matches the roadmap's wrapper-first posture.
It also means this lane should stay survey-and-validation heavy until one concrete boundary helper beyond MMIO needs the next typed policy consumer.

## Next Bounded Step

The next honest follow-on inside this family is still narrow:

- keep the current `layout_assert`, panic, allocator, typed `InteropPolicy`, raw-pointer bridge readers, narrow unsafe, scoped MMIO, and focused `rbtree.RootView` layout packet stable until one roadmap-backed helper beyond `zigux/helpers/mmio.zig` needs direct `DecodedInteropPolicy` consumption
- if that helper lands later, keep the change inside the same bounded ABI substrate packet rather than widening into global runtime policy machinery
- refresh `PHASE3_SURVEYED_COMMIT` and the packet-local `*_BLOB_SHA` markers whenever the directly coupled policy-and-unsafe packet paths are deliberately resurveyed after boundary-local changes

This lane does not justify broad runtime allocator integration, broader raw-pointer helpers, or a generic unsafe substrate expansion on its own.
