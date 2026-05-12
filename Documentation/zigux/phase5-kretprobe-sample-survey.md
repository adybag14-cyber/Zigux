# Phase 5 Kretprobe Sample Survey

This note tracks the bounded Phase 5 survey for the roadmap's `samples/kprobes/kretprobe_example.c` anchor.

## Status

- `PHASE5_STATUS=parked-doc-accuracy`
- `PHASE5_LANE_KEY=P5-L22`
- `PHASE5_SLICE=kretprobe-reference-sample-readback`
- `PHASE5_SURVEYED_COMMIT=readback-gap-2026-05-12`
- scope: keep the kretprobe survey note truthful against current directly readable repo evidence, the roadmap's approved Phase 5 anchor set, and the freeze-map boundary

## Why this note exists

Phase 5 is still the roadmap's "Samples and Reference Patterns" tranche, and `samples/kprobes/kretprobe_example.c` is still one of the four approved Linux anchors that should make Zigux idioms reviewable and repeatable.

The bounded job for this note is no longer to invent missing sample behavior or broaden runtime claims. It is to say exactly what current `master` exposes today and avoid restating older sample-root or shared-build claims that this run could not directly read back.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-12 found these kretprobe-adjacent surfaces directly readable today:

- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `.github/workflows/zigux-bootstrap.yml`

The same readback also found these current public-tree gaps for the kretprobe packet:

- `samples/zigux/kretprobe_example.zig` was not directly readable
- `zigux/tests/phase5_build.zig` was not directly readable
- `zigux/tests/phase5_kretprobe_example.zig` was not directly readable
- `zigux/tests/phase5_kretprobe_example_manifest.json` was not directly readable
- `zigux/tests/phase5_kretprobe_example_survey.zig` was not directly readable

That means this note should not claim a fresh direct `zig test samples/zigux/kretprobe_example.zig`, `zig test zigux/tests/phase5_kretprobe_example_survey.zig`, or `zig build test --build-file zigux/tests/phase5_build.zig --summary all` replay on current `master`.

## What still remains true

Even with that narrower readback, the roadmap and ledger still keep the intended Phase 5 ownership clear:

- the approved Linux anchor is still `samples/kprobes/kretprobe_example.c`
- the Phase 5 goal is still reviewable, repeatable sample-backed idioms rather than runtime-substrate closure
- `.github/workflows/zigux-bootstrap.yml` still names the shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` route in the workflow packet, so any later same-lane follow-up should keep the workflow reminder, docs, and directly readable sample packet aligned rather than inventing a fifth sample or widening into the separate Phase 9 `runtime_kretprobe` family

## Recorded gap vs roadmap

The precise current gap is narrower than the previous version of this note claimed:

- the roadmap still calls for a reviewable Phase 5 kretprobe reference-pattern anchor
- current `master` still carries shared Phase 5 reminder surfaces that talk about that anchor and its reviewer packet
- current direct readback for this run did not confirm the kretprobe sample-root file, the focused Phase 5 kretprobe test packet, or the shared Phase 5 build file themselves

So the honest same-lane posture is readback truthfulness, not a fresh claim that the full landed kretprobe packet is directly readable today.

## Non-goals

This note still does not claim:

- `register_kretprobe()` parity
- `unregister_kretprobe()` parity
- `pt_regs` or `regs_return_value()` parity
- runtime module wiring

## Next bounded step

Keep this lane parked unless a follow-up run can directly read or restore the missing kretprobe sample-root and focused Phase 5 test surfaces on current `master`. If the repo stays in this state, the next same-lane task should be another one-file truthfulness repair in the shared Phase 5 reminder packet rather than widening sample behavior or runtime work.
