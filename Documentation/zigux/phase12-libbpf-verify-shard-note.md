# Phase 12 Libbpf Verify Shard Note

This note is the parked verify-shard companion for the shared Phase 12 libbpf packet.

It keeps a bounded verify-shard boundary visible without turning the shared release packet into a focused libbpf replay route.

## Status

- `PHASE12_STATUS=parked`
- scope: keep the directly readable `tools/lib/bpf/zigux_segments/verify.zig` compile-together shard explicit for the current helper-first footing while the shared Phase 12 release packet still ships the validator-first support bundle, the returned `phase12-validate` wrapper, the smoke-first complex-driver packet, the survey note, the snapshot checker, the snapshot-backed reviewability anchor, and the focused reviewability-lab build route
- shared survey companion: `Documentation/zigux/phase12-libbpf-segment-survey.md`
- release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- shared heavy-consumer anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- shared complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`
- snapshot checker: `scripts/zigux/check-phase12-libbpf-snapshot.py`
- lane-marker guard: `scripts/zigux/check-phase12-libbpf-lane-marker.py`
- snapshot anchor: `zigux/tests/fixtures/phase12_libbpf_snapshot.json`
- focused reviewability-lab build route: `zig build test --build-file zigux/tests/phase12_libbpf_reviewability_build.zig --summary all`

## Parked Boundary

- `tools/lib/bpf/zigux_segments/verify.zig` is directly readable on current `master`, but it stays a bounded compile-together shard for the currently readable helper subset rather than proof that the shared release packet adopted a focused libbpf replay route
- `zigux/tests/phase12_libbpf_reviewability_build.zig` now reruns the checked-in `zigux/tests/phase12_libbpf_reviewability.zig` gate as a focused compile-and-test lab without promoting that parked packet into the shared smoke-first route
- the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` stay recorded only through shared survey, parked, or anti-overlap notes until they land again on current `master`
- the current verify shard keeps the currently readable helper subset explicit through `cpu_mask.zig`, `logging.zig`, `online_cpu_routing.zig`, `perf_buffer_poll.zig`, `pin_path.zig`, and `type_names.zig` together with the directly readable sidecar family `cpu_mask_verify.zig`, `logging_verify.zig`, `online_cpu_routing_verify.zig`, `perf_buffer_poll_verify.zig`, `perf_buffer_ready_window.zig`, `pin_path_verify.zig`, `ready_buffer_attempt_verify.zig`, `ready_buffer_fd_verify.zig`, `ready_buffer_window_verify.zig`, and `type_names_verify.zig`
- `tools/lib/bpf/zigux_segments/manifest.json` remains directly readable on current `master` as the helper-first packet catalog, but it still is not proof that the shared release packet adopted a shipped libbpf replay route
- the snapshot anchor remains the truthful bounded signal here while those direct replay files stay absent from the shipped checkout
- the snapshot checker and lane-marker guard keep that parked note-owned packet fail-closed around `Documentation/zigux/phase12-libbpf-segment-survey.md`, this verify-shard note, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` without promoting the parked replay files into the shipped smoke-first route
- the current validator-first support bundle remains separate: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and the returned wrapper `make -C zigux phase12-validate` keep the shared release packet fail-closed without turning this parked note into a second direct replay route, while the returned `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` wrappers stay evidence for the broader shared smoke-first packet rather than proof for this parked note by themselves

## Boundaries

- This note must not imply a shared libbpf-only replay, a cross-build replay, object-loader parity, relocation parity, or direct queue-routing delivery.
- `Documentation/zigux/freeze-map.md` remains the boundary owner for deeper queueing and transport anchors, so this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- The helper footing is real, and the dedicated reviewability-lab build route is real, but the shared Phase 12 smoke-and-test order is still narrower than the parked libbpf reviewability packet described only through those note-owned boundaries.

## Next Bounded Step

If the shared Phase 12 libbpf packet moves again, reread this note beside `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `zigux/tests/phase12_libbpf_reviewability_build.zig`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, then refresh only the narrowest shared wording or checker surface that drifts next before widening helper-local or loader-facing claims.
