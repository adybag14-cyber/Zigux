# Phase 5 Argv-Split No-Sample Boundary

This note keeps one Phase 5 contributor boundary explicit: current `master` still ships no standalone `samples/zigux/*argv*` reference sample, so `argv_split` reviewability stays under its existing Phase 7 helper-owned packet rather than the four landed Phase 5 samples.

## Why this note exists

The active Phase 5 packet is intentionally small and sample-backed:
- `samples/zigux/bytestream_fifo.zig`
- `samples/zigux/kobject_example.zig`
- `samples/zigux/kretprobe_example.zig`
- `samples/zigux/trace_events_sample.zig`

Contributors still need one compact reminder that `argv_split` belongs to the separate helper lane even when a Phase 5 wording refresh touches shared reviewer guidance.

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

This note does not widen Phase 5 into a new `argv_split` sample, runtime-loader work, command-line substrate work, or any other follow-on beyond the already-shipped four-sample packet.
