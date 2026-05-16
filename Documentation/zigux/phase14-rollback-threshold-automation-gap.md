# Phase 14 Rollback-Threshold Automation Gap

## Status

- `PHASE14_ROLLBACK_THRESHOLD_GAP=present`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_KIND=makefile_selftest_coverage_drift`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_SCOPE=shared_smoke_packet_only`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_STATUS_BUCKET=study_only`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_OWNER=Repo Tooling Pod`
- verified against current `master` head `40f2a065b1c06d7ea621c1c0c388e6202b0b22b7`

## Why this gap note exists

The Phase 14 roadmap keeps `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`
in study-only boundary mode and keeps `net/core/skbuff.c` plus
`kernel/rcu/tree.c` under freeze-in-C governance. That makes shared smoke
automation truthfulness more valuable than new bridge growth.

Current `master` already publishes a newer shared-smoke packet than the
dedicated rollback-threshold checker exact-checks today:

- `Documentation/zigux/phase14-end-to-end-smoke-survey.md` now names
  `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` in the shared
  packet and says `zigux/Makefile` replays both
  `scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test` and
  `scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test`
  before the live checker invocations inside `make -C zigux phase14-validate`.
- `Documentation/zigux/phase14-release-boundary-survey.md` also lists
  `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` inside the shared
  smoke packet.
- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py` still exact-checks
  the older smaller `phase14-validate` subset and does not yet require those
  newer tests-root and rollback-checker self-test markers.

## Current bounded gap

The live shared packet has advanced, but the dedicated rollback-threshold
checker has not yet caught up to the newer self-test inventory it now describes.
That creates a narrow truthfulness gap: the packet can still overstate what the
rollback checker itself proves about `phase14-validate`.

## Next bounded fix

Refresh `scripts/zigux/check-phase14-rollback-threshold-sequencing.py` so its
exact Makefile expectations catch up to the current shared-smoke packet by
requiring:

- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test`
- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`
- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test`

Stop there. Do not widen into anchor-local bridge ownership, new Phase 14
delivery claims, or broader shared-smoke note churn while this gap remains
strictly checker-local.
