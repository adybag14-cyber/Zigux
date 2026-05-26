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

Each materialized slice is paired with focused `*_verify.zig` coverage so stable outputs stay reviewable without widening into loader, verifier, or object-model churn. The new bridge foothold currently ships through `file_path_handle_bridge_verify.zig`; wiring it into the directory-level `verify.zig` aggregator remains a same-lane follow-up so this change stays bounded.

## Current Repo Gap

Current master now carries the shared bridge destination for two helper-only footholds:

- bounded `/proc/.../fdinfo/<fd>` pathname shaping
- bounded reused-map name retention for NUL-terminated and fixed-width observations

The remaining fdinfo text parser, numeric map-info decoder, reuse-compatibility summarizer, and token-planning helpers are still queued groundwork inside `file_path_handle_bridge.zig`, so fdinfo-map-info and map-reuse slices remain only partially landed.

## Still Deferred

The following Phase 8 families remain intentionally deferred:

- direct procfs reads, descriptor ownership flow, and other file-path or handle side effects
- broader online-CPU setup and `perf_event` wiring
- skeleton population
- object and ELF loader work
- BTF relocation and program-load flow

That keeps the directory aligned with the roadmap rule for segmented `libbpf` work: helper-first progress with stable outputs, not speculative mirror-tree expansion.
