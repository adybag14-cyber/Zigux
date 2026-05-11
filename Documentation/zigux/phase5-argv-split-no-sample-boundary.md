# Phase 5 Argv-Split No-Sample Boundary

This note keeps one Phase 5 contributor boundary explicit: current `master` still ships no standalone `samples/zigux/*argv*` reference sample, so `argv_split` reviewability stays under its existing Phase 7 helper-owned packet rather than the still-unlanded Phase 5 reference-sample packet described by the roadmap.

## Why this note exists

The roadmap-backed Phase 5 destination set is intentionally small:
- `samples/kfifo/bytestream-example.c`
- `samples/kobject/kobject-example.c`
- `samples/kprobes/kretprobe_example.c`
- `samples/trace_events/trace-events-sample.c`

Current `master` still does not verify those four planned Zig sample surfaces in the tree, so contributors still need one compact reminder that `argv_split` belongs to the separate helper lane even when a Phase 5 wording refresh touches shared reviewer guidance.

## No-sample rule

Do not count `argv_split` as a fifth Phase 5 sample.

Keep `argv_split` reviewability under these existing Phase 7 surfaces:
- `Documentation/zigux/phase7-argv-split-slice.md`
- `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`
- `lib/argv_split.zig`
- `zigux/tests/phase7_argv_split.zig`
- `zigux/tests/phase7_argv_split_survey.zig`
- `zigux/tests/phase7_argv_split_manifest.json`
- `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
- `scripts/zigux/validate-phase7.py`
- `scripts/zigux/check-phase7-make-wrapper.py`
- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
- `scripts/zigux/check-phase7-build-wiring.py`
- `scripts/zigux/check-phase7-argv-split-packet.py`
- `zigux/Makefile`
- `zigux/tests/phase7_build.zig`

## Contributor refresh cue

If a shared Phase 5 guide, checklist, or README change mentions the no-`argv` sample boundary, keep this note aligned with:
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

## Non-goals

This note does not widen Phase 5 into a new `argv_split` sample, runtime-loader work, command-line substrate work, or any other follow-on beyond the approved four-anchor Phase 5 lane.
