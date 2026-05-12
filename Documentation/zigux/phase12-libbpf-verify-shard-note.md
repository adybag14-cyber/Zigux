# Phase 12 Libbpf Verify Shard Note

This note records the bounded Phase 12 reviewability intent around `tools/lib/bpf/zigux_segments/verify.zig`.

## Status

- `PHASE12_STATUS=parked`
- `PHASE12_SLICE=libbpf-verify-shard`
- lane scope: keep the dedicated `zigux_segments/verify.zig` shard reviewable now that it is present on current `master`, without widening into direct helper behavior changes, bridge implementation, queue routing, skeleton population, object loading, or verifier-facing relocation work
- current repo reality on `master`: the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/verify.zig` are present on head as reviewability evidence, while the shared `scripts/zigux/check-build-only-phase12-surface.py` checker still stays intentionally narrower than that parked shard instead of treating those files as shipped required paths
- paired review packet:
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

This note now keeps that split explicit while also recording the current narrower shipped replay reality.

## Current Ownership

The intended `verify.zig` shard is a reviewability-only packet, and the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/verify.zig` are present on current `master` even though the shared replay packet still does not adopt them.

- the earlier note shape assumed imports from `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `file_path_handle_bridge.zig`, and `perf_buffer_poll.zig`
- the earlier note shape also assumed a focused `std.testing.refAllDecls` compile-reachability shard plus the directly coupled `zigux/tests/phase12_libbpf_reviewability.zig` gate
- today, the honest repo-reality signal stays split: the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/verify.zig` are present on head as reviewability evidence, while the shared Phase 12 checker still only enforces the shipped docs, workflow, Makefile, and `virtio_scsi` smoke-first build packet
- that means this note must stay a parked owner map until the shared replay packet explicitly adopts the verify shard, not until those files merely become readable again on `master`

## Review Rules

- treat this note as a bounded owner map for the verify shard, not as proof that the shard is part of the shipped replay order on `master`, and not as proof of direct procfs reads, bpffs opens, token creation, online-CPU routing, skeleton population, object loading, or verifier-facing relocation work
- keep the verify-shard wording aligned with the same shared build-only checker packet, while staying clear that the checker does not yet treat the direct `phase12_libbpf_*` replay files or `tools/lib/bpf/zigux_segments/verify.zig` as shipped required paths
- the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/verify.zig` should stay described as present reviewability evidence on head while remaining outside the shared shipped replay order
- the snapshot anchor remains the truthful bounded signal here while those direct replay files stay outside the shipped checkout contract
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
2. treat the snapshot anchor plus the present direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/verify.zig` as the truthful bounded signal here while those files remain outside the shipped replay contract
3. treat `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` as shared Phase 12 smoke-first anchors only; they keep the published `virtio_scsi` packet reviewable today but do not by themselves prove that the parked libbpf verify shard has joined the shipped replay order

## Next Bounded Step

If this lane reopens, reread `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` against the current parked verify-shard packet. Prefer the next one-file scripts-root or tests-root truthfulness update that keeps present Phase 12 libbpf verify-shard files from being described as absent while still avoiding any claim that they are shipped release-packet surfaces before the shared build route adopts them.
