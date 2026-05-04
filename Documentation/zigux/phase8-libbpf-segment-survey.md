# Phase 8 Libbpf Segment Survey

This document tracks the bounded Phase 8 userspace-adjacent tooling survey for Zigux around `tools/lib/bpf/libbpf.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=libbpf-segment-survey`
- scope: segment manifest plus six landed helper-first starter slices, the separate bounded perf-buffer poll bookkeeping adjunct, one deferred resource boundary, one deferred interrupt-routing boundary, one blocked object-model follow-on, and two deferred loader-facing follow-ons
- survey checkpoint: refreshed against inspected `master` head `897cdd2f62c4428d2a050275a187950e161b66eb`
- product boundary:
  - `tools/lib/bpf/zigux_segments/manifest.json`
  - `tools/lib/bpf/zigux_segments/cpu_mask.zig`
  - `tools/lib/bpf/zigux_segments/logging.zig`
  - `tools/lib/bpf/zigux_segments/pin_path.zig`
  - `tools/lib/bpf/zigux_segments/type_names.zig`
  - `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
  - `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
  - `zigux/tests/phase8_cpu_mask.zig`
  - `zigux/tests/phase8_bpf_type_names.zig`
  - `zigux/tests/phase8_file_path_handle_bridge.zig`
  - `zigux/tests/phase8_logging.zig`
  - `zigux/tests/phase8_pin_path.zig`
  - `zigux/tests/phase8_libbpf_segments.zig`
  - `zigux/tests/phase8_libbpf_segments_only_build.zig`
  - `zigux/tests/phase8_perf_buffer_poll.zig`
  - `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/bpf/libbpf.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/bpf/zigux_segments/` as the bounded Zigux destination for a segmented rollout.

The live repo already carried the full C libbpf tree, but it still had no `tools/lib/bpf/zigux_segments/` scaffold and no Phase 8 libbpf note to explain how Zigux should enter this surface without exploding into mirror-tree churn. The highest-value lane-local step was to close that planning gap with a concrete, testable segment catalog before any direct libbpf port work starts.

## Survey findings

- `tools/lib/bpf/libbpf.c` is still the dominant anchor at 14771 lines.
- companion C leaves such as `btf.c`, `linker.c`, `bpf.c`, `features.c`, `ringbuf.c`, `netlink.c`, `nlattr.c`, and `libbpf_utils.c` confirm that Phase 8 needs a segmented rollout instead of a single-file port attempt.
- before this survey landed, the repo had no `tools/lib/bpf/zigux_segments/` directory and no dedicated Phase 8 libbpf review note.
- the first realistic Zigux entry points are helper-first clusters with stable text or path behavior, while direct file reads, path opens, token handles, fd ownership, and perf-buffer CPU routing still need explicit deferred boundaries before any broader object work starts.

## Segment catalog

The manifest currently records eleven bounded segments.

That eleven-segment catalog intentionally excludes the separate `perf_buffer_poll.zig` adjunct packet: the poll helper is landed and reviewable, but it remains a narrower bookkeeping-only follow-on beside the deferred `perf-buffer-online-cpu-routing` segment rather than a twelfth catalog entry inside the main libbpf segment manifest.

The recorded segments are:

- `logging-version-and-errno`
- `pin-path-helpers`
- `cpu-mask-parsing`
- `type-name-helpers`
- `fdinfo-map-info-helpers`
- `map-reuse-compatibility`
- `file-path-and-handle-bridge`
- `perf-buffer-online-cpu-routing`
- `skeleton-population`
- `object-and-elf-loader`
- `btf-relocation-and-program-load`

Each segment ID in that manifest stays under the historical `P8-L15-S..` prefix as a stable segment catalog identifier, while the active scheduled ownership and cleanup lane for this packet is `P8-L13`, so the landed helper packet, the focused survey replay, and the lane memory stay aligned on the same bounded Phase 8 catalog without reviving older `P8-L10` or `P8-L14` residue.

`cpu-mask-parsing`, `logging-version-and-errno`, `pin-path-helpers`, `type-name-helpers`, `fdinfo-map-info-helpers`, and `map-reuse-compatibility` have now moved from planned work to landed starter slices under `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/type_names.zig`, and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`. The file-path helper now keeps `bpf_get_map_info_from_fdinfo()` bounded to `/proc/<pid>/fdinfo/<fd>` path construction, fdinfo text parsing for `map_type`, `key_size`, `value_size`, `max_entries`, `map_flags`, and `map_extra`, the reused-map-name chooser inside `bpf_map__reuse_fd()`, and the bounded map reuse compatibility comparison that preserves libbpf's DEVMAP readonly-prog exception without claiming pinned-object reopen flow or FD duplication side effects. `file-path-and-handle-bridge` stays deferred as the remaining resource-boundary cluster around `bpf_object_prepare_token()`, `bpf_object__reuse_map()`, because it still crosses real procfs reads, bpffs opens, token creation, `bpf_obj_get()` reopen flows, and fd close or ownership semantics without yet requiring full ELF or skeleton parity. The separate `perf-buffer-online-cpu-routing` segment stays deferred next to the landed cpu-mask helper because `perf_buffer__new()` still combines `/sys/devices/system/cpu/online` reads, cached `/sys/devices/system/cpu/possible` counts, online CPU filtering, perf-event-array map updates, epoll-backed perf FD registration, and timeout-driven `perf_buffer__poll(timeout_ms)` waits that return ready-buffer counts into one interrupt-routing-sensitive timing boundary. Phase 8 still ships no standalone timer helper and no standalone clockevent helper for that broader poll path. The repo now also carries a separate bounded `Documentation/zigux/phase8-perf-buffer-poll-slice.md` packet through `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` and `zigux/tests/phase8_perf_buffer_poll.zig`, but that helper is limited to wait-result classification and ready-buffer bookkeeping only. It now keeps the ordered `perf_buffer__process_records()` pass reviewable as a bounded fail-fast summary helper, rejects impossible post-wait buffer state combinations for timeout, interrupt, and already-failed wait observations, and still does not claim direct `epoll_wait()` parity, timer or clockevent parity, or broader interrupt-routing behavior. The remaining object-adjacent and loader-facing segments stay explicitly blocked or deferred until more model parity exists.

## Current landed segment progress

The current starter implementation stays deliberately bounded:

- `cpu_mask.zig` ports the string-parsing core of `parse_cpu_mask_str()`
- the segment now includes an injected chunk-reader interface for sysfs-style buffered input without claiming direct file-descriptor parity
- the starter now exposes dense `[]bool` mask output plus set-bit counting, bounded perf-buffer auto-CPU sizing, pure online-CPU eligibility checks, pure caller-supplied explicit perf-buffer target planning, bounded sequential positive-CPU fallback planning, and pure auto-selected CPU planning from already-injected possible and online masks for future perf-buffer and feature-probe callers
- delimiter skipping now mirrors libbpf's comma-and-newline loop while still allowing the `sscanf()`-style leading whitespace that the C helper already consumes, without widening into real file I/O
- the survey now keeps the separate `perf-buffer-online-cpu-routing` boundary explicit so the landed parser-and-planning helper is not mistaken for online CPU selection, perf-event-array routing, or direct `perf_buffer__poll(timeout_ms)` parity
- malformed ranges still fail fast instead of silently stretching the segment into broader object or verifier-facing work
- `type_names.zig` ports the exported attach, link, map, and program type string tables as pure dense lookups over the current `tools/include/uapi/linux/bpf.h` ordinal space
- the type-name helper keeps unknown negative and oversized ordinals returning `null`, matching libbpf's bounded helper behavior without widening into name-to-type parsing or object lifecycle state
- `logging.zig` ports libbpf's bounded print-level parsing, verbosity gating, major or minor version reporting, and the libbpf-specific strerror table without claiming environment reads, stderr output, or full errno-name coverage
- the logging helper keeps invalid `LIBBPF_LOG_LEVEL`-style values explicit for callers instead of printing directly
- custom libbpf error text is exposed through a compact helper and unknown or unmapped codes fall back to a stable `"Unknown libbpf error N"` formatter
- `pin_path.zig` ports the pure pathname join and bpffs dot-sanitization helpers behind explicit buffer-based APIs that mirror `pathname_concat()`, `build_map_pin_path()`, and `sanitize_pin_path()`
- the pin-path helper defaults to `/sys/fs/bpf` when callers leave the root unset, but still keeps actual map pinning, directory creation, and filesystem validation outside the Zig slice
- pin-path overflows stay explicit as bounded helper errors instead of silently truncating output or widening into direct `PATH_MAX`, `mkdir()`, `statfs()`, or `unlink()` parity
- `file_path_handle_bridge.zig` ports the pure `/proc/<pid>/fdinfo/<fd>` path construction, a current-process convenience wrapper that mirrors libbpf's `getpid()`-based anchor, a `planTokenPreparation()` helper that keeps optional-versus-mandatory bpffs intent explicit around `bpf_object_prepare_token()`, a `classifyTokenPreparationFailure()` helper that keeps optional failure fallback versus mandatory failure behavior reviewable without claiming live token creation, and bounded `map_type`, `key_size`, `value_size`, `max_entries`, `map_flags`, and `map_extra` text parsing from `bpf_get_map_info_from_fdinfo()`
- the file-path-handle helper now also exposes the reused-map-name chooser from `bpf_map__reuse_fd()`, preserving the original requested name only when the kernel-provided info name is exactly `BPF_OBJ_NAME_LEN - 1` bytes and matches the truncated prefix
- the same helper now also exposes the bounded map reuse compatibility check from `bpf_object__reuse_map()`, including libbpf's DEVMAP readonly-prog exception, without claiming bpffs reopen flow, FD duplication, or close-on-replacement side effects
- the file-path-handle helper accepts reordered or whitespace-padded fdinfo lines, keeps missing fields zero-initialized, lets later duplicate keys overwrite earlier values the same way libbpf's fallback does, and still keeps malformed values explicit for callers
- the same helper now keeps empty-string token prevention, default `/sys/fs/bpf` optional probing, caller-provided mandatory token paths, and the `skip_optional_missing_delegation` versus `fail` split explicit without claiming real `open()`, `close()`, or `bpf_token_create()` behavior
- the new helper still does not claim `fopen()`, `fgets()`, `fclose()` ownership, `open()` or `close()` ownership, `bpf_obj_get()` reopen flows, `bpf_token_create()` handle lifecycle parity, or FD duplication and replacement side effects
- `perf_buffer_poll.zig` keeps the already-observed `timeout_ms` classes, explicit wait-result variants, ready-buffer counts, first-ready indexing, first-error surfacing, the ordered `perf_buffer__process_records()` fail-fast summary, and impossible post-wait buffer-state rejection reviewable without widening into epoll-backed wait behavior or direct routing parity

The current tests check:

- mixed single-CPU and `start-end` ranges expand into the expected dense mask
- repeated delimiters, newline-terminated inputs, and leading-whitespace-at-token-start inputs still parse cleanly
- chunked reader input can split ranges, delimiters, and `sscanf()`-style leading whitespace across scratch-buffer boundaries
- the bounded set-bit counter matches the parsed mask contents
- the bounded auto-CPU count clamp keeps possible-CPU sizing inside the map entry budget while still treating zero as the uncapped case
- explicit online-mask eligibility behavior stays visible for automatic versus caller-pinned CPU budgets
- explicit caller-supplied CPU and map-key planning keeps pair ordering, count mismatches, and negative targets reviewable without widening into perf-buffer routing
- the synthetic sequential positive-CPU fallback remains available for pure non-routing callers that only need a bounded CPU index list
- auto-selected CPU planning keeps only online possible CPUs, respects the bounded map-entry budget, and treats truncated injected online masks as offline instead of widening into direct sysfs reads
- empty, malformed, and trailing-whitespace-only ranges report explicit errors
- reader contract failures stay explicit instead of silently truncating input
- the manifest-backed survey now rejects dropping the deferred perf-buffer online-CPU routing boundary from the segment catalog
- the survey summary keeps both the deferred file-path resource boundary and the blocked skeleton follow-on visible so the landed helper set is not mistaken for object-model progress
- every exported attach, link, map, and program type-name table entry stays reachable through the paired helper
- representative late ordinals from `tools/include/uapi/linux/bpf.h` still resolve to the shipped type-name strings
- out-of-range negative and oversized type ordinals are rejected cleanly
- warn, info, and debug verbosity resolution stays case-insensitive and preserves libbpf's gating order
- invalid log-level text stays explicit while callers still receive the default `info` minimum level
- the bounded major, minor, and version-string helpers match the current `tools/lib/bpf/libbpf_version.h` tuple
- libbpf-specific custom error text stays stable and unmapped custom codes fall back cleanly
- default and caller-provided pin roots join cleanly with map names
- `.` characters inside pin roots and map names sanitize to `_` the same way bpffs pin-name helpers do in libbpf
- buffer exhaustion during pin-path assembly stays explicit
- proc fdinfo paths format cleanly for representative pid and fd pairs, including the current-process `getpid()` convenience path, without widening into direct file reads
- token-preparation planning keeps prevented, optional, and mandatory bpffs intent explicit while still stopping short of live directory opens or token creation
- token-preparation failure handling keeps the optional `bpffs_open` and `token_create` fallback branches reviewable through `classifyTokenPreparationFailure()` while mandatory token setup remains an explicit fail-fast boundary
- bounded fdinfo map metadata parsing accepts reordered lines plus explicit `map_flags` and `map_extra` bases, keeps omitted fields zero-initialized, resolves duplicate keys last-wins, and still rejects malformed values
- truncated kernel map names only expand back to the requested full name when the `BPF_OBJ_NAME_LEN - 1` prefix matches, keeping reused-map naming rules explicit without widening into FD duplication or pinned-object side effects
- the same file-path helper packet now also keeps map reuse compatibility reviewable by proving the DEVMAP readonly-prog exception stays normalized while non-DEVMAP flag mismatches remain explicit
- the bounded perf-buffer poll helper keeps wait-result classification and ready-buffer bookkeeping explicit, keeps the ordered `perf_buffer__process_records()` pass reviewable through a separate fail-fast summary helper, and rejects impossible post-wait buffer state combinations without claiming direct `epoll_wait()` parity or broader timer, clockevent, or interrupt-routing behavior

## Gates

The shared review path now fail-closes through the shared Phase 8 validator, the validator-flow audit, the dedicated tests-readme alignment checker, the dedicated perf-buffer poll gate checker, and all four built-in self-tests before the focused survey, focused perf-buffer poll shard, and shared build replays run, so this survey stays tied to the same docs-root, tests-root, Makefile, workflow, and segmented libbpf packet that the repo already ships.

1. `python3 scripts/zigux/validate-phase8.py --self-test`
2. `python3 scripts/zigux/check-phase8-validator-flow.py --self-test`
3. `python3 scripts/zigux/check-phase8-tests-readme-alignment.py --self-test`
4. `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py --self-test`
5. `python3 scripts/zigux/validate-phase8.py`
6. `python3 scripts/zigux/check-phase8-validator-flow.py`
7. `python3 scripts/zigux/check-phase8-tests-readme-alignment.py`
8. `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
9. `make -C zigux phase8-validate`
10. `zig test zigux/tests/phase8_libbpf_segments.zig`
11. `zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`
12. `make -C zigux phase8-perf-buffer-poll-test`
13. `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`
14. `zig build test --build-file zigux/tests/phase8_build.zig --summary all`
15. `make -C zigux phase8`

## Latest committed gate snapshot

- provenance and anchor alignment rechecked against inspected `master` head `897cdd2f62c4428d2a050275a187950e161b66eb`
- the committed `phase8-validate` bundle in `zigux/Makefile` now routes through `validate-phase8.py`, `check-phase8-validator-flow.py`, `check-phase8-tests-readme-alignment.py`, and `check-phase8-perf-buffer-poll-gate.py` in both self-test and live modes before the focused and shared replay steps
- `scripts/zigux/check-phase8-validator-flow.py` currently publishes `PHASE8_VALIDATOR_FLOW_SELF_TEST_CASE_COUNT=17`
- `scripts/zigux/check-phase8-tests-readme-alignment.py` currently publishes `PHASE8_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=40`
- `scripts/zigux/check-phase8-perf-buffer-poll-gate.py` currently publishes `PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST_CASE_COUNT=8`
- `.github/workflows/zigux-bootstrap.yml` currently keeps a dedicated `Run focused Phase 8 perf-buffer poll tests` step wired to `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
- `Documentation/zigux/phase8-perf-buffer-poll-slice.md` and `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` both keep the dedicated checker plus the focused perf-buffer poll shard explicit inside the same shared Phase 8 tooling packet

## Non-goals

This survey slice does not yet claim:

- any direct Zig port of `tools/lib/bpf/libbpf.c`
- `parse_cpu_mask_file()` parity or direct file reads
- `perf_buffer__new()` online CPU filtering, perf-event-array population, epoll registration, or interrupt-routing parity
- direct `mkdir()`, `statfs()`, `unlink()`, or `bpf_obj_pin()` parity for map or program pinning
- direct `/proc/.../fdinfo` reads, `fopen()` or `fclose()` ownership, `open()` or `close()` ownership, `bpf_obj_get()` reopen flows, or `bpf_token_create()` handle lifecycle parity
- BTF relocation parity
- ELF loader parity
- direct `epoll_wait()` parity or broader `perf_buffer__poll(timeout_ms)` routing-loop timeout parity
- any standalone timer helper or standalone clockevent helper for perf-buffer polling
- perf-buffer runtime behavior
- object-model parity for `bpf_object`, `bpf_map`, or `bpf_program`

## Next bounded step

Treat the Phase 8 helper-first entry as substantively landed for now: keep the shared Phase 8 gate honest, leave both the remaining file-path-and-handle bridge segment and the separate perf-buffer online-CPU routing boundary explicitly deferred, and only reopen `tools/lib/bpf/zigux_segments/` for another bounded helper if fresh repo reality exposes one that stays smaller and lower risk than those remaining resource or routing boundaries and the currently blocked object-model or loader-facing work.
