# Phase 3 Policy and Unsafe Boundary Survey

This note records the current policy and narrow-unsafe boundary for the bounded Phase 3 ABI substrate on live `master`.

## Status

- `PHASE3_LAYOUT_ASSERT_PATH=zigux/helpers/layout_assert.zig`
- `PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings`
- `PHASE3_LAYOUT_ASSERT_BLOB_SHA=97d95039506e077488ec2e58e0242dce64be7d39`
- `PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig`
- `PHASE3_PANIC_POLICY=explicit-modes-only`
- `PHASE3_PANIC_POLICY_BLOB_SHA=94e0d91cd9673d137bd302a8c2aba1034d948805`
- `PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig`
- `PHASE3_ALLOCATOR_POLICY=explicit-modes-only`
- `PHASE3_ALLOCATOR_POLICY_BLOB_SHA=e91de23f1980a5d4acb7b415c04388114d7f2970`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_BLOB_SHA=b4d56107ff0f3d2845d7c26dac87d5f594602a28`
- `PHASE3_UNSAFE_PATH=zigux/unsafe/narrow.zig`
- `PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge`
- `PHASE3_UNSAFE_BLOB_SHA=b0642439ef6ae7a2ff80b38e5e6689b8b388c523`
- `PHASE3_ABI_TEST_PATH=zigux/tests/phase3_abi.zig`
- `PHASE3_ABI_TEST_BLOB_SHA=7c3c7887bb23d1acccd835ed3bb71eba3824c45d`
- `PHASE3_ABI_DUMP_PATH=zigux/tests/phase3_abi_dump.zig`
- `PHASE3_ABI_DUMP_BLOB_SHA=77eeb1a928ae2032b72960546277290d5116ab0b`
- `PHASE3_ABI_MANIFEST_BLOB_SHA=cc34bb652830f5214adb55558b1ad932de9dd975`
- `PHASE3_ABI_SLICE_DOC_BLOB_SHA=c908bf6993caa9bf76273dc65ac1c07cf62b264d`
- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi`
- `PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`
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

- `zigux/helpers/layout_assert.zig` keeps compile-time size, alignment, and offset checks for `BoundaryHeader`, `ExportStatus`, and `InteropPolicy` on the canonical ABI surface.
- `zigux/helpers/panic_policy.zig` keeps panic action explicit through `abort`, `bug`, and `warn`, and its focused test still proves the return policy directly from those enum values.
- `zigux/helpers/allocator_policy.zig` keeps caller-provided ownership and global-fallback policy explicit through the current helper-local predicates.
- `zigux/unsafe/narrow.zig` stays deliberately small: address math, pointer formation, const slice reads, const pointer reads, and direct value writes remain the whole explicit raw-pointer bridge.
- `zigux/helpers/mmio.zig` consumes that same narrow layer for `range()`, `read8()`, `write8()`, `read32()`, and `write32()` rather than widening into a larger policy substrate.
- `zigux/tests/phase3_abi.zig` is the live shared Zig proof packet that imports these helpers today, and `zigux/tests/phase3_abi_dump.zig` keeps the ABI-side `InteropPolicy` and `MmioRange` layout and constant evidence visible on the shared dump path.
- `zigux/tests/fixtures/phase3_abi_manifest.json`, `Documentation/zigux/phase3-abi-slice.md`, and `scripts/zigux/validate-phase3.py` already treat these helpers as part of the shared `abi` slice.

The current tree does not ship the broader typed-policy decode helper, a dedicated `phase3_policy_unsafe` replay pair, or the richer policy/unsafe helper family that older versions of this note described. Those claims had become stale review noise and should not steer the lane.

## Ledger Alignment

This policy-and-unsafe note is still evidence for the same bounded Phase 3 ABI substrate packet recorded in `BOOTSTRAP_COMMIT_LEDGER.md` entry `26`, `feat(zigux): start bounded Phase 3 abi substrate skeleton`.

That means this lane remains note-and-marker maintenance inside the shared ABI packet rather than a new standalone tranche.

## Current Boundary Gap

No new helper-local panic, allocator, MMIO, or unsafe bug was proven in this run.

The real gap was documentation drift:

- the dedicated survey note had started claiming policy/unsafe surfaces that are not present on current `master`
- the shared ABI manifest, ABI slice note, validator, and the live helper files still describe a smaller and internally consistent packet
- future same-lane work should only expand this note when the repo actually lands a new reviewable policy or unsafe helper surface

## Next Bounded Step

- leave this lane parked unless one of the shared ABI packet files drifts again or a real dedicated policy/unsafe helper expansion lands
- keep the next same-lane change to one note, manifest, or validator alignment step tied only to this packet
- if a broader policy decode or focused replay pair lands later, resurvey this note against the exact live files before claiming that surface here
