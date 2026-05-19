# Phase 5 Trace-Events Approved Idiom Gap

This note keeps the roadmap-backed Phase 5 trace-events packet truthful when shared reviewer surfaces need to mention the bounded formatting idiom that current `master` still approves.

## Current approved cue on `master`

The roadmap-backed Phase 5 trace-events anchor is still:

- `samples/trace_events/trace-events-sample.c`

Authenticated sample-root readback still directly exposes this bounded non-runtime formatting companion:

- `samples/zigux/trace_events_string_formatting_sample.zig`

Fresh shared-packet reread on 2026-05-19 reconfirmed that the broader non-runtime trace-events sample-local companions still need fresh reread proof before they can be treated as returned direct current-`master` evidence:

- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

The shared `zigux/tests/phase5_build.zig` route remains useful support material too, but keep it framed as current public-tree-backed companion evidence until authenticated contents reread returns that path directly again.

Keep the approved formatting idiom bounded to the current landed reminder packet:

- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `samples/zigux/trace_events_string_formatting_sample.zig`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase5-review-guide-surface.py`
- `zigux/tests/README.md`

That packet should keep the selected-string plus `iter=%d` formatting cue explicit while staying honest about the current split: the bounded formatting companion remains directly readable through the authenticated sample-root route, the older non-runtime trace-events sample-local companions stay in the repo-reality-gap or public-tree-backed companion bucket until a fresh reread proves they returned directly on `master`, the shared `zigux/tests/phase5_build.zig` path is still public-tree-backed companion evidence rather than returned authenticated proof, and `scripts/zigux/check-phase5-review-guide-surface.py` remains the shipped shared guard for that reminder family rather than an optional extra.

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
Current `master` also still ships no standalone Phase 5 `samples/zigux/*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.
Keep that no-extra-sample boundary separate from the bounded trace-events formatting companion so this note does not blur helper-family reminders into trace-events proof.

Use this note only to restate the bounded formatting cue that Phase 5 reviewers should preserve inside the roadmap-backed `trace_events` anchor.

Do not treat this note as proof of:

- standalone formatting-helper delivery
- standalone broad `*format*` sample delivery
- standalone `printf` parity
- standalone `vsprintf` parity
- standalone string-helper delivery
- standalone `*cmdline*` sample delivery
- standalone `*argv*` sample delivery
- standalone `*rbtree*` sample delivery
- standalone `*bitmap*` sample delivery
- a fifth approved Phase 5 sample

Keep standalone formatting-helper evidence under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 helper reminders, keep `cmdline`, `argv_split`, and `rbtree` evidence under the bounded Phase 7 helper packet, keep direct bitmap helper reviewability under the closed Phase 1 plus bounded Phase 4 reminder packet, and keep runtime-facing trace-events loader work under the separate Phase 9 lane.

## Next bounded step

Leave this note parked unless a fresh reread shows that another shared trace-events reminder surface still treats the narrower formatting companion as a returned full trace-events packet, loses the selected-string plus `iter=%d` cue, stops naming the shipped guide-surface guard, or stops framing `zigux/tests/phase5_build.zig` and the older sample-local companions as public-tree-backed companion evidence or repo-reality gaps while authenticated contents reread still misses those paths.