# Phase 12 Libbpf Segment Survey

This document records the bounded Phase 12 survey lane around `tools/lib/bpf/libbpf.c` and the existing `tools/lib/bpf/zigux_segments/` rollout.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=libbpf-segment-survey`
- `PHASE12_LANE_KEY=P12-L16`
- scope: Phase 12 survey manifest, dedicated snapshot/packet/focused-replay gates, shared validator wiring, focused libbpf-only replay evidence, and a lane note that compares the current `zigux_segments/` footing against the roadmap's heavy-helper consumer plan
- product boundary:
  - `zigux/tests/phase12_libbpf_manifest.json`
  - `zigux/tests/phase12_libbpf_segments.zig`
  - `zigux/tests/phase12_libbpf_reviewability.zig`
  - `zigux/tests/phase12_libbpf_only_build.zig`
  - `zigux/tests/fixtures/phase12_libbpf_snapshot.json`
  - `tools/lib/bpf/zigux_segments/manifest.json`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
  - `scripts/zigux/check-phase12-libbpf-snapshot.py`
  - `scripts/zigux/check-phase12-libbpf-packet.py`
  - `scripts/zigux/check-phase12-libbpf-focused-replay.py`
  - `scripts/zigux/validate-phase12.py`
  - `zigux/Makefile`

## Why this slice exists

The roadmap now places `tools/lib/bpf/libbpf.c` in Phase 12, alongside the other high-risk production-facing consumers, because the file is both large and semantically dense even though it lives under `tools/`.

That matters because the live repo already has real helper-first progress under `tools/lib/bpf/zigux_segments/`: a segment catalog, dense type-name tables, a CPU-mask helper with the deferred chunk-reader path for sysfs-style buffered input, a bounded logging helper, bounded bpffs pin-path helpers, a bounded proc-fdinfo, map-info, and map-reuse compatibility helper packet, and a bounded perf-buffer poll helper for wait-result and ready-buffer bookkeeping. Those are useful footholds, but they still need a current Phase 12 survey checkpoint that explains how the earlier helper work fits the modern roadmap instead of leaving libbpf stranded in older Phase 8 wording or stale Phase 12 reviewability assumptions.

The highest-value honest step in this lane is therefore a survey checkpoint that records the existing segmented footing, keeps the Phase 12 build gate aware of it, verifies that the landed helper files still match the segment plan, and keeps the blocked-risk split current instead of drifting behind the live tree. The note also needs to name the live snapshot, packet-alignment, focused-replay, shared-validator, and Makefile routes directly so reviewers do not have to infer the active infrastructure packet only from later gate prose.

This checkpoint was last re-verified against packet-local head `d62742e7ff0747ed15f71f67d505f68ea15ec7ab`, with the landed helper set widened to include the bounded map-reuse compatibility slice, the cpu-mask helper now also carrying the same automatic perf-buffer CPU-budget clamp that libbpf applies before it opens per-CPU buffers, and with the deferred risk split still holding between the skeleton blocker, the deferred file-path and perf-buffer boundaries that share helper files, the deferred object-loader bucket, and the deferred relocation or verifier-facing bucket. This note now keeps that recorded verification head explicit instead of calling it the current `master` tip, while also recording that the live helper set has since gained the bounded `perf_buffer__poll()` wait-result and ready-buffer bookkeeping helper without collapsing the broader perf-buffer routing boundary into claimed runtime parity.

## Survey findings

- at the recorded surveyed head `d62742e7ff0747ed15f71f67d505f68ea15ec7ab`, `tools/lib/bpf/libbpf.c` measured 14,771 lines, which is large enough to cross helper, loader, object-model, relocation, and verifier-facing concerns in one file.
- the live repo already ships the earlier `tools/lib/bpf/zigux_segments/manifest.json` survey plus six landed helper files that carry seven bounded helper slices:
  - `type_names.zig` for exported attach, link, map, and program type string tables
  - `cpu_mask.zig` for bounded CPU-mask parsing, set-bit counting, the automatic perf-buffer CPU-budget clamp, and a deferred reader interface that still stops short of direct file I/O while keeping libbpf's fixed-width cpu-mask input ceiling explicit
  - `logging.zig` for bounded print-level parsing, version reporting, and libbpf-specific error text formatting
  - `pin_path.zig` for bounded bpffs path joining, pin-name and root-path validation, and dot-sanitization without directory or syscall parity
  - `file_path_handle_bridge.zig` for explicit `/proc/<pid>/fdinfo/<fd>` path construction, bounded `map_type`, `key_size`, `value_size`, `max_entries`, and `map_flags` text parsing, the reused-map-name chooser, the bounded map reuse compatibility comparison that preserves libbpf's DEVMAP readonly-prog exception, and token-preparation recovery classification without direct procfs reads, token creation, or reopen-flow parity
  - `perf_buffer_poll.zig` for bounded `perf_buffer__poll(timeout_ms)` wait-result classification, ready-buffer bookkeeping, and fail-fast `perf_buffer__process_records()` ordering without claiming direct `epoll_wait()` parity, callback delivery, online CPU routing, or timer ownership
- the earlier Phase 8 tooling lane proved that helper-first segmentation works for libbpf, but the current roadmap places the broader heavy-consumer rollout in Phase 12 because the remaining work depends on object-model discipline, loader boundaries, and high-risk validation gates.
- the current Phase 12 build now re-checks the landed helper-first foundations directly by compiling `type_names.zig`, `cpu_mask.zig`, `logging.zig`, `pin_path.zig`, and `file_path_handle_bridge.zig` through a reviewability gate, by proving the deferred CPU-mask reader still rejects over-ceiling buffered input instead of silently widening past libbpf's fixed cpu-mask file budget, by proving the bounded helper also keeps libbpf's automatic perf-buffer CPU-budget clamp explicit before any per-CPU buffer opens happen, by proving the landed map-reuse compatibility helper still compiles inside the shared bridge file, and by confirming that the manifest keeps shared helper files separate from the still-deferred file-handle and perf-buffer routing boundaries they sit beside.
- the same Phase 12 packet now also carries a focused libbpf-only replay: `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py` fails closed if `zigux/tests/phase12_libbpf_only_build.zig` stops compiling the dedicated `phase12-libbpf-segment-survey-tests` and `phase12-libbpf-reviewability-tests` pair, and `zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all` replays that bounded packet without widening into the rest of the shared Phase 12 driver bundle. The focused replay checker and the broader packet checker now both exact-count the dedicated review-hook line in `Documentation/zigux/review-checklist.md` and the corresponding focused-replay checklist entry inside `scripts/zigux/validate-phase12.py`, while the shared validator itself now also self-tests duplicate focused-replay review-hook drift through `CHECKLIST_EXACT_COUNTS`, so this packet no longer needs to carry that validator gap forward as the next bounded libbpf governance step.
- the shared Phase 12 validation path now also carries a committed reproducibility packet for this bounded libbpf lane: `scripts/zigux/check-phase12-libbpf-snapshot.py` rebuilds the manifest, survey gate, reviewability gate, survey note, and legacy segment catalog snapshot twice, proves the JSON is stable across repeat runs, compares it against `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, and now also refuses to trust that snapshot packet unless `zigux/tests/phase12_libbpf_reviewability.zig` still keeps the committed snapshot test name, the tracked-file-count assertion, the per-path assertion, and the same five tracked paths explicit. The same bounded packet now also keeps `python3 scripts/zigux/check-phase12-build-inventory.py --self-test`, `python3 scripts/zigux/check-phase12-build-inventory.py`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-libbpf-packet.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-packet.py`, `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test`, and `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py` explicit ahead of `python3 scripts/zigux/validate-phase12.py` and `make -C zigux phase12-validate`, so the shared build-inventory, bounded libbpf snapshot, bounded libbpf packet-alignment, and focused replay checks all fail closed before the shared validator or bundled replay claim aligned evidence.
- the bounded file-path-and-handle helper packet now also mirrors the libbpf token-preparation recovery split more faithfully: optional probes still degrade gracefully, mandatory probes still fail hard, the optional `-ENOENT` delegation-miss path stays distinct from the generic open or token-create failure path, and the landed map-reuse compatibility helper still keeps the DEVMAP readonly-prog exception explicit without claiming any direct `open()` or `bpf_token_create()` parity.
- the legacy Phase 8 segment catalog now records the bounded `perf_buffer_poll.zig` helper as a landed helper-first slice while still keeping two important same-file boundaries explicit: `file-path-and-handle-bridge` stays deferred even though smaller helpers already live in `file_path_handle_bridge.zig`, and perf-buffer-online-cpu-routing stays deferred even though the bounded parser helper already lives in `cpu_mask.zig` and the bounded wait-result and ready-buffer bookkeeping helper already lives in `perf_buffer_poll.zig`.
- the repo still has no `skeleton.zig`, `object_loader.zig`, or relocation-facing Zig slice, and it still intentionally avoids direct ELF collection, `bpf_object` parity, BTF relocation, and load-time verifier interactions.
- the current risk split is now explicit again: `skeleton.zig` remains the nearest post-helper cluster and is still blocked on the missing object model, `object_loader.zig` stays deferred as the heavier ELF-collection bucket that could otherwise collapse into mirror-tree sprawl, and `relocation.zig` stays deferred as the separate verifier-facing boundary for BTF fixups and load-time interactions.
- with the bounded helper-first utility slices now landed, the next honest libbpf-facing step is to keep reviewability aligned and avoid collapsing the nearer skeleton-population blocker into the broader loader risk unless fresh repo reality changes the actual segment boundaries.

## Recorded gaps

The survey manifest now records:

- the landed `phase12-build-gate`
- the landed `phase12-make-target`
- the landed `phase12-libbpf-segment-manifest-foundation`
- the landed `phase12-libbpf-type-name-helper-foundation`
- the landed `phase12-libbpf-cpu-mask-helper-foundation`
- the landed `phase12-libbpf-logging-helper-foundation`
- the landed `phase12-libbpf-pin-path-helper-foundation`
- the landed `phase12-libbpf-file-path-handle-helper-foundation`
- the landed `phase12-libbpf-map-reuse-compatibility-helper-foundation`
- the landed `phase12-libbpf-survey-gate`
- the landed `phase12-libbpf-reviewability-gate`
- the landed `phase12-libbpf-survey-note`
- the still-deferred `phase12-libbpf-file-path-and-handle-bridge-boundary`
- the still-deferred `phase12-libbpf-perf-buffer-online-cpu-routing-boundary`
- the still-blocked `phase12-libbpf-skeleton-population`
- the still-deferred `phase12-libbpf-object-and-elf-loader`
- the still-deferred `phase12-libbpf-btf-relocation-and-program-load`

This keeps the lane explicit without overstating progress: Zigux already has real libbpf helper footholds, including the deferred CPU-mask reader path, bounded logging and pin-path validation helpers, the bounded fdinfo path, map-info parser, map-reuse compatibility, and token-recovery classifier helper packet, the bounded perf-buffer poll helper, and the focused libbpf-only replay checker, but the heavy helper consumer still stops first at the missing skeleton or object-model boundary and then well short of the separate file-handle, perf-buffer routing, loader, relocation, or syscall-backed surfaces.

## Rollback And Reversible Delivery

- owner: `BPF Tooling Lane`
- rollback owner: `BPF Tooling Lane`
- fallback path: keep `tools/lib/bpf/libbpf.c` as the source of truth, keep the already-landed `type_names.zig`, `cpu_mask.zig`, `logging.zig`, `pin_path.zig`, `file_path_handle_bridge.zig`, and `perf_buffer_poll.zig` helper slice on its bounded helper footing, keep the deferred file-handle and perf-buffer boundaries explicit, and drop the Phase 12 libbpf survey packet back out of `zigux/tests/phase12_build.zig` if the shared reviewability packet regresses.
- reversible delivery evidence: this Phase 12 packet only adds `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, and this survey note around preexisting helper foundations, so the survey can be removed without inventing a second libbpf implementation or mutating `tools/lib/bpf/libbpf.c`. The same bounded packet also keeps `zigux/tests/phase12_libbpf_only_build.zig` and `scripts/zigux/check-phase12-libbpf-focused-replay.py` explicit as dedicated focused replay surfaces around those same helper-first foundations, so rollback can back out the shared Phase 12 libbpf survey wiring without touching `tools/lib/bpf/libbpf.c` or widening the landed helper files.
- rollback drill: run `python3 scripts/zigux/check-phase12-build-inventory.py --self-test`, `python3 scripts/zigux/check-phase12-build-inventory.py`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-libbpf-packet.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-packet.py`, `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py`, and `make -C zigux phase12-validate`; if the libbpf survey packet is the only failing slice, repair `scripts/zigux/check-phase12-libbpf-snapshot.py` plus `zigux/tests/fixtures/phase12_libbpf_snapshot.json` first if the reproducibility packet drifted, otherwise rerun `zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all`, remove the `phase12-libbpf-segment-survey-tests` and `phase12-libbpf-reviewability-tests` entries from `zigux/tests/phase12_build.zig` if the focused packet has to be backed out, keep the C anchor and landed helper files unchanged, then rerun `zig build test --build-file zigux/tests/phase12_build.zig --summary all` so the shared Phase 12 packet stays truthful while the libbpf survey note or gate is repaired.

## Non-goals

This survey slice does not claim:

- direct Zig parity for `tools/lib/bpf/libbpf.c`
- object-model parity for `bpf_object`, `bpf_map`, or `bpf_program`
- ELF collection or object loading
- BTF relocation recording
- load-time verifier interactions
- syscall-backed libbpf runtime behavior

## Gates

1. run the shared Phase 12 validator-first path
- `python3 scripts/zigux/check-phase12-build-inventory.py --self-test`
- `python3 scripts/zigux/check-phase12-build-inventory.py`
- `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`
- `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`
- `python3 scripts/zigux/check-phase12-libbpf-packet.py --self-test`
- `python3 scripts/zigux/check-phase12-libbpf-packet.py`
- `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test`
- `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py`
- `python3 scripts/zigux/validate-phase12.py`
- `make -C zigux phase12-validate`

2. run the focused libbpf-only replay
- `zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all`

3. run the dedicated Phase 12 build
- `zig build test --build-file zigux/tests/phase12_build.zig --summary all`

4. run the convenience target
- `make -C zigux phase12`

## Next bounded step

Keep the Phase 12 libbpf survey and reviewability lane aligned with the live helper set, and treat the duplicate focused libbpf-only replay review-hook self-test as landed shared-validator evidence rather than an open backlog item. Only reopen `tools/lib/bpf/zigux_segments/` for another bounded utility slice if fresh repo reality shows something materially smaller than the still-blocked skeleton, loader, and relocation work.