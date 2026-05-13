# Phase 5 Kretprobe Sample Survey

This note tracks the bounded Phase 5 survey for the roadmap's `samples/kprobes/kretprobe_example.c` anchor.

## Status

- `PHASE5_STATUS=parked-readback-gap-aligned`
- `PHASE5_LANE_KEY=P5-L16`
- `PHASE5_SLICE=kretprobe-reference-sample-readback`
- `PHASE5_SURVEYED_COMMIT=readback-gap-confirmed-2026-05-13`
- scope: keep the kretprobe survey note truthful against current directly readable repo evidence, the roadmap's approved Phase 5 anchor set, and the freeze-map boundary without widening into runtime work

## Why this note exists

Phase 5 is still the roadmap's "Samples and Reference Patterns" tranche, and `samples/kprobes/kretprobe_example.c` is still one of the four approved Linux anchors that should make Zigux idioms reviewable and repeatable.

The bounded job for this note is now to record the current public-tree gap honestly and keep shared reminder surfaces from overstating a restored packet that direct readback no longer returns.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-13 still found these kretprobe-adjacent surfaces directly readable today:

- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

That same direct readback did not recover the older restored kretprobe packet paths:

- `samples/zigux/kretprobe_example.zig`
- `zigux/tests/phase5_build.zig`
- `zigux/tests/phase5_kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example_manifest.json`
- `zigux/tests/phase5_kretprobe_example_survey.zig`

Treat those paths as the current public-tree gap for this lane until a fresh reread proves they returned.

The same readback split also narrowed which shared reminder surfaces still need attention. On current `master`:

- `Documentation/zigux/phase5-sample-review-guide.md` and `samples/zigux/README.md` already keep the missing kretprobe sample-root, focused-test, manifest, survey-replay, and shared-build paths explicit as a current gap
- `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still overstate that missing packet by naming `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_build.zig`, or the `phase5_kretprobe_example*` replay files as directly readable current-`master` evidence

## What still remains true

Even with that missing readback, the roadmap and ledger still keep the intended Phase 5 ownership clear:

- the approved Linux anchor is still `samples/kprobes/kretprobe_example.c`
- the Phase 5 goal is still reviewable, repeatable sample-backed idioms rather than runtime-substrate closure
- the separate `samples/zigux/runtime_kretprobe.zig` and `samples/zigux/runtime_kretprobe_loader.zig` family still belongs to the later Phase 9 runtime lane and should not be counted as extra proof for the non-runtime Phase 5 packet
- shared reviewer surfaces should keep the probe-lifecycle and ownership cues explicit only when they also keep the current readback gap explicit instead of claiming a directly readable sample-root-plus-tests packet

## Recorded gap vs roadmap

The precise current gap is packet-local again:

- the roadmap still calls for a reviewable Phase 5 kretprobe reference-pattern anchor
- current `master` does not directly expose the non-runtime sample root, focused replay, manifest-backed packet, dedicated survey replay, or shared `phase5_build.zig` route for that anchor
- `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still describe part of that missing packet as directly readable current-`master` evidence, while `Documentation/zigux/phase5-sample-review-guide.md` and `samples/zigux/README.md` already keep the gap explicit

So the honest same-lane correction is to keep the missing-path caveat active again, trim stale restored-readback wording, and leave the lane parked until the kretprobe packet either returns or the remaining shared reminder surfaces are fully aligned to the current gap.

## Non-goals

This note still does not claim:

- `register_kretprobe()` parity
- `unregister_kretprobe()` parity
- `pt_regs` or `regs_return_value()` parity
- runtime module wiring

## Next bounded step

Keep this lane parked unless a fresh kretprobe-local reread finds one of two bounded changes to make:

- repair `Documentation/zigux/README.md` first, then `scripts/zigux/README.md` or `zigux/tests/README.md` if they still claim the missing `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_build.zig`, or `phase5_kretprobe_example*` packet as directly readable evidence
- the missing kretprobe sample packet paths return and the shared reminder surfaces need to be switched back to restored-readback wording

Do not widen that follow-up into runtime work.