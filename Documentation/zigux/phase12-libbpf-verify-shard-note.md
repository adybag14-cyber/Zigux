# Phase 12 Libbpf Verify Shard Note

This note records the bounded Phase 12 reviewability intent around `tools/lib/bpf/zigux_segments/verify.zig`.

## Status

- `PHASE12_STATUS=verify-shard-present-not-shipped`
- `PHASE12_SLICE=libbpf-verify-shard`
- lane scope: keep the dedicated `zigux_segments/verify.zig` shard reviewable without widening into direct helper behavior changes, bridge implementation, queue routing, skeleton population, object loading, or verifier-facing relocation work
- current branch reality: `tools/lib/bpf/zigux_segments/verify.zig` is now materialized as a reviewability-only shard, while the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` still stay recorded only through shared survey, parked, or anti-overlap notes until they land on current `master`; the older `tools/lib/bpf/zigux_segments/manifest.json` catalog remains a snapshot-backed helper signal rather than shipped smoke-first evidence, and the shared `zigux/tests/phase12_build.zig` plus `zigux/Makefile` replay order still stays intentionally narrower than that parked packet
- paired review packet:
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
  - `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
  - `zigux/tests/fixtures/phase12_libbpf_snapshot.json`
  - `zigux/tests/phase12_build.zig`
  - `zigux/Makefile`

## Why this note exists

Earlier Phase 12 wording treated the libbpf packet as if it had either no dedicated verify shard at all or a broader shipped replay packet than the repo could actually support.

This note keeps three packets separate:

- the deterministic helper snapshot
- the compile-together reviewability shard
- the heavier bridge-local, queue-routing, object-model, and loader-risk buckets

Landing `tools/lib/bpf/zigux_segments/verify.zig` is useful because it gives the existing helper-first segment family a real Phase 12 reviewability foothold without pretending that the still-absent direct `phase12_libbpf_*` replay files or the shared smoke-first packet have already caught up.

## Current Ownership

The verify shard is now a bounded reviewability-only foothold on this branch.

- `tools/lib/bpf/zigux_segments/verify.zig` imports the existing `logging.zig`, `cpu_mask.zig`, `type_names.zig`, `online_cpu_routing.zig`, and `perf_buffer_poll.zig` helpers and keeps one narrow compile-and-test surface around them
- the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` still remain absent on current `master`, so this shard must stay explicitly smaller than the broader parked reviewability packet
- the older `tools/lib/bpf/zigux_segments/manifest.json` catalog remains readable historical helper evidence, but it is still not the same thing as the shipped Phase 12 smoke-first replay order
- the shared build packet still belongs to `zigux/tests/phase12_build.zig` and `zigux/Makefile`; this note does not claim that the verify shard has been adopted there yet

## Review Rules

- treat this note as the owner map for a bounded verify shard, not as proof that the shard is part of the shipped replay order on `master`
- keep the verify-shard wording aligned with `zigux/tests/fixtures/phase12_libbpf_snapshot.json` so the snapshot no longer reports `tools/lib/bpf/zigux_segments/verify.zig` as absent
- keep the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` explicit as still-parked boundaries until those files land for real
- preserve the split between the deterministic helper packet, the compile-together verify shard, the bridge-local helper destination, and the later object-model and loader-risk buckets instead of collapsing them back into one vague `libbpf` bucket
- do not use this shard to imply direct procfs reads, bpffs opens, pinned-object reopen flow, online-CPU setup-side delivery, object loading, or verifier-facing relocation behavior

## Non-goals

This note does not claim:

- that the direct `phase12_libbpf_*` replay files are now present on `master`
- that `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` is already materialized on current `master`
- that `zigux/tests/phase12_build.zig` or `zigux/Makefile` already run the verify shard
- direct procfs or bpffs interaction
- pinned-object reopen flow or descriptor ownership side effects
- online-CPU routing setup or callback delivery
- `bpf_object`, `bpf_map`, or `bpf_program` model parity
- skeleton population
- ELF collection, object loading, or load-time verifier interaction
- BTF relocation or program-load coverage

## Gates

1. keep the snapshot aligned with the new shard foothold
   - reread `zigux/tests/fixtures/phase12_libbpf_snapshot.json`
2. keep the shard itself parse-valid and testable as a bounded helper packet
   - `zig fmt --check tools/lib/bpf/zigux_segments/verify.zig`
   - `zig test tools/lib/bpf/zigux_segments/verify.zig`
3. treat `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` as shared Phase 12 smoke-first anchors only; they keep the published `virtio_scsi` plus starter-present `virtio_net` packet reviewable today but do not by themselves prove that the libbpf verify shard has joined the shipped replay order

## Next Bounded Step

If this lane reopens, align `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` with the same narrower truth:

- `tools/lib/bpf/zigux_segments/verify.zig` is now present as a bounded reviewability foothold
- the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` still remain parked
- the shared smoke-first Phase 12 replay packet still has not adopted the libbpf verify shard

That follow-up should stay a truthfulness repair, not a claim that the broader libbpf replay packet is already shipped.