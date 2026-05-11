# Phase 12 Libbpf Verify Shard Note

This note records the bounded Phase 12 reviewability intent around `tools/lib/bpf/zigux_segments/verify.zig`.

## Status

- `PHASE12_STATUS=parked`
- `PHASE12_SLICE=libbpf-verify-shard`
- lane scope: keep the dedicated `zigux_segments/verify.zig` shard reviewable when it is actually present, without widening into direct helper behavior changes, bridge implementation, queue routing, skeleton population, object loading, or verifier-facing relocation work
- current repo reality on `master`: the parked libbpf verify packet is snapshot-anchored rather than fully absent or fully shipped. `zigux/tests/fixtures/phase12_libbpf_snapshot.json` still reads back on current `master`, but the bounded verify shard, its paired Phase 12 libbpf reviewability source files, and `tools/lib/bpf/zigux_segments/manifest.json` do not, so the shared `scripts/zigux/check-build-only-phase12-surface.py` checker stays intentionally narrower than that parked shard instead of treating those missing paths as shipped required files
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

The intended `verify.zig` shard is a reviewability-only packet, but current `master` only exposes the snapshot anchor, not the verify, manifest, or reviewability source files themselves.

- the earlier note shape assumed imports from `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `file_path_handle_bridge.zig`, and `perf_buffer_poll.zig`
- the earlier note shape also assumed a focused `std.testing.refAllDecls` compile-reachability shard plus the directly coupled `zigux/tests/phase12_libbpf_reviewability.zig` gate
- today, the honest repo-reality signal is snapshot-only rather than mixed: current `master` still returns direct contents-read 404s for `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/manifest.json`, `zigux/tests/phase12_libbpf_reviewability.zig`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_manifest.json`, `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`, and `zigux/tests/phase12_libbpf_snapshot_determinism.zig`, while `zigux/tests/fixtures/phase12_libbpf_snapshot.json` still reads back successfully and the shared Phase 12 checker only enforces the shipped docs, workflow, Makefile, and `virtio_scsi` smoke-first build packet
- that means this note must stay a parked owner map until fresh repo reality again exposes the helper packet or a narrower shared truthfulness repair removes the stale references first

## Review Rules

- treat this note as a bounded owner map for the verify shard, not as proof that the shard currently ships on `master`, and not as proof of direct procfs reads, bpffs opens, token creation, online-CPU routing, skeleton population, object loading, or verifier-facing relocation work
- keep the parked verify-shard wording aligned with the same shared build-only checker packet, while staying clear that the checker no longer treats the missing libbpf reviewability files as shipped required paths
- treat the snapshot-only readback set as the truthful bounded signal here: the deterministic helper snapshot remains reviewable, but it does not by itself re-open the parked compile-together verify shard
- preserve the split between the deterministic helper packet, the compile-together verify shard, the bridge-local helper destination, and the later object-model and loader-risk buckets instead of collapsing them back into one vague `libbpf` bucket

## Non-goals

This note does not claim:

- that `tools/lib/bpf/zigux_segments/verify.zig` is currently present on `master`
- direct procfs or bpffs interaction
- pinned-object reopen flow or descriptor ownership side effects
- online-CPU routing or callback delivery
- `bpf_object`, `bpf_map`, or `bpf_program` model parity
- skeleton population
- ELF collection, object loading, or load-time verifier interaction
- BTF relocation or program-load coverage

## Gates

1. `python3 scripts/zigux/check-build-only-phase12-surface.py`
2. treat the current snapshot-only readback set for the parked verify-shard files as the truthful bounded signal until those files actually land again on `master`
3. treat `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` as shared Phase 12 smoke-first anchors only; they keep the published `virtio_scsi` packet reviewable today but do not by themselves prove that the parked libbpf verify shard has relanded

## Next Bounded Step

If this lane reopens, reread `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` against the current snapshot-only packet before choosing another shared reminder repair. Prefer the next one-file scripts-root or tests-root truthfulness update that stops parked Phase 12 libbpf verify-shard files from being presented as shipped release-packet surfaces before widening into helper behavior or blocked object-model work.
