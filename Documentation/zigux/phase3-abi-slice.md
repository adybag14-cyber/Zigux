# Phase 3 ABI Substrate Slice

This document starts the first bounded Phase 3 slice for Zigux.

## Status

- `PHASE3_STATUS=active`
- `PHASE3_SLICE=abi-substrate-skeleton`
- scope: first permanent C/Zigux boundary only
- product boundary:
  - `include/linux/zigux.h`
  - `include/zigux/abi.h`
  - `include/zigux/dev_t.h`
  - `zigux/bindings/abi.zig`
  - `zigux/bindings/dev_t.zig`
  - `zigux/kernel/export_shim.zig`
  - `zigux/helpers/*`
  - `zigux/unsafe/narrow.zig`
  - `zigux/uapi/version.zig`
  - `zigux/tests/phase3_abi.zig`
  - `zigux/tests/phase3_low_level_wrappers.zig`
- current export shim starter:
  - `PHASE3_EXPORT_SCOPE=shim-only starter nested inside the ABI substrate slice`
  - `PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig`
  - `PHASE3_EXPORT_SHIM_BLOB_SHA=8c905094d131e7221ae1d3ba7e2f552612bb2bd7`
  - current helper surface remains `header`, `ok`, `errno`, and `isOk`
- current UAPI starter:
  - `PHASE3_UAPI_SCOPE=version-only starter nested inside the ABI substrate slice`
  - `PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig`
  - `PHASE3_UAPI_VERSION_BLOB_SHA=f6b080efc7d06998da6125f487b75181fe1d8ae8`
  - no additional files currently ship under `zigux/uapi/`
- current export/UAPI survey shape:
  - `PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice`
  - current `master` no longer ships the older dedicated `phase3_export_uapi*` replay or `phase3-export-uapi-boundary-survey.md` note family
  - current boundary evidence therefore lives in this shared ABI slice plus `include/linux/zigux.h`, `zigux/kernel/export_shim.zig`, and `zigux/uapi/version.zig`
- current shared ABI replay:
  - `PHASE3_ABI_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`
  - `PHASE3_ABI_MANIFEST_FILE_COUNT=26`
  - `PHASE3_ABI_REPLAY_SCOPE=shared dump plus focused low-level wrapper replay`
  - the live `phase3_abi` packet now exercises the curated boundary header and export status root, bitmap and cpumask views, list and hlist views, err_ptr and xarray summaries, the current ida and minor-allocation/dev-region planning ladder, and the currently shipped chrdev notify/ack delivery-budget guard families through the shared dump and layout harness
  - the focused syntax gate now fail-closes on fused top-level `;pub const` declarations in `zigux/bindings/abi.zig` or `zigux/bindings/dev_t.zig` until the curated bindings body is split back into parse-clean lines

## Why this slice exists

Phase 3 is where Zigux stops being only helper and tool scaffolding and starts defining the real boundary between C and Zig.

The first correct move is not a broad runtime port.
It is a small substrate that makes future ports measurable:

- one C header pair
- curated Zig boundary bindings that keep the ABI root and `dev_t` starter surface reviewable
- one export-shim module
- explicit panic and allocator policies
- explicit atomic, barrier, and MMIO wrappers
- one narrow unsafe layer
- one shared C-vs-Zig layout gate plus one focused low-level wrapper replay

## Gates

1. validate slice shape
- `python3 scripts/zigux/validate-phase3.py`
- bounded ABI replay when unrelated Phase 3 slices are still in flight:
  `python3 scripts/zigux/validate-phase3.py --slug abi`

2. check C-vs-Zig ABI layout parity
- `python3 scripts/zigux/run-phase3-checks.py --slug abi`

3. run Zig substrate tests and the direct ABI dump replay
- `zig build phase3-test --build-file zigux/tests/build.zig`
- `zig build phase3-dump --build-file zigux/tests/build.zig`

4. catch fused top-level ABI binding declarations across the curated `abi.zig` and `dev_t.zig` packet before they hide inside the wider Phase 3 packet
- `python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py`
- `python3 scripts/zigux/validate-phase3-abi-bindings-syntax.py --self-test`

5. rerun the validator-support packet and its review-surface guard without duplicating the default route
- `python3 scripts/zigux/validate_phase3_selftest.py`
- `python3 scripts/zigux/check-phase3-selftest-surface.py`
- `python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test`
- `python3 scripts/zigux/check-phase3-readme-tooling-inventory.py`
- `python3 scripts/zigux/check-phase3-abi-dump-gate.py --self-test`
- `python3 scripts/zigux/check-phase3-abi-dump-gate.py`
- `python3 scripts/zigux/phase3_catalog.py --self-test`
- `python3 scripts/zigux/phase3_check_lib.py --self-test`
- `python3 scripts/zigux/generate-phase3-check-wrappers.py --check`
- `python3 scripts/zigux/run-phase3-checks.py --self-test`
- `python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py`
- `python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `make -C zigux phase3-selftest`
- focused support-script safety check only; `make -C zigux phase3-validate` already invokes the underlying helper self-tests, README tooling inventory checks, catalog sanity checks, wrapper drift checks, and shared runner self-checks directly.

- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py`
- `PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi`
- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`
- `PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig`

## Low-Level Wrapper Reality

The current Phase 3 low-level wrapper packet is still intentionally small, but it now carries direct focused proof alongside the shared ABI packet:

- `zigux/helpers/atomic.zig` now exposes `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, `fetchMin`, `fetchMax`, `compareExchange()`, and `compareExchangeWeak()`.
- `zigux/helpers/barrier.zig` now exposes `acquire`, `release`, `full`, and `acquireRelease()` through local compile-review scaffolding rather than a module-global fence word.
- `zigux/helpers/mmio.zig` now exposes `range`, direct `read8` and `write8`, and direct `read32` and `write32`.
- `zigux/tests/phase3_low_level_wrappers.zig` now directly replays the shipped helper surface, including non-`seq_cst` atomic ordering coverage plus byte and 32-bit MMIO access, while the shared ABI packet still carries the wider compile, layout, and dump proof.

## Interop rules

- `include/zigux/abi.h` is the authoritative C-facing layout surface for this slice.
- `zigux/bindings/abi.zig` must mirror it with `extern struct` layout, not approximate it.
- `include/zigux/dev_t.h` and `zigux/bindings/dev_t.zig` stay curated beside the ABI root so `dev_t` encode, decode, and range policy remains reviewable at the same boundary.
- new boundary structs require committed fixture updates under `zigux/tests/fixtures/phase3_abi/`.
- export shims must return explicit status codes instead of hidden failure behavior.
- future bindings generators are allowed later, but this slice stays curated and reviewable.

## Policy surfaces

Panic policy:
- explicit modes only: `abort`, `bug`, `warn`
- no implicit panic behavior in boundary helpers

Allocator policy:
- explicit modes only: `caller_provided`, `kernel_heap`, `arena`
- boundary code must be able to state whether it requires a caller allocator

Unsafe policy:
- raw pointer and volatile access stay inside `zigux/unsafe/narrow.zig` and `zigux/helpers/mmio.zig`
- new unsafe entry points must be justified and reviewed as boundary expansion

## Boundary

This slice does not claim:

- generated bindings
- full kernel UAPI exposure
- full runtime allocator integration
- driver ports
- scheduler ports
