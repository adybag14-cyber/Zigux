# Phase 3 Policy and Unsafe Boundary Survey

This note records the current policy and narrow-unsafe boundary for the bounded Phase 3 ABI substrate on live `master`.

## Status

- `PHASE3_SURVEY_PROVENANCE=connector-current-head-sha-unavailable-in-run`
- `PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig`
- `PHASE3_LAYOUT_ASSERT_SCOPE=generic-layout-helper-plus-canonical-abi-byte-and-field-asserts-consumed-by-shared-abi-replays`
- `PHASE3_LAYOUT_ASSERT_BLOB_SHA=1a5dfe0dc320c74902912cfaa25165dd8fed54b5`
- `PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig`
- `PHASE3_PANIC_POLICY=explicit-modes-only`
- `PHASE3_PANIC_POLICY_BLOB_SHA=c34586d28ebfa7cdb89a30054b4ae49da5fd5550`
- `PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig`
- `PHASE3_ALLOCATOR_POLICY=explicit-modes-plus-init-flow`
- `PHASE3_ALLOCATOR_POLICY_BLOB_SHA=bbdb90c04304ad7058341718319782833b9cf46b`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_BLOB_SHA=d310c9ac47558079c2274af88037f6008dd29820`
- `PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig`
- `PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge`
- `PHASE3_UNSAFE_BLOB_SHA=f78eefc1208df3e44662f5d9067edabd18ea4f12`
- `PHASE3_ABI_TEST_PATH=zigux/tests/phase3_abi.zig`
- `PHASE3_ABI_TEST_BLOB_SHA=beae4ef4ca27d08606835421945cc149a3b4acd9`
- `PHASE3_ABI_DUMP_PATH=zigux/tests/phase3_abi_dump.zig`
- `PHASE3_ABI_DUMP_BLOB_SHA=243141d56c39fd7f8a16ed32fe36c6fd7a91661f`
- `PHASE3_POLICY_UNSAFE_TEST_PATH=zigux/tests/phase3_policy_unsafe.zig`
- `PHASE3_POLICY_UNSAFE_BUILD_PATH=zigux/tests/phase3_policy_unsafe_build.zig`
- `PHASE3_POLICY_UNSAFE_FOCUSED_GATE=zig build test --build-file zigux/tests/phase3_policy_unsafe_build.zig`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=bfceb3241a2a9b4f3d0122c5b193727d2a57c728`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=ba7a2bb284c3cb72c258b2249f1d084bbaf26cdc`
- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py`
- `PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`
- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`
- `PHASE3_POLICY_BYTE_GUARD=python3 scripts/zigux/check-phase3-policy-byte-guards.py`
- `PHASE3_BOUNDARY_GAP=dedicated-focused-policy-unsafe-replay-pair-ships-while-the-shared-abi-packet-still-owns-the-broader-policy-and-unsafe-review-surface`
- `PHASE3_NEXT_BOUNDED_STEP=leave-this-survey-parked-unless-the-shared-abi-manifest-the-shared-abi-slice-or-the-dedicated-phase3_policy_unsafe-replay-pair-drifts-again`

## Roadmap Contract

Phase 3 is where Zigux starts defining permanent C and Zig boundary rules rather than only helper scaffolding.

For this lane, the roadmap-backed contract is still narrow:

- canonical layout assertions on the curated ABI bindings
- explicit panic policy modes
- explicit allocator policy modes and init ownership
- one narrow unsafe surface for raw pointers and MMIO
- shared ABI validation and replay gates that keep those rules reviewable

This lane does not justify broad runtime policy machinery on its own.

## Live Repo Reality

This survey is anchored to packet-local blob IDs because the current connector run could inspect the live Phase 3 packet files directly but did not expose a trustworthy branch-head commit SHA. The blob markers above are therefore the authoritative current boundary evidence for this directly coupled policy-and-unsafe packet.

The current tree still carries a real bounded policy-and-unsafe packet, but the shared ABI replay owns more of the visible proof surface than older versions of this survey claimed:

- `zigux/helpers/layout_assert.zig` is still a small generic helper, but it now centralizes compile-time layout checks for `BoundaryHeader`, `ExportStatus`, and `InteropPolicy` plus the current panic, allocator, and unsafe-scope byte values, and it now also keeps the current chrdev notify ack-window policy budget-window delivery-window view, summary, budget-view, and budget-summary layouts explicit so those ABI structs no longer live only in the shared replays.
- `zigux/helpers/panic_policy.zig` keeps panic action explicit both through the typed enum path and through `modeFromInteropPolicyBytes`, `actionForInteropPolicyBytes`, and `canReturnInteropPolicyBytes` so unknown panic modes and nonzero reserved bytes fail closed before raw-byte callers infer behavior elsewhere in the packet.
- `zigux/helpers/allocator_policy.zig` keeps allocator mode, init ownership, and global-fallback policy explicit through `InitFlow`, `initFlowFor`, `modeFromInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, `permitsGlobalFallbackPolicyBytes`, `initializesOwnedStatePolicyBytes`, and `requiresResetOnInitPolicyBytes` so unknown allocator modes, helper-owned initialization, arena reset requirements, and nonzero reserved bytes fail closed before raw-byte or typed shared callers infer behavior elsewhere in the packet.
- `zigux/unsafe/narrow.zig` still keeps the raw-pointer bridge deliberately small, but it also decodes `InteropPolicy` unsafe-scope bytes explicitly through `scopeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, `permitsVolatileMmioPolicyBytes`, and `permitsRawPointerBridgePolicyBytes` so unknown scopes and reserved-byte drift do not have to be inferred elsewhere in the packet.
- `zigux/unsafe/narrow.zig` also mirrors the panic and allocator helper style with typed `InteropPolicy` entry points through `scopeFromInteropPolicy`, `recognizesInteropPolicy`, `permitsNoUnsafeInteropPolicy`, `permitsVolatileMmioInteropPolicy`, and `permitsRawPointerBridgeInteropPolicy`, while keeping the direct raw-pointer bridge relays narrowed to the `sliceAt*`, `constSliceAt*`, `constPointerAt*`, `pointerAt*`, and `writeValueAt*` helper family instead of widening into a broader unsafe facade.
- `zigux/helpers/mmio.zig` consumes that same narrow layer for direct `range()`, `read8()`, `write8()`, `read16()`, `write16()`, `read32()`, `write32()`, `read64()`, and `write64()` access while also routing policy-aware MMIO through `allowsInteropPolicy*`, `requireInteropPolicy*`, `rangeInteropPolicy*`, `read*InteropPolicy*`, and `write*InteropPolicy*` relays so volatile-MMIO callers stay inside the bounded unsafe contract.
- `scripts/zigux/check-phase3-policy-byte-guards.py` gives the shared policy-and-unsafe survey validator a dedicated reserved-byte and typed-wrapper guard across the policy helpers, this survey note, the paired `scripts/zigux/check-phase3-policy-unsafe-focused-replay.py` and `scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py` packet checks, and the explicit shared dump gate, so the existing `phase3-validate` path can fail closed on policy-byte drift instead of leaving that contract implicit.
- `zigux/tests/phase3_abi.zig` is the live shared Zig proof packet for this family today, and it now proves the `BoundaryHeader`, `ExportStatus`, and `InteropPolicy` layouts, exported constants, `export_shim` compatibility rules, and direct panic-policy, allocator-policy, and unsafe-scope decoding alignment by importing the shared policy helpers themselves.
- `zigux/tests/phase3_abi_dump.zig` keeps the current shared dump path explicit by emitting ABI constants plus the `InteropPolicy` and chrdev budget-window struct layouts; it no longer claims a dedicated policy/unsafe dump family or helper-local `MmioRange` layout packet of its own.

The current tree now ships a dedicated `phase3_policy_unsafe` replay pair through `zigux/tests/phase3_policy_unsafe.zig` and `zigux/tests/phase3_policy_unsafe_build.zig`, but the live validator packet still keeps the broader policy-and-unsafe boundary inside the shared `abi` slice rather than turning that focused replay pair into a new standalone tranche. This note should therefore stay tied to the real shared ABI packet while also recording the dedicated focused replay pair that now ships beside it.

## Ledger Alignment

This policy-and-unsafe note is still evidence for the same bounded Phase 3 ABI substrate packet recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`.

That means this lane remains survey-and-marker maintenance inside the shared ABI packet rather than a new standalone tranche.

## Current Boundary Gap

Current same-family progress already includes helper-local explicit-byte decoding, explicit allocator init-flow reviewability, typed-policy relays, shared ABI proof refreshes, and the dedicated focused replay pair:

- the panic helper decodes ABI panic-mode bytes explicitly and rejects nonzero reserved bytes instead of forcing raw-byte callers to re-map `.abort`, `.bug`, and `.warn` elsewhere in the packet
- the allocator helper decodes ABI allocator-mode bytes explicitly, names caller-prepared versus helper-owned init flow through `InitFlow`, and rejects nonzero reserved bytes so shared callers do not have to rediscover caller ownership, helper-owned initialization, global fallback, or arena-reset policy elsewhere in the packet
- the narrow unsafe helper decodes ABI unsafe-scope bytes explicitly, now exposes a mutable `sliceAt*` bridge alongside the existing pointer and const-slice relays, mirrors the typed `InteropPolicy` entry-point style already used by the panic and allocator helpers, and now keeps reserved-byte denial explicit across the remaining `sliceAt*`, `constPointerAt*`, `constSliceAt*`, `pointerAt*`, and `writeValueAt*` relay families instead of leaving those typed-policy rejection paths implicit or forcing shared callers to split bytes by hand
- the MMIO helper routes policy-aware reads and writes through explicit byte and typed `InteropPolicy` relays while keeping denied-scope accesses fail-closed instead of spreading that contract across unrelated callers
- the layout helper now keeps the canonical starter layouts, the chrdev budget-window delivery-window layouts, and the interop byte values explicit again, while the shared ABI proof packet still owns the broader exported-constant, helper-decoding, and emitted dump-surface evidence
- the dedicated `phase3_policy_unsafe` replay pair now keeps the focused raw-pointer and MMIO policy relays explicit beside the broader shared ABI packet without widening this lane into a new standalone Phase 3 tranche
- the remaining same-lane gap is only to keep this survey aligned with the live helper roles, the shipped dedicated focused replay pair, the shared ABI replay surfaces, and the current blob markers without overstating this packet into a broader runtime policy subsystem

## Next Bounded Step

- leave this lane parked unless `zigux/tests/fixtures/phase3_abi_manifest.json`, `Documentation/zigux/phase3-abi-slice.md`, `zigux/tests/phase3_policy_unsafe.zig`, or `zigux/tests/phase3_policy_unsafe_build.zig` drifts again
- keep the next same-lane change to one shared-ABI marker, one dedicated `phase3_policy_unsafe` replay note refresh, or one validator-wording refresh tied only to this packet
- if the dedicated `phase3_policy_unsafe` replay pair, the directly coupled focused low-level replay, one of the dedicated policy packet checks, or a broader policy-and-unsafe helper family changes later, resurvey this note against the exact live files before claiming that surface here