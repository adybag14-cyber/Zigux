# Phase 7 Make-Wrapper Selftest Alignment

This note keeps the shipped Phase 7 make-wrapper packet reviewable on current `master`.

## Status

- `PHASE7_SHARED_STATUS=parked`
- `PHASE7_SHARED_PACKET=leaf-helper-make-wrapper-selftest-alignment`
- scope: confirm the Linux-style `make -C zigux` routes and the dedicated checker self-tests still point at the same bounded Phase 7 helper family
- current family: `string_helpers`, `cmdline`, `argv_split`, and `rbtree`

## Shared packet

Current `master` keeps the shared Phase 7 packet under these review surfaces:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase7.py`
- `scripts/zigux/check-phase7-make-wrapper.py`
- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
- `scripts/zigux/check-phase7-argv-split-packet.py`
- `scripts/zigux/check-phase7-rbtree-parity.py`
- `scripts/zigux/check-phase7-build-wiring.py`
- `zigux/tests/README.md`
- `zigux/tests/phase7_build.zig`
- `zigux/Makefile`

The direct helper-local and dedicated survey surfaces that remain inside that same bounded packet are:

- `lib/string_helpers.zig`
- `zigux/tests/phase7_string_helpers.zig`
- `zigux/tests/phase7_string_helpers_survey.zig`
- `zigux/tests/phase7_string_helpers_manifest.json`
- `zigux/tests/phase7_string_helpers_sample_boundary.zig`
- `lib/cmdline.zig`
- `zigux/tests/phase7_cmdline.zig`
- `zigux/tests/phase7_cmdline_survey.zig`
- `zigux/tests/phase7_cmdline_manifest.json`
- `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`
- `lib/argv_split.zig`
- `zigux/tests/phase7_argv_split.zig`
- `zigux/tests/phase7_argv_split_survey.zig`
- `zigux/tests/phase7_argv_split_manifest.json`
- `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
- `lib/rbtree.zig`
- `zigux/tests/phase7_rbtree.zig`
- `zigux/tests/phase7_rbtree_survey.zig`
- `zigux/tests/phase7_rbtree_manifest.json`
- `zigux/tests/fixtures/phase7_rbtree.json`
- `zigux/tests/fixtures/phase7_rbtree_c_harness.c`

## Alignment rules

The current make-wrapper packet stays honest when these routes continue to agree on the same bounded family:

1. `make -C zigux phase7-validate` reruns the shared validator-first route.
2. That validator-first route keeps the dedicated checker self-tests explicit:
   - `python3 scripts/zigux/validate-phase7.py --self-test`
   - `python3 scripts/zigux/check-phase7-make-wrapper.py --self-test`
   - `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test`
   - `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`
   - `python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test`
   - `python3 scripts/zigux/check-phase7-build-wiring.py --self-test`
3. `make -C zigux phase7` remains the Linux-style replay route for that same parked helper packet.
4. `make -C zigux phase7` continues to flow through `phase7-validate` and `phase7-test` instead of introducing a second shared inventory surface.
5. The shared packet remains the four landed Phase 7 helper families only; it does not imply an extra standalone `samples/zigux/*rbtree*` or other Phase 5 sample.

## Current boundary

This note is intentionally about wrapper and self-test alignment only.

It does not add a new helper-local parity claim, and it does not widen the packet into an unshipped `check-phase7-build-inventory.py` or `phase7_build_inventory.json` surface.

## Next bounded step

Keep this note parked unless a future Phase 7 shared-surface pass changes one of the shipped `make -C zigux phase7-validate` or `make -C zigux phase7` routes, removes one of the dedicated checker self-tests from that packet, changes the landed four-helper family named above, or closes the still-pending docs-root shared-surface truthfulness pass around the broad Phase 7 reminder in `Documentation/zigux/README.md`, starting with the cmdline-manifest wording that the other Phase 7 shared surfaces already keep explicit.
