# Phase 5 Trace-Events Next Safe Step

This note records the current repo-backed state of the roadmap's `samples/trace_events/trace-events-sample.c` anchor on `master`.

- `samples/zigux/trace_events_sample.zig`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` already agree that the landed Phase 5 packet is the bounded non-runtime tracing-and-ownership sample for this anchor.
- The live sample keeps the public callback-boundary packet reviewable through `runCallbackBoundaryReplay()`: the replay records the callback path, restores registration balance, and preserves the exact six-entry `checked_focus` order without asking reviewers to read private sample state.
- The live survey note and survey test already keep the formatting boundary honest too: current `master` still ships no standalone Phase 5 `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` reference sample, so the approved formatting cue remains the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig`, while standalone formatting-helper evidence stays under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet.

## Next safe step

Keep this lane narrow: update only `scripts/zigux/validate-phase5.py` so its `samples/zigux/README.md` markers and self-test packet explicitly require the same trace-events formatting-boundary wording already enforced by `zigux/tests/phase5_trace_events_sample_survey.zig`.

Do not widen this follow-through into the separate Phase 9 runtime trace-events family, other Phase 5 samples, or any new standalone formatting sample.
