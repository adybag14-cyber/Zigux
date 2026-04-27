# Phase 8 Libbpf Segment Survey

This document tracks the bounded Phase 8 userspace-adjacent tooling survey for Zigux around `tools/lib/bpf/libbpf.c`.

## Status

- `PHASE8_STATUS=active`
- `PHASE8_SLICE=libbpf-segment-survey`
- scope: segment manifest plus four landed helper-first starter slices
- product boundary:
  - `tools/lib/bpf/zigux_segments/manifest.json`
  - `tools/lib/bpf/zigux_segments/cpu_mask.zig`
  - `tools/lib/bpf/zigux_segments/logging.zig`
  - `tools/lib/bpf/zigux_segments/pin_path.zig`
  - `tools/lib/bpf/zigux_segments/type_names.zig`
  - `zigux/tests/phase8_cpu_mask.zig`
  - `zigux/tests/phase8_bpf_type_names.zig`
  - `zigux/tests/phase8_logging.zig`
  - `zigux/tests/phase8_pin_path.zig`
  - `zigux/tests/phase8_libbpf_segments.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/bpf/libbpf.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/bpf/zigux_segments/` as the bounded Zigux destination for a segmented rollout.

The live repo already carried the full C libbpf tree, but it still had no `tools/lib/bpf/zigux_segments/` scaffold and no Phase 8 libbpf note to explain how Zigux should enter this surface without exploding into mirror-tree churn. The highest-value lane-local step was to close that planning gap with a concrete, testable segment catalog before any direct libbpf port work starts.

## Survey findings

- `tools/lib/bpf/libbpf.c` is still the dominant anchor at 14771 lines.
- companion C leaves such as `btf.c`, `linker.c`, `bpf.c`, `features.c`, `ringbuf.c`, `netlink.c`, `nlattr.c`, and `libbpf_utils.c` confirm that Phase 8 needs a segmented rollout instead of a single-file port attempt.
- before this survey landed, the repo had no `tools/lib/bpf/zigux_segments/` directory and no dedicated Phase 8 libbpf review note.
- the first realistic Zigux entry points are helper-first clusters with stable text or path behavior, while direct file reads, path opens, token handles, and fd ownership still need an explicit deferred boundary before any broader object work starts.

## Segment catalog

The manifest currently records eight bounded segments:

- `logging-version-and-errno`
- `pin-path-helpers`
- `cpu-mask-parsing`
- `type-name-helpers`
- `file-path-and-handle-bridge`
- `skeleton-population`
- `object-and-elf-loader`
- `btf-relocation-and-program-load`

`cpu-mask-parsing`, `logging-version-and-errno`, `pin-path-helpers`, and `type-name-helpers` have now moved from planned work to landed starter slices under `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, and `tools/lib/bpf/zigux_segments/type_names.zig`. `file-path-and-handle-bridge` is now called out separately as the next deferred resource-boundary cluster around `bpf_get_map_info_from_fdinfo()`, `bpf_object_prepare_token()`, and `bpf_object__reuse_map()`, because it crosses real procfs reads, bpffs opens, token creation, `bpf_obj_get()` reopen flows, and fd close or ownership semantics without yet requiring full ELF or skeleton parity. The remaining object-adjacent and loader-facing segments stay explicitly blocked or deferred until more model parity exists.

## Current landed segment progress

The current starter implementation stays deliberately bounded:

- `cpu_mask.zig` ports the string-parsing core of `parse_cpu_mask_str()`
- the segment now includes an injected chunk-reader interface for sysfs-style buffered input without claiming direct file-descriptor parity
- the starter exposes dense `[]bool` mask output plus set-bit counting for future perf-buffer and feature-probe callers
- delimiter skipping accepts the newline-terminated `/sys/devices/system/cpu/possible` style input without widening into real file I/O
- malformed ranges still fail fast instead of silently stretching the segment into broader object or verifier-facing work
- `type_names.zig` ports the exported attach, link, map, and program type string tables as pure dense lookups over the current `tools/include/uapi/linux/bpf.h` ordinal space
- the type-name helper keeps unknown negative and oversized ordinals returning `null`, matching libbpf's bounded helper behavior without widening into name-to-type parsing or object lifecycle state
- `logging.zig` ports libbpf's bounded print-level parsing, verbosity gating, major or minor version reporting, and the libbpf-specific strerror table without claiming environment reads, stderr output, or full errno-name coverage
- the logging helper keeps invalid `LIBBPF_LOG_LEVEL`-style values explicit for callers instead of printing directly
- custom libbpf error text is exposed through a compact helper and unknown or unmapped codes fall back to a stable `"Unknown libbpf error N"` formatter
- `pin_path.zig` ports the pure pathname join and bpffs dot-sanitization helpers behind explicit buffer-based APIs that mirror `pathname_concat()`, `build_map_pin_path()`, and `sanitize_pin_path()`
- the pin-path helper defaults to `/sys/fs/bpf` when callers leave the root unset, but still keeps actual map pinning, directory creation, and filesystem validation outside the Zig slice
- pin-path overflows stay explicit as bounded helper errors instead of silently truncating output or widening into direct `PATH_MAX`, `mkdir()`, `statfs()`, or `unlink()` parity

The current tests check:

- mixed single-CPU and `start-end` ranges expand into the expected dense mask
- repeated delimiters and newline-terminated inputs still parse cleanly
- chunked reader input can split ranges and delimiters across scratch-buffer boundaries
- the bounded set-bit counter matches the parsed mask contents
- empty and malformed ranges report explicit errors
- reader contract failures stay explicit instead of silently truncating input
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

## Gates

1. run the dedicated Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig`

2. run the convenience target
- `make -C zigux phase8`

## Non-goals

This survey slice does not yet claim:

- any direct Zig port of `tools/lib/bpf/libbpf.c`
- `parse_cpu_mask_file()` parity or direct file reads
- direct `mkdir()`, `statfs()`, `unlink()`, or `bpf_obj_pin()` parity for map or program pinning
- direct `/proc/.../fdinfo` reads, `open()` or `close()` ownership, `bpf_obj_get()` reopen flows, or `bpf_token_create()` handle lifecycle parity
- BTF relocation parity
- ELF loader parity
- perf-buffer runtime behavior
- object-model parity for `bpf_object`, `bpf_map`, or `bpf_program`

## Next bounded step

Treat the Phase 8 helper-first entry as substantively landed for now: keep the shared Phase 8 gate honest, leave the new file or path or handle bridge segment explicitly deferred, and only reopen `tools/lib/bpf/zigux_segments/` for another bounded helper if fresh repo reality exposes one that stays smaller and lower risk than this direct resource-boundary cluster and the currently blocked object-model or loader-facing work.
