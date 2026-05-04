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
- `PHASE3_ATOMIC_SCOPE=load-store-exchange-compare-exchange-compare-exchange-weak-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-min-fetch-max`
- `PHASE3_BARRIER_SCOPE=acquire-release-acquire-release-combined-full`
- `PHASE3_MMIO_SCOPE=range-read8-read16-read32-read64-write8-write16-write32-write64-plus-scoped-read8-write8-read16-write16-read32-write32-read64-write64-plus-policy-read8-write8-read16-write16-read32-write32-read64-write64-and-generic-policy-bridges`
- `PHASE3_ROADMAP_ANCHORS=rust-exports-lib-bitmap-lib-rbtree-lib-cpumask`
- `PHASE3_CURRENT_INTEROP_FAMILIES=bitmap-cpumask-rbtree-list-hlist-errptr-xarray-idr-ida-minor-alloc-dev-region-cdev-chrdev`
- `PHASE3_CURRENT_INTEROP_FAMILIES_DETAIL=bitmap-cpumask-rbtree-dedicated-boundary-plus-shared-root-view-list-hlist-errptr-xarray-idr-ida-minor-alloc-dev-region-cdev-chrdev-notify-ack-window-delivery-guard`
- `PHASE3_CURRENT_INTEROP_GAP=repo-now-carries-curated-phase3-parity-slices-beyond-the-original-roadmap-anchor-set`
- `PHASE3_CURRENT_INTEROP_GAP_DETAIL=live-build-graph-now-carries-deep-chrdev-tail-packets-while-the-curated-shared-include-zigux-abi-h-plus-zigux-bindings-abi-zig-rbtree-root-view-lift-is-landed-and-the-honest-remaining-gap-is-survey-and-validator-wording-that-still-describes-that-shared-lift-as-missing`
- `PHASE3_NEXT_SAFE_STEP=align-shared-rbtree-survey-and-validator-wording-before-any-more-shared-abi-growth`
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

## Current Interop Gap

The roadmap still describes the Phase 3 boundary through a narrow anchor set:

- `rust/exports.c`
- `lib/bitmap.c`
- `lib/rbtree.c`
- `lib/cpumask.c`

Current repo reality is broader than that original anchor list.
The live curated Phase 3 packet now also carries parity slices for:

- bitmap, cpumask, and dedicated rbtree boundary views plus the shared `rbtree` root-view lift inside the canonical ABI packet
- list and hlist traversal views
- err-pointer, xarray, xarray-slot, idr, and ida planning views
- minor-allocation and dev-region planning slices
- cdev add and cdev lookup planning slices
- chrdev open, fops, route, io, transfer, resume, retry, requeue, and completion planning slices
- chrdev notification, ack, budget, window, delivery, and delivery-guard tail chains

Current repo reality therefore includes the dedicated `rbtree` boundary packet, the landed shared `rbtree` root-view lift inside the canonical ABI packet, plus minor-allocation, dev-region, cdev, and chrdev planning and notification chains.

That is real repo-backed interop progress, but it is also the current survey gap:

- the roadmap wording is still narrower than the committed Phase 3 fixture catalog and build graph under `zigux/tests/build.zig`, which now carries chrdev tail dumps well past the original notify and ack starters
- the repo already treats those extra curated parity slices as current interop reality through `zigux/bindings/abi.zig`, the committed Phase 3 fixture manifests, `Documentation/zigux/artifact-diff.md`, and `Documentation/zigux/phase3-roadmap-gap-survey.md`; the shared ABI replay now also carries `zigux_rbtree_root_view` through the curated shared `include/zigux/abi.h` plus `zigux/bindings/abi.zig` surface, with the same record replayed by `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`, and `zigux/tests/fixtures/phase3_abi/expected.json`
- future Phase 3 work should therefore prefer documenting and validating this larger current catalog honestly while aligning the remaining survey and validator wording that still describes the shared `rbtree` lift as missing before adding still more chrdev tail growth

## Next Safe Step

Current repo evidence narrows the next honest shared ABI move to one bounded wording-alignment pass before any more shared packet growth.

- align the remaining shared Phase 3 survey and validator wording with the landed shared `zigux_rbtree_root_view` lift in `include/zigux/abi.h` and `zigux/bindings/abi.zig`
- keep the shared ABI replay, manifest catalog, and dedicated `rbtree` packet explicit in that wording
- stop there; do not widen this boundary handoff into new chrdev tail growth or unrelated Phase 3 packet churn

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
- the validator self-test now proves that missing Phase 3 layout-assert source markers fail fast instead of silently weakening the canonical binding survey

Panic policy:
- explicit modes only: `abort`, `bug`, `warn`
- helpers now decode raw `InteropPolicy.panic_mode` bytes explicitly before deciding whether return is permitted
- no implicit panic behavior in boundary helpers
- the validator self-test now proves that missing panic-policy byte-decoder markers fail the focused Phase 3 source audit

Allocator policy:
- explicit modes only: `caller_provided`, `kernel_heap`, `arena`
- helpers now decode raw `InteropPolicy.allocator_mode` bytes explicitly before deciding caller ownership, fallback, and reset requirements
- boundary code must be able to state whether it requires a caller allocator
- the validator self-test now proves that missing allocator reset-policy markers fail the same focused Phase 3 source audit

Whole-policy decode policy:
- `zigux/helpers/interop_policy.zig` now treats `InteropPolicy` as one typed boundary record instead of three unrelated byte checks
- reserved bits, panic mode, allocator mode, and unsafe scope now fail through one explicit decode path before boundary code decides caller ownership, return behavior, allocator-owned initialization or reset requirements, or unsafe permissions
- the same typed record now also keeps read-only raw-pointer bridge use reviewable through `constSliceAt()`, `constPointerAt()`, and `readValueAt()` helpers instead of re-deriving those permissions in ad hoc pointer helpers
- focused replay gate: `zigux/tests/phase3_policy_unsafe.zig` now verifies both successful whole-record decoding and rejection of partial or reserved policy bytes, and it also keeps those decoded-policy raw-pointer bridge consumers attached to the same bounded replay path

Unsafe policy:
- raw pointer and volatile access stay inside `zigux/unsafe/narrow.zig` and `zigux/helpers/mmio.zig`
- `zigux/unsafe/narrow.zig` now mirrors that boundary with a local `UnsafeScopeTag` for `none`, `volatile_mmio`, and `raw_pointer_bridge`, plus explicit permit helpers, alignment checks on scoped entry points, overflow rejection before scoped pointers or slices are formed, read-only typed value helpers through `constValueAt()` and `scopedConstValueAt()`, and Zig tests
- new unsafe entry points must be justified and reviewed as boundary expansion
- focused replay gate: `zigux/tests/phase3_policy_unsafe.zig` now keeps `layout_assert`, panic, allocator, whole-record interop-policy decoding, unsafe-byte decoding, decoded-policy raw-pointer bridge consumers, declared-scope enforcement, and overflow rejection aligned on its own compile-and-test path instead of relying only on the much broader `phase3_abi.zig` bundle
- the validator self-test now proves that removing the narrow-unsafe misalignment guard marker fails the focused Phase 3 source audit before broader ABI replay runs

Low-level wrapper survey:
- atomic reality today: `zigux/helpers/atomic.zig` currently limits the approved wrapper set to `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, `fetchMin`, `fetchMax`, `compareExchange`, and `compareExchangeWeak`, all parameterized by Zig atomic order rather than exposing a broader kernel-style helper family, and the focused wrapper replay now keeps the `fetchMin()` and `fetchMax()` floor-and-ceiling paths, non-seq-cst `load`/`store` replay, and strong plus weak compare-exchange ordering replay for `acquire`, `release`, `monotonic`, and `acq_rel` reviewable under the same bounded gate
- barrier reality today: `zigux/helpers/barrier.zig` currently limits the approved barrier surface to `acquire`, `release`, `acquireRelease`, and `full`, each expressed through a throwaway ordered atomic probe so the helper does not keep hidden shared state, and the focused wrapper replay now keeps that local probe behavior under the same bounded gate
- MMIO reality today: `zigux/helpers/mmio.zig` currently limits the approved MMIO surface to `range`, `read8`, `read16`, `read32`, and `read64`, `write8`, `write16`, `write32`, and `write64`, plus scoped `read8`, `write8`, `read16`, `write16`, `read32`, and `write32`, `read64`, and `write64` entry points, width-specific `read8Policy`, `write8Policy`, `read16Policy`, `write16Policy`, `read32Policy`, and `write32Policy`, `read64Policy`, and `write64Policy` entry points, and the generic `readScopedWithPolicy` plus `writeScopedWithPolicy` bridges that keep decoded-policy MMIO access routed back through the declared narrow unsafe layer, reject misaligned scoped addresses before pointer formation where the width requires it, reject overflowed scoped address math before pointer formation, and share the canonical `MmioRange` layout assertions with the focused low-level wrapper gate through `zigux/helpers/layout_assert.zig`
- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` and `scripts/zigux/validate-phase3-low-level-wrapper-survey.py` now keep that atomic, barrier, and MMIO packet explicit as its own bounded review surface beside the broader ABI slice note, while `zigux/tests/phase3_policy_unsafe.zig` and `scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py` keep the decoded-policy MMIO bridge reviewable beside the focused low-level gate, so broader kernel-style atomic or barrier families plus MMIO expansion beyond the current direct, scoped, and decoded-policy 8-bit, 16-bit, 32-bit, and 64-bit helpers still stay deferred until a roadmap-backed boundary slice really needs them
- focused replay gate: `zigux/tests/phase3_low_level_wrappers.zig` now keeps the atomic, barrier, direct MMIO, scoped MMIO, width-specific decoded-policy MMIO entry points, generic decoded-policy bridge coverage across the same widths, non-seq-cst `load`/`store` replay, and narrow-unsafe helper contract on its own compile-and-test path, including strong and weak compare-exchange acquire, release, monotonic, and `acq_rel` coverage, the acquire-only, release-only, combined acquire-plus-release, and full barrier probes, denied-scope checks, width-specific direct and scoped 8-bit, 16-bit, 32-bit, and 64-bit MMIO coverage, misalignment and overflow failures, `fetchMin()` and `fetchMax()` coverage, strong compare-exchange success and mismatch coverage, and weak compare-exchange retry and mismatch coverage; the broader whole-record policy decode and second-boundary-helper MMIO story remain reviewable through `zigux/tests/phase3_policy_unsafe.zig`, and `python3 scripts/zigux/validate-phase3.py` now treats both focused gates as real anti-regression surfaces instead of presence-only file lists

## Boundary

Current repo-backed boundary survey:
- export shim reality today: `zigux/kernel/export_shim.zig` stays a narrow explicit-status helper, and it now exposes a small local boundary-header surface that keeps exact canonical-size replay separate from broader future-compatible header acceptance without widening the public export namespace further
- C helper-header reality today: `include/linux/zigux.h` stays inside the same bounded packet as the C-facing relay for the shared `BoundaryHeader` and `ExportStatus` ABI types through `#include <zigux/abi.h>` plus local `zigux_status_ok()` and `zigux_status_err()` helpers, but current repo reality has also already grown that header into a broader aggregation surface for landed Phase 3 interop helper families, so this packet must keep the boundary wording and resurvey rule explicit while slice-local validators keep owning semantic proof for the gathered helper surfaces
- UAPI reality today: `zigux/uapi/version.zig` now exposes the ABI version plus an explicit boundary-header constructor whose exact canonical-size replay stays separate from broader future-compatible compatibility, which is still bounded but makes the public boundary less ad hoc than a version constant alone
- focused replay gate: `zigux/tests/phase3_export_uapi.zig` now keeps that export-shim and UAPI version contract on its own compile-and-test path instead of leaving it visible only through the much broader `phase3_abi.zig` bundle
- focused layout replay gate: `zigux/tests/phase3_export_uapi_layout.zig` and `zigux/tests/phase3_export_uapi_layout_build.zig` now keep the canonical `BoundaryHeader` and `ExportStatus` size-and-offset contract explicit beside the broader export/UAPI smoke gate

This slice does not claim:

- generated bindings
- full kernel UAPI exposure
- full runtime allocator integration
- driver ports
- scheduler ports
