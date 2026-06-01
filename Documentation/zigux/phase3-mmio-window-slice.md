# Phase 3 MMIO Window Slice

## Why This Landed

Phase 3 requires approved MMIO wrappers and a narrow unsafe surface. Current `master` already had:

- policy decoding for `volatile_mmio` in `zigux/helpers/unsafe_policy.zig`
- typed volatile helpers in `zigux/helpers/mmio.zig`
- raw-pointer bridge helpers in `zigux/unsafe/narrow.zig`

What was still missing was one bounded helper for address-based MMIO windows that keeps integer-address access behind the existing `volatile_mmio` policy gate instead of reusing the raw-pointer bridge path.

## Landed Helper

- `zigux/unsafe/mmio_window.zig`

The helper adds explicit address-gated MMIO entry points for:

- mutable volatile pointers
- const volatile pointers
- typed reads
- typed writes
- exchange-style writes

Each entry point requires:

- `volatile_mmio` scope approval
- a clear reserved byte
- enough byte coverage for the requested type
- an address-span overflow check

## Validation

Focused local Zig validation passed for an exact mirror of the landed helper with:

- `zig test` using the attached `zig-x86_64-linux-0.17.0-dev.758+748e7c5e3` toolchain

The self-tests cover:

- allowed MMIO reads, writes, and exchanges
- denial for `none` and `raw_pointer_bridge` scopes
- denial when the reserved byte is set
- byte-coverage rejection
- odd-aligned `u16` access through the explicit MMIO window path

## Scope

This is a bounded unsafe-substrate addition. It does not claim broader Phase 3 completion, and it does not open a new helper-chain family.
