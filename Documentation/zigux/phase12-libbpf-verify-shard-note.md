# Phase 12 Libbpf Verify Shard Note

This note is the parked verify-shard companion for the shared Phase 12 libbpf packet.

It keeps a bounded note-owned replay boundary visible without turning the shared release packet into a focused libbpf replay route.

## Status

- `PHASE12_STATUS=parked`
- scope: keep the parked verify-shard boundary explicit for the helper-first `tools/lib/bpf/zigux_segments/` footing while the shared Phase 12 release packet still ships only the validator-first support bundle, the smoke-first complex-driver packet, the survey note, the snapshot checker, and the snapshot-backed reviewability anchor
- shared survey companion: `Documentation/zigux/phase12-libbpf-segment-survey.md`
- release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- shared heavy-consumer anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- shared complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`
- snapshot checker: `scripts/zigux/check-phase12-libbpf-snapshot.py`
- snapshot anchor: `zigux/tests/fixtures/phase12_libbpf_snapshot.json`

## Parked Boundary

- the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/verify.zig` stay recorded only through shared survey, parked, or anti-overlap notes until they land again on current `master`
- `tools/lib/bpf/zigux_segments/manifest.json` remains the legacy helper catalog for the parked libbpf packet rather than proof of a shipped shared replay route
- the snapshot anchor remains the truthful bounded signal here while those direct replay files stay absent from the shipped checkout
- the snapshot checker keeps that parked note-owned packet fail-closed around `Documentation/zigux/phase12-libbpf-segment-survey.md`, this verify-shard note, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` without promoting the parked replay files into the shipped smoke-first route
- the current validator-first support bundle remains separate: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and the reminder-only wrapper name `make -C zigux phase12-validate` keep the shared release packet fail-closed without turning this parked note into a second direct replay route, while the returned `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` wrappers stay evidence for the broader shared smoke-first packet rather than proof for this parked note by themselves

## Boundaries

- This note must not imply a focused libbpf-only replay, a cross-build replay, object-loader parity, relocation parity, or direct queue-routing delivery.
- `Documentation/zigux/freeze-map.md` remains the boundary owner for deeper queueing and transport anchors, so this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- The helper footing is real, but the shared Phase 12 smoke-and-test order is still narrower than the parked libbpf reviewability packet described only through those note-owned boundaries.

## Next Bounded Step

If the shared Phase 12 libbpf packet moves again, reread this note beside `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, then refresh only the narrowest shared wording or checker surface that drifts next before widening helper-local or loader-facing claims.
