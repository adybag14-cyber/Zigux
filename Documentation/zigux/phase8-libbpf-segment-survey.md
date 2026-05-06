# Phase 8 Libbpf Segment Survey
This document tracks the bounded Phase 8 userspace-adjacent tooling survey for Zigux around `tools/lib/bpf/libbpf.c`.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=libbpf-segment-survey`
- surveyed commit: `897cdd2f62c4428d2a050275a187950e161b66eb`
- scope: segment manifest plus five landed bounded slices across four helper-first starters and one perf-buffer poll adjunct, with the bounded fdinfo bridge helper packet kept adjacent to the next queued libbpf catalog step
- product boundary:
  - `tools/lib/bpf/zigux_segments/manifest.json`
  - `tools/lib/bpf/zigux_segments/cpu_mask.zig`
  - `tools/lib/bpf/zigux_segments/logging.zig`
  - `tools/lib/bpf/zigux_segments/pin_path.zig`
  - `tools/lib/bpf/zigux_segments/type_names.zig`
  - `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
  - `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
  - `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`
  - `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
  - `zigux/tests/phase8_cpu_mask.zig`
  - `zigux/tests/phase8_logging.zig`
  - `zigux/tests/phase8_pin_path.zig`
  - `zigux/tests/phase8_bpf_type_names.zig`
  - `zigux/tests/phase8_file_path_handle_bridge.zig`
  - `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
  - `zigux/tests/phase8_perf_buffer_poll.zig`
  - `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
  - `zigux/tests/phase8_libbpf_segments.zig`
  - `zigux/tests/phase8_libbpf_segments_only_build.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists
The Phase 8 roadmap explicitly names `tools/lib/bpf/libbpf.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/bpf/zigux_segments/` as the bounded Zigux destination for a segmented rollout.

The live repo already carried the full C libbpf tree, but it still had no `tools/lib/bpf/zigux_segments/` scaffold and no Phase 8 libbpf note to explain how Zigux should enter this surface without exploding into mirror-tree churn. The highest-value lane-local step was to close that planning gap with a concrete, testable segment catalog before any direct libbpf port work starts.

## Survey findings
- `tools/lib/bpf/libbpf.c` is still the dominant anchor at 14771 lines.
- companion C leaves such as `btf.c`, `linker.c`, `bpf.c`, `features.c`, `ringbuf.c`, `netlink.c`, `nlattr.c`, and `libbpf_utils.c` confirm that Phase 8 needs a segmented rollout instead of a single-file port attempt.
- before this survey landed, the repo had no `tools/lib/bpf/zigux_segments/` directory and no dedicated Phase 8 libbpf review note.
- the first realistic Zigux entry points are helper-first clusters with stable text or path behavior, not the BTF relocation or program-load core.

## Segment catalog
The manifest currently records twelve bounded segments:
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
- `perf-buffer-poll-bookkeeping`

`cpu-mask-parsing`, `logging-version-and-errno`, `pin-path-helpers`, `type-name-helpers`, and `perf-buffer-poll-bookkeeping` have now moved from planned work to landed bounded slices under `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/type_names.zig`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`.

`fdinfo-map-info-helpers` and `map-reuse-compatibility` still stay queued helper-first catalog entries, but no longer because the bridge packet paths are missing: the repo now carries the bounded fdinfo helper packet at `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, and `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, plus the adjacent bridge-boundary notes at `Documentation/zigux/phase8-file-path-handle-bridge-slice.md` and `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, while the broader helper-first catalog entries remain queued until that shared bridge packet is explicitly promoted beyond the current fdinfo-only surface.

The broader `file-path-and-handle-bridge` resource-boundary packet still stays deferred around direct procfs reads, bpffs opens, token creation, `bpf_obj_get()` reopen flow, and fd ownership semantics.

## Current landed segment progress
The current starter implementation stays deliberately bounded:
- `cpu_mask.zig` ports the string-parsing core of `parse_cpu_mask_str()`
- the segment now includes an injected chunk-reader interface for sysfs-style buffered input without claiming direct file-descriptor parity
- the starter exposes dense `[]bool` mask output plus set-bit counting for future perf-buffer and feature-probe callers
- delimiter skipping accepts the newline-terminated `/sys/devices/system/cpu/possible` style input without widening into real file I/O
- malformed ranges still fail fast instead of silently stretching the segment into broader object or verifier-facing work
- `logging.zig` ports libbpf's bounded print-level parsing, verbosity gating, major or minor version reporting, and the libbpf-specific strerror table without claiming environment reads, stderr output, or full errno-name coverage
- the logging helper keeps invalid `LIBBPF_LOG_LEVEL`-style values explicit for callers instead of printing directly
- custom libbpf error text is exposed through a compact helper and unknown or unmapped codes fall back to a stable `"Unknown libbpf error N"` formatter
- `pin_path.zig` ports the pure pathname join and bpffs dot-sanitization helpers behind explicit buffer-based APIs that mirror `pathname_concat()`, `build_map_pin_path()`, and `sanitize_pin_path()`
- the pin-path helper defaults to `/sys/fs/bpf` when callers leave the root unset, but still keeps actual map pinning, directory creation, and filesystem validation outside the Zig slice
- pin-path overflows stay explicit as bounded helper errors instead of silently truncating output or widening into direct `PATH_MAX`, `mkdir()`, `statfs()`, or `unlink()` parity
- `type_names.zig` ports the exported attach, link, map, and program type name tables as dense lookup helpers with stable string output
- the type-name helper keeps out-of-range values explicit with `null` instead of widening into section parsing, object loading, or feature probing
- `file_path_handle_bridge.zig` now ports the bounded `"/proc/%d/fdinfo/%d"` assembly plus compact fdinfo map-info parsing and summary helpers without claiming direct procfs reads, `bpf_obj_get()` reopen flow, token creation, or fd ownership semantics
- the bounded file-path bridge keeps reuse-planning cues explicit for callers while leaving bpffs opens, descriptor duplication, close-on-replacement behavior, and pinned-object reopen flow outside the current Zig slice
- `perf_buffer_poll.zig` keeps `perf_buffer__poll(timeout_ms)` wait-result classification, ready-buffer bookkeeping, and ordered process-record summaries reviewable without claiming live epoll wiring or per-CPU setup
- the broader `perf-buffer-online-cpu-routing` setup remains deferred around per-CPU `perf_event_open()` setup, perf-buffer ring `mmap()` setup, and `PERF_EVENT_IOC_ENABLE` enablement
- the current packet does not claim online-CPU filtering, epoll registration, timer semantics, or broader interrupt-routing behavior beyond those explicit setup-side anchors

The current tests check:
- mixed single-CPU and `start-end` ranges expand into the expected dense mask
- repeated delimiters and newline-terminated inputs still parse cleanly
- chunked reader input can split ranges and delimiters across scratch-buffer boundaries
- the bounded set-bit counter matches the parsed mask contents
- empty and malformed ranges report explicit errors
- reader contract failures stay explicit instead of silently truncating input
- warn, info, and debug verbosity resolution stays case-insensitive and preserves libbpf's gating order
- invalid log-level text stays explicit while callers still receive the default `info` minimum level
- the bounded major, minor, and version-string helpers match the current `tools/lib/bpf/libbpf_version.h` tuple
- libbpf-specific custom error text stays stable and unmapped custom codes fall back cleanly
- default and caller-provided pin roots join cleanly with map names
- `.` characters inside pin roots and map names sanitize to `_` the same way bpffs pin-name helpers do in libbpf
- buffer exhaustion during pin-path assembly stays explicit
- every exported attach, link, map, and program type table entry remains reachable through the corresponding helper
- representative late enum ordinals such as `trace_fsession` still resolve to the expected stable names
- bounded `/proc//fdinfo/` path assembly, compact fdinfo map-info parsing, and summary rendering stay explicit without widening into direct procfs reads or pinned-object reopen flow
- bounded perf-buffer wait summaries keep ready-count, first-error, processed-record totals, and first-processing-failure selection compact and explicit
- ready-buffer processing attempts cannot exceed observed ready events

## Gates
1. run the shared Phase 8 validator route first
   - `make -C zigux phase8-validate`
2. run the focused libbpf survey wrapper
   - `make -C zigux phase8-libbpf-segments-test`
   - `zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`
3. run the focused perf-buffer poll wrapper
   - `make -C zigux phase8-perf-buffer-poll-test`
   - `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`
4. run the shared Phase 8 wrapper
   - `make -C zigux phase8-test`
   - `zig build test --build-file zigux/tests/phase8_build.zig --summary all`
5. run the convenience target
   - `make -C zigux phase8`

## Non-goals
This survey slice does not yet claim:
- any direct Zig port of `tools/lib/bpf/libbpf.c`
- `parse_cpu_mask_file()` parity or direct file reads
- direct procfs reads, token creation, `bpf_obj_get()` reopen flow, or fd ownership semantics for the bounded file-path bridge helper
- direct `mkdir()`, `statfs()`, `unlink()`, or `bpf_obj_pin()` parity for map or program pinning
- BTF relocation parity
- ELF loader parity
- deferred `perf-buffer-online-cpu-routing` setup around per-CPU `perf_event_open()` setup, perf-buffer ring `mmap()` setup, or `PERF_EVENT_IOC_ENABLE` enablement
- live epoll wiring, mmap-backed ring ownership, or per-CPU perf-buffer runtime behavior
- standalone timer or clockevent helper behavior
- object-model parity for `bpf_object`, `bpf_map`, or `bpf_program`

## Next bounded step
Treat the current starter packet as substantively landed for now: keep the shared `make -C zigux phase8-validate` gate honest, leave the bounded fdinfo-only bridge helper and its adjacent boundary survey parked as adjacent review surface, keep `fdinfo-map-info-helpers` and `map-reuse-compatibility` queued as the next helper-first catalog entries, and reopen only when the deferred `file-path-and-handle-bridge` resource boundary around direct procfs-read, bpffs-open, token-creation, reopen-flow, and fd-ownership semantics can be reviewed as one tighter packet ahead of the still-blocked object-model and loader-facing work.
