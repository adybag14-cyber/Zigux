# Phase 3 Policy and Unsafe Boundary Survey

This note records the current policy and narrow-unsafe boundary for the bounded Phase 3 ABI substrate on live `master`.

## Status

- `PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig`
- `PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings-plus-mmio-and-rbtree-views`
- `PHASE3_LAYOUT_ASSERT_BLOB_SHA=8d9eb1068a058337823d91766fc15a147e525bb3`
- `PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig`
- `PHASE3_PANIC_POLICY=explicit-modes-only`
- `PHASE3_PANIC_POLICY_BLOB_SHA=269261b82ec8babdbbaaf71fe5230b765b59d033`
- `PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig`
- `PHASE3_ALLOCATOR_POLICY=explicit-modes-only`
- `PHASE3_ALLOCATOR_POLICY_BLOB_SHA=507e544f4416b2cb6cfddcc7572cb034cb004493`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_BLOB_SHA=f1516b1fcfc9b6af323d17b45f1bb19f9678a87f`
- `PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig`
- `PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge`
- `PHASE3_UNSAFE_BLOB_SHA=1574ad5713729e1e23f2aa23de244c6ee8d052fc`
- `PHASE3_ABI_TEST_PATH=zigux/tests/phase3_abi.zig`
- `PHASE3_ABI_TEST_BLOB_SHA=7c3c7887bb23d1acccd835ed3bb71eba3824c45d`
- `PHASE3_ABI_DUMP_PATH=zigux/tests/phase3_abi_dump.zig`
- `PHASE3_ABI_DUMP_BLOB_SHA=77eeb1a928ae2032b72960546277290d5116ab0b`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=4cdf556d8b2cf2182bf7dbc625e7e062d9d367c2`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=605b8f54f732ea7f3e08e3f68b46fe4e38195090`
- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi`
- `PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`
- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`
- `PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet`
- `PHASE3_NEXT_BOUNDED_STEP=keep-this-note-aligned-with-the-shared-abi-packet-until-a-real-policy-or-unsafe-helper-expansion-lands`

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

The current tree still carries a real bounded policy-and-unsafe packet, but it is smaller than older versions of this survey claimed:

- `zigux/helpers/layout_assert.zig` keeps compile-time size, alignment, field-type, and offset checks for the canonical ABI root while also covering the shipped `MmioRange` and `RbtreeRootView` layouts that now sit inside the same bounded packet.
- `zigux/helpers/panic_policy.zig` now keeps panic action explicit both through the typed enum path and through `modeFromInteropPolicyBytes`, `actionForInteropPolicyBytes`, and `canReturnInteropPolicyBytes` so unknown panic modes and nonzero reserved bytes fail closed before raw-byte callers infer behavior elsewhere in the packet.
- `zigux/helpers/allocator_policy.zig` now keeps caller-provided ownership and global-fallback policy explicit both through the typed predicates and through `modeFromInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, and `permitsGlobalFallbackPolicyBytes` so unknown allocator modes and nonzero reserved bytes fail closed before raw-byte callers infer behavior elsewhere in the packet.
- `zigux/unsafe/narrow.zig` still keeps the raw-pointer bridge deliberately small, but it now also decodes `InteropPolicy` unsafe-scope bytes explicitly through `scopeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, `permitsVolatileMmioPolicyBytes`, and `permitsRawPointerBridgePolicyBytes` so unknown scopes and reserved-byte drift do not have to be inferred elsewhere in the packet.
- `zigux/helpers/mmio.zig` still consumes that same narrow layer for `range()`, `read8()`, `write8()`, `read16()`, `write16()`, `read32()`, and `write32()` rather than widening into a larger policy substrate.
- `scripts/zigux/check-phase3-policy-byte-guards.py` now gives the shared ABI check path a dedicated reserved-byte guard across the policy helpers, this survey note, and the explicit shared dump gate instead of leaving that contract implicit.
- `zigux/tests/phase3_abi.zig` is the live shared Zig proof packet that imports these helpers today, and `zigux/tests/phase3_abi_dump.zig` plus the shared `zig build phase3-dump --build-file zigux/tests/build.zig` route keep the ABI-side `InteropPolicy` and `MmioRange` layout and constant evidence visible on the dump path.
- `zigux/tests/fixtures/phase3_abi_manifest.json`, `Documentation/zigux/phase3-abi-slice.md`, and `scripts/zigux/validate-phase3.py` already treat these helpers as part of the shared `abi` slice.

The current tree still does not ship a dedicated `phase3_policy_unsafe` replay pair or a broader policy-and-unsafe helper family. This note should stay tied to the real shared ABI packet instead of claiming more than that.

## Ledger Alignment

This policy-and-unsafe note is still evidence for the same bounded Phase 3 ABI substrate packet recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`.

That means this lane remains note-and-marker maintenance inside the shared ABI packet rather than a new standalone tranche.

## Current Boundary Gap

Current same-family progress already includes three helper-local byte-policy tightenings:

- the panic helper now decodes ABI panic-mode bytes explicitly and rejects nonzero reserved bytes instead of forcing raw-byte callers to re-map `.abort`, `.bug`, and `.warn` elsewhere in the packet
- the allocator helper now decodes ABI allocator-mode bytes explicitly and rejects nonzero reserved bytes instead of forcing raw-byte callers to rediscover caller-ownership and global-fallback policy elsewhere in the packet
- the narrow unsafe helper now decodes the ABI unsafe-scope bytes explicitly instead of leaving reserved-byte and unknown-scope handling implicit
- the shared ABI packet now also carries a dedicated `scripts/zigux/check-phase3-policy-byte-guards.py` guard, so shared docs-root and scripts-root summaries should keep that policy-byte gate explicit whenever this packet moves instead of flattening the current substrate back into helpers-plus-survey wording alone
- the remaining same-lane gap is still the absence of a dedicated focused replay pair beyond the shared ABI packet, not a need for a broader runtime policy subsystem

## Next Bounded Step

- leave this lane parked unless one of the shared ABI packet files drifts again or a real dedicated policy/unsafe focused replay pair lands
- keep the next same-lane change to one note, manifest, validator, or focused-test alignment step tied only to this packet
- if a broader policy-and-unsafe helper family ever lands later, resurvey this note against the exact live files before claiming that surface here
