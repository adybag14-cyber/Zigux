# Phase 3 Low-Level Wrapper MMIO Width Refresh

This bounded note refreshes the low-level wrapper survey for the MMIO width-alias surface that already exists on current `master`.

## Why This Refresh Exists

The Phase 3 roadmap and bootstrap ledger both treat atomic, barrier, and MMIO wrappers as approved low-level wrapper leaf work inside the bounded ABI and interop substrate lane. Direct repo readback confirms that those wrapper leafs are present, tested, and lane-local on current `master`.

The remaining same-lane survey gap is narrower than helper implementation: some existing repo-reality wording around the MMIO width aliases under-describes the landed helper surface by naming only part of the width-specific entrypoints.

## Current Repo Reality

Current `master` already exposes the full width-specific MMIO helper family in `zigux/helpers/mmio.zig`:

- `read8InteropPolicyBytes()` and `write8InteropPolicyBytes()`
- `read8InteropPolicyByte()` and `write8InteropPolicyByte()`
- `read16InteropPolicyBytes()` and `write16InteropPolicyBytes()`
- `read16InteropPolicyByte()` and `write16InteropPolicyByte()`
- `read32InteropPolicyBytes()` and `write32InteropPolicyBytes()`
- `read32InteropPolicyByte()` and `write32InteropPolicyByte()`
- `read64InteropPolicyBytes()` and `write64InteropPolicyBytes()`
- `read64InteropPolicyByte()` and `write64InteropPolicyByte()`

That landed width-specific surface sits beside the already-readable generic MMIO helpers:

- `MmioRange`
- `rangeScoped()`
- `rangeInteropPolicy()`
- `rangeInteropPolicyBytes()`
- `rangeInteropPolicyByte()`
- `readScoped()`, `writeScoped()`, `exchangeScoped()`, and `writeMaskedScoped()`
- `readInteropPolicy()`, `writeInteropPolicy()`, `exchangeInteropPolicy()`, and `writeMaskedInteropPolicy()`
- `readInteropPolicyBytes()`, `writeInteropPolicyBytes()`, `exchangeInteropPolicyBytes()`, and `writeMaskedInteropPolicyBytes()`
- `readInteropPolicyByte()`, `writeInteropPolicyByte()`, `exchangeInteropPolicyByte()`, and `writeMaskedInteropPolicyByte()`

## Gap Decision

There is no roadmap-backed implementation gap here for atomic, barrier, or MMIO leaf presence inside the current bounded packet. The honest same-lane gap is survey precision: the wrapper-family reminder surface should account for the full width-specific MMIO alias set that current `master` already ships.

## Next Bounded Step

Keep the low-level wrapper lane bounded to truthfulness work around existing helper-local evidence. If the main wrapper survey is refreshed later, it should explicitly carry the full width-specific MMIO alias family instead of naming only a partial subset.
