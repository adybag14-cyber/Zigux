# Phase 5 Kretprobe Sample Next-Step Note

This note records one bounded follow-through step for the current Phase 5 `samples/kprobes/kretprobe_example.c` anchor while the earlier non-runtime Zigux packet is not directly readable on `master`.

## Status

- `PHASE5_STATUS=parked-gap-confirmed`
- `PHASE5_LANE_KEY=P5-L18`
- `PHASE5_SLICE=kretprobe-sample-next-safe-step-note`
- scope: note-only review-surface truthfulness for the non-runtime kretprobe anchor while the sample packet remains absent from direct readback

## Current repo evidence

Fresh repo evidence on 2026-05-13 keeps the live kretprobe lane narrower than this note previously claimed.

Directly readable reminder surfaces are:

- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `samples/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

That same direct readback did not recover the older non-runtime sample packet:

- `samples/zigux/kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example_manifest.json`
- `zigux/tests/phase5_kretprobe_example_survey.zig`
- `zigux/tests/phase5_build.zig`

So the current packet-local drift is note wording, not sample behavior. This note can no longer truthfully describe live helper names, manifest prompts, or shared replay routes as current directly readable evidence.

## One bounded next safe step

Keep the follow-through note-only and gap-aligned:

- treat `Documentation/zigux/phase5-kretprobe-sample-survey.md` as the current review entrypoint for the non-runtime kretprobe anchor
- repair one dedicated or shared kretprobe reminder surface at a time if it still claims the missing sample-root, focused-replay, manifest, survey-replay, or shared-build packet as already landed
- do not reopen sample behavior, manifest structure, or the separate Phase 9 runtime kretprobe family while the direct-readback gap is still the missing non-runtime packet itself

## Why this is the safest next move

The smallest honest follow-through is no longer a helper-name wording repair inside `samples/zigux/README.md`. The stronger current constraint is that the non-runtime sample packet is not directly readable at all, so the next same-lane step must stay inside note truthfulness until those missing packet paths return.

## Non-goals

This note does not reopen:

- sample behavior in `samples/zigux/kretprobe_example.zig`
- manifest or focused-replay structure for files that are not currently directly readable on `master`
- shared multi-sample Phase 5 cleanup beyond one directly coupled kretprobe reminder surface at a time
- runtime `kretprobe` starter or loader work
