# Phase 12 Libbpf Heavy-Consumer Lane Sequencing

This note is the anti-overlap companion for the shared Phase 12 libbpf heavy-consumer packet.

It keeps the helper-first `tools/lib/bpf/zigux_segments/` footing reviewable inside the shared Phase 12 release packet without collapsing into object-loader, relocation, queue-routing, or direct runtime delivery claims.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_LANE=libbpf-heavy-consumer-shared-release-packet`
- scope: shared release-planning truthfulness, fallback wording, smoke-first replay reminders, the focused reviewability-lab rerun, and anti-overlap guidance for the bounded libbpf survey packet plus the parked verify-shard boundary, the checked-in reviewability gate, and the helper-local determinism companion already documented on current `master`
- release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
- closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`

## Lane Scope

- Keep the shared libbpf packet explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, the still-present `zigux/tests/fixtures/phase12_libbpf_snapshot.json` snapshot anchor, the checked-in `zigux/tests/phase12_libbpf_reviewability.zig` gate, the focused rerun handle `zigux/tests/phase12_libbpf_reviewability_build.zig`, and the helper-local `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` determinism companion, while treating the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` as parked note-owned boundaries until they land again on current `master`, while keeping `tools/lib/bpf/zigux_segments/verify.zig` explicit as the directly readable compile-together shard for the current helper footing, and while keeping `tools/lib/bpf/zigux_segments/manifest.json` explicit as the directly readable helper-first packet catalog rather than as proof of a shipped shared replay route.
- Keep the shared validator-first then smoke-first order fixed unless a new shipped route lands first:
  1. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`
  2. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
  3. shipped wrapper evidence on current `master`: `make -C zigux phase12-smoke`
  4. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
  5. shipped wrapper evidence on current `master`: `make -C zigux phase12-test`
  6. shipped wrapper evidence on current `master`: `make -C zigux phase12`
- Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on current `master`, so keep `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` explicit here as shipped wrapper evidence and keep the directly readable support bundle explicit through `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py`, `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `scripts/zigux/validate-phase12.py` beside the returned smoke-and-test wrappers.
- The shipped lane-marker guard now sits beside that same support bundle too: `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py --self-test` and `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py` keep the parked survey lane-key, manifest, and verify-shard boundary fail-closed beside the snapshot checker and shared validator entrypoint without turning the shared release packet into a focused libbpf replay route.
- The shipped heavy-consumer guard now sits beside that same support bundle too: `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test` and `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the parked helper-first packet fail-closed beside the snapshot checker and shared validator entrypoint without turning the shared release packet into a focused libbpf replay route.
- The focused reviewability-lab rerun now sits beside that same support bundle too: `zig build test --build-file zigux/tests/phase12_libbpf_reviewability_build.zig --summary all` reruns the checked-in reviewability gate without promoting it into the shared Phase 12 smoke-first packet.
- If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the shipped attached-toolchain reruns `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only fallback entrypoint.
- Keep the degraded-workflow support bundle explicit beside that same order too:
  - `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
  - `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`
  - `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`
  - `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py --self-test`
  - `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py`
  - `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test`
  - `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`
  - `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`
  - `scripts/zigux/validate-phase12.py`
  - shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`

## Anti-Overlap Rules

- Shared-packet follow-through here should prefer one-file truthfulness repairs in `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, or `scripts/zigux/check-build-only-phase12-surface.py` before reopening helper-local behavior.
- Keep the shared fallback split explicit here too: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the one commit-pinned direct replay fallback artifact, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the current-master gap-inventory companion, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors.
- Keep the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` explicit as parked note-owned boundaries, while staying clear that `tools/lib/bpf/zigux_segments/verify.zig` remains directly readable current-master helper footing, that `tools/lib/bpf/zigux_segments/manifest.json` remains directly readable as the helper-first packet catalog rather than shared replay proof, that `zigux/tests/fixtures/phase12_libbpf_snapshot.json` stays the parked visibility anchor, that `zigux/tests/phase12_libbpf_reviewability.zig` stays the checked-in reviewability gate for the same parked packet, that `zigux/tests/phase12_libbpf_reviewability_build.zig` stays a focused rerun surface for that same parked packet rather than a shared packet promotion, and that `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` stays the helper-local determinism companion rather than a shipped shared replay route.
- Leave driver-local replay and survey evolution to the separate complex-driver companion and the concrete `nvme_pci`, `virtio_net`, or `virtio_scsi` packet that changes.
- The older helper-first segment footing remains a Phase 12 heavy-consumer packet on current `master`; do not recast it as lingering Phase 8 work now that the roadmap and docs root already place it in the shared Phase 12 release packet.

## Boundaries

- This note must not imply `skeleton.zig`, object-loader parity, relocation parity, direct queue-routing delivery, or other unshipped libbpf runtime surfaces.
- Current `master` keeps the directly readable validator-first support bundle explicit through `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `scripts/zigux/validate-phase12.py`, while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` now stay shipped wrapper evidence; the focused reviewability-lab rerun now exists, but it remains outside the shared smoke-first packet and there is still no shared libbpf-only replay or cross-build replay, so this note must keep that support bundle, the checked-in reviewability gate, the focused rerun surface, and the helper-local determinism companion distinct from the smoke-first shared replay order.
- `Documentation/zigux/freeze-map.md` remains the boundary owner for deeper queueing and transport anchors, so this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.

## Next Bounded Step

If this lane reopens soon, reread `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` against the current validator-first then smoke-first Phase 12 packet, the same dedicated support checker set, the same two-versus-two fallback split, the same snapshot anchor, the same checked-in reviewability gate, the focused rerun surface at `zigux/tests/phase12_libbpf_reviewability_build.zig`, the same helper-local determinism companion, and the same present-versus-shipped verify-shard boundary before widening helper-local or loader-facing claims.

Current `master` already keeps those shared wording surfaces aligned around that bounded packet, so the next honest same-lane follow-through is to leave this owner map parked unless that shared release packet, the dedicated support checker set, the fallback split, the focused rerun surface, or the parked verify-shard boundary moves first rather than reopening helper-local, scripts-root, or tests-root churn preemptively.
