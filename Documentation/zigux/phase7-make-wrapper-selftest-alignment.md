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

Current `master` keeps this shared Phase 7 control surface parked, not green:
`lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig` are still
missing from the live tree. Treat `make -C zigux phase7-validate`,
`make -C zigux phase7-test`, `zig build test --build-file
zigux/tests/phase7_build.zig --summary all`, and `make -C zigux phase7` as the
authoritative blocker-bearing bundle routes until that missing implementation
pair is restored; this shared note is not evidence that the full four-helper
packet currently passes on `master`.

`Documentation/zigux/phase7-string-helpers-slice.md` and
`zigux/tests/phase7_string_helpers_manifest.json` remain the dedicated owners of
the missing-helper record. Their `P7-L04` marker is now only a packet-local
historical helper-slice tag, while this shared note stays on `P7-Y05` and
should not be read as the active bootstrap-glue schedule owner for restoring
that missing implementation pair.

`zigux/tests/README.md` is also a shared-control reminder surface owned by
`P7-Y05`. Its Phase 7 entry list is not a helper-local proof packet: while
current `master` still lists the missing `zigux/tests/phase7_string_helpers.zig`
replay beside the parked shared build bundle, any tests-root truthfulness repair
that narrows that missing-pair wording or the blocked shared-build reminder
belongs here instead of `P7-L04`, `P7-L05`, `P7-L09`, or `P7-L13`.

`Documentation/zigux/phase7-helper-lane-sequencing.md` remains the dedicated
shared owner-map note for how `P7-Y05` stays on this shared control surface,
`P7-Y06` owns only the helper-lane map, and the helper-local slices keep their
own `P7-L*` lane keys.

The same parked packet also depends on the shared docs-root and scripts-root
Phase 5 no-sample reminders staying honest for `string_helpers`, `cmdline`,
`argv_split`, and `rbtree`. Current `master` now keeps the fuller parked packet
equally explicit from both `Documentation/zigux/README.md` and
`scripts/zigux/README.md`: the docs-root summary names the parked string-helpers
survey, manifest, sample-boundary, validator, build-wiring, Makefile, and
workflow surfaces beside the sibling Phase 7 slice surfaces, while the
scripts-root summary also keeps `Documentation/zigux/review-checklist.md`,
`Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, the parked
string-helpers survey and sample-boundary packet, the shared validator, the
build-wiring checker, the Makefile route, and the workflow-backed replay packet
visible beside the same parked helper bundle. Treat those docs-root and
scripts-root README syncs as landed shared context for this note rather than as
pending backlog.

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
`zigux/tests/phase7_build.zig` aligned around that same shared replay packet,
the parked string-helpers blocker, and the already-synced docs-root and
scripts-root packet so the parked `string_helpers`, `cmdline`, `argv_split`,
and `rbtree` bundle does not drift back toward per-slice ad hoc checks or a
false all-green shared status.

`make -C zigux phase7-validate`, the dedicated survey and sample-boundary
replays, `make -C zigux phase7-test`, and `make -C zigux phase7` remain the
Linux-style review routes for this shared control surface while the bundle stays
parked.

this note does not reopen `lib/string_helpers.zig`, `lib/cmdline.zig`,
`lib/argv_split.zig`, `lib/rbtree.zig`, or the missing string-helpers
implementation pair; it only keeps the already-landed shared control surface
truthful and the `P7-L04` ownership split explicit.
