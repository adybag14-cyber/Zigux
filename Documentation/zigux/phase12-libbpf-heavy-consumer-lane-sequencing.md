# Phase 12 Libbpf Heavy-Consumer Lane Sequencing

This note is the anti-overlap companion for the shared Phase 12 libbpf heavy-consumer packet.

It keeps the helper-first `tools/lib/bpf/zigux_segments/` footing reviewable inside the shared Phase 12 release packet without collapsing into object-loader, relocation, queue-routing, or direct runtime delivery claims.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_LANE=libbpf-heavy-consumer-shared-release-packet`
- scope: shared release-planning truthfulness, fallback wording, smoke-first replay reminders, and anti-overlap guidance for the bounded libbpf survey packet plus the parked verify-shard boundary already documented on current `master`
- release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
- closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`

## Lane Scope
- Keep the shared libbpf packet explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and the still-present `zigux/tests/fixtures/phase12_libbpf_snapshot.json` snapshot anchor, while treating the parked `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `zigux/tests/phase12_libbpf_manifest.json`, `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`, `tools/lib/bpf/zigux_segments/verify.zig`, and `tools/lib/bpf/zigux_segments/manifest.json` paths as publicly present reviewability files that still remain outside the shared shipped replay order until `scripts/zigux/check-build-only-phase12-surface.py`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile` adopt them explicitly.
- Keep the shared replay order fixed unless a new shipped route lands first:
  1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
  2. `make -C zigux phase12-smoke`
  3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
  4. `make -C zigux phase12`
- If `zig` is unavailable on `PATH`, reuse that same order only through the shipped Make routes with `ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only fallback entrypoint.
- Keep the degraded-workflow checker pair explicit beside that same order too:
  - `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
  - `python3 scripts/zigux/check-build-only-phase12-surface.py`

## Anti-Overlap Rules
- Shared-packet follow-through here should prefer one-file truthfulness repairs in `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, or `scripts/zigux/check-build-only-phase12-surface.py` before reopening helper-local behavior.
- Keep the shared fallback split explicit here too: only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned fallback artifacts, while `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors.
- Keep the publicly-present-parked-file boundary and reviewability wording explicit so the release-facing libbpf packet does not collapse back into manifest-only prose, does not hide the still-shipped snapshot anchor, and does not wrongly treat those parked reviewability files as either absent or shipped current-`master` surfaces.
- Leave driver-local replay and survey evolution to the separate complex-driver companion and the concrete `nvme_pci`, `virtio_net`, or `virtio_scsi` packet that changes.
- The older helper-first segment footing remains a Phase 12 heavy-consumer packet on current `master`; do not recast it as lingering Phase 8 work now that the roadmap and docs root already place it in the shared Phase 12 release packet.

## Boundaries
- This note must not imply `skeleton.zig`, object-loader parity, relocation parity, direct queue-routing delivery, or other unshipped libbpf runtime surfaces.
- There is still no shipped shared `scripts/zigux/validate-phase12.py`, `check-phase12-*.py`, focused-libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route on current `master`.
- `Documentation/zigux/freeze-map.md` remains the boundary owner for deeper queueing and transport anchors, so this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.

## Next Bounded Step
If this lane reopens soon, prefer the next one-file shared wording or review-surface sync that keeps `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` aligned with the current smoke-first Phase 12 packet, the same checker pair, the same two-versus-two fallback split, and the same publicly visible parked verify-shard boundary before widening helper-local or loader-facing claims.