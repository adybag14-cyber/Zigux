# Phase 12 Libbpf Verify Shard Note

This note records the bounded reviewability surface already present in `tools/lib/bpf/zigux_segments/verify.zig`.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=libbpf-verify-shard`
- `PHASE12_PACKET_ROLE=active-shared-release-companion`
- lane scope: keep the dedicated `zigux_segments/verify.zig` shard reviewable as an active companion inside the shipped Phase 12 release packet without widening into direct helper behavior changes, bridge implementation, queue routing, skeleton population, object loading, or verifier-facing relocation work
- release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
- closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- fallback companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
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

The live Phase 12 libbpf packet already ships a dedicated `verify.zig` shard, but that shard sat between bigger review surfaces without its own bounded note. That made it too easy for nearby runs to blur three different packets together:

- the deterministic five-file helper snapshot
- the shared compile-together and reviewability shard
- the heavier bridge-local, queue-routing, object-model, and loader-risk buckets

This note keeps that split explicit while matching the fact that the shared Phase 12 release packet now treats the verify shard as an active companion rather than a separately parked reminder.

## Current Ownership

The current `verify.zig` shard is an active companion inside the shared Phase 12 release packet, while direct helper-behavior expansion around it remains parked.

- it imports `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `file_path_handle_bridge.zig`, and `perf_buffer_poll.zig`
- its focused test uses `std.testing.refAllDecls` across those segment files so the landed helper foundations, the shared bridge destination, and their local tests stay compile-reachable together
- the directly coupled `zigux/tests/phase12_libbpf_reviewability.zig` gate then exact-checks the bounded behavior surface that this shard is meant to keep live: CPU-mask parsing and counting, libbpf type-name tables, logging version and bounded errno text, pin-path sanitization, fdinfo path and map-info parsing, reused-map name resolution, and bounded perf-buffer wait classification
- the deterministic snapshot remains smaller on purpose: it tracks only the five pure helper-first files, while `verify.zig` and the bridge-local `file_path_handle_bridge.zig` surface stay outside that snapshot because they serve shared reviewability and bridge-local ownership rather than the pure-helper packet itself
- the shared PMO companions now rely on this note as part of the active release packet, so release-facing wording should keep the verify shard visible beside the sequencing, closure, readiness, coordination, fallback, scripts-root, and tests-root reminders even while helper-local expansion stays out of scope

## Review Rules

- treat this note as a bounded owner map for the verify shard, not as proof of direct procfs reads, bpffs opens, token creation, online-CPU routing, skeleton population, object loading, or BTF relocation work
- keep this note aligned with `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` so the active shared packet keeps one truthful release-planning story
- keep the verify shard aligned with the same shared packet that already owns `zigux/tests/phase12_libbpf_reviewability.zig`, the deterministic snapshot fixtures, the shared build-only checker, the smoke-first replay order, and the Linux-style `phase12` replay route
- keep the degraded-workflow checker pair and the attached-toolchain Make fallback explicit beside that same smoke-first order so this note does not drift into implying a focused libbpf-only fallback route
- preserve the split between the deterministic five-path helper packet, the compile-together verify shard, the bridge-local helper destination, and the later object-model and loader-risk buckets instead of collapsing them back into one vague `libbpf` bucket

## Non-goals

This note does not claim:

- direct procfs or bpffs interaction
- pinned-object reopen flow or descriptor ownership side effects
- online-CPU routing or callback delivery
- `bpf_object`, `bpf_map`, or `bpf_program` model parity
- skeleton population
- ELF collection, object loading, or load-time verifier interaction
- BTF relocation or program-load coverage

## Gates

1. `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
2. `python3 scripts/zigux/check-build-only-phase12-surface.py`
3. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
4. `make -C zigux phase12-smoke`
5. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
6. `make -C zigux phase12`
7. If `zig` is unavailable on `PATH`, reuse the same smoke-first order only through the shipped Make routes with `ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only fallback entrypoint.
- `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
- `make -C zigux phase12 ZIG=<attached-zig-path>`

## Next Bounded Step

If this lane reopens, reread `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` against the same live verify shard before choosing another shared reminder repair. Current `master` already keeps the shared release packet explicit about this verify-shard companion, so the next honest same-lane follow-through is whichever remaining one-file PMO reminder drifts next while keeping the shared smoke-first packet, the checker pair, the two-versus-two fallback split, and the bounded verify-shard ownership split aligned before widening into helper behavior or blocked object-model work.
