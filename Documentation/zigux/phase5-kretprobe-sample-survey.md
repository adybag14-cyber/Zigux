# Phase 5 Kretprobe Sample Survey

This note tracks the bounded Phase 5 survey for the roadmap's `samples/kprobes/kretprobe_example.c` anchor.

## Status

- `PHASE5_STATUS=parked-readback-aligned`
- `PHASE5_LANE_KEY=P5-L22`
- `PHASE5_SLICE=kretprobe-reference-sample-readback`
- `PHASE5_SURVEYED_COMMIT=readback-restored-2026-05-13`
- scope: keep the kretprobe survey note truthful against current directly readable repo evidence, the roadmap's approved Phase 5 anchor set, and the freeze-map boundary without widening into runtime work

## Why this note exists

Phase 5 is still the roadmap's "Samples and Reference Patterns" tranche, and `samples/kprobes/kretprobe_example.c` is still one of the four approved Linux anchors that should make Zigux idioms reviewable and repeatable.

The bounded job for this note is now narrower than the older missing-path version: say exactly what current `master` exposes today, keep the landed non-runtime kretprobe packet explicit, and avoid widening the sample into runtime-substrate claims.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-13 found these kretprobe-adjacent surfaces directly readable today:

- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `samples/zigux/kretprobe_example.zig`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase5_build.zig`
- `zigux/tests/phase5_kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example_manifest.json`
- `zigux/tests/phase5_kretprobe_example_survey.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

That same readback closes the older missing-path caveat: current `master` now exposes the sample root, focused replay, manifest-backed packet, dedicated survey replay, and shared `phase5_build.zig` route as directly readable evidence for the non-runtime kretprobe sample packet.

The directly readable shared reviewer packet is already aligned with that landed state:

- `Documentation/zigux/phase5-sample-review-guide.md` keeps sample-owned `runRetargetReplay()`, `runRecoveryReplay()`, `runOwnershipReplay()`, and `runLifecycleGuardReplay()` explicit together with the fixed `maxactiveBudget()` cue, the outstanding-instance exit boundary, timestamp-order rejection and recovery, the one-missed-instance summary, and post-exit handler rejection
- `Documentation/zigux/review-checklist.md` keeps the same lifecycle snapshots and replay-owned guard cues explicit as the current landed review packet
- `samples/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` all treat the kretprobe packet as part of the shipped four-sample non-runtime Phase 5 route instead of as a missing sample-root or focused-test gap

## What still remains true

Even with that restored readback, the roadmap and ledger still keep the intended Phase 5 ownership clear:

- the approved Linux anchor is still `samples/kprobes/kretprobe_example.c`
- the Phase 5 goal is still reviewable, repeatable sample-backed idioms rather than runtime-substrate closure
- `zigux/tests/phase5_build.zig`, `make -C zigux phase5-test`, and `make -C zigux phase5` remain the shared replay routes for the four-sample non-runtime packet, while `zig test samples/zigux/kretprobe_example.zig` stays the sample-local direct self-check named by the shared reviewer packet
- the later `samples/zigux/runtime_kretprobe.zig` and `samples/zigux/runtime_kretprobe_loader.zig` family still belongs to the separate Phase 9 runtime lane and should not be counted as extra proof for the non-runtime Phase 5 sample packet

## Recorded gap vs roadmap

The precise current gap is now note-local rather than sample-local:

- the roadmap still calls for a reviewable Phase 5 kretprobe reference-pattern anchor
- current `master` now directly exposes the landed sample root, focused replay, manifest-backed packet, dedicated survey replay, and shared build route for that anchor
- the directly readable shared reviewer packet already describes that landed state honestly
- the remaining truthfulness gap was this survey note's older missing-path wording

So the honest same-lane correction is to retire the older missing-path caveat and park the lane unless one of the directly coupled kretprobe packet surfaces drifts again.

## Non-goals

This note still does not claim:

- `register_kretprobe()` parity
- `unregister_kretprobe()` parity
- `pt_regs` or `regs_return_value()` parity
- runtime module wiring

## Next bounded step

Leave this lane parked unless a fresh kretprobe-local reread finds drift between this note and the directly readable sample packet under `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_build.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, or `zigux/tests/phase5_kretprobe_example_survey.zig`. If it reopens, keep the follow-up to one sample-local note, manifest, or replay-contract alignment step before widening into shared Phase 5 wording or separate runtime work.
