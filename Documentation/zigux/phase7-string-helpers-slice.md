# Phase 7 String Helpers Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/string_helpers.c`.

## Status

- `PHASE7_STATUS=starter_landed`
- `PHASE7_SLICE=string-helpers-runtime-leaf`
- `PHASE7_LANE_KEY=P7-L04`
- lane-key note: this `P7-L04` marker is a packet-local historical helper-slice tag for the restored string-helpers starter packet and should not be read as the current bootstrap-glue schedule owner
- scope: keep the Phase 7 string-helpers lane limited to the restored starter packet and the no-sample review boundary
- lane state: current `master` now carries both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`, while the dedicated survey, dedicated no-string-sample boundary replay, dedicated manifest packet, shared build-wiring checker, shared validator, make-wrapper alignment note, shared build route, and Linux-style `make -C zigux phase7` replay keep that restored starter packet reviewable without claiming the broader parked family is fully landed
- product boundary:
  - `lib/string_helpers.zig`
  - `zigux/tests/phase7_string_helpers.zig`
  - `zigux/tests/phase7_string_helpers_survey.zig`
  - `zigux/tests/phase7_string_helpers_sample_boundary.zig`
  - `zigux/tests/phase7_string_helpers_manifest.json`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/README.md`
  - `scripts/zigux/validate-phase7.py`
  - `scripts/zigux/check-phase7-make-wrapper.py`
  - `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  - `scripts/zigux/check-phase7-build-wiring.py`
  - `zigux/tests/phase7_build.zig`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Slice Exists

Phase 7 is where Zigux starts moving from earlier standalone helper ports into reusable in-kernel runtime helper families.

The current `string_helpers` state on `master` is no longer the older missing-helper gap. Instead, the lane now carries a restored starter packet that keeps the lowest-risk first-NUL and whitespace-sensitive helpers reviewable while the broader family stays deliberately out of scope.

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane. Current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample, so the dedicated boundary replay should keep that separation explicit while the restored starter packet advances through helper-local review surfaces only.

## Gates

1. keep the restored starter tests explicit
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all`
- `zigux/tests/phase7_string_helpers.zig`

2. keep the shared validator-first packet explicit
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/check-phase7-make-wrapper.py`
- `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
- `python3 scripts/zigux/check-phase7-build-wiring.py`
- `make -C zigux phase7-validate`

3. keep the helper wired through the shared Phase 7 convenience route
- `make -C zigux phase7`

4. keep the dedicated survey gate reviewable
- `zigux/tests/phase7_string_helpers_survey.zig`

5. keep the dedicated no-string-sample boundary guard reviewable
- `samples/zigux/README.md`
- `zigux/tests/phase7_string_helpers_sample_boundary.zig`
- `make -C zigux phase7-string-helpers-sample-boundary`

6. keep the dedicated manifest packet explicit
- `zigux/tests/phase7_string_helpers_manifest.json`

## Current Parity Surface

The restored starter packet on current `master` covers:

- `skipSpaces()` and `skip_spaces()`
- `trimSpaces()` and `strim()`
- `sysfsStreq()` and `sysfs_streq()`
- `matchString()` and `match_string()`
- `sysfsMatchString()` and `__sysfs_match_string()`
- `strreplace()`

The current starter replay keeps these proofs explicit:

- leading whitespace skipping that stops at the first NUL
- in-place leading and trailing trimming that preserves bytes beyond the first exported C-string prefix
- newline-aware sysfs equality
- bounded null-sentinel table matching through the first NULL entry
- in-place replacement behavior that stops at the first NUL
- the dedicated survey gate, manifest packet, no-sample boundary replay, shared validator route, shared build route, and Linux-style `make -C zigux phase7` replay

## Non-goals

This restored starter slice does not yet claim:

- the older parked missing-helper gap
- the broader full-family packet that previously named `memcpy_and_pad()`, `string_get_size()`, `parse_int_array()`, `string_unescape()`, `string_escape_mem()`, `kasprintf_strarray()`, `kfree_strarray()`, or the allocator-backed duplication follow-ons as landed on current `master`
- a new `samples/zigux/` string-helper reference sample

## Next Bounded Step

The next bounded follow-through should stay inside the restored starter packet: keep the survey, manifest, boundary replay, validator, and slice note aligned with the helper pair that is now back on current `master`, then take one helper-local expansion step only after that packet stays truthful again.
