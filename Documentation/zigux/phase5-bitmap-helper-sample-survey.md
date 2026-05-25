# Phase 5 Bitmap Helper Sample Survey

This note records the bounded Phase 5 survey for the roadmap-approved sample lane when contributors compare the current sample tree against bitmap-related helper work.

## Status

- `PHASE5_STATUS=verified-boundary-gap-vs-roadmap`
- `PHASE5_LANE_KEY=P5-L07`
- `PHASE5_SLICE=bitmap-helper-sample-survey`
- scope: keep the approved Phase 5 sample packet honest about the roadmap-backed anchor set, the current absence of a standalone bitmap helper reference sample under `samples/zigux/`, and the separate later-phase bitmap packets that already exist elsewhere in Zigux

## Why this slice exists

Phase 5 is still the roadmap's "Samples and Reference Patterns" lane.
Its approved Linux sample anchors remain:

- `samples/kfifo/bytestream-example.c`
- `samples/kobject/kobject-example.c`
- `samples/kprobes/kretprobe_example.c`
- `samples/trace_events/trace-events-sample.c`

A bitmap helper sample is not one of those four approved anchors.
The same-lane review risk on current `master` is therefore not "missing committed bitmap sample work" so much as reminder drift: bitmap helper evidence can be mistaken for a missing Phase 5 port even though the roadmap keeps bitmap work in other packets.

## Current repo reality on `master`

Fresh repo-first inspection in this run confirmed these Phase 5 and adjacent bitmap facts:

- `samples/zigux/README.md` still keeps the current non-runtime Phase 5 packet bounded to the four roadmap-backed sample anchors above.
- that same sample-root reminder still says current `master` ships no standalone `samples/zigux/*bitmap*` Phase 5 reference sample.
- the sample root does directly expose `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig`, but those files are already framed there as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof.
- current documentation also directly exposes `Documentation/zigux/phase3-bitmap-cpumask-slice.md`, which keeps the bounded helper-local bitmap/cpumask starter packet explicit as a Phase 3 interop slice rather than a Phase 5 sample-root port.
- the shared Phase 5 reminder packet already keeps standalone `*bitmap*` sample claims out of the current non-runtime sample lane beside the existing bytestream, kobject, kretprobe, and trace-events notes.

That means the honest bitmap-related gap versus the roadmap is a boundary question, not an unclaimed Phase 5 sample family:

- there is no approved standalone bitmap helper reference sample under `samples/zigux/` for Phase 5 on current `master`
- existing bitmap work is already represented through the Phase 3 helper-local slice and the separate Phase 9 runtime sample family
- same-lane reminder surfaces should not reinterpret those existing bitmap packets as evidence that a fifth approved Phase 5 sample landed, and they also should not treat the lack of a Phase 5 bitmap sample as roadmap drift by itself

## Approved idiom boundary

For the current roadmap-backed Phase 5 lane, the approved bitmap idiom is still a negative boundary:

- keep bitmap helper reviewability tied to its existing helper or runtime packets instead of inventing a new Phase 5 sample family
- keep `samples/zigux/runtime_bitmap*.zig` framed only as Phase 9 runtime-pilot evidence
- keep helper-local bitmap/cpumask reviewability tied to the existing Phase 3 slice instead of treating helper-local interop coverage as sample-root proof
- keep the four approved non-runtime sample anchors explicit whenever a shared reminder surface mentions the current Phase 5 packet
- keep standalone `*bitmap*` sample claims out of the shared Phase 5 packet unless the roadmap itself changes

## Contributor refresh prompts

When a same-lane change touches the shared Phase 5 sample packet, keep these prompts explicit:

- does the reminder still name only the four roadmap-backed Phase 5 sample anchors?
- does it still say there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`?
- does it still keep `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` framed as separate Phase 9 runtime evidence rather than extra Phase 5 proof?
- does it still keep the helper-local bitmap/cpumask packet separate from the sample-root packet?
- does it avoid treating the absence of a Phase 5 bitmap sample as proof that the roadmap-approved sample packet is incomplete when the roadmap still limits Phase 5 to the four named Linux anchors?

## Non-goals

This survey does not claim:

- delivery of a new `samples/zigux/*bitmap*` Phase 5 sample
- promotion of runtime bitmap files into Phase 5 proof
- promotion of helper-local bitmap/cpumask coverage into sample-root proof
- roadmap expansion beyond the four approved Phase 5 sample anchors

## Next bounded step

Leave this note parked unless a fresh same-lane reread finds a shared Phase 5 reminder surface that:

- drops the no-standalone-`*bitmap*` boundary
- misclassifies the Phase 9 runtime bitmap files as Phase 5 evidence
- or treats the current lack of a Phase 5 bitmap sample as roadmap drift even though the approved Phase 5 anchor set still does not include bitmap helper delivery
