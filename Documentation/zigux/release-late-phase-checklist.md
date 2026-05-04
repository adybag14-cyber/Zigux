# Zigux Late-Phase Release Checklist

This note turns the current late-phase Zigux release picture into one bounded PMO checklist. It exists so release review can confirm the active tranche order, gate commands, and non-goals in one place without reading any single phase note as global closure.

## Status

- `RELEASE_CHECKLIST_VERSION=1`
- `ACTIVE_RELEASE_SPAN=phase10-through-phase15`
- `GLOBAL_RELEASE_CLOSED=no`
- `PMO_READY_FOR_GLOBAL_CLOSE=no`
- `PHASE10_STATUS=active-not-closed`
- `PHASE12_STATUS=active-not-closed`
- `PHASE13_STATUS=active-helper-release-packet`
- `PHASE14_STATUS=boundary-only-smoke`
- `PHASE15_STATUS=governance-freeze-gate`
- `PHASE12_SHARED_VALIDATOR_PROMOTION=open`

## Sequence guardrails

1. Treat Phase 1 and Phase 2 as closed baseline tranches, not as the current late-phase release gate.
2. Read the active late-phase order as Phase 10, then Phase 12, then Phase 13, then Phase 14, then Phase 15.
3. Do not let the helper-first Phase 13 packet imply closure for the still-active Phase 10 or Phase 12 packets.
4. Do not let the Phase 14 smoke packet imply active subsystem delivery.
5. Do not let the Phase 15 governance gate be described as permission to reopen deep-core freeze areas.

## PMO checks

### Phase 10 closure packet

Verify all of these still stay explicit together:

- `Documentation/zigux/phase10-closure-evidence.md`
- `python3 scripts/zigux/check-phase10-closure-inventory.py`
- `python3 scripts/zigux/validate-phase10-closure.py`
- `python3 scripts/zigux/check-phase10-harness-coverage.py`
- `make -C zigux phase10-validate`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Release reading:
- Phase 10 remains active and bounded.
- Phase 10 still does not claim risky transport, lifecycle, or broader virtio closure.

### Phase 12 release-facing packet

Verify all of these still stay explicit together:

- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/phase12-cross-compile-smoke.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`
- `python3 scripts/zigux/check-phase12-release-readiness-packet.py`
- `python3 scripts/zigux/validate-phase12.py`
- `make -C zigux phase12-validate`
- `make -C zigux phase12`

Release reading:
- Phase 12 remains active and bounded.
- The approved non-native smoke set remains `x86_64-linux-musl`, `aarch64-linux-musl`, and `riscv64-linux-musl`.
- The public-read fallback split remains two commit-pinned artifacts and two shared-tree-only anchors.
- The dedicated PMO packet is live, but the broader shared validator still needs to mirror that packet directly.

### Phase 13 helper release packet

Verify all of these still stay explicit together:

- `Documentation/zigux/phase13-release-notes-survey.md`
- `python3 scripts/zigux/validate-phase13-release.py`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Release reading:
- Phase 13 remains helper-first.
- Phase 13 still does not imply deeper runtime, transport, or driver closure.

### Phase 14 boundary smoke packet

Verify all of these still stay explicit together:

- `Documentation/zigux/phase14-release-boundary-survey.md`
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- `python3 scripts/zigux/validate-phase14.py`
- `make -C zigux phase14-validate`
- `make -C zigux phase14`

Release reading:
- Phase 14 remains boundary-only.
- `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain study-only.
- `kernel/rcu/tree.c` and `net/core/skbuff.c` remain freeze-controlled rather than active delivery lanes.

### Phase 15 governance gate

Verify all of these still stay explicit together:

- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `python3 scripts/zigux/validate-phase15.py`
- `make -C zigux phase15-validate`
- `make -C zigux phase15`

Release reading:
- Phase 15 remains the freeze and governance gate.
- No deep-core reopening claim is release-valid until the governance packet says so explicitly.

## Handoff rule

Do not describe the active late-phase tranche as globally release-ready unless all of these remain true at the same time:

- Phase 10 stays active-not-closed.
- Phase 12 stays active-not-closed.
- Phase 13 stays helper-first.
- Phase 14 stays boundary-only.
- Phase 15 stays the freeze and governance gate.
- The still-open Phase 12 shared-validator promotion is either closed or still called out plainly as open.

## Next bounded PMO step

Promote the dedicated Phase 12 PMO release-readiness packet into the shared `scripts/zigux/validate-phase12.py` surface so the broader validator directly names the release-readiness survey, the dedicated PMO checker, the docs-root marker, and the PMO checklist marker that are already live elsewhere.
