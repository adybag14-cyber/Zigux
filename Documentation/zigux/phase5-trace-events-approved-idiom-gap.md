# Phase 5 Trace-Events Approved Idiom Gap

This note keeps the roadmap-backed Phase 5 trace-events packet truthful when shared reviewer surfaces need to mention the bounded formatting idiom that current `master` still approves.

## Current approved cue on `master`

The roadmap-backed Phase 5 trace-events anchor is still:

- `samples/trace_events/trace-events-sample.c`

Authenticated sample-root readback still directly exposes this bounded non-runtime formatting companion:

- `samples/zigux/trace_events_string_formatting_sample.zig`

Fresh public-tree reread on 2026-05-18 also reconfirmed that current `master` exposes the broader non-runtime trace-events sample packet through:

- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

The shared `zigux/tests/phase5_build.zig` route remains useful support material too, but keep it framed as current public-tree-backed companion evidence until authenticated contents reread returns that path directly again.

Keep the approved formatting idiom bounded to the current landed reminder packet:

- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `samples/zigux/trace_events_sample.zig`
- `samples/zigux/trace_events_string_formatting_sample.zig`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

That packet should keep the selected-string plus `iter=%d` formatting cue explicit while staying honest about the current split: the full non-runtime trace-events sample packet is again readable through the public tree, the bounded formatting companion remains directly readable through the authenticated sample-root route, and the shared `zigux/tests/phase5_build.zig` path is still public-tree-backed companion evidence rather than returned authenticated proof.

## Exact checks run on 2026-05-18

This run verified the current formatting companion with the attached Zig toolchain `0.17.0-dev.87+9b177a7d2` using a focused `zig test` against the current `master` file body.

The exact checks that passed were:

- `phase 5 trace-events formatting companion keeps the selected-string cue reviewable`
- `phase 5 trace-events formatting companion keeps lifecycle boundaries explicit`
- `phase 5 trace-events formatting companion keeps bounded destination failures explicit`

Those checks confirmed this current sample behavior:

- `runAnchorReplay(7)` still keeps the roadmap anchor explicit, transitions from `.initialized` to `.replay_complete`, selects `"Gandalf"`, and renders `"iter=7"` with length `6` while keeping four focus cues visible.
- lifecycle boundaries still fail closed: replay before `init()` and `exit()` before initialization both reject with `error.InvalidLifecycleTransition`; negative replay input rejects with `error.InvalidIterationCount`; replay after `exit()` rejects again; the successful replay-plus-exit path leaves `init_runs`, `replay_runs`, and `exit_runs` at `1` each.
- bounded destination behavior is now directly covered too: `formatIterationMessageInto(12, [5]u8)` returns `error.NoSpaceLeft` without changing the sample stage or incrementing `replay_runs`, while `formatIterationMessageInto(12, [7]u8)` returns `"iter=12"` and keeps the sample in the `.initialized` stage.

## Review boundary

Current `master` still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample outside the bounded trace-events companion.

Use this note only to restate the bounded formatting cue that Phase 5 reviewers should preserve inside the roadmap-backed `trace_events` anchor.

Do not treat this note as proof of:

- standalone formatting-helper delivery
- standalone broad `*format*` sample delivery
- standalone `printf` parity
- standalone `vsprintf` parity
- standalone string-helper delivery
- a fifth approved Phase 5 sample

Keep standalone formatting-helper evidence under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 helper reminders, and keep runtime-facing trace-events loader work under the separate Phase 9 lane.

## Next bounded step

Leave this note parked unless a fresh reread shows that another shared trace-events reminder surface still treats the returned non-runtime sample packet as absent, loses the selected-string plus `iter=%d` cue, stops mentioning the bounded destination failure check, or stops framing `zigux/tests/phase5_build.zig` as public-tree-backed companion evidence while authenticated contents reread still misses that path.
