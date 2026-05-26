# Zigux `libbpf` Segments

This directory holds the bounded Phase 8 Zigux footholds for `tools/lib/bpf/libbpf.c`.

Current master materializes helper-first or helper-adjacent slices in:

- `cpu_mask.zig`
- `file_path_handle_bridge.zig`
- `logging.zig`
- `online_cpu_routing.zig`
- `perf_buffer_poll.zig`
- `perf_buffer_ready_window.zig`
- `pin_path.zig`
- `ready_buffer_fd_lookup.zig`
- `type_names.zig`

Each materialized slice is paired with focused `*_verify.zig` coverage so stable outputs stay reviewable without widening into loader, verifier, or object-model churn. The shared bridge foothold is now wired into the directory-level `verify.zig` aggregator through `file_path_handle_bridge_verify.zig`, so the stable-output aggregate replay covers the bridge helper packet without widening it beyond the current bounded slice.

## Current Repo Gap

Current master now carries the shared bridge destination for two helper-only footholds:

- bounded `/proc/.../fdinfo/<fd>` pathname shaping
- bounded fdinfo line splitting and trimming
- bounded reused-map name retention for NUL-terminated and fixed-width observations

The remaining numeric map-info decoder, full fdinfo metadata parser, reuse-compatibility summarizer, and token-planning helpers are still queued groundwork inside `file_path_handle_bridge.zig`, so fdinfo-map-info and map-reuse slices remain only partially landed.

## Still Deferred

The following Phase 8 families remain intentionally deferred:

- direct procfs reads, descriptor ownership flow, and other file-path or handle side effects
- broader online-CPU setup and `perf_event` wiring
- skeleton population
- object and ELF loader work
- BTF relocation and program-load flow

That keeps the directory aligned with the roadmap rule for segmented `libbpf` work: helper-first progress with stable outputs, not speculative mirror-tree expansion.
