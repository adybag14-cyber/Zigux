# Phase 14 Smoke Coverage Evidence - 2026-05-29

This note records the `P14-L03` end-to-end smoke lane readback for current `master` on 2026-05-29. It is evidence-only: it does not claim new Phase 14 runtime parity, wrapper ownership, or a broader smoke route.

## Scope

- lane: `P14-L03`
- roadmap phase: Phase 14, core-adjacent bounded internals
- roadmap posture: wrapper-first or study-only for `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, `net/core/skbuff.c`, and `kernel/rcu/tree.c`
- verification mode: authenticated GitHub contents readback through the repository connector; direct raw `raw.githubusercontent.com` fetch from the runtime still failed with a CONNECT tunnel `403`, so no full checkout or Zig replay was available in this run

## Readable Smoke Packet Evidence

The following current-`master` files were directly readable through the contents path during this run:

- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, blob `83793609ada351c5c46b8f2b0b3e2d22b3c59c99`
- `scripts/zigux/check-phase14-shared-smoke-route.py`, blob `f2bb6d69a9ba2051fc91ee20fa965f8635a6e7c1`
- `scripts/zigux/validate-phase14.py`, blob `c1f45e1b6029c5435c0bcc13b1e45dff9d86d246`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`, blob `4fdee52d122e7d2651e5f51de3b80d8b4e5c1051`
- `zigux/Makefile`, blob `47952e68dfa7f1579860db9b6bed6a6c7fd361d9`
- `.github/workflows/zigux-bootstrap.yml`, blob `5bdb136b8b6710c08c19566879d5a9da42b63445`
- `kernel/workqueue_bridge.zig`, blob `d30efc0552a2189121808bef20147b673deb6e33`
- `zigux/tests/phase14_workqueue_reviewability.zig`, blob `0adbeb90e0ee0baa7fc22973784d840bb26cf366`
- `zigux/tests/phase14_ring_buffer_survey.zig`, blob `d012d655d508e1bf5d2d811bfede889d4b1f85c4`
- `zigux/tests/phase14_end_to_end_smoke_survey.zig`, blob `1e448021d674da9e08aab9d1c6f4166486b2fd21`
- `zigux/tests/phase14_skbuff_bridge.zig`, blob `5f881b6503423a2813d7849b9e97beadfc26ee08`

The last two entries are important drift evidence for this lane: the older shared smoke survey still lists `zigux/tests/phase14_end_to_end_smoke_survey.zig` and `zigux/tests/phase14_skbuff_bridge.zig` among unrecovered executable packet members, but both returned through the same contents readback mode in this run.

## Still Missing Through Exact Contents Readback

The following files still returned GitHub contents-path `404` in this run:

- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_rcu_tree_survey.zig`
- `net/core/skbuff_bridge.zig`

This keeps the end-to-end smoke lane partial. The returned end-to-end and skbuff test readback should not be treated as a full Phase 14 executable packet until the build-file route and the remaining anchor-local companions are readable in the same mode.

## Route Coverage Observed

Current `zigux/Makefile` blob `47952e68dfa7f1579860db9b6bed6a6c7fd361d9` lists `phase14-validate` in `.PHONY`, but the fetched body ends after the Phase 12 route family and the line-range readback did not show a `phase14-validate:` recipe. Current `.github/workflows/zigux-bootstrap.yml` blob `5bdb136b8b6710c08c19566879d5a9da42b63445` still contains `run: make -C zigux phase14-validate`.

That means the current smoke evidence should be read conservatively: the workflow still names the Phase 14 validation route, but this lane did not prove that current `zigux/Makefile` executes the Phase 14 checker bundle through a recipe body. A future lane should reconcile the shared smoke survey, manifest, and checker expectations with the exact Makefile body before claiming `make -C zigux phase14-validate` as an active replay gate.

## Manifest Evidence

`zigux/tests/phase14_end_to_end_smoke_manifest.json` blob `4fdee52d122e7d2651e5f51de3b80d8b4e5c1051` still records:

- `surveyed_on`: `2026-05-25`
- `validation_gate`: `make -C zigux phase14-validate`
- `smoke_commands`: `["make -C zigux phase14-validate"]`
- `smoke_shard_commands`: `["zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"]`
- `phase14_make_target_present`: `true`
- `phase14_make_smoke_target_present`: `false`
- `workflow_runs_phase14_validate`: `true`
- `workflow_runs_phase14_build`: `false`
- `workflow_runs_phase14_smoke_shard`: `false`

Because `zigux/tests/phase14_build.zig` still returns `404` through this lane's exact contents path, the raw build-file shard remains reminder vocabulary rather than verified local replay evidence in this run.

## Next Bounded Step

Keep `P14-L03` on smoke-coverage truthfulness. The next useful repair is to update the shared smoke survey or checker packet so it records the returned `phase14_end_to_end_smoke_survey.zig` and `phase14_skbuff_bridge.zig` readback, while fail-closing on the missing Makefile `phase14-validate:` recipe if that recipe is still absent on the next current-`master` readback.
