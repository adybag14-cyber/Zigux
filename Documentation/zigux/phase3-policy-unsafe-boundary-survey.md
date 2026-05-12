# Phase 3 Policy and Unsafe Boundary Survey

This note records the current policy and narrow-unsafe boundary for the bounded Phase 3 ABI substrate on live `master`.

## Status

- `PHASE3_SURVEY_PROVENANCE=connector-plus-tree-fallback-current-head-sha-unavailable-in-run`
- `PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig`
- `PHASE3_LAYOUT_ASSERT_SCOPE=generic-layout-helper-plus-canonical-abi-byte-and-field-asserts-consumed-by-shared-abi-replays`
- `PHASE3_LAYOUT_ASSERT_BLOB_SHA=2a72bb87c3e6ecec0c336ced708cbffe2b32ac81`
- `PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig`
- `PHASE3_PANIC_POLICY=explicit-modes-only`
- `PHASE3_PANIC_POLICY_BLOB_SHA=8bb6db9c5625d3f04369e034d88ef4eff9048bcf`
- `PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig`
- `PHASE3_ALLOCATOR_POLICY=explicit-modes-only`
- `PHASE3_ALLOCATOR_POLICY_BLOB_SHA=264b9dbcb591fe6fd6bc1112bce7889b1e5f1b7c`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_BLOB_SHA=da243407a376213cc583d46e824862985ba75477`
- `PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig`
- `PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge`
- `PHASE3_UNSAFE_BLOB_SHA=f385239f26c9b27f86361179284b846cda11d5d0`
- `PHASE3_ABI_TEST_PATH=zigux/tests/phase3_abi.zig`
- `PHASE3_ABI_TEST_BLOB_SHA=c21736d6ca2e9cb8e90da003a5c1185d8b4394df`
- `PHASE3_ABI_DUMP_PATH=zigux/tests/phase3_abi_dump.zig`
- `PHASE3_ABI_DUMP_BLOB_SHA=0859efb2c4ba1a8178d10171321223b21273ae02`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=5f6b08f92b17db5893cccb712f05ff4c6542f79b`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=af72583ea041d8204745103a9a7c89057a2c0257`
- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi`
- `PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`
- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`
- `PHASE3_POLICY_BYTE_GUARD=python3 scripts/zigux/check-phase3-policy-byte-guards.py`
- `PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet`
- `PHASE3_NEXT_BOUNDED_STEP=keep-this-survey-aligned-with-the-live-helper-roles-and-shared-abi-markers-until-a-real-policy-or-unsafe-helper-expansion-lands`

## Roadmap Contract

Phase 3 is where Zigux starts defining permanent C and Zig boundary rules rather than only helper scaffolding.

For this lane, the roadmap-backed contract is still narrow:

- canonical layout assertions on the curated ABI bindings
- explicit panic policy modes
- explicit allocator policy modes
- one narrow unsafe surface for raw pointers and MMIO
- shared ABI validation and replay gates that keep those rules reviewable

This lane does not justify broad runtime policy machinery on its own.

## Live Repo Reality

This survey is anchored to packet-local blob IDs because the current connector run could inspect the live Phase 3 packet files directly but did not expose a trustworthy branch-head commit SHA. The blob markers above are therefore the authoritative current boundary evidence for this directly coupled policy-and-unsafe packet.

The current tree still carries a real bounded policy-and-unsafe packet, but the shared ABI replay owns more of the visible proof surface than older versions of this survey claimed:

- `zigux/helpers/layout_assert.zig` is still a small generic helper, but it now centralizes compile-time layout checks for `BoundaryHeader`, `ExportStatus`, and `InteropPolicy` plus the current panic, allocator, and unsafe-scope byte values, and it now also keeps the current chrdev notify ack-window policy budget-window delivery-window view, summary, budget-view, and budget-summary layouts explicit so those ABI structs no longer live only in the shared replays.
- `zigux/helpers/panic_policy.zig` keeps panic action explicit both through the typed enum path and through `modeFromInteropPolicyBytes`, `actionForInteropPolicyBytes`, and `canReturnInteropPolicyBytes` so unknown panic modes and nonzero reserved bytes fail closed before raw-byte callers infer behavior elsewhere in the packet.
- `zigux/helpers/allocator_policy.zig` keeps caller-provided ownership and global-fallback policy explicit both through the typed predicates and through `modeFromInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, `requiresExplicitCallerInteropPolicy`, `requiresExplicitCallerByte`, `permitsGlobalFallbackPolicyBytes`, `permitsGlobalFallbackInteropPolicy`, and `permitsGlobalFallbackByte` so unknown allocator modes and nonzero reserved bytes fail closed before raw-byte or typed shared callers infer behavior elsewhere in the packet.
- `zigux/unsafe/narrow.zig` still keeps the raw-pointer bridge deliberately small, but it also decodes `InteropPolicy` unsafe-scope bytes explicitly through `scopeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, `permitsVolatileMmioPolicyBytes`, and `permitsRawPointerBridgePolicyBytes` so unknown scopes and reserved-byte drift do not have to be inferred elsewhere in the packet.
- `zigux/unsafe/narrow.zig` also mirrors the panic and allocator helper style with typed `InteropPolicy` entry points through `scopeFromInteropPolicy`, `recognizesInteropPolicy`, `permitsNoUnsafeInteropPolicy`, `permitsVolatileMmioInteropPolicy`, and `permitsRawPointerBridgeInteropPolicy`, while keeping the direct raw-pointer bridge relays narrowed to the `constSliceAt*`, `constPointerAt*`, `pointerAt*`, and `writeValueAt*` helper family instead of widening into a broader unsafe facade.
- `zigux/helpers/mmio.zig` consumes that same narrow layer for direct `range()`, `read8()`, `write8()`, `read16()`, `write16()`, `read32()`, `write32()`, `read64()`, and `write64()` access while also routing policy-aware MMIO through `allowsInteropPolicy*`, `requireInteropPolicy*`, `rangeInteropPolicy*`, `read*InteropPolicy*`, and `write*InteropPolicy*` relays so volatile-MMIO callers stay inside the bounded unsafe contract.
- `scripts/zigux/check-phase3-policy-byte-guards.py` gives the shared policy-and-unsafe survey validator a dedicated reserved-byte and typed-wrapper guard across the policy helpers, this survey note, and the explicit shared dump gate, so the existing `phase3-validate` path can fail closed on policy-byte drift instead of leaving that contract implicit.
- `zigux/tests/phase3_abi.zig` is the live shared Zig proof packet for this family today, but it currently proves the `BoundaryHeader`, `ExportStatus`, and `InteropPolicy` layouts, exported constants, and `export_shim` compatibility rules directly against `abi_bindings` and `export_shim` rather than importing the policy helpers themselves.
- `zigux/tests/phase3_abi_dump.zig` keeps the current shared dump path explicit by emitting ABI constants plus the `InteropPolicy` and chrdev budget-window struct layouts; it no longer claims a dedicated policy/unsafe dump family or helper-local `MmioRange` layout packet of its own.
- `zigux/tests/fixtures/phase3_abi_manifest.json`, `Documentation/zigux/phase3-abi-slice.md`, and `scripts/zigux/validate-phase3.py` still treat these helpers and review surfaces as part of the shared `abi` slice.

The current tree still does not ship a dedicated `phase3_policy_unsafe` replay pair, and the live validator packet keeps this boundary inside the shared `abi` slice alone. This note should stay tied to the real shared ABI packet instead of implying an extra focused replay family or helper-local layout surface that the live tests tree no longer carries.

## Ledger Alignment

This policy-and-unsafe note is still evidence for the same bounded Phase 3 ABI substrate packet recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`.

That means this lane remains survey-and-marker maintenance inside the shared ABI packet rather than a new standalone tranche.

## Current Boundary Gap

Current same-family progress already includes helper-local explicit-byte decoding, typed-policy relays, and shared ABI proof refreshes:

- the panic helper decodes ABI panic-mode bytes explicitly and rejects nonzero reserved bytes instead of forcing raw-byte callers to re-map `.abort`, `.bug`, and `.warn` elsewhere in the packet
- the allocator helper decodes ABI allocator-mode bytes explicitly and rejects nonzero reserved bytes instead of forcing raw-byte callers to rediscover caller-ownership and global-fallback policy elsewhere in the packet
- the narrow unsafe helper decodes ABI unsafe-scope bytes explicitly and mirrors the typed `InteropPolicy` entry-point style already used by the panic and allocator helpers, instead of leaving reserved-byte and unknown-scope handling implicit or forcing shared callers to split bytes by hand
- the MMIO helper routes policy-aware reads and writes through explicit byte and typed `InteropPolicy` relays while keeping denied-scope accesses fail-closed instead of spreading that contract across unrelated callers
- the layout helper now keeps the canonical starter layouts, the chrdev budget-window delivery-window layouts, and the interop byte values explicit again, while the shared ABI proof packet still owns the broader exported-constant evidence and the emitted dump-surface replay
- the remaining same-lane gap is only to keep this survey aligned with the live helper roles, shared ABI replay surfaces, and current blob markers without implying a retired focused replay family or a broader runtime policy subsystem

## Next Bounded Step

- leave this lane parked unless one of the shared ABI packet files or the directly coupled survey surfaces drifts again
- keep the next same-lane change to one survey-side wording or marker refresh tied only to this packet
- if a broader policy-and-unsafe helper family or a new direct focused replay ever lands later, resurvey this note against the exact live files before claiming that surface here
