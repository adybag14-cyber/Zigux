# Phase 3 Policy and Unsafe Boundary Survey

This note records the current policy and narrow-unsafe boundary for the bounded Phase 3 ABI substrate on live `master`.

## Status

- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`
- `PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig`
- `PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings-plus-mmio-and-rbtree-views`
- `PHASE3_LAYOUT_ASSERT_BLOB_SHA=21b239f78ad5806868079f99cbf111d3cb97de25`
- `PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig`
- `PHASE3_PANIC_POLICY=explicit-modes-only`
- `PHASE3_PANIC_POLICY_BLOB_SHA=c0d9d09ba2421cfc20813c94b3371498dcd9bd79`
- `PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig`
- `PHASE3_ALLOCATOR_POLICY=explicit-modes-only`
- `PHASE3_ALLOCATOR_POLICY_BLOB_SHA=5f212bc871d5c6c194be3249ef8d91ca3b5d09cf`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_BLOB_SHA=70bf700a8ec952ff7bbaf230cf5522071af810d0`
- `PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig`
- `PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge`
- `PHASE3_UNSAFE_BLOB_SHA=78319221371f440f974759985dd667d63e617dc1`
- `PHASE3_ABI_TEST_PATH=zigux/tests/phase3_abi.zig`
- `PHASE3_ABI_TEST_BLOB_SHA=7c3c7887bb23d1acccd835ed3bb71eba3824c45d`
- `PHASE3_ABI_DUMP_PATH=zigux/tests/phase3_abi_dump.zig`
- `PHASE3_ABI_DUMP_BLOB_SHA=77eeb1a928ae2032b72960546277290d5116ab0b`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=91537cc1e4d6ae3cff25907efb47bef231d540b1`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=2b4eeab14deb6381cd646381e074eaf53c078903`
- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi`
- `PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`
- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`
- `PHASE3_POLICY_BYTE_GUARD=python3 scripts/zigux/check-phase3-policy-byte-guards.py`
- `PHASE3_BOUNDARY_GAP=dedicated-policy-unsafe-focused-replay-pair-now-ships-inside-the-shared-abi-packet`
- `PHASE3_NEXT_BOUNDED_STEP=keep-this-note-aligned-with-the-shared-abi-packet-and-the-dedicated-phase3_policy_unsafe-focused-replay-pair-until-a-broader-helper-expansion-lands`

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

The current tree still carries a real bounded policy-and-unsafe packet, but it is smaller than older versions of this survey claimed:

- `zigux/helpers/layout_assert.zig` keeps compile-time size, alignment, field-type, and offset checks for the canonical ABI root while also covering the shipped `MmioRange` and `RbtreeRootView` layouts that now sit inside the same bounded packet.
- `zigux/helpers/panic_policy.zig` now keeps panic action explicit both through the typed enum path and through `modeFromInteropPolicyBytes`, `actionForInteropPolicyBytes`, and `canReturnInteropPolicyBytes` so unknown panic modes and nonzero reserved bytes fail closed before raw-byte callers infer behavior elsewhere in the packet.
- `zigux/helpers/allocator_policy.zig` now keeps caller-provided ownership and global-fallback policy explicit both through the typed predicates and through `modeFromInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, `requiresExplicitCallerInteropPolicy`, `requiresExplicitCallerByte`, `permitsGlobalFallbackPolicyBytes`, `permitsGlobalFallbackInteropPolicy`, and `permitsGlobalFallbackByte` so unknown allocator modes and nonzero reserved bytes fail closed before raw-byte or typed shared callers infer behavior elsewhere in the packet.
- `zigux/unsafe/narrow.zig` still keeps the raw-pointer bridge deliberately small, but it now also decodes `InteropPolicy` unsafe-scope bytes explicitly through `scopeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, `permitsVolatileMmioPolicyBytes`, and `permitsRawPointerBridgePolicyBytes` so unknown scopes and reserved-byte drift do not have to be inferred elsewhere in the packet.
- `zigux/unsafe/narrow.zig` now also mirrors the panic and allocator helper style with typed `InteropPolicy` entry points through `scopeFromInteropPolicy`, `recognizesInteropPolicy`, `permitsNoUnsafeInteropPolicy`, `permitsVolatileMmioInteropPolicy`, and `permitsRawPointerBridgeInteropPolicy` so shared callers do not have to split unsafe-scope bytes out by hand before checking the bounded unsafe contract.
- `zigux/helpers/mmio.zig` still consumes that same narrow layer for `range()`, `read8()`, `write8()`, `read16()`, `write16()`, `read32()`, `write32()`, `read64()`, and `write64()` rather than widening into a larger policy substrate.
- `zigux/helpers/mmio.zig` now also mirrors the Phase 3 policy helpers with explicit `InteropPolicy`-gated `range`, `read*`, and `write*` entry points instead of forcing volatile MMIO callers to re-check unsafe-scope bytes outside the helper before using the bounded pointer bridge.
- `scripts/zigux/check-phase3-policy-byte-guards.py` now gives the shared policy-and-unsafe survey validator a dedicated reserved-byte and typed-wrapper guard across the policy helpers, this survey note, and the explicit shared dump gate, so the existing `phase3-validate` path fails closed on policy-byte drift instead of leaving that contract implicit.
- `zigux/tests/phase3_abi.zig` is the live shared Zig proof packet that imports these helpers today, and `zigux/tests/phase3_abi_dump.zig` plus the shared `zig build phase3-dump --build-file zigux/tests/build.zig` route keep the ABI-side `InteropPolicy` and `MmioRange` layout and constant evidence visible on the dump path.
- `zigux/tests/fixtures/phase3_abi_manifest.json`, `Documentation/zigux/phase3-abi-slice.md`, and `scripts/zigux/validate-phase3.py` already treat these helpers as part of the shared `abi` slice.
The current tree now ships a dedicated `phase3_policy_unsafe` replay pair through `zigux/tests/phase3_policy_unsafe.zig` and `zigux/tests/phase3_policy_unsafe_build.zig`, but it still does not ship a broader policy-and-unsafe helper family. This note should stay tied to the real shared ABI packet and that focused replay pair instead of claiming more than that.

## Ledger Alignment

This policy-and-unsafe note is still evidence for the same bounded Phase 3 ABI substrate packet recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`.

That means this lane remains note-and-marker maintenance inside the shared ABI packet rather than a new standalone tranche.

## Current Boundary Gap

Current same-family progress already includes three helper-local reserved-byte tightenings plus one typed unsafe-entry alignment and one shared packet guard:

- the panic helper now decodes ABI panic-mode bytes explicitly and rejects nonzero reserved bytes instead of forcing raw-byte callers to re-map `.abort`, `.bug`, and `.warn` elsewhere in the packet
- the allocator helper now decodes ABI allocator-mode bytes explicitly and rejects nonzero reserved bytes instead of forcing raw-byte callers to rediscover caller-ownership and global-fallback policy elsewhere in the packet
- the narrow unsafe helper now decodes the ABI unsafe-scope bytes explicitly and now mirrors the typed `InteropPolicy` entry-point style already used by the panic and allocator helpers, instead of leaving reserved-byte and unknown-scope handling implicit or forcing shared callers to split bytes by hand
- the MMIO helper now exposes explicit `InteropPolicy`-gated `range`, `read*`, and `write*` entry points instead of forcing volatile MMIO callers to re-check unsafe-scope bytes outside the helper before using the bounded pointer bridge
- the shared ABI packet now also carries a dedicated `scripts/zigux/check-phase3-policy-byte-guards.py` guard, so shared docs-root and scripts-root summaries should keep that policy-byte gate explicit whenever this packet moves instead of flattening the current substrate back into helpers-plus-survey wording alone
- the remaining same-lane gap is no longer a missing focused replay pair; it is only the need to keep this survey, the shared ABI packet, and the dedicated `phase3_policy_unsafe` focused replay pair aligned without implying a broader runtime policy subsystem

## Next Bounded Step

- leave this lane parked unless one of the shared ABI packet files or the dedicated `phase3_policy_unsafe` focused replay pair drifts again
- keep the next same-lane change to one note, manifest, validator, or focused-test alignment step tied only to this packet
- if a broader policy-and-unsafe helper family ever lands later, resurvey this note against the exact live files before claiming that surface here
