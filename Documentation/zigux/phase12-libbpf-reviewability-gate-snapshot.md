# Phase 12 Libbpf Reviewability Gate Snapshot

This note records the bounded `P12-L18` follow-up for the Phase 12 libbpf deterministic artifact snapshotting lane.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_SLICE=libbpf-reviewability-gate-snapshot`
- `PHASE12_LANE_KEY=P12-L18`
- scope: keep the snapshot fixture's reviewability-gate evidence tied to the checked-in `zigux/tests/phase12_libbpf_reviewability.zig` gate without claiming that the parked direct `phase12_libbpf_*` replay files are part of the shipped smoke-first Phase 12 route

## Why this note exists
`zigux/tests/fixtures/phase12_libbpf_snapshot.json` now carries explicit `verification_evidence.reviewability_gate` metadata for `zigux/tests/phase12_libbpf_reviewability.zig`. That metadata is only useful if it keeps proving the actual reviewability gate still parses the primary snapshot's `surveyed_commit` field and asserts that it remains a lowercase 40-character hex SHA.

The bounded product gap was not a new libbpf helper or a broader Phase 12 replay claim. It was a deterministic snapshot evidence gap: the fixture could name the reviewability gate while a future edit loosened the gate, changed the referenced path, or let the recorded gate blob drift without an immediate fail-closed check.

## Guardrail
`scripts/zigux/check-phase12-libbpf-reviewability-gate-snapshot.py` is intentionally narrow. It checks:
- the primary libbpf snapshot fixture exists
- `verification_evidence.reviewability_gate.path` is exactly `zigux/tests/phase12_libbpf_reviewability.zig`
- the recorded reviewability-gate blob is a lowercase 40-character SHA and matches the current Git blob of the reviewability gate
- the evidence string still states that the primary snapshot replay parses `surveyed_commit` and asserts that it is a lowercase 40-character hex SHA
- the reviewability gate still contains the exact snapshot-anchor test name, the `surveyed_commit` fixture field, the `isHexSha(fixture.surveyed_commit)` assertion, the primary snapshot fixture path, and the current snapshot checker blob assertion

## Boundaries
This note does not claim:
- direct Zig parity for `tools/lib/bpf/libbpf.c`
- that `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` has landed
- that the parked direct `phase12_libbpf_*` replay files are wired into `zigux/tests/phase12_build.zig`
- that `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, or `make -C zigux phase12` exercise the parked libbpf reviewability packet directly

## Validation
Rerun the focused guard before treating this evidence as current:
- `python3 scripts/zigux/check-phase12-libbpf-reviewability-gate-snapshot.py --self-test`
- `python3 scripts/zigux/check-phase12-libbpf-reviewability-gate-snapshot.py`

Then keep the broader validator-side packet in its existing order:
- `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`
- `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`
- `python3 scripts/zigux/validate-phase12.py`
- `make -C zigux phase12-validate`

## Next Bounded Step
If this lane reopens, first reread `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/phase12_libbpf_reviewability.zig`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, and `scripts/zigux/check-phase12-libbpf-reviewability-gate-snapshot.py` together. Prefer another one-file fail-closed evidence repair over adding more libbpf helper scope or promoting the parked replay packet into the shared smoke-first route.
