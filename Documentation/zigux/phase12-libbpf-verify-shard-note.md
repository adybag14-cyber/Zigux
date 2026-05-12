# Phase 12 Libbpf Verify Shard Note

This note records the bounded Phase 12 reviewability intent around `tools/lib/bpf/zigux_segments/verify.zig`.

## Status

- `PHASE12_STATUS=parked`
- `PHASE12_SLICE=libbpf-verify-shard`
- lane scope: keep the dedicated `zigux_segments/verify.zig` shard reviewable when it is actually present, without widening into direct helper behavior changes, bridge implementation, queue routing, skeleton population, object loading, or verifier-facing relocation work
- current repo reality on `master`: the parked libbpf verify packet is publicly present again but still outside the shipped Phase 12 replay order. Public-tree readback now shows `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/manifest.json`, `zigux/tests/phase12_libbpf_reviewability.zig`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_manifest.json`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` on current `master`, while the shared `scripts/zigux/check-build-only-phase12-surface.py` checker still stays intentionally narrower than that parked shard instead of treating those files as shipped required paths
- paired review packet:
  - `tools/lib/bpf/zigux_segments/verify.zig`
  - `zigux/tests/phase12_libbpf_reviewability.zig`
  - `zigux/tests/phase12_libbpf_manifest.json`
  - `zigux/tests/fixtures/phase12_libbpf_snapshot.json`
  - `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
  - `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
  - `scripts/zigux/check-build-only-phase12-surface.py`
  - `zigux/tests/phase12_build.zig`
  - `zigux/Makefile`

## Why this note exists

Earlier Phase 12 wording treated the libbpf packet as if it still shipped a dedicated `verify.zig` shard, and that made it too easy for nearby runs to blur three different packets together:

- the deterministic helper snapshot
- the shared compile-together and reviewability shard
- the heavier bridge-local, queue-routing, object-model, and loader-risk buckets

This note now keeps that split explicit while also recording the current narrower repo reality.

## Current Ownership

The intended `verify.zig` shard is a reviewability-only packet, and current `master` now exposes the verify, manifest, reviewability, and survey-gate source files again through public-tree readback, but the shared release packet still keeps them parked outside the shipped replay order.

- the earlier note shape assumed imports from `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `file_path_handle_bridge.zig`, and `perf_buffer_poll.zig`
- the earlier note shape also assumed a focused `std.testing.refAllDecls` compile-reachability shard plus the directly coupled `zigux/tests/phase12_libbpf_reviewability.zig` gate
- today, the honest repo-reality signal is publicly visible but still parked: current `master` shows `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/manifest.json`, `zigux/tests/phase12_libbpf_reviewability.zig`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_manifest.json`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, while the shared Phase 12 checker still only enforces the shipped docs, workflow, Makefile, and `virtio_scsi` smoke-first build packet
- that means this note must stay a parked owner map until the shared replay packet explicitly adopts the verify shard, not until the files merely appear on current `master`

## Review Rules

- treat this note as a bounded owner map for the verify shard, not as proof that the shard is part of the shipped replay order on `master`, and not as proof of direct procfs reads, bpffs opens, token creation, online-CPU routing, skeleton population, object loading, or verifier-facing relocation work
- keep the parked verify-shard wording aligned with the same shared build-only checker packet, while staying clear that the checker does not yet treat the publicly present libbpf reviewability files as shipped required paths
- treat the public verify-shard file set plus snapshot anchor as the truthful bounded signal here: the parked compile-together packet is visible again, but it does not by itself move into the shipped smoke-first replay order
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
2. treat the current publicly visible parked verify-shard file set plus snapshot anchor as the truthful bounded signal until the shared checker and smoke-first replay packet explicitly adopt those files
3. treat `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` as shared Phase 12 smoke-first anchors only; they keep the published `virtio_scsi` packet reviewable today but do not by themselves prove that the parked libbpf verify shard has joined the shipped replay order

## Next Bounded Step

If this lane reopens, reread `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` against the current publicly visible parked verify-shard packet before choosing another shared reminder repair. Prefer the next one-file scripts-root or tests-root truthfulness update that stops parked Phase 12 libbpf verify-shard files from being presented as either absent files or shipped release-packet surfaces before widening into helper behavior or blocked object-model work.