# Phase 3 ABI Substrate Slice

This document starts the first bounded Phase 3 slice for Zigux.

## Status

- `PHASE3_STATUS=active`
- `PHASE3_SLICE=abi-substrate-skeleton`
- `PHASE3_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header`
- `PHASE3_UAPI_SCOPE=version-and-boundary-header`
- `PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings`
- `PHASE3_PANIC_POLICY=explicit-modes-only`
- `PHASE3_ALLOCATOR_POLICY=explicit-modes-only`
- `PHASE3_INTEROP_POLICY_SCOPE=whole-record-decode-explicit-mode-and-scope-validation`
- `PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge`
- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`
- `PHASE3_EXPORT_UAPI_GATE=zig build phase3-export-uapi-test --build-file zigux/tests/phase3_export_uapi_build.zig`
- `PHASE3_POLICY_UNSAFE_GATE=zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig`
- `PHASE3_ATOMIC_SCOPE=load-store-exchange-compare-exchange-fetch-add-fetch-sub-fetch-and-fetch-and-fetch-or-fetch-xor`
- `PHASE3_BARRIER_SCOPE=acquire-release-full`
- `PHASE3_MMIO_SCOPE=range-read16-read32-write16-write32-plus-scoped-read16-write16-read32-write32`
- scope: first permanent C/Zigux boundary only
- product boundary:
  - `include/linux/zigux.h`
  - `include/zigux/abi.h`
  - `zigux/bindings/abi.zig`
  - `zigux/kernel/export_shim.zig`
  - `zigux/helpers/*`
  - `zigux/unsafe/narrow.zig`
  - `zigux/uapi/version.zig`
  - `zigux/tests/phase3_abi.zig`

## Why this slice exists

Phase 3 is where Zigux stops being only helper and tool scaffolding and starts defining the real boundary between C and Zig.

The first correct move is not a broad runtime port.
It is a small substrate that makes future ports measurable:

- one C header pair
- one curated Zig binding
- one export-shim module
- explicit panic and allocator policies
- explicit atomic, barrier, and MMIO wrappers
- one narrow unsafe layer
- one C-vs-Zig layout gate

## Gates

1. validate slice shape
- `python3 scripts/zigux/validate-phase3.py`
- bounded ABI replay when unrelated Phase 3 slices are still in flight:
  `python3 scripts/zigux/validate-phase3.py --slug abi`
- the shared validator now also fails early if the curated substrate packet drifts at the source level, including the canonical marker set in `include/zigux/abi.h`, `include/linux/zigux.h`, and `zigux/bindings/abi.zig`

2. check C-vs-Zig ABI layout parity
- `python3 scripts/zigux/run-phase3-checks.py --slug abi`

3. replay the direct ABI dump build
- `zig build phase3-dump --build-file zigux/tests/build.zig`

4. run Zig substrate tests
- `zig build phase3-test --build-file zigux/tests/build.zig`

5. replay the focused export-shim and UAPI smoke gate
- `zig build phase3-export-uapi-test --build-file zigux/tests/phase3_export_uapi_build.zig`

6. replay the focused low-level wrapper gate
- `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`

7. replay the focused policy and unsafe gate
- `zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig`

- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py`
- `PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`
- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`
- `PHASE3_EXPORT_UAPI_GATE=zig build phase3-export-uapi-test --build-file zigux/tests/phase3_export_uapi_build.zig`
- `PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_POLICY_UNSAFE_GATE=zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig`

## Interop rules

- `include/zigux/abi.h` is the authoritative C-facing layout surface for this slice.
- `zigux/bindings/abi.zig` must mirror it with `extern struct` layout, not approximate it.
- `python3 scripts/zigux/validate-phase3.py` now audits the core source markers in `include/zigux/abi.h`, `include/linux/zigux.h`, and `zigux/bindings/abi.zig` before the focused ABI dump replay runs, so ledger-backed boundary drift fails before fixture parity is replayed.
- new boundary structs require committed fixture updates under `zigux/tests/fixtures/phase3_abi/`.
- export shims must return explicit status codes instead of hidden failure behavior.
- future bindings generators are allowed later, but this slice stays curated and reviewable.

## Policy surfaces

Layout assertion policy:
- canonical bindings only: `zigux/helpers/layout_assert.zig`
- boundary layout checks must stay attached to the curated ABI surface
- the shared layout-assert helper now owns the canonical `BoundaryHeader`, `ExportStatus`, `InteropPolicy`, and `MmioRange` size, alignment, and field-offset checks so focused gates do not drift on the core ABI packet

Panic policy:
- explicit modes only: `abort`, `bug`, `warn`
- helpers now decode raw `InteropPolicy.panic_mode` bytes explicitly before deciding whether return is permitted
- no implicit panic behavior in boundary helpers

Allocator policy:
- explicit modes only: `caller_provided`, `kernel_heap`, `arena`
- helpers now decode raw `InteropPolicy.allocator_mode` bytes explicitly before deciding caller ownership, fallback, and reset requirements
- boundary code must be able to state whether it requires a caller allocator

Whole-policy decode policy:
- `zigux/helpers/interop_policy.zig` now treats `InteropPolicy` as one typed boundary record instead of three unrelated byte checks
- reserved bits, panic mode, allocator mode, and unsafe scope now fail through one explicit decode path before boundary code decides caller ownership, return behavior, or unsafe permissions
- focused replay gate: `zigux/tests/phase3_policy_unsafe.zig` now verifies both successful whole-record decoding and rejection of partial or reserved policy bytes

Unsafe policy:
- raw pointer and volatile access stay inside `zigux/unsafe/narrow.zig` and `zigux/helpers/mmio.zig`
- `zigux/unsafe/narrow.zig` now mirrors that boundary with a local `UnsafeScopeTag` for `none`, `volatile_mmio`, and `raw_pointer_bridge`, plus explicit permit helpers, alignment checks on scoped entry points, and Zig tests
- new unsafe entry points must be justified and reviewed as boundary expansion
- focused replay gate: `zigux/tests/phase3_policy_unsafe.zig` now keeps `layout_assert`, panic, allocator, whole-record interop-policy decoding, unsafe-byte decoding, and declared-scope enforcement aligned on its own compile-and-test path instead of relying only on the much broader `phase3_abi.zig` bundle

Low-level wrapper survey:
- atomic reality today: `zigux/helpers/atomic.zig` currently limits the approved wrapper set to `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, and `compareExchange`, all parameterized by Zig atomic order rather than exposing a broader kernel-style helper family
- barrier reality today: `zigux/helpers/barrier.zig` currently limits the approved barrier surface to `acquire`, `release`, and `full`, each expressed through a throwaway ordered atomic probe so the helper does not keep hidden shared state
- MMIO reality today: `zigux/helpers/mmio.zig` currently limits the approved MMIO surface to `range`, `read16`, `read32`, `write16`, and `write32`, plus scoped `read16`, `write16`, `read32`, and `write32` entry points that keep volatile pointer formation routed back through the declared narrow unsafe layer, reject misaligned scoped addresses before pointer formation, and now share the canonical `MmioRange` layout assertions with the focused low-level wrapper gate through `zigux/helpers/layout_assert.zig`
- focused replay gate: `zigux/tests/phase3_low_level_wrappers.zig` now keeps the atomic, barrier, MMIO, and scoped narrow-unsafe helper contract on its own compile-and-test path, while the dedicated `zigux/tests/phase3_policy_unsafe.zig` gate owns layout, panic, allocator, and interop-policy unsafe-byte decoding

## Boundary

Current repo-backed boundary survey:
- export shim reality today: `zigux/kernel/export_shim.zig` stays a narrow explicit-status helper, while the focused export/UAPI replay now keeps that shim aligned with the shared `zigux/uapi/version.zig` current-version and current-size predicates without widening the kernel-side surface itself
- UAPI reality today: `zigux/uapi/version.zig` now exposes the ABI version, the canonical boundary-header size, an explicit boundary-header constructor, and named current-version/current-size predicates whose exact canonical-size replay stays separate from broader future-compatible compatibility, which is still bounded but makes the public boundary less ad hoc than a version constant alone
- focused replay gate: `zigux/tests/phase3_export_uapi.zig` now keeps that export-shim and UAPI version contract on its own compile-and-test path instead of leaving it visible only through the much broader `phase3_abi.zig` bundle

This slice does not claim:

- generated bindings
- full kernel UAPI exposure
- full runtime allocator integration
- driver ports
- scheduler ports
