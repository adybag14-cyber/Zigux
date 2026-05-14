# Phase 12 Libbpf Verify Shard Note

This note records the bounded Phase 12 reviewability intent around `tools/lib/bpf/zigux_segments/verify.zig`.

## Status

- `PHASE12_STATUS=parked`
- `PHASE12_SLICE=libbpf-verify-shard`
- lane scope: keep the dedicated `zigux_segments/verify.zig` shard reviewable without widening into direct helper behavior changes, bridge implementation, queue routing, skeleton population, object loading, or verifier-facing relocation work
- current repo reality on `master`: the direct `phase12_libbpf_*` reviewability files, `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/verify.zig`, and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` are all materialized on current `master`, but the shared `scripts/zigux/check-build-only-phase12-surface.py` checker, `zigux/tests/phase12_build.zig`, and `zigux/Makefile` still stay intentionally narrower than that parked libbpf packet instead of treating those files as shipped required paths
- paired review packet:
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
  - `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
  - `scripts/zigux/check-build-only-phase12-surface.py`
  - `zigux/tests/phase12_build.zig`
  - `zigux/Makefile`

## Why this note exists

Earlier Phase 12 wording treated the libbpf packet as if it either shipped a dedicated `verify.zig` shard through the shared replay order or kept the whole reviewability packet absent, and that made it too easy for nearby runs to blur three different packets together:

- the deterministic helper snapshot
- the parked compile-together and reviewability shard already materialized on current `master`
- the heavier bridge-local, queue-routing, object-model, and loader-risk buckets

This note keeps that split explicit while also recording the current narrower shipped replay reality.

## Current Ownership

The intended `verify.zig` shard is materialized on current `master`, but it still belongs to a reviewability-only packet rather than to the shipped Phase 12 smoke-first replay order.

- the current shard imports from `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `file_path_handle_bridge.zig`, and `perf_buffer_poll.zig`
- the current packet also includes the directly coupled `zigux/tests/phase12_libbpf_segments.zig` survey gate, `zigux/tests/phase12_libbpf_reviewability.zig` reviewability gate, and `tools/lib/bpf/zigux_segments/manifest.json` catalog
- today, the honest repo-reality signal stays split: those reviewability files are present on current `master`, while the shared Phase 12 checker still only enforces the shipped docs, workflow, Makefile, and `virtio_scsi` plus starter-present `virtio_net` smoke-first build packet
- that means this note must stay a parked owner map until the shared replay packet explicitly adopts the verify shard, not until those files merely become readable again on `master`

## Review Rules

- treat this note as a bounded owner map for the verify shard, not as proof that the shard is part of the shipped replay order on `master`, and not as proof of direct procfs reads, bpffs opens, token creation, online-CPU routing, skeleton population, object loading, or verifier-facing relocation work
- keep the verify-shard wording aligned with the same shared build-only checker packet, while staying clear that the checker does not yet treat the direct `phase12_libbpf_*` replay files, `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/verify.zig`, or `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` as shipped required paths
- the direct `phase12_libbpf_*` reviewability files, `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/verify.zig`, and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` should stay described as present parked reviewability paths rather than as absent files or shipped replay evidence
- the snapshot anchor remains a truthful bounded signal here because it keeps the same packet reviewable even while the shared Phase 12 smoke-first route still omits that packet
- when rechecking this parked packet, reread `zigux/tests/fixtures/phase12_libbpf_snapshot.json` first and treat its `surveyed_commit` plus the live `zigux_segments` reviewability files, the survey note, and the anti-overlap notes as the truthful bounded signal rather than as proof that the shared replay order already ships that packet
- preserve the split between the deterministic helper packet, the compile-together verify shard, the bridge-local helper destination, and the later object-model and loader-risk buckets instead of collapsing them back into one vague `libbpf` bucket

## Non-goals

This note does not claim:

- that `tools/lib/bpf/zigux_segments/verify.zig` is part of the shipped shared replay order on `master`
- direct procfs or bpffs interaction
- pinned-object reopen flow or descriptor ownership side effects
- online-CPU routing or callback delivery
- `bpf_object`, `bpf_map`, or `bpf_program` model parity
- skeleton population
- ELF collection, object loading, or load-time verifier interaction
- BTF relocation or program-load coverage

## Gates

1. `python3 scripts/zigux/check-build-only-phase12-surface.py`
2. reread `zigux/tests/fixtures/phase12_libbpf_snapshot.json` first and treat its `surveyed_commit` plus the live `phase12_libbpf_*` reviewability files, `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/verify.zig`, and the paired survey-plus-anti-overlap notes as the truthful bounded signal here while those files remain outside the shared shipped replay order
3. treat `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` as shared Phase 12 smoke-first anchors only; they keep the published `virtio_scsi` plus starter-present `virtio_net` packet reviewable today but do not by themselves prove that the parked libbpf verify shard has joined the shipped replay order

## Next Bounded Step

If this lane reopens, reread `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `zigux/tests/phase12_libbpf_manifest.json`, and `zigux/tests/phase12_libbpf_reviewability.zig` against the current parked-but-materialized verify shard packet. Prefer the next one-file truthfulness or reviewability-gate repair that keeps present Phase 12 libbpf verify-shard files from being described as absent while still avoiding any claim that they are shipped release-packet surfaces before the shared build route adopts them.