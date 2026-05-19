# Phase 7 Helper Lane Sequencing

This note keeps the current Phase 7 helper packet reviewable without letting shared control-surface lanes and helper-local lanes claim the same ownership.

## Lane Map

- argv-split packet, lane `P7-L09`:
  - `Documentation/zigux/phase7-argv-split-slice.md`
  - `lib/argv_split.zig`
  - `zigux/tests/phase7_argv_split.zig`
  - `zigux/tests/phase7_argv_split_survey.zig`
  - `zigux/tests/phase7_argv_split_manifest.json`
  - `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
  - `scripts/zigux/check-phase7-argv-split-packet.py`
  - scheduled alias note: recurring scheduled lane `P7-Y07` is the older schedule label for this same argv-split packet and must be treated as the same owner, not as a second helper lane

## Current Repo Reality

- `argv_split` currently survives through `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, and `scripts/zigux/check-phase7-argv-split-packet.py`. Fresh helper-local reread for this slot confirmed the dedicated fixture vectors have now returned on current `master`, so `P7-L09` should treat the slice-helper-test-fixture-survey-manifest-checker packet as the current same-lane packet instead of carrying the fixture as a missing follow-on.

## Anti-Overlap Rules

- Treat scheduled lane `P7-Y07` as the argv-split alias for `P7-L09`; if a scheduled run starts under `P7-Y07`, keep the work inside the currently returned `argv_split` slice, helper, dedicated test, dedicated fixture, survey, manifest, and checker surfaces.
- `P7-L09` owns only argv-split helper-local parity, survey, manifest, fixture, checker, or reminder drift; because the current slot could directly reread `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, and `scripts/zigux/check-phase7-argv-split-packet.py`, keep same-lane work inside those returned surfaces.

## Next Bounded Step

- If the drift is a partially returned `argv_split` surface, keep the change inside `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, or `scripts/zigux/check-phase7-argv-split-packet.py` while the helper-local packet stays the lane owner.
