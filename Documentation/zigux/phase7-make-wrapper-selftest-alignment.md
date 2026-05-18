# Phase 7 Make-Wrapper Selftest Alignment

This note keeps the shared Phase 7 make-wrapper review route honest.
## Status

  * `PHASE7_STATUS=parked`
  * `PHASE7_SLICE=make-wrapper-shared-control-surface`
  * `PHASE7_LANE_KEY=P7-Y05`

The current shared Phase 7 helper packet depends on `make -C zigux phase7-validate` replaying both the built-in self-tests and the direct repo-root checks for the same checker family:
  * `python3 scripts/zigux/validate-phase7.py --self-test`
  * `python3 scripts/zigux/validate-phase7.py`
  * `python3 scripts/zigux/check-phase7-make-wrapper.py --self-test`
  * `python3 scripts/zigux/check-phase7-make-wrapper.py`
  * `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test`
  * `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  * `python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test`
  * `python3 scripts/zigux/check-phase7-cmdline-packet.py`
  * `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`
  * `python3 scripts/zigux/check-phase7-argv-split-packet.py`
  * `python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test`
  * `python3 scripts/zigux/check-phase7-rbtree-parity.py`
  * `python3 scripts/zigux/check-phase7-build-wiring.py --self-test`
  * `python3 scripts/zigux/check-phase7-build-wiring.py`
The same parked packet also depends on the dedicated survey, sample-boundary, helper-local direct build-step, and direct summarized test routes staying explicit beside that shared validator surface:
  * `make -C zigux phase7-string-helpers-survey`
  * `make -C zigux phase7-string-helpers-sample-boundary`
  * `make -C zigux phase7-cmdline-survey`
  * `make -C zigux phase7-argv-split-survey`
  * `make -C zigux phase7-rbtree-survey`
  * `make -C zigux phase7-test`
  * `zig build phase7-string-helpers-test --build-file zigux/tests/phase7_build.zig --summary all`
  * `zig build phase7-cmdline-test --build-file zigux/tests/phase7_build.zig --summary all`
  * `zig build phase7-argv-split-test --build-file zigux/tests/phase7_build.zig --summary all`
  * `zig build phase7-rbtree-test --build-file zigux/tests/phase7_build.zig --summary all`
  * `zig build test --build-file zigux/tests/phase7_build.zig --summary all`
Current `master` keeps this shared Phase 7 control surface route-present rather than missing-path blocked: `Documentation/zigux/phase7-helper-lane-sequencing.md`, `Documentation/zigux/phase7-rbtree-slice.md`, `zigux/tests/README.md`, and `zigux/tests/phase7_build.zig` now all read back `zigux/tests/phase7_rbtree.zig` beside the other helper-local packets.
Treat `make -C zigux phase7-validate`, `make -C zigux phase7-test`, `zig build test --build-file zigux/tests/phase7_build.zig --summary all`, and `make -C zigux phase7` as shared bundle reminders rather than evidence that the full four-helper packet is green on current `master`; this shared note still does not claim a fully passing all-helper bundle.
Treat the direct `zig build phase7-*-test --build-file zigux/tests/phase7_build.zig --summary all` routes as route-present focused helper-local adapters exposed by the shared build graph rather than as a claim that the parked shared bundle is newly all-green.
The older string-helpers missing-pair reminder and the older missing-rbtree replay reminder are no longer the live blocker for this shared note. Keep helper-local owner routing under `Documentation/zigux/phase7-helper-lane-sequencing.md`; this shared note stays on `P7-Y05` and should not be read as the helper-local owner for reopening any already-landed helper packet.
`zigux/tests/README.md` is also a shared-control reminder surface owned by `P7-Y05`. Its Phase 7 entry list is not a helper-local proof packet: while current `master` now lists the landed `zigux/tests/phase7_rbtree.zig` replay beside the shared build bundle, any tests-root truthfulness repair that changes shared-build wording or the landed-packet reminder belongs here instead of `P7-L04`, `P7-L05`, `P7-L09`, or `P7-L13`.
`Documentation/zigux/phase7-helper-lane-sequencing.md` remains the dedicated shared owner-map note for how `P7-Y05` stays on this shared control surface, `P7-Y06` owns only the helper-lane map, and the helper-local slices keep their own `P7-L*` lane keys.
The same parked packet also depends on the shared docs-root and scripts-root Phase 5 no-sample reminders staying honest for `string_helpers`, `cmdline`, `argv_split`, and `rbtree`. Current `master` now keeps those README surfaces aligned around the route-present shared packet and the Phase 5 no-sample boundary. Treat future docs-root or scripts-root drift there as adjacent shared-reminder backlog, not as a currently open blocker recorded by this note.
For `string_helpers`, those shared no-sample reminders should also keep the ownership-focus packet explicit: first-NUL trimming and prefix skipping stop at the exported C-string boundary, exact-fit, terminator-only, and zero-capacity unescape destinations stay caller-owned, append-limited escape accounting stays inside caller storage, `kasprintfStrarray()` and `kfreeStrarray()` keep per-string allocations, the NULL-terminated pointer view, the shared zero-length sentinel, and teardown ownership explicit for caller-held results, and `memcpyAndPad()` plus `strreplace()` stay bounded by caller-provided destinations.
Keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase7-string-helpers-slice.md`, `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-argv-split-slice.md`, `Documentation/zigux/phase7-rbtree-slice.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-cmdline-packet.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/check-phase7-rbtree-parity.py`, `scripts/zigux/check-phase7-build-wiring.py`, `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, `lib/rbtree.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_manifest.json`, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase7_build.zig` aligned around that same shared replay packet, the landed route-present readback, and the shared no-sample packet so the parked `string_helpers`, `cmdline`, `argv_split`, and `rbtree` bundle does not drift back toward per-slice ad hoc checks or a false all-green shared status.
`make -C zigux phase7-validate`, the dedicated survey and sample-boundary replays, the direct `zig build phase7-*-test --build-file zigux/tests/phase7_build.zig --summary all` adapters, `make -C zigux phase7-test`, and `make -C zigux phase7` remain the Linux-style review routes for this shared control surface while the bundle stays parked.
