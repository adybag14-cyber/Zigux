# Phase 7 Make-Wrapper Selftest Alignment

This note keeps the shared Phase 7 make-wrapper review route honest.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=make-wrapper-shared-control-surface`
- `PHASE7_LANE_KEY=P7-Y05`

The current shared Phase 7 helper packet depends on `make -C zigux phase7-validate`
replaying both the built-in self-tests and the direct repo-root checks for the
same checker family:

- `python3 scripts/zigux/validate-phase7.py --self-test`
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/check-phase7-make-wrapper.py --self-test`
- `python3 scripts/zigux/check-phase7-make-wrapper.py`
- `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
- `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`
- `python3 scripts/zigux/check-phase7-argv-split-packet.py`
- `python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test`
- `python3 scripts/zigux/check-phase7-rbtree-parity.py`
- `python3 scripts/zigux/check-phase7-build-wiring.py --self-test`
- `python3 scripts/zigux/check-phase7-build-wiring.py`

The same parked packet also depends on the dedicated survey, sample-boundary,
and direct summarized test routes staying explicit beside that shared validator
surface:

- `make -C zigux phase7-string-helpers-survey`
- `make -C zigux phase7-string-helpers-sample-boundary`
- `make -C zigux phase7-cmdline-survey`
- `make -C zigux phase7-argv-split-survey`
- `make -C zigux phase7-rbtree-survey`
- `make -C zigux phase7-test`
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all`

The same parked packet also depends on the shared docs-root Phase 5 no-sample
reminders staying equally explicit for `string_helpers`, `cmdline`,
`argv_split`, and `rbtree` so `Documentation/zigux/README.md` does not
under-describe the parked helper bundle compared with
`Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, and the
four Phase 7 slice notes.

Keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`,
`Documentation/zigux/phase7-string-helpers-slice.md`,
`Documentation/zigux/phase7-cmdline-slice.md`,
`Documentation/zigux/phase7-argv-split-slice.md`,
`Documentation/zigux/phase7-rbtree-slice.md`, `scripts/zigux/README.md`,
`samples/zigux/README.md`, `zigux/tests/README.md`,
`scripts/zigux/validate-phase7.py`,
`scripts/zigux/check-phase7-make-wrapper.py`,
`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`,
`scripts/zigux/check-phase7-argv-split-packet.py`,
`scripts/zigux/check-phase7-rbtree-parity.py`,
`scripts/zigux/check-phase7-build-wiring.py`, `lib/string_helpers.zig`,
`lib/cmdline.zig`, `lib/argv_split.zig`, `lib/rbtree.zig`,
`zigux/tests/phase7_string_helpers.zig`,
`zigux/tests/phase7_string_helpers_survey.zig`,
`zigux/tests/phase7_string_helpers_manifest.json`,
`zigux/tests/phase7_string_helpers_sample_boundary.zig`,
`zigux/tests/phase7_cmdline.zig`,
`zigux/tests/phase7_cmdline_survey.zig`,
`zigux/tests/phase7_cmdline_manifest.json`,
`zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`,
`zigux/tests/phase7_argv_split.zig`,
`zigux/tests/phase7_argv_split_survey.zig`,
`zigux/tests/phase7_argv_split_manifest.json`,
`zigux/tests/fixtures/phase7_argv_split_vectors.zig`,
`zigux/tests/phase7_rbtree.zig`,
`zigux/tests/phase7_rbtree_survey.zig`,
`zigux/tests/phase7_rbtree_manifest.json`,
`zigux/tests/fixtures/phase7_rbtree.json`,
`zigux/tests/fixtures/phase7_rbtree_c_harness.c`,
`.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and
`zigux/tests/phase7_build.zig` aligned around that same shared replay packet so
the parked `string_helpers`, `cmdline`, `argv_split`, and `rbtree` bundle does
not drift back toward per-slice ad hoc checks.

`make -C zigux phase7-validate`, the dedicated survey and sample-boundary
replays, `make -C zigux phase7-test`, and `make -C zigux phase7` remain the
Linux-style review routes for this shared control surface.

this note does not reopen `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, or `lib/rbtree.zig`; it only keeps the already-landed shared control surface truthful.
