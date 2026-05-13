# Phase 3 Low-Level Wrapper Boundary Survey

This note records the current low-level wrapper packet that `master` still routes through the shared Phase 3 review surface.

## Status

- `PHASE3_ATOMIC_PATH=zigux/helpers/atomic.zig`
- `PHASE3_ATOMIC_SCOPE=load-store-exchange-fetchadd-fetchsub-fetchand-fetchor-fetchxor-fetchnand-fetchmin-fetchmax-bittest-bitset-bitreset-bittoggle-compareexchange-compareexchangeweak`
- `PHASE3_BARRIER_PATH=zigux/helpers/barrier.zig`
- `PHASE3_BARRIER_SCOPE=compiler-acquire-release-full-acquirerelease`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_SCOPE=direct-range-read-write-8-16-32-64-width-alignment-and-odd-offset-replay`
- `PHASE3_LOW_LEVEL_BUILD_PATH=zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_LOW_LEVEL_TEST_PATH=zigux/tests/phase3_low_level_wrappers.zig`
- `PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_BOUNDARY_GAP=no-new-kernel-style-low-level-family-landed-beyond-current-atomic-barrier-and-direct-mmio-packet`
- `PHASE3_NEXT_BOUNDED_STEP=keep-this-lane-limited-to-packet-local-survey-validator-or-build-surface-repairs-for-atomic-barrier-and-direct-mmio-ownership-only`

## Current Packet

Current `master` already carries a real low-level wrapper packet.
The approved helper surface here is the direct wrapper family, not the adjacent policy-and-unsafe owner packet.
The direct helper files plus the focused replay keep that surface explicit.

- `zigux/helpers/atomic.zig` keeps the approved atomic surface explicit through `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, `fetchNand`, `fetchMin`, `fetchMax`, `bitTest`, `bitSet`, `bitReset`, `bitToggle`, `compareExchange`, and `compareExchangeWeak`, including helper-local non-`seq_cst` ordering, signed min/max, and bit-wrapper replays.
- `zigux/helpers/barrier.zig` keeps the approved barrier surface explicit through `compiler`, `acquire`, `release`, `full`, and `acquireRelease`, with `compiler()` staying helper-local while current `master` still ships the barrier-locality and handoff replays in the focused route.
- `zigux/helpers/mmio.zig` keeps the approved direct MMIO packet explicit through `range()`, direct 8-, 16-, 32-, and 64-bit reads and writes, width coverage, alignment handling, and odd-offset replay behavior in the focused test route.
- `zigux/tests/phase3_low_level_wrappers.zig` remains the current focused replay for the shared direct wrapper packet, including the direct MMIO width, alignment, odd-offset, and byte-scoped interop-policy checks plus the non-`seq_cst` atomic, barrier locality or handoff, and shared allocator-or-panic consumer proofs, while the atomic bit wrappers stay helper-local in `zigux/helpers/atomic.zig` and `compiler()` stays helper-local in `zigux/helpers/barrier.zig` to keep this focused route bounded.
- `zigux/tests/phase3_low_level_wrappers_build.zig` is the focused build route that lets this packet stay reviewable without reopening the broader `zigux/tests/build.zig` lane.

## Adjacent Packet Boundary

This lane no longer owns the policy-and-unsafe packet just because the current focused replay still imports adjacent helpers.

- `zigux/helpers/allocator_policy.zig`, `zigux/helpers/panic_policy.zig`, and `zigux/unsafe/narrow.zig` stay owned by `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` and its coupled policy validators, even when the current low-level replay still imports them for the shared allocator-and-panic consumer proof.
- the policy-aware MMIO relays in `zigux/helpers/mmio.zig`, including `allowsInteropPolicy*`, `requireInteropPolicy*`, `rangeInteropPolicy*`, `read*InteropPolicy*`, and `write*InteropPolicy*`, stay owned by the policy-and-unsafe packet even though the focused low-level replay currently exercises them.
- `zigux/tests/phase3_low_level_wrappers.zig` still exercises byte-scoped MMIO policy relays such as `allowsInteropPolicyByte`, `rangeInteropPolicyByte`, `read8InteropPolicyByte`, `write8InteropPolicyByte`, `read8InteropPolicyBytes`, and `write8InteropPolicyBytes`, but those focused checks continue to serve the adjacent policy-and-unsafe owner packet rather than widening direct MMIO ownership here.
- `zigux/tests/phase3_low_level_wrappers.zig` now also replays raw-pointer bridge admission helpers such as `permitsRawPointerBridgeInteropPolicy`, `pointerAtInteropPolicy`, `sliceAtInteropPolicy`, `constSliceAtInteropPolicy`, and `writeValueAtInteropPolicy`, but those focused checks still belong to the adjacent policy-and-unsafe packet instead of widening this lane beyond the direct atomic, barrier, and MMIO wrapper family.
- this low-level wrapper note should therefore describe direct MMIO behavior only and leave policy admission, reserved-byte decoding, raw-pointer bridge scope, allocator policy, and panic policy drift to the adjacent packet.

## Roadmap Fit

Phase 3 is where Zigux defines an explicit permanent C/Zigux boundary.
For this lane, the roadmap-backed requirement is still narrow and helper-first:

- approved atomic wrappers
- approved barrier wrappers
- approved direct MMIO wrappers

That means the right work here is packet-local truthfulness.
It does not justify broad new helper-family growth on its own.

## Boundary Reading

The current helper-and-replay packet shows that the shipped direct wrapper surface now includes:

- helper-local atomic bit-set, bit-reset, bit-toggle, and bit-test coverage in `zigux/helpers/atomic.zig`
- helper-local `compiler()` barrier coverage in `zigux/helpers/barrier.zig`
- 64-bit direct MMIO coverage in the focused test route
- direct MMIO width, alignment, and odd-offset behavior in the focused test route
- non-`seq_cst` ordering coverage and signed atomic edges in the focused test route
- barrier-locality and handoff replays

The bounded gap is therefore not absence.
The remaining gap is still breadth control.
This lane should only reopen for one more survey, validator, or focused build repair inside atomic, barrier, or direct MMIO ownership unless that direct helper surface moves again.

## Next Step

The next honest follow-on inside `shared-subsystems` stays small:

- keep the dedicated survey, validator, helper-local atomic proof surface, helper-local barrier proof surface, and focused build route aligned with the current atomic, barrier, and direct-MMIO packet
- keep policy admission, allocator policy, panic policy, and raw-pointer bridge follow-through in the adjacent policy-and-unsafe packet
- avoid widening this lane into broader ABI, policy, export, or generated-wrapper cleanup
