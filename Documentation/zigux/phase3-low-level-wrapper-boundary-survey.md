# Phase 3 Low-Level Wrapper Boundary Survey

This note records the current low-level wrapper packet that `master` still routes through the shared Phase 3 review surface.

## Status

- `PHASE3_ATOMIC_PATH=zigux/helpers/atomic.zig`
- `PHASE3_ATOMIC_SCOPE=load-store-exchange-fetchadd-fetchsub-fetchand-fetchor-fetchxor-fetchnand-fetchmin-fetchmax-compareexchange-compareexchangeweak`
- `PHASE3_BARRIER_PATH=zigux/helpers/barrier.zig`
- `PHASE3_BARRIER_SCOPE=acquire-release-full-acquirerelease`
- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`
- `PHASE3_MMIO_SCOPE=range-read-write-8-16-32-64-plus-interop-policy-and-policy-byte-entrypoints`
- `PHASE3_NARROW_UNSAFE_PATH=zigux/unsafe/narrow.zig`
- `PHASE3_LOW_LEVEL_BUILD_PATH=zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_LOW_LEVEL_TEST_PATH=zigux/tests/phase3_low_level_wrappers.zig`
- `PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`
- `PHASE3_BOUNDARY_GAP=no-new-kernel-style-low-level-family-landed-beyond-current-atomic-barrier-mmio-and-narrow-unsafe-packet`
- `PHASE3_NEXT_BOUNDED_STEP=keep-this-lane-limited-to-packet-local-survey-validator-or-build-surface-repairs-unless-the-current-helper-surface-moves-again`

## Current Packet

Current `master` already carries a real low-level wrapper packet.
The approved helper surface is no longer just the earliest atomic, barrier, and 32-bit MMIO footholds.
The focused replay now proves the current packet directly.

- `zigux/helpers/atomic.zig` keeps the approved atomic surface explicit through `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, `fetchNand`, `fetchMin`, `fetchMax`, `compareExchange`, and `compareExchangeWeak`, including non-`seq_cst` orderings and signed min/max edges.
- `zigux/helpers/barrier.zig` keeps the approved barrier surface explicit through `acquire`, `release`, `full`, and `acquireRelease`, including the barrier-locality and handoff replays that current `master` already ships.
- `zigux/helpers/mmio.zig` keeps the approved MMIO packet explicit through direct 8-, 16-, 32-, and 64-bit reads and writes plus the interop-policy and policy-byte entrypoints that the focused replay exercises.
- `zigux/unsafe/narrow.zig` remains the declared narrow-unsafe boundary for the raw-pointer bridge and volatile-MMIO scopes used by that same packet.
- `zigux/tests/phase3_low_level_wrappers.zig` is the current exact replay for this packet, including the MMIO interop-policy gate, the raw-pointer bridge gate, non-`seq_cst` atomic edges, and the barrier locality and handoff proofs.
- `zigux/tests/phase3_low_level_wrappers_build.zig` is the focused build route that lets this packet stay reviewable without reopening the broader `zigux/tests/build.zig` lane.

## Roadmap Fit

Phase 3 is where Zigux defines an explicit permanent C/Zigux boundary.
For this lane, the roadmap-backed requirement is still narrow and helper-first:

- approved atomic wrappers
- approved barrier wrappers
- approved MMIO wrappers
- explicit narrow unsafe scope instead of hidden pointer expansion

That means the right work here is packet-local truthfulness.
It does not justify broad new helper-family growth on its own.

## Boundary Reading

The current focused replay shows that the shipped packet now includes:

- 64-bit MMIO coverage in the focused test route
- interop-policy and policy-byte MMIO entrypoints in the focused test route
- raw-pointer bridge scope gates in `zigux/unsafe/narrow.zig` and the focused test route
- non-`seq_cst` ordering coverage and signed atomic edges in the focused test route
- barrier-locality and handoff replays in both `zigux/helpers/barrier.zig` and the focused test route

The bounded gap is therefore not absence.
The remaining gap is still breadth control.
This lane should only reopen for one more survey, validator, or focused build repair unless the current helper surface moves again.

## Next Step

The next honest follow-on inside `P3-L22` stays small:

- keep the dedicated survey, validator, and focused build route aligned with the current low-level wrapper replay
- keep the helper packet narrow until a roadmap-backed boundary slice needs another explicit low-level helper
- avoid widening this lane into broader ABI, policy, export, or generated-wrapper cleanup
