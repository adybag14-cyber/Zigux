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
- Keep the shared libbpf packet explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and the still-present `zigux/tests/fixtures/phase12_libbpf_snapshot.json` snapshot anchor, while treating the direct `phase12_libbpf_*` replay files, `tools/lib/bpf/zigux_segments/verify.zig`, and `tools/lib/bpf/zigux_segments/manifest.json` as parked note-owned boundaries until they land again on current `master`.
- Keep the shared validator-first then smoke-first order fixed unless a new shipped route lands first:
  1. `make -C zigux phase12-validate`
  2. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
  3. `make -C zigux phase12-smoke`
  4. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
  5. `make -C zigux phase12`
- If `zig` is unavailable on `PATH`, reuse that same validator-first then smoke-first order only through the shipped Make routes with `ZIG=<attached-zig-path>`: `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `make -C zigux phase12`, instead of inventing a focused libbpf-only fallback entrypoint.
- Keep the degraded-workflow support bundle explicit beside that same order too:
  - `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
  - `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`
  - `make -C zigux phase12-validate`

## Anti-Overlap Rules
- Shared-packet follow-through here should prefer one-file truthfulness repairs in `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, or `scripts/zigux/check-build-only-phase12-surface.py` before reopening helper-local behavior.
- Keep the shared fallback split explicit here too: only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned fallback artifacts, while `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors.
- Keep the direct `phase12_libbpf_*` replay files, `tools/lib/bpf/zigux_segments/verify.zig`, and `tools/lib/bpf/zigux_segments/manifest.json` explicit as parked note-owned boundaries while staying clear that they are still outside the shared shipped replay order until they land again on current `master`.
- Leave driver-local replay and survey evolution to the separate complex-driver companion and the concrete `nvme_pci`, `virtio_net`, or `virtio_scsi` packet that changes.
- The older helper-first segment footing remains a Phase 12 heavy-consumer packet on current `master`; do not recast it as lingering Phase 8 work now that the roadmap and docs root already place it in the shared Phase 12 release packet.

## Boundaries
- This note must not imply `skeleton.zig`, object-loader parity, relocation parity, direct queue-routing delivery, or other unshipped libbpf runtime surfaces.
- Current `master` now ships the validator-first support bundle through `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, and `make -C zigux phase12-validate`, but there is still no focused-libbpf-only replay or cross-build replay, so this note must keep that support bundle distinct from the smoke-first shared replay order.
- `Documentation/zigux/freeze-map.md` remains the boundary owner for deeper queueing and transport anchors, so this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.

## Next Bounded Step
If this lane reopens soon, reread `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` against the current validator-first then smoke-first Phase 12 packet, the same dedicated support checker, the same two-versus-two fallback split, and the same present-versus-shipped verify-shard boundary before widening helper-local or loader-facing claims. Current `master` already keeps those shared wording surfaces aligned around that bounded packet, so the next honest same-lane follow-through is to leave this owner map parked unless that shared release packet, the dedicated support checker, the fallback split, or the parked verify-shard boundary moves first rather than reopening helper-local, scripts-root, or tests-root churn preemptively.
