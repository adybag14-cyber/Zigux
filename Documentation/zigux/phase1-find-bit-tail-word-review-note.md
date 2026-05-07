# Phase 1 Find Bit Tail-Word Review Note

This note records the current helper-local review ownership for the already-landed tail-word next-scan proofs in `tools/lib/find_bit.zig`.

## Scope

- phase: `Phase 1`
- helper: `tools/lib/find_bit.zig`
- boundary: helper-local review ownership only

## Current Evidence

The live helper now carries these direct tail-word next-scan anchors:

- `test "tail-word next set scans skip earlier in-range matches before clamping"`
- `test "tail-word next zero and shared scans skip earlier in-range matches before clamping"`

Those tests prove two bounded rules that are easy to lose in broader parity summaries:

- same-tail-word starts must skip earlier in-range matches instead of re-reading bits that fall before the caller-selected `start`
- trailing masked bits beyond `nbits` must still clamp back to `nbits` instead of surfacing out-of-range set, zero, or shared matches

## Ownership Rule

The shared Phase 1 replay already keeps the tail-clamped result fields explicit through `zigux/tests/fixtures/phase1_helpers.json` and `zigux/tests/phase1_helpers.zig`, but that shared replay does not isolate same-tail-word starts.

Because of that split, these two helper-local tests remain the owning review anchors whenever `findNextBit()`, `findNextZeroBit()`, or `findNextAndBit()` changes.

## Why This Exists

Phase 1 in the roadmap is supposed to keep helper ports reviewable with clear ownership rules beside the Linux C source. This note closes that requirement for the current tail-word `find_bit` surface without widening into unrelated helpers or broader closure-packet edits.
